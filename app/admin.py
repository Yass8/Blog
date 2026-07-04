from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.forms import EmptyForm
from app.models import User
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_owner:
            flash("Accès réservé aux propriétaires.", 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users')
@login_required
@owner_required
def user_list():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@owner_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    form = EmptyForm()

    if form.validate_on_submit():
        if 'toggle_role' in request.form:
            if request.method == 'POST':
                if 'toggle_role' in request.form:
                    # Ne pas se rétrograder soi-même
                    if user.id == current_user.id:
                        flash('Vous ne pouvez pas modifier votre propre rôle ici.', 'warning')
                    else:
                        user.is_owner = not user.is_owner
                        db.session.commit()
                        flash(f'Rôle de {user.username} mis à jour.', 'success')
                elif 'delete_user' in request.form:
                    if user.id == current_user.id:
                        flash('Vous ne pouvez pas vous supprimer vous-même depuis cette interface.', 'warning')
                    else:
                        db.session.delete(user)
                        db.session.commit()
                        flash(f'Utilisateur {user.username} supprimé.', 'info')
                        return redirect(url_for('admin.user_list'))
                return redirect(url_for('admin.user_detail', user_id=user.id))
    return render_template('admin/user_detail.html', user=user, form=form)