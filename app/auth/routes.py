"""
Autentifikační routes - přihlašování, odhlašování, registrace
"""

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm, EditProfileForm
from app.models import User, Role

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlašovací stránka."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Neplatné přihlašovací údaje', 'danger')
            # Log neúspěšný pokus o přihlášení
            if user:
                user.log_activity('failed_login', 'Neúspěšný pokus o přihlášení', 
                                request.remote_addr)
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Váš účet byl deaktivován. Kontaktujte administrátora.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Úspěšné přihlášení
        login_user(user, remember=form.remember_me.data)
        user.last_seen = datetime.utcnow()
        user.last_login_ip = request.remote_addr
        db.session.commit()
        
        # Log úspěšné přihlášení
        user.log_activity('login', 'Úspěšné přihlášení do systému', request.remote_addr)
        
        flash(f'Vítejte zpět, {user.get_full_name()}!', 'success')
        
        # Přesměrování na původně požadovanou stránku
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Přihlášení', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Odhlášení uživatele."""
    # Log odhlášení
    current_user.log_activity('logout', 'Odhlášení ze systému', request.remote_addr)
    
    logout_user()
    flash('Byli jste úspěšně odhlášeni', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registrační stránka - pouze pro administrátory."""
    if current_user.is_authenticated:
        if not current_user.is_administrator():
            flash('Nemáte oprávnění k registraci nových uživatelů', 'danger')
            return redirect(url_for('main.index'))
    else:
        # Pokud není nikdo přihlášen, přesměruj na login
        return redirect(url_for('auth.login'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Vytvoření nového uživatele
        user = User(
            username=form.username.data.lower(),
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            confirmed=True  # Administrátor vytváří již potvrzené účty
        )
        user.set_password(form.password.data)
        
        # Přiřazení výchozí role
        default_role = Role.query.filter_by(default=True).first()
        if default_role:
            user.role = default_role
        
        db.session.add(user)
        db.session.commit()
        
        # Log vytvoření uživatele
        current_user.log_activity('user_created', 
                                f'Vytvořen nový uživatel: {user.username}',
                                request.remote_addr)
        
        flash(f'Uživatel {user.get_full_name()} byl úspěšně vytvořen', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('auth/register.html', title='Registrace uživatele', form=form)

@bp.route('/profile')
@login_required
def profile():
    """Profil uživatele."""
    return render_template('auth/profile.html', title='Můj profil')

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Úprava profilu uživatele."""
    form = EditProfileForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        current_user.username = form.username.data.lower()
        current_user.email = form.email.data.lower()
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.department = form.department.data
        current_user.position = form.position.data
        
        db.session.commit()
        
        # Log úpravy profilu
        current_user.log_activity('profile_updated', 'Aktualizace profilu', 
                                request.remote_addr)
        
        flash('Váš profil byl úspěšně aktualizován', 'success')
        return redirect(url_for('auth.profile'))
    
    elif request.method == 'GET':
        # Předvyplnění formuláře
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
        form.department.data = current_user.department
        form.position.data = current_user.position
    
    return render_template('auth/edit_profile.html', title='Upravit profil', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Změna hesla."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Současné heslo není správné', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.password.data)
        db.session.commit()
        
        # Log změny hesla
        current_user.log_activity('password_changed', 'Změna hesla', request.remote_addr)
        
        flash('Vaše heslo bylo úspěšně změněno', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', title='Změnit heslo', form=form)

@bp.before_app_request
def before_request():
    """Funkce spuštěná před každým requestem."""
    if current_user.is_authenticated:
        current_user.ping()  # Aktualizace času poslední aktivity