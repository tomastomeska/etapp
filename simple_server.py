#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simplified main app without complex templates
"""

import os
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-secret-key-123'

# Jednoduchá "databáze" uživatelů
USERS = {
    'admin@europeantransport.cz': {
        'password': generate_password_hash('admin123'),
        'name': 'Administrátor Systému',
        'role': 'admin'
    },
    'user@europeantransport.cz': {
        'password': generate_password_hash('user123'),
        'name': 'Test Uživatel',
        'role': 'user'
    }
}

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>European Transport CZ - {{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; }
        .navbar { background: #2c5aa0 !important; }
        .card { box-shadow: 0 0 15px rgba(0,0,0,0.1); }
        .btn-primary { background: #2c5aa0; border-color: #2c5aa0; }
        .logo { font-weight: bold; color: white !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand logo" href="/">🚛 European Transport CZ</a>
            <div class="navbar-nav ms-auto">
                {% if session.user %}
                    <span class="navbar-text me-3">👤 {{ session.user.name }}</span>
                    <a class="nav-link" href="/logout">Odhlásit</a>
                {% else %}
                    <a class="nav-link" href="/login">Přihlásit</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' if category == 'success' else 'info' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {{ content | safe }}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    """Hlavní stránka."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    content = f"""
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3>🏠 Vítejte v aplikačním serveru</h3>
                </div>
                <div class="card-body">
                    <h4>Vítejte, {session['user']['name']}!</h4>
                    <p class="lead">Úspěšně jste přihlášeni do firemního aplikačního serveru European Transport CZ s.r.o.</p>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h5>📰 Novinky</h5>
                                    <p>Firemní novinky a oznámení</p>
                                    <a href="#" class="btn btn-primary">Zobrazit</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body text-center">
                                    <h5>💬 Zprávy</h5>
                                    <p>Interní komunikace</p>
                                    <a href="#" class="btn btn-primary">Zobrazit</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>ℹ️ Systémové informace</h5>
                </div>
                <div class="card-body">
                    <p><strong>Uživatel:</strong> {session['user']['name']}</p>
                    <p><strong>Role:</strong> {session['user']['role']}</p>
                    <p><strong>Stav:</strong> <span class="badge bg-success">Online</span></p>
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(BASE_TEMPLATE, title="Dashboard", content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlašovací stránka."""
    if 'user' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        
        if email in USERS and check_password_hash(USERS[email]['password'], password):
            session['user'] = {
                'email': email,
                'name': USERS[email]['name'],
                'role': USERS[email]['role']
            }
            flash('Úspěšně přihlášeno!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Neplatné přihlašovací údaje!', 'error')
    
    login_form = """
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header text-center">
                    <h3>🔐 Přihlášení</h3>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email:</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Heslo:</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Přihlásit se</button>
                    </form>
                    
                    <hr>
                    <div class="text-muted small">
                        <strong>Testovací účty:</strong><br>
                        📧 admin@europeantransport.cz / admin123<br>
                        📧 user@europeantransport.cz / user123
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(BASE_TEMPLATE, title="Přihlášení", content=login_form)

@app.route('/logout')
def logout():
    """Odhlášení."""
    session.pop('user', None)
    flash('Úspěšně odhlášeno!', 'info')
    return redirect(url_for('login'))

@app.route('/test')
def test():
    """Test endpoint."""
    return {
        "status": "OK", 
        "app": "European Transport CZ - Simplified",
        "user": session.get('user', 'Not logged in')
    }

if __name__ == '__main__':
    print("="*50)
    print("🚀 European Transport CZ - SIMPLIFIED SERVER")
    print("="*50)
    print("📍 URL: http://127.0.0.1:5003")
    print("👤 Admin: admin@europeantransport.cz / admin123")
    print("👤 User:  user@europeantransport.cz / user123")
    print("="*50)
    
    app.run(debug=True, host='127.0.0.1', port=5003)