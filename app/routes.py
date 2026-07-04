from flask import Blueprint, flash, render_template, redirect, url_for, request, make_response
from app.forms import PostForm, CommentForm
from app.models import Post, Comment
from flask_login import login_required, current_user
from app import db
from functools import wraps

bp = Blueprint('main', __name__)

# Décorateur personnalisé pour restreindre aux owners
def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_owner:
            flash("Vous n'avez pas les droits nécessaires.", 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@bp.route('/sitemap.xml')
def sitemap():
    pages = [
        {'loc': url_for('main.index', _external=True), 'changefreq': 'daily', 'priority': '1.0'},
        # Ajoute ici des pages statiques (about, contact) si tu en as
    ]
    posts = Post.query.all()
    for post in posts:
        pages.append({
            'loc': url_for('main.post', slug=post.slug, _external=True),
            'lastmod': post.timestamp.strftime('%Y-%m-%d'),
            'changefreq': 'weekly',
            'priority': '0.8'
        })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{page["loc"]}</loc>\n'
        if 'lastmod' in page:
            xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += '  </url>\n'
    xml += '</urlset>'

    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@bp.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: " + url_for('main.sitemap', _external=True)
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response

@bp.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = CommentForm()
    # Traitement du commentaire (POST)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Connectez-vous pour commenter.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        parent_id = request.form.get('parent_id')  # None si commentaire principal
        if parent_id:
            parent = Comment.query.get(int(parent_id))
            if parent is None or parent.post_id != post.id:
                flash('Réponse invalide.', 'danger')
                return redirect(url_for('main.post', slug=post.slug))

        comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            post_id=post.id,
            parent_id=int(parent_id) if parent_id else None
        )
        db.session.add(comment)
        db.session.commit()
        flash('Commentaire ajouté.', 'success')
        return redirect(url_for('main.post', slug=post.slug))

    # Affichage : récupérer les commentaires de premier niveau
    top_comments = Comment.query.filter_by(post_id=post.id, parent_id=None)\
                                .order_by(Comment.timestamp.asc()).all()
    return render_template('post.html', post=post, form=form, top_comments=top_comments)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@owner_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        slug = Post.make_slug(form.title.data)
        # Assurer l'unicité en cas de doublon
        original_slug = slug
        counter = 1
        while Post.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        post = Post(title=form.title.data, body=form.body.data, slug=slug, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Article créé avec succès !', 'success')
        return redirect(url_for('main.post', slug=slug))
    return render_template('create_post.html', form=form)

@bp.route('/post/<slug>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author != current_user:
        flash('Vous ne pouvez pas modifier cet article.', 'danger')
        return redirect(url_for('main.index'))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        new_slug = Post.make_slug(form.title.data)
        if new_slug != post.slug:
            # Vérifier l'unicité
            original_slug = new_slug
            counter = 1
            while Post.query.filter(Post.slug == new_slug, Post.id != post.id).first():
                new_slug = f"{original_slug}-{counter}"
                counter += 1
            post.slug = new_slug
        db.session.commit()
        flash('Article modifié avec succès.', 'success')
        return redirect(url_for('main.post', slug=post.slug))
    return render_template('edit_post.html', form=form, post=post)

@bp.route('/post/<slug>/delete', methods=['POST'])
@login_required
@owner_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author != current_user:
        flash('Vous ne pouvez pas supprimer cet article.', 'danger')
        return redirect(url_for('main.index'))
    db.session.delete(post)
    db.session.commit()
    flash('Article supprimé.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    # Seul l'auteur du commentaire peut l'éditer
    if comment.user_id != current_user.id:
        flash("Vous ne pouvez pas modifier ce commentaire.", 'danger')
        return redirect(url_for('main.post', post_id=comment.post_id))

    form = CommentForm(obj=comment)
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.commit()
        flash('Commentaire modifié.', 'success')
        return redirect(url_for('main.post', post_id=comment.post_id))
    return render_template('edit_comment.html', form=form, comment=comment)


@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    # Seul l'auteur du commentaire ou un owner peut supprimer
    if comment.user_id != current_user.id and not current_user.is_owner:
        flash("Vous ne pouvez pas supprimer ce commentaire.", 'danger')
        return redirect(url_for('main.post', post_id=comment.post_id))

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Commentaire supprimé.', 'info')
    return redirect(url_for('main.post', post_id=post_id))