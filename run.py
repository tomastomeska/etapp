#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
European Transport CZ s.r.o. - Firemní Aplikační Server
Hlavní spouštěcí skript
"""

import os
from app import create_app, db, socketio
from app.models import User, Role, Permission, News, Comment, Poll, PollOption, UserActivity
from flask_migrate import upgrade

def deploy():
    """Nasazení aplikace do produkce."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        # Vytvoření databázových tabulek
        db.create_all()
        
        # Vytvoření základních rolí
        Role.insert_roles()
        
        # Vytvoření administrátora pokud neexistuje
        admin_email = 'admin@europeantransport.cz'
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                username='admin',
                email=admin_email,
                first_name='Administrátor',
                last_name='Systému',
                confirmed=True
            )
            admin.set_password('admin123')
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin.role = admin_role
            db.session.add(admin)
            db.session.commit()
            print(f'Administrátor vytvořen: {admin_email} / admin123')

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    # Vytvoření tabulek a základních dat při prvním spuštění
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        
        # Kontrola existence administrátora
        admin_email = 'admin@europeantransport.cz'
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                username='admin',
                email=admin_email,
                first_name='Administrátor',
                last_name='Systému',
                confirmed=True
            )
            admin.set_password('admin123')
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin.role = admin_role
            db.session.add(admin)
            db.session.commit()
            print(f'✓ Administrátor vytvořen: {admin_email} / admin123')
        
        # Vytvoření testovacího uživatele
        user_email = 'user@europeantransport.cz'
        if not User.query.filter_by(email=user_email).first():
            user = User(
                username='testuser',
                email=user_email,
                first_name='Test',
                last_name='Uživatel',
                confirmed=True
            )
            user.set_password('user123')
            user_role = Role.query.filter_by(name='Uživatel').first()
            user.role = user_role
            db.session.add(user)
            db.session.commit()
            print(f'✓ Testovací uživatel vytvořen: {user_email} / user123')
    
    print('='*50)
    print('🚀 European Transport CZ - Aplikační Server')
    print('='*50)
    print('📍 URL: http://localhost:5000')
    print('👤 Admin: admin@europeantransport.cz / admin123')
    print('👤 User:  user@europeantransport.cz / user123')
    print('='*50)
    
    # Spuštění aplikace
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)