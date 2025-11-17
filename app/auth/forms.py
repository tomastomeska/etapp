"""
Formuláře pro autentifikaci
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """Formulář pro přihlášení."""
    email = StringField('Email', validators=[
        DataRequired(message='Email je povinný'),
        Email(message='Zadejte platný email')
    ], render_kw={'placeholder': 'vas-email@europeantransport.cz'})
    
    password = PasswordField('Heslo', validators=[
        DataRequired(message='Heslo je povinné')
    ], render_kw={'placeholder': 'Vaše heslo'})
    
    remember_me = BooleanField('Zůstat přihlášen')
    submit = SubmitField('Přihlásit se')

class RegistrationForm(FlaskForm):
    """Formulář pro registraci nového uživatele."""
    username = StringField('Uživatelské jméno', validators=[
        DataRequired(message='Uživatelské jméno je povinné'),
        Length(min=4, max=20, message='Uživatelské jméno musí mít 4-20 znaků')
    ], render_kw={'placeholder': 'uzivatelskejmeno'})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email je povinný'),
        Email(message='Zadejte platný email')
    ], render_kw={'placeholder': 'vas-email@europeantransport.cz'})
    
    first_name = StringField('Křestní jméno', validators=[
        DataRequired(message='Křestní jméno je povinné'),
        Length(max=64, message='Křestní jméno je příliš dlouhé')
    ], render_kw={'placeholder': 'Jan'})
    
    last_name = StringField('Příjmení', validators=[
        DataRequired(message='Příjmení je povinné'),
        Length(max=64, message='Příjmení je příliš dlouhé')
    ], render_kw={'placeholder': 'Novák'})
    
    password = PasswordField('Heslo', validators=[
        DataRequired(message='Heslo je povinné'),
        Length(min=6, message='Heslo musí mít alespoň 6 znaků')
    ], render_kw={'placeholder': 'Minimálně 6 znaků'})
    
    password2 = PasswordField('Potvrdit heslo', validators=[
        DataRequired(message='Potvrzení hesla je povinné'),
        EqualTo('password', message='Hesla se neshodují')
    ], render_kw={'placeholder': 'Zopakujte heslo'})
    
    submit = SubmitField('Registrovat')
    
    def validate_username(self, username):
        """Kontrola jedinečnosti uživatelského jména."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Toto uživatelské jméno je již použito')
    
    def validate_email(self, email):
        """Kontrola jedinečnosti emailu."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Tento email je již registrován')

class ChangePasswordForm(FlaskForm):
    """Formulář pro změnu hesla."""
    old_password = PasswordField('Současné heslo', validators=[
        DataRequired(message='Současné heslo je povinné')
    ])
    
    password = PasswordField('Nové heslo', validators=[
        DataRequired(message='Nové heslo je povinné'),
        Length(min=6, message='Heslo musí mít alespoň 6 znaků')
    ])
    
    password2 = PasswordField('Potvrdit nové heslo', validators=[
        DataRequired(message='Potvrzení hesla je povinné'),
        EqualTo('password', message='Hesla se neshodují')
    ])
    
    submit = SubmitField('Změnit heslo')

class EditProfileForm(FlaskForm):
    """Formulář pro úpravu profilu."""
    username = StringField('Uživatelské jméno', validators=[
        DataRequired(message='Uživatelské jméno je povinné'),
        Length(min=4, max=20, message='Uživatelské jméno musí mít 4-20 znaků')
    ])
    
    first_name = StringField('Křestní jméno', validators=[
        DataRequired(message='Křestní jméno je povinné'),
        Length(max=64, message='Křestní jméno je příliš dlouhé')
    ])
    
    last_name = StringField('Příjmení', validators=[
        DataRequired(message='Příjmení je povinné'),
        Length(max=64, message='Příjmení je příliš dlouhé')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email je povinný'),
        Email(message='Zadejte platný email')
    ])
    
    phone = StringField('Telefon', validators=[
        Length(max=20, message='Telefon je příliš dlouhý')
    ], render_kw={'placeholder': '+420 XXX XXX XXX'})
    
    department = StringField('Oddělení', validators=[
        Length(max=100, message='Název oddělení je příliš dlouhý')
    ], render_kw={'placeholder': 'IT oddělení'})
    
    position = StringField('Pozice', validators=[
        Length(max=100, message='Název pozice je příliš dlouhý')
    ], render_kw={'placeholder': 'Programátor'})
    
    submit = SubmitField('Uložit změny')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        """Kontrola jedinečnosti uživatelského jména."""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Toto uživatelské jméno je již použito')
    
    def validate_email(self, email):
        """Kontrola jedinečnosti emailu."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Tento email je již registrován')

class RequestPasswordResetForm(FlaskForm):
    """Formulář pro žádost o obnovení hesla."""
    email = StringField('Email', validators=[
        DataRequired(message='Email je povinný'),
        Email(message='Zadejte platný email')
    ], render_kw={'placeholder': 'vas-email@europeantransport.cz'})
    
    submit = SubmitField('Poslat odkaz pro obnovení')

class ResetPasswordForm(FlaskForm):
    """Formulář pro nastavení nového hesla."""
    password = PasswordField('Nové heslo', validators=[
        DataRequired(message='Heslo je povinné'),
        Length(min=6, message='Heslo musí mít alespoň 6 znaků')
    ])
    
    password2 = PasswordField('Potvrdit heslo', validators=[
        DataRequired(message='Potvrzení hesla je povinné'),
        EqualTo('password', message='Hesla se neshodují')
    ])
    
    submit = SubmitField('Nastavit nové heslo')