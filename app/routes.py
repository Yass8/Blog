from flask import Blueprint, flash, render_template, redirect, url_for, request
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

@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
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
                return redirect(url_for('main.post', post_id=post.id))

        comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            post_id=post.id,
            parent_id=int(parent_id) if parent_id else None
        )
        db.session.add(comment)
        db.session.commit()
        flash('Commentaire ajouté.', 'success')
        return redirect(url_for('main.post', post_id=post.id))

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
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Article créé avec succès !', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_post.html', form=form)


@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('Vous ne pouvez pas modifier cet article.', 'danger')
        return redirect(url_for('main.index'))
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash('Article modifié avec succès.', 'success')
        return redirect(url_for('main.post', post_id=post.id))
    return render_template('edit_post.html', form=form, post=post)


@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
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