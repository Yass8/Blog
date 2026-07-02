from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class PostForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(min=2, max=128)])
    body = TextAreaField('Contenu', validators=[DataRequired()])
    submit = SubmitField('Publier')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('S\'inscrire')

    # Validation personnalisée pour vérifier que l'email/nom n'existent pas déjà
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà pris.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cet email est déjà utilisé.')
        

class CommentForm(FlaskForm):
    body = TextAreaField('Votre commentaire', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Commenter')


class EditProfileForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Length(max=280)])
    submit = SubmitField('Enregistrer')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Ce nom d\'utilisateur est déjà pris.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Cet email est déjà utilisé.')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le nouveau mot de passe', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Changer le mot de passe')

class DeleteAccountForm(FlaskForm):
    password = PasswordField('Mot de passe pour confirmer', validators=[DataRequired()])
    submit = SubmitField('Supprimer mon compte')

class EmptyForm(FlaskForm):
    pass