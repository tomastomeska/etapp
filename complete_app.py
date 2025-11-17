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
            min-height: 80px;
        }
        .app-tile:hover { border-color: #2c5aa0; background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%); }
        .app-tile .small { font-size: 0.8rem; margin: 0; }
        .app-tile h6.small { margin-bottom: 5px; }
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
        
    </div>
    
    {{ content | safe }}
    
    <!-- Modal pro editaci uzivatele -->
    <div class="modal fade" id="editUserModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Editace uzivatele</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="editUserForm" method="POST" action="/admin/edit_user">
                    <div class="modal-body">
                        <input type="hidden" id="editUserEmail" name="user_email">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Jmeno</label>
                                    <input type="text" class="form-control" id="editFirstName" name="first_name" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Prijmeni</label>
                                    <input type="text" class="form-control" id="editLastName" name="last_name">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" id="editEmail" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Role</label>
                            <select class="form-control" id="editRole" name="role">
                                <option value="user">Uzivatel</option>
                                <option value="admin">Administrator</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Avatar</label>
                            <select class="form-control" id="editAvatar" name="avatar">
                                <option value="👤">👤 Uzivatel</option>
                                <option value="👨‍💼">👨‍💼 Manager</option>
                                <option value="👩">👩 Zena</option>
                                <option value="👨‍🔧">👨‍🔧 Technik</option>
                                <option value="🚛">🚛 Ridic</option>
                                <option value="📋">📋 Admin</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Status</label>
                            <select class="form-control" id="editStatus" name="status">
                                <option value="online">Aktivni</option>
                                <option value="offline">Neaktivni</option>
                            </select>
                        </div>
                        <hr>
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="resetPassword" name="reset_password">
                            <label class="form-check-label" for="resetPassword">Resetovat heslo na "user123"</label>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrusit</button>
                        <button type="submit" class="btn btn-primary">Ulozit zmeny</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Modal pro přidání aplikace -->
    <div class="modal fade" id="addAppModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Přidat novou aplikaci</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="/admin/add_app">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Název aplikace</label>
                            <input type="text" class="form-control" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Ikona (emoji)</label>
                            <select class="form-control" name="icon" required>
                                <option value="🚛">🚛 Správa vozidel</option>
                                <option value="📍">📍 GPS tracking</option>
                                <option value="📦">📦 Sklady</option>
                                <option value="💰">💰 Účetnictví</option>
                                <option value="📊">📊 Analýzy</option>
                                <option value="📅">📅 Plánování</option>
                                <option value="👥">👥 HR</option>
                                <option value="📧">📧 Email</option>
                                <option value="📋">📋 Dokumenty</option>
                                <option value="⚙️">⚙️ Nastavení</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Popis</label>
                            <textarea class="form-control" name="description" rows="2" placeholder="Krátký popis aplikace"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Odkaz/Adresa</label>
                            <input type="url" class="form-control" name="url" placeholder="https://example.com">
                            <small class="text-muted">Nechání prázdné = zůstane "Plánováno"</small>
                        </div>
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" name="require_password" id="requirePassword">
                            <label class="form-check-label" for="requirePassword">
                                Vyžadovat heslo před přechodem
                            </label>
                        </div>
                        <div class="mb-3" id="passwordField" style="display: none;">
                            <label class="form-label">Heslo pro přístup</label>
                            <input type="password" class="form-control" name="access_password" placeholder="Heslo pro přístup k aplikaci">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-primary">Přidat aplikaci</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Modal pro editaci aplikace -->
    <div class="modal fade" id="editAppModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Editovat aplikaci</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="editAppForm" method="POST" action="/admin/edit_app">
                    <div class="modal-body">
                        <input type="hidden" id="editAppId" name="app_id">
                        <div class="mb-3">
                            <label class="form-label">Název aplikace</label>
                            <input type="text" class="form-control" id="editAppName" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Ikona (emoji)</label>
                            <select class="form-control" id="editAppIcon" name="icon" required>
                                <option value="🚛">🚛 Správa vozidel</option>
                                <option value="📍">📍 GPS tracking</option>
                                <option value="📦">📦 Sklady</option>
                                <option value="💰">💰 Účetnictví</option>
                                <option value="📊">📊 Analýzy</option>
                                <option value="📅">📅 Plánování</option>
                                <option value="👥">👥 HR</option>
                                <option value="📧">📧 Email</option>
                                <option value="📋">📋 Dokumenty</option>
                                <option value="⚙️">⚙️ Nastavení</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Popis</label>
                            <textarea class="form-control" id="editAppDescription" name="description" rows="2" placeholder="Krátký popis aplikace"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Odkaz/Adresa</label>
                            <input type="url" class="form-control" id="editAppUrl" name="url" placeholder="https://example.com">
                            <small class="text-muted">Nechání prázdné = zůstane "Plánováno"</small>
                        </div>
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" id="editRequirePassword" name="require_password">
                            <label class="form-check-label" for="editRequirePassword">
                                Vyžadovat heslo před přechodem
                            </label>
                        </div>
                        <div class="mb-3" id="editPasswordField" style="display: none;">
                            <label class="form-label">Heslo pro přístup</label>
                            <input type="password" class="form-control" id="editAppPassword" name="access_password" placeholder="Heslo pro přístup k aplikaci">
                        </div>
                        <hr>
                        <div class="text-danger">
                            <h6>Nebezpečná zóna</h6>
                            <button type="button" class="btn btn-danger btn-sm" onclick="deleteApp()">Smazat aplikaci</button>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-primary">Uložit změny</button>
                    </div>
                </form>
            </div>
        </div>
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
        
        function editUser(email) {
            // Najdeme uzivatele v datech (toto by v realnem systemu bylo AJAX)
            const users = {
                'admin@europeantransport.cz': {'name': 'Administrator Systemu', 'role': 'admin', 'avatar': '👨‍💼', 'status': 'online'},
                'user@europeantransport.cz': {'name': 'Jan Novak', 'role': 'user', 'avatar': '👤', 'status': 'online'},
                'marie@europeantransport.cz': {'name': 'Marie Svobodova', 'role': 'user', 'avatar': '👩', 'status': 'offline'}
            };
            
            const user = users[email];
            if (user) {
                document.getElementById('editUserEmail').value = email;
                document.getElementById('editEmail').value = email;
                const nameParts = user.name.split(' ');
                document.getElementById('editFirstName').value = nameParts[0] || '';
                document.getElementById('editLastName').value = nameParts.slice(1).join(' ') || '';
                document.getElementById('editRole').value = user.role;
                document.getElementById('editAvatar').value = user.avatar;
                document.getElementById('editStatus').value = user.status;
                
                const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
                modal.show();
            }
        }
        
        function toggleUserStatus(email) {
            if (confirm('Opravdu chcete zmenit status tohoto uzivatele?')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/admin/toggle_user_status';
                
                const emailInput = document.createElement('input');
                emailInput.type = 'hidden';
                emailInput.name = 'user_email';
                emailInput.value = email;
                
                form.appendChild(emailInput);
                document.body.appendChild(form);
                form.submit();
            }
        }
        
        function addUser() {
            // Vycistime modal
            document.getElementById('editUserEmail').value = '';
            document.getElementById('editEmail').value = '';
            document.getElementById('editFirstName').value = '';
            document.getElementById('editLastName').value = '';
            document.getElementById('editRole').value = 'user';
            document.getElementById('editAvatar').value = '👤';
            document.getElementById('editStatus').value = 'online';
            document.getElementById('resetPassword').checked = false;
            
            // Zmenime action na pridani
            document.getElementById('editUserForm').action = '/admin/add_user';
            document.querySelector('#editUserModal .modal-title').textContent = 'Pridat noveho uzivatele';
            
            const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
            modal.show();
        }
        
        function showAddAppModal() {
            const modal = new bootstrap.Modal(document.getElementById('addAppModal'));
            modal.show();
        }
        
        // Zobraz/skryj pole pro heslo
        document.addEventListener('DOMContentLoaded', function() {
            const checkbox = document.getElementById('requirePassword');
            const passwordField = document.getElementById('passwordField');
            
            if (checkbox) {
                checkbox.addEventListener('change', function() {
                    passwordField.style.display = this.checked ? 'block' : 'none';
                });
            }
            
            // Pro editaci aplikace
            const editCheckbox = document.getElementById('editRequirePassword');
            const editPasswordField = document.getElementById('editPasswordField');
            
            if (editCheckbox) {
                editCheckbox.addEventListener('change', function() {
                    editPasswordField.style.display = this.checked ? 'block' : 'none';
                });
            }
        });
        
        function openApp(appId, url, requiresPassword) {
            if (!url) {
                alert('Aplikace je ještě ve vývoji');
                return;
            }
            
            if (requiresPassword) {
                const password = prompt('Zadejte heslo pro přístup k aplikaci:');
                if (password) {
                    // Zde by byla kontrola hesla - pro demo jen otevřeme
                    window.open(url, '_blank');
                } else {
                    alert('Přístup zrušen');
                }
            } else {
                window.open(url, '_blank');
            }
        }
        
        function editAppContext(appId) {
            // Najdeme aplikaci podle ID
            const apps = {
                1: {name: 'Správa vozidel', icon: '🚛', description: 'Modul pro správu vozového parku', url: '', require_password: false, access_password: ''},
                2: {name: 'GPS tracking', icon: '📍', description: 'Sledování pozice vozidel', url: '', require_password: false, access_password: ''},
                3: {name: 'Sklady', icon: '📦', description: 'Správa skladových zásob', url: '', require_password: false, access_password: ''},
                4: {name: 'Účetnictví', icon: '💰', description: 'Finanční modul', url: '', require_password: false, access_password: ''}
            };
            
            // V reálné aplikaci by zde byl AJAX call pro získání dat
            const app = apps[appId];
            if (app) {
                document.getElementById('editAppId').value = appId;
                document.getElementById('editAppName').value = app.name;
                document.getElementById('editAppIcon').value = app.icon;
                document.getElementById('editAppDescription').value = app.description || '';
                document.getElementById('editAppUrl').value = app.url || '';
                document.getElementById('editRequirePassword').checked = app.require_password || false;
                document.getElementById('editAppPassword').value = app.access_password || '';
                
                // Zobraz/skryj pole pro heslo
                document.getElementById('editPasswordField').style.display = app.require_password ? 'block' : 'none';
                
                const modal = new bootstrap.Modal(document.getElementById('editAppModal'));
                modal.show();
            }
        }
        
        function deleteApp() {
            const appId = document.getElementById('editAppId').value;
            if (confirm('Opravdu chcete smazat tuto aplikaci? Tato akce je nevratná!')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/admin/delete_app';
                
                const idInput = document.createElement('input');
                idInput.type = 'hidden';
                idInput.name = 'app_id';
                idInput.value = appId;
                
                form.appendChild(idInput);
                document.body.appendChild(form);
                form.submit();
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
    
    # Kompaktní verze novinek pro sidebar
    news_cards_html = ""
    for news in NEWS:
        featured_class = "border-danger" if news.get('featured', False) else "border-primary"
        comments_count = len(news.get('comments', []))
        star = "⭐ " if news.get('featured', False) else ""
        
        news_cards_html += f'''
        <div class="card {featured_class} mb-2" style="border-left: 4px solid;">
            <div class="card-body p-2">
                <h6 class="card-title mb-1" style="font-size: 0.9rem;">{star}{news["title"]}</h6>
                <p class="card-text small mb-2">{news["content"][:80]}...</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted" style="font-size: 0.75rem;">
                        {news["author"]} • {news["created"][:10]}
                    </small>
                    <span class="badge bg-info" style="font-size: 0.7rem;">💬 {comments_count}</span>
                </div>
            </div>
        </div>
        '''
    
    # Originální news_html pro kompatibilitu
    news_html = news_cards_html
    
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
    
    # Aplikace pro levy panel
    apps_html = ""
    for app in APPLICATIONS:
        status_text = "Plánováno" if app.get('status') == 'planned' else "Dostupné"
        status_class = "bg-warning" if app.get('status') == 'planned' else "bg-success"
        url = app.get('url', '')
        require_password = app.get('require_password', False)
        
        onclick = f"openApp({app['id']}, '{url}', {str(require_password).lower()})" if url else "alert('Aplikace je ve vývoji')"
        cursor_style = "cursor: pointer;" if url or app.get('status') == 'planned' else ""
        
        # Přidáme context menu pro adminy
        context_menu = f"oncontextmenu='editAppContext({app['id']}); return false;'" if is_admin else ""
        
        apps_html += f'''
        <div class="col-6 mb-2">
            <div class="card app-tile text-center p-2" onclick="{onclick}" {context_menu} style="{cursor_style}">
                <div style="font-size: 1.5rem;">{app["icon"]}</div>
                <h6 class="small">{app["name"]}</h6>
                <span class="badge {status_class} small">{status_text}</span>
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
                    <button class="btn btn-sm btn-outline-primary" onclick="editUser('{email}')">Editovat</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="toggleUserStatus('{email}')">{action_btn}</button>
                </td>
            </tr>
            '''
            users_html += '</tbody></table></div><button class="btn btn-success" onclick="addUser()">+ Pridat uzivatele</button>'
    
    content = f'''
    <div class="row">
        <!-- Levý sidebar s kompaktním obsahem -->
        <div class="col-md-4">
            <div class="sidebar p-3 mb-4">
                <!-- Profil -->
                <div class="mb-4">
                    <h5><i class="bi bi-person-circle"></i> Profil</h5>
                    <div class="card-body p-0">
                        <h6>{user["name"]}</h6>
                        <p class="text-muted small mb-2">{user["role"].title()} účet</p>
                        <button class="btn btn-outline-primary btn-sm" onclick="toggleSection('edit-profile')">
                            <i class="bi bi-pencil"></i> Editovat profil
                        </button>
                    </div>
                </div>

                <!-- Statistiky -->
                <div class="mb-4">
                    <h6><i class="bi bi-bar-chart"></i> Statistiky</h6>
                    <ul class="list-unstyled small">
                        <li><i class="bi bi-newspaper"></i> Novinky: {total_news}</li>
                        <li><i class="bi bi-envelope"></i> Nepřečteno: {unread_messages}</li>
                        <li><i class="bi bi-clock"></i> Online: {datetime.now().strftime("%H:%M")}</li>
                    </ul>
                </div>


                
                <!-- Firemní aplikace -->
                <div class="mb-4">
                    <h6><i class="bi bi-grid-3x3-gap"></i> Firemní aplikace</h6>
                    <div class="row g-2">
                        {apps_html}
                    </div>
                    {f'<button class="btn btn-primary btn-sm w-100 mt-2" onclick="showAddAppModal()"><i class="bi bi-plus"></i> Přidat aplikaci</button>' if is_admin else ''}
                </div>
            </div>
        </div>
        
        <!-- Hlavní obsah -->
        <div class="col-md-8">
            

            
            <!-- Editace profilu -->
            <div id="edit-profile" class="content-section" style="display:none;">
                <h5><i class="bi bi-person-gear"></i> Editace profilu</h5>
                <form method="POST" action="/edit_profile">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Jmeno</label>
                                <input type="text" class="form-control" name="first_name" value="{user['name'].split()[0] if ' ' in user['name'] else user['name']}" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Prijmeni</label>
                                <input type="text" class="form-control" name="last_name" value="{user['name'].split()[1] if ' ' in user['name'] and len(user['name'].split()) > 1 else ''}">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" name="email" value="{user['email']}" required>
                    </div>
                    {f'<div class="mb-3"><label class="form-label">Avatar (emoji)</label><select class="form-control" name="avatar"><option value="👤" {"selected" if user["avatar"] == "👤" else ""}>👤 Uzivatel</option><option value="👨‍💼" {"selected" if user["avatar"] == "👨‍💼" else ""}>👨‍💼 Manager</option><option value="👩" {"selected" if user["avatar"] == "👩" else ""}>👩 Zena</option><option value="👨‍🔧" {"selected" if user["avatar"] == "👨‍🔧" else ""}>👨‍🔧 Technik</option><option value="🚛" {"selected" if user["avatar"] == "🚛" else ""}>🚛 Ridic</option><option value="📋" {"selected" if user["avatar"] == "📋" else ""}>📋 Admin</option></select></div>' if is_admin else ''}
                    <hr>
                    <h6>Zmena hesla (volitelne)</h6>
                    <div class="mb-3">
                        <label class="form-label">Soucasne heslo</label>
                        <input type="password" class="form-control" name="current_password">
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Nove heslo</label>
                                <input type="password" class="form-control" name="new_password">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Potvrzeni hesla</label>
                                <input type="password" class="form-control" name="confirm_password">
                            </div>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Ulozit zmeny</button>
                    <button type="button" class="btn btn-secondary ms-2" onclick="toggleSection('edit-profile')">Zrusit</button>
                </form>
            </div>
            
            <!-- Hlavní obsah -->
            <div class="content-section">
                <div class="row">
                    <div class="col-md-6">
                        <!-- Firemní novinky -->
                        <div class="card mb-4">
                            <div class="card-header">
                                <h6 class="mb-0"><i class="bi bi-newspaper"></i> Firemní novinky</h6>
                            </div>
                            <div class="card-body" style="max-height: 500px; overflow-y: auto;">
                                {news_cards_html if news_cards_html else '<p class="text-muted">Zatím žádné novinky</p>'}
                            </div>
                        </div>

                    </div>
                    
                    <div class="col-md-6">
                        <!-- Interní zprávy -->
                        <div class="card mb-4">
                            <div class="card-header">
                                <h6 class="mb-0"><i class="bi bi-envelope"></i> Interní zprávy</h6>
                            </div>
                            <div class="card-body" style="max-height: 500px; overflow-y: auto;">
                                {messages_html if messages_html else '<p class="text-muted">Zatím žádné zprávy</p>'}
                            </div>
                        </div>
                    </div>
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

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    """Editace profilu uzivatele."""
    if 'user' not in session:
        flash('Nejste prihlaseni!', 'error')
        return redirect(url_for('login'))
    
    user_email = session['user']['email']
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').lower().strip()
    avatar = request.form.get('avatar', '👤')
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validace
    if not first_name:
        flash('Jmeno je povinne!', 'error')
        return redirect(url_for('index'))
    
    if not email:
        flash('Email je povinny!', 'error')
        return redirect(url_for('index'))
    
    # Kontrola, zda email uz neexistuje (pokud se menil)
    if email != user_email and email in USERS:
        flash('Tento email uz pouziva jiny uzivatel!', 'error')
        return redirect(url_for('index'))
    
    # Zmena hesla
    if new_password:
        if not current_password:
            flash('Pro zmenu hesla musíte zadat soucasne heslo!', 'error')
            return redirect(url_for('index'))
        
        if not check_password_hash(USERS[user_email]['password'], current_password):
            flash('Soucasne heslo je neplatne!', 'error')
            return redirect(url_for('index'))
        
        if new_password != confirm_password:
            flash('Nova hesla se neshoduji!', 'error')
            return redirect(url_for('index'))
        
        if len(new_password) < 6:
            flash('Heslo musi mit alespon 6 znaku!', 'error')
            return redirect(url_for('index'))
    
    # Aktualizace dat
    user_data = USERS[user_email].copy()
    user_data['name'] = f"{first_name} {last_name}".strip()
    
    # Avatar muze menit jen admin
    if session['user']['role'] == 'admin':
        user_data['avatar'] = avatar
    
    if new_password:
        user_data['password'] = generate_password_hash(new_password)
    
    # Pokud se email zmenil, presuneme data
    if email != user_email:
        USERS[email] = user_data
        del USERS[user_email]
        session['user']['email'] = email
    else:
        USERS[user_email] = user_data
    
    # Aktualizace session
    session['user']['name'] = user_data['name']
    session['user']['avatar'] = user_data['avatar']
    
    flash('Profil byl uspesne aktualizovan!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/edit_user', methods=['POST'])
def admin_edit_user():
    """Editace uzivatele adminem."""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Nemáte opravneni!', 'error')
        return redirect(url_for('index'))
    
    user_email = request.form.get('user_email')
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').lower().strip()
    role = request.form.get('role', 'user')
    avatar = request.form.get('avatar', '👤')
    status = request.form.get('status', 'online')
    reset_password = 'reset_password' in request.form
    
    # Validace
    if not user_email and not email:
        flash('Email je povinny!', 'error')
        return redirect(url_for('index'))
    
    if not first_name:
        flash('Jmeno je povinne!', 'error')
        return redirect(url_for('index'))
    
    # Kontrola duplicitniho emailu
    if user_email and email != user_email and email in USERS:
        flash('Tento email uz pouziva jiny uzivatel!', 'error')
        return redirect(url_for('index'))
    
    if user_email:  # Editace existujiciho
        if user_email not in USERS:
            flash('Uzivatel nenalezen!', 'error')
            return redirect(url_for('index'))
        
        user_data = USERS[user_email].copy()
        user_data['name'] = f"{first_name} {last_name}".strip()
        user_data['role'] = role
        user_data['avatar'] = avatar
        user_data['status'] = status
        
        if reset_password:
            user_data['password'] = generate_password_hash('user123')
        
        # Presun dat pri zmene emailu
        if email != user_email:
            USERS[email] = user_data
            del USERS[user_email]
        else:
            USERS[user_email] = user_data
        
        flash('Uzivatel byl uspesne upraven!', 'success')
    
    return redirect(url_for('index'))

@app.route('/admin/add_user', methods=['POST'])
def admin_add_user():
    """Pridani noveho uzivatele adminem."""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').lower().strip()
    role = request.form.get('role', 'user')
    avatar = request.form.get('avatar', '👤')
    status = request.form.get('status', 'online')
    
    if not first_name or not email:
        flash('Jmeno a email jsou povinne!', 'error')
        return redirect(url_for('index'))
    
    if email in USERS:
        flash('Uzivatel s timto emailem uz existuje!', 'error')
        return redirect(url_for('index'))
    
    # Vytvoreni noveho uzivatele
    USERS[email] = {
        'id': max([u['id'] for u in USERS.values()], default=0) + 1,
        'password': generate_password_hash('user123'),
        'name': f"{first_name} {last_name}".strip(),
        'role': role,
        'avatar': avatar,
        'status': status,
        'created': datetime.now().strftime('%Y-%m-%d')
    }
    
    flash(f'Uzivatel {email} byl uspesne pridan! Vychozi heslo: user123', 'success')
    return redirect(url_for('index'))

@app.route('/admin/toggle_user_status', methods=['POST'])
def admin_toggle_user_status():
    """Prepnuti statusu uzivatele."""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    user_email = request.form.get('user_email')
    
    if user_email not in USERS:
        flash('Uzivatel nenalezen!', 'error')
        return redirect(url_for('index'))
    
    # Prepnuti statusu
    current_status = USERS[user_email]['status']
    new_status = 'offline' if current_status == 'online' else 'online'
    USERS[user_email]['status'] = new_status
    
    status_text = 'aktivovan' if new_status == 'online' else 'deaktivovan'
    flash(f'Uzivatel byl uspesne {status_text}!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/add_app', methods=['POST'])
def add_app():
    """Pridani nove aplikace."""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    name = request.form.get('name')
    icon = request.form.get('icon')
    description = request.form.get('description', '')
    url = request.form.get('url', '')
    require_password = 'require_password' in request.form
    access_password = request.form.get('access_password', '')
    
    if not name or not icon:
        flash('Nazev a ikona jsou povinne!', 'error')
        return redirect(url_for('index'))
    
    # Najdeme nejvyssi ID
    max_id = max([app['id'] for app in APPLICATIONS], default=0)
    
    new_app = {
        'id': max_id + 1,
        'name': name,
        'icon': icon,
        'description': description,
        'status': 'active' if url else 'planned',
        'url': url,
        'require_password': require_password,
        'access_password': access_password
    }
    
    APPLICATIONS.append(new_app)
    flash('Aplikace byla uspesne pridana!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/edit_app', methods=['POST'])
def edit_app():
    """Editace existujici aplikace."""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    app_id = int(request.form.get('app_id'))
    name = request.form.get('name')
    icon = request.form.get('icon')
    description = request.form.get('description', '')
    url = request.form.get('url', '')
    require_password = 'require_password' in request.form
    access_password = request.form.get('access_password', '')
    
    if not name or not icon:
        flash('Nazev a ikona jsou povinne!', 'error')
        return redirect(url_for('index'))
    
    # Najdeme aplikaci podle ID
    app_to_edit = None
    for i, app in enumerate(APPLICATIONS):
        if app['id'] == app_id:
            app_to_edit = i
            break
    
    if app_to_edit is None:
        flash('Aplikace nenalezena!', 'error')
        return redirect(url_for('index'))
    
    # Aktualizujeme aplikaci
    APPLICATIONS[app_to_edit].update({
        'name': name,
        'icon': icon,
        'description': description,
        'status': 'active' if url else 'planned',
        'url': url,
        'require_password': require_password,
        'access_password': access_password
    })
    
    flash('Aplikace byla uspesne aktualizovana!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/delete_app', methods=['POST'])
def delete_app():
    """Smazani aplikace."""
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    app_id = int(request.form.get('app_id'))
    
    # Najdeme a smazeme aplikaci
    global APPLICATIONS
    APPLICATIONS = [app for app in APPLICATIONS if app['id'] != app_id]
    
    flash('Aplikace byla uspesne smazana!', 'success')
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