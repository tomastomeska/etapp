"""
Formuláře pro hlavní část aplikace
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed

class NewsForm(FlaskForm):
    """Formulář pro vytváření a úpravu novinek."""
    title = StringField('Nadpis', validators=[
        DataRequired(message='Nadpis je povinný'),
        Length(max=200, message='Nadpis je příliš dlouhý')
    ], render_kw={'placeholder': 'Zadejte nadpis novinky'})
    
    summary = TextAreaField('Shrnutí', validators=[
        Length(max=300, message='Shrnutí je příliš dlouhé')
    ], render_kw={
        'placeholder': 'Krátké shrnutí novinky (zobrazí se v přehledu)',
        'rows': 3
    })
    
    content = TextAreaField('Obsah', validators=[
        DataRequired(message='Obsah je povinný')
    ], render_kw={
        'placeholder': 'Zde napište obsah novinky...',
        'rows': 10
    })
    
    image = FileField('Obrázek', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Povolené formáty: JPG, PNG, GIF')
    ])
    
    featured = BooleanField('Zvýraznit noviku')
    allow_comments = BooleanField('Povolit komentáře', default=True)
    published = BooleanField('Publikovat ihned', default=True)
    
    submit = SubmitField('Uložit')

class CommentForm(FlaskForm):
    """Formulář pro komentáře."""
    content = TextAreaField('Komentář', validators=[
        DataRequired(message='Komentář nemůže být prázdný'),
        Length(max=1000, message='Komentář je příliš dlouhý')
    ], render_kw={
        'placeholder': 'Napište svůj komentář...',
        'rows': 4
    })
    
    submit = SubmitField('Přidat komentář')

class PollForm(FlaskForm):
    """Formulář pro vytváření anket."""
    question = StringField('Otázka', validators=[
        DataRequired(message='Otázka je povinná'),
        Length(max=200, message='Otázka je příliš dlouhá')
    ], render_kw={'placeholder': 'Zadejte otázku ankety'})
    
    description = TextAreaField('Popis', validators=[
        Length(max=500, message='Popis je příliš dlouhý')
    ], render_kw={
        'placeholder': 'Volitelný popis ankety',
        'rows': 3
    })
    
    # Možnosti budou přidávány dynamicky přes JavaScript
    option1 = StringField('Možnost 1', validators=[
        DataRequired(message='Alespoň jedna možnost je povinná')
    ])
    option2 = StringField('Možnost 2', validators=[
        DataRequired(message='Alespoň dvě možnosti jsou povinné')
    ])
    option3 = StringField('Možnost 3')
    option4 = StringField('Možnost 4')
    option5 = StringField('Možnost 5')
    
    multiple_choice = BooleanField('Povolit více odpovědí')
    anonymous = BooleanField('Anonymní hlasování')
    
    submit = SubmitField('Vytvořit anketu')

class MessageForm(FlaskForm):
    """Formulář pro zprávy."""
    recipient = SelectField('Příjemce', coerce=int, validators=[
        DataRequired(message='Vyberte příjemce')
    ])
    
    subject = StringField('Předmět', validators=[
        DataRequired(message='Předmět je povinný'),
        Length(max=200, message='Předmět je příliš dlouhý')
    ], render_kw={'placeholder': 'Zadejte předmět zprávy'})
    
    body = TextAreaField('Zpráva', validators=[
        DataRequired(message='Zpráva nemůže být prázdná')
    ], render_kw={
        'placeholder': 'Napište svou zprávu...',
        'rows': 8
    })
    
    priority = SelectField('Priorita', choices=[
        ('low', 'Nízká'),
        ('normal', 'Normální'),
        ('high', 'Vysoká')
    ], default='normal')
    
    submit = SubmitField('Odeslat zprávu')

class BroadcastMessageForm(FlaskForm):
    """Formulář pro hromadné zprávy."""
    subject = StringField('Předmět', validators=[
        DataRequired(message='Předmět je povinný'),
        Length(max=200, message='Předmět je příliš dlouhý')
    ], render_kw={'placeholder': 'Zadejte předmět zprávy'})
    
    body = TextAreaField('Zpráva', validators=[
        DataRequired(message='Zpráva nemůže být prázdná')
    ], render_kw={
        'placeholder': 'Napište zprávu pro všechny uživatele...',
        'rows': 8
    })
    
    priority = SelectField('Priorita', choices=[
        ('low', 'Nízká'),
        ('normal', 'Normální'),
        ('high', 'Vysoká')
    ], default='normal')
    
    submit = SubmitField('Odeslat všem')

class SearchForm(FlaskForm):
    """Formulář pro vyhledávání."""
    query = StringField('Hledat', validators=[
        DataRequired(message='Zadejte hledaný výraz')
    ], render_kw={'placeholder': 'Hledat v novinkách, komentářích...'})
    
    submit = SubmitField('Hledat')