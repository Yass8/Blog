from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app import db
from app.models import User
from app.forms import EditProfileForm, ChangePasswordForm, DeleteAccountForm

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def view():
    delete_form = DeleteAccountForm()
    return render_template('profile/view.html', user=current_user, delete_form=delete_form)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm(current_user.username, current_user.email, obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Profil mis à jour.', 'success')
        return redirect(url_for('profile.view'))
    return render_template('profile/edit.html', form=form)

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Mot de passe actuel incorrect.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Mot de passe modifié.', 'success')
            return redirect(url_for('profile.view'))
    return render_template('profile/change_password.html', form=form)

@profile_bp.route('/delete', methods=['POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash('Mot de passe incorrect.', 'danger')
            return redirect(url_for('profile.view'))
        # Déconnexion puis suppression
        user = current_user._get_current_object()
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('Votre compte a été supprimé.', 'info')
        return redirect(url_for('main.index'))
    return redirect(url_for('profile.view'))