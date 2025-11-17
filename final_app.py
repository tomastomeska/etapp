#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
European Transport CZ - Kompletni funkci aplikace
"""

import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'european-transport-secret-key-2024'

# Simulovana databaze
USERS = {
    'admin@europeantransport.cz': {
        'id': 1,
        'password': generate_password_hash('admin123'),
        'name': 'Administrator Systemu',
        'role': 'admin',
        'avatar': '👨‍💼',
        'status': 'online',
        'created': '2024-01-01'
    },
    'user@europeantransport.cz': {
        'id': 2,
        'password': generate_password_hash('user123'),
        'name': 'Jan Novak',
        'role': 'user',
        'avatar': '👤',
        'status': 'online',
        'created': '2024-02-15'
    },
    'marie@europeantransport.cz': {
        'id': 3,
        'password': generate_password_hash('marie123'),
        'name': 'Marie Svobodova',
        'role': 'user',
        'avatar': '👩',
        'status': 'offline',
        'created': '2024-03-10'
    }
}

NEWS = [
    {
        'id': 1,
        'title': 'Novy system pro spravu vozidel',
        'content': 'Spoustime novy modul pro spravu vozoveho parku. Umozni lepsi sledovani udrzby a spotreby paliva.',
        'author': 'Administrator Systemu',
        'created': '2024-11-10 10:30',
        'featured': True,
        'comments': []
    },
    {
        'id': 2,
        'title': 'Aktualizace bezpecnostnich protokolu',
        'content': 'Vsichni ridici si prosim prostudujte nove bezpecnostni smernice v priloze.',
        'author': 'Administrator Systemu',
        'created': '2024-11-08 14:15',
        'featured': False,
        'comments': [
            {'author': 'Jan Novak', 'text': 'Dokumenty jsem prostudoval', 'time': '2024-11-09 08:00'}
        ]
    }
]

MESSAGES = [
    {
        'id': 1,
        'from': 'Administrator Systemu',
        'to': 'Jan Novak',
        'subject': 'Nove smernice',
        'content': 'Zdravim Jene, prosim prostuduj si nove smernice pro mezinarodni prepravu.',
        'created': '2024-11-12 09:15',
        'read': False
    }
]

APPLICATIONS = [
    {'id': 1, 'name': 'Sprava vozidel', 'icon': '🚛', 'status': 'planned', 'description': 'Modul pro spravu vozoveho parku'},
    {'id': 2, 'name': 'GPS tracking', 'icon': '📍', 'status': 'planned', 'description': 'Sledovani pozice vozidel'},
    {'id': 3, 'name': 'Sklady', 'icon': '📦', 'status': 'planned', 'description': 'Sprava skladovych zasob'},
    {'id': 4, 'name': 'Ucetnictvi', 'icon': '💰', 'status': 'planned', 'description': 'Financni modul'},
]

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>European Transport CZ - {{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background: linear-gradient(135deg, #2c5aa0 0%, #1e3a72 100%) !important; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card { box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: none; transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); }
        .btn-primary { background: #2c5aa0; border-color: #2c5aa0; }
        .btn-primary:hover { background: #1e3a72; }
        .logo { font-weight: bold; color: white !important; font-size: 1.2rem; }
        .admin-badge { background: linear-gradient(45deg, #dc3545, #fd7e14); color: white; }
        .user-badge { background: linear-gradient(45deg, #198754, #20c997); color: white; }
        .news-card { border-left: 4px solid #2c5aa0; }
        .featured-news { border-left: 4px solid #dc3545; background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%); }
        .app-tile { 
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
            border: 2px dashed #dee2e6; 
            transition: all 0.3s;
            cursor: pointer;
        }
        .app-tile:hover { border-color: #2c5aa0; background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%); }
        .message-item { border-left: 3px solid #17a2b8; }
        .unread { background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%); border-left-color: #dc3545; }
        .sidebar { background: white; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        .content-section { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .admin-panel { background: linear-gradient(135deg, #fff3cd 0%, #ffffff 100%); border: 1px solid #ffeaa7; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand logo" href="/">🚛 European Transport CZ</a>
            <div class="navbar-nav ms-auto">
                {% if session.user %}
                    <span class="navbar-text me-3">
                        {{ session.user.avatar }} {{ session.user.name }}
                        <span class="badge ms-1 {{ 'admin-badge' if session.user.role == 'admin' else 'user-badge' }}">
                            {{ session.user.role|title }}
                        </span>
                    </span>
                    <a class="nav-link" href="/logout"><i class="bi bi-box-arrow-right"></i> Odhlasit</a>
                {% else %}
                    <a class="nav-link" href="/login"><i class="bi bi-box-arrow-in-right"></i> Prihlasit</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' if category == 'success' else 'info' }} alert-dismissible fade show">
                        <i class="bi bi-{{ 'exclamation-triangle' if category == 'error' else 'check-circle' if category == 'success' else 'info-circle' }}"></i>
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {{ content | safe }}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function toggleSection(sectionId) {
            const section = document.getElementById(sectionId);
            if (section.style.display === 'none') {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Hlavni dashboard - vse na jedne strance."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    is_admin = user['role'] == 'admin'
    
    # Pocitani statistik
    unread_messages = len([m for m in MESSAGES if not m['read']])
    total_users = len(USERS)
    total_news = len(NEWS)
    
    # Generovani obsahu
    news_html = ""
    for news in NEWS:
        card_class = "featured-news" if news.get("featured") else "news-card"
        star = "⭐ " if news.get("featured") else ""
        comments_count = len(news.get("comments", []))
        comments_html = f'<div class="mt-2"><small class="text-muted">💬 {comments_count} komentaru</small></div>' if comments_count > 0 else ""
        
        news_html += f'''
        <div class="card mb-3 {card_class}">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <h6>{star}{news["title"]}</h6>
                    <small class="text-muted">{news["created"]}</small>
                </div>
                <p>{news["content"]}</p>
                <small class="text-muted">Autor: {news["author"]}</small>
                {comments_html}
            </div>
        </div>
        '''
    
    # Zpravy
    messages_html = ""
    for message in MESSAGES:
        unread_class = "unread" if not message["read"] else ""
        messages_html += f'''
        <div class="card mb-2 message-item {unread_class}">
            <div class="card-body p-3">
                <div class="d-flex justify-content-between">
                    <strong>{message["subject"]}</strong>
                    <small class="text-muted">{message["created"]}</small>
                </div>
                <p class="mb-1">{message["content"][:100]}...</p>
                <small class="text-muted">Od: {message["from"]} → {message["to"]}</small>
            </div>
        </div>
        '''
    
    # Aplikace
    apps_html = ""
    for app in APPLICATIONS:
        apps_html += f'''
        <div class="col-md-3 mb-3">
            <div class="card app-tile text-center p-3">
                <div style="font-size: 2rem;">{app["icon"]}</div>
                <h6>{app["name"]}</h6>
                <p class="small text-muted">{app["description"]}</p>
                <span class="badge bg-warning">Planovano</span>
            </div>
        </div>
        '''
    
    # Sprava uzivatelu
    users_html = ""
    if is_admin:
        users_html = '<div class="table-responsive"><table class="table"><thead><tr><th>Uzivatel</th><th>Email</th><th>Role</th><th>Status</th><th>Akce</th></tr></thead><tbody>'
        for email, usr in USERS.items():
            role_badge = "admin-badge" if usr["role"] == "admin" else "user-badge"
            status_badge = "success" if usr["status"] == "online" else "secondary"
            action_btn = "Deaktivovat" if usr["status"] == "online" else "Aktivovat"
            
            users_html += f'''
            <tr>
                <td>{usr["avatar"]} {usr["name"]}</td>
                <td>{email}</td>
                <td><span class="badge {role_badge}">{usr["role"]}</span></td>
                <td><span class="badge bg-{status_badge}">{usr["status"]}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary">Editovat</button>
                    <button class="btn btn-sm btn-outline-danger">{action_btn}</button>
                </td>
            </tr>
            '''
        users_html += '</tbody></table></div><button class="btn btn-success">+ Pridat uzivatele</button>'
    
    content = f'''
    <div class="row">
        <!-- Levy panel -->
        <div class="col-md-3">
            <div class="sidebar p-3">
                <h5><i class="bi bi-person-circle"></i> Profil</h5>
                <p><strong>{user["name"]}</strong><br>
                <small class="text-muted">{user["role"].title()} ucet</small></p>
                
                <h6 class="mt-4"><i class="bi bi-graph-up"></i> Statistiky</h6>
                <ul class="list-unstyled">
                    <li>📰 Novinek: {total_news}</li>
                    <li>💬 Neprecteno: {unread_messages}</li>
                    <li>👥 Uzivatelu: {total_users}</li>
                    <li>🕒 Online: {datetime.now().strftime("%H:%M")}</li>
                </ul>
            </div>
            
            {f'<div class="admin-panel mt-3 p-3"><h6><i class="bi bi-gear"></i> Administrace</h6><button class="btn btn-sm btn-primary w-100 mb-2" onclick="toggleSection(\'admin-tools\')">Sprava systemu</button><button class="btn btn-sm btn-outline-primary w-100 mb-2" onclick="toggleSection(\'user-management\')">Sprava uzivatelu</button><button class="btn btn-sm btn-outline-primary w-100" onclick="toggleSection(\'add-news\')">Pridat novinku</button></div>' if is_admin else ''}
        </div>
        
        <!-- Hlavni obsah -->
        <div class="col-md-9">
            
            {f'<div id="admin-tools" class="content-section admin-panel" style="display:none;"><h5><i class="bi bi-tools"></i> Administrativni nastroje</h5><div class="row"><div class="col-md-6"><h6>Systemove akce</h6><button class="btn btn-warning btn-sm me-2">Restart systemu</button><button class="btn btn-info btn-sm me-2">Backup DB</button><button class="btn btn-secondary btn-sm">Logy</button></div><div class="col-md-6"><h6>Statistiky systemu</h6><p>Aktivni uzivatele: 2<br>Vyuziti mista: 45%<br>Posledni backup: 12.11.2024</p></div></div></div>' if is_admin else ''}
            
            {f'<div id="user-management" class="content-section" style="display:none;"><h5><i class="bi bi-people"></i> Sprava uzivatelu</h5>{users_html}</div>' if is_admin else ''}
            
            {f'<div id="add-news" class="content-section" style="display:none;"><h5><i class="bi bi-newspaper"></i> Pridat novinku</h5><form method="POST" action="/add_news"><div class="mb-3"><label class="form-label">Nadpis</label><input type="text" class="form-control" name="title" required></div><div class="mb-3"><label class="form-label">Obsah</label><textarea class="form-control" name="content" rows="4" required></textarea></div><div class="form-check mb-3"><input type="checkbox" class="form-check-input" name="featured" id="featured"><label class="form-check-label" for="featured">Oznacit jako dulezite</label></div><button type="submit" class="btn btn-primary">Publikovat</button></form></div>' if is_admin else ''}
            
            <!-- Novinky -->
            <div class="content-section">
                <h5><i class="bi bi-newspaper"></i> Firemni novinky</h5>
                {news_html}
                {f'<button class="btn btn-sm btn-outline-primary" onclick="toggleSection(\'add-news\')">+ Pridat novinku</button>' if is_admin else ''}
            </div>
            
            <!-- Zpravy -->
            <div class="content-section">
                <h5><i class="bi bi-envelope"></i> Interni zpravy</h5>
                {messages_html}
                <button class="btn btn-sm btn-success">✉️ Napsat zpravu</button>
                {f'<button class="btn btn-sm btn-outline-primary ms-2">📢 Hromadne oznameni</button>' if is_admin else ''}
            </div>
            
            <!-- Budouci aplikace -->
            <div class="content-section">
                <h5><i class="bi bi-grid"></i> Firemni aplikace</h5>
                <div class="row">
                    {apps_html}
                    {f'<div class="col-md-3 mb-3"><div class="card app-tile text-center p-3"><div style="font-size: 2rem;">➕</div><h6>Nova aplikace</h6><p class="small text-muted">Pridat modul</p><button class="btn btn-sm btn-primary">Vytvorit</button></div></div>' if is_admin else ''}
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Dashboard", content=content)

@app.route('/add_news', methods=['POST'])
def add_news():
    """Pridani nove novinky."""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    featured = 'featured' in request.form
    
    new_news = {
        'id': max([n['id'] for n in NEWS], default=0) + 1,
        'title': title,
        'content': content,
        'author': session['user']['name'],
        'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'featured': featured,
        'comments': []
    }
    
    NEWS.insert(0, new_news)
    flash('Novinka byla uspesne pridana!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Prihlasovaci stranka."""
    if 'user' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        
        if email in USERS and check_password_hash(USERS[email]['password'], password):
            session['user'] = USERS[email].copy()
            session['user']['email'] = email
            flash(f'Vitejte, {USERS[email]["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Neplatne prihlasovaci udaje!', 'error')
    
    login_form = '''
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header text-center" style="background: linear-gradient(135deg, #2c5aa0 0%, #1e3a72 100%); color: white;">
                    <h3><i class="bi bi-shield-lock"></i> Prihlaseni do systemu</h3>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="email" class="form-label"><i class="bi bi-envelope"></i> Email:</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label"><i class="bi bi-lock"></i> Heslo:</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100"><i class="bi bi-box-arrow-in-right"></i> Prihlasit se</button>
                    </form>
                    
                    <hr>
                    <div class="text-muted small">
                        <strong><i class="bi bi-info-circle"></i> Testovaci ucty:</strong><br>
                        👨‍💼 <strong>Admin:</strong> admin@europeantransport.cz / admin123<br>
                        👤 <strong>User:</strong> user@europeantransport.cz / user123<br>
                        👩 <strong>User:</strong> marie@europeantransport.cz / marie123
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Prihlaseni", content=login_form)

@app.route('/logout')
def logout():
    """Odhlaseni."""
    name = session.get('user', {}).get('name', 'Uzivatel')
    session.pop('user', None)
    flash(f'Nashledanou, {name}!', 'info')
    return redirect(url_for('login'))

@app.route('/api/stats')
def api_stats():
    """API endpoint pro statistiky."""
    return {
        "users": len(USERS),
        "news": len(NEWS),
        "messages": len(MESSAGES),
        "applications": len(APPLICATIONS),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == '__main__':
    print("="*60)
    print("🚀 European Transport CZ - KOMPLETNI APLIKACE")
    print("="*60)
    print("📍 URL: http://127.0.0.1:5004")
    print("👨‍💼 Admin: admin@europeantransport.cz / admin123")
    print("👤 User:  user@europeantransport.cz / user123")
    print("👩 User:  marie@europeantransport.cz / marie123")
    print("="*60)
    print("🎯 Funkce:")
    print("   • Kompletni dashboard na jedne strance")
    print("   • Administracni panel pro admina")
    print("   • Sprava uzivatelu")
    print("   • Pridavani novinek")
    print("   • Zobrazeni budoucich aplikaci")
    print("   • Interni zpravy")
    print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=5004)