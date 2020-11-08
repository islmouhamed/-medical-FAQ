from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from sadm.models import User, Post

class RegistrationForm(FlaskForm):
    name = StringField('nom',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('prénom',
                           validators=[DataRequired(), Length(min=2, max=20)])
    nai_date = DateField('date de naissance', format='%d/%m/%Y')
                           
    adresse = StringField('adresse',
                           validators=[DataRequired(), Length(min=2, max=60)])
    
    num_pro = StringField(' Num profesionelle', validators=[DataRequired(), Length(min=8, max=20)])
                          
    
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    specialite = RadioField('Spécialité ', choices=[('value', 'neurologue'), ('value_two', 'radiologue')])
    
    submit = SubmitField('inscrire')
   
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ce email  est pris. S’il vous plaît choisir un autre.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('mot de passe ', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('connexion')

class UpdateAccountForm(FlaskForm):
    name = StringField('nom',
                           validators=[DataRequired(), Length(min=2, max=20)])
    firstname = StringField('prénom',
                           validators=[DataRequired(), Length(min=2, max=20)])
    nai_date = DateField('date de naissance', format='%d/%m/%Y')
                           
    adresse = StringField('adresse',
                           validators=[DataRequired(), Length(min=2, max=60)])
    num_pro = StringField(' Num profesionelle', validators=[DataRequired(), Length(min=8, max=20)])
    
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('importé image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Modifier')
   
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
class PostForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    picture1 = FileField('importé image', validators=[FileAllowed(['jpg', 'png'])])
    content = TextAreaField('Contenus', validators=[DataRequired()])
    submit = SubmitField('Posté')
    
    
                
                
class AddCommentForm(FlaskForm):
    body = StringField("Body", validators=[DataRequired()])
    submit = SubmitField("Post")


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')