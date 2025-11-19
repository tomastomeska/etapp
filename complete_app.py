#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
European Transport CZ - Kompletni funkci aplikace
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'european-transport-secret-key-2024'

# Simulovana databaze
USERS = {
    1: {
        'id': 1,
        'username': 'admin',
        'email': 'admin@europeantransport.cz',
        'password': generate_password_hash('admin123'),
        'full_name': 'Administrator Systému',
        'role': 'admin',
        'avatar': 'https://via.placeholder.com/50',
        'active': True,
        'created': '2024-01-01'
    },
    2: {
        'id': 2,
        'username': 'jan.novak',
        'email': 'user@europeantransport.cz',
        'password': generate_password_hash('user123'),
        'full_name': 'Jan Novák',
        'role': 'ridic',
        'avatar': 'https://via.placeholder.com/50',
        'active': True,
        'created': '2024-02-15'
    },
    3: {
        'id': 3,
        'username': 'marie.svobodova',
        'email': 'marie@europeantransport.cz',
        'password': generate_password_hash('marie123'),
        'full_name': 'Marie Svobodová',
        'role': 'administrativa',
        'avatar': 'https://via.placeholder.com/50',
        'active': True,
        'created': '2024-03-10'
    }
}

NEWS = [
    {
        'id': 1,
        'title': 'Novy system pro spravu vozidel',
        'content': 'Spoustime novy modul pro spravu vozoveho parku. Umozni lepsi sledovani udrzby a spotreby paliva.',
        'content_full': 'Spouštíme nový modul pro správu vozového parku! 🚛\n\nTento komplexní systém umožní:\n- Sledování údržby vozidel\n- Monitoring spotřeby paliva\n- Plánování servisních intervalů\n- Real-time GPS tracking\n- Elektronická kniha jízd\n\nModul bude dostupný od příštího měsíce pro všechny řidiče a dispečery.',
        'author': 'Administrator Systemu',
        'created': '2024-11-10 10:30',
        'featured': True,
        'image': '',
        'read_by': [],
        'comments': []
    },
    {
        'id': 2,
        'title': 'Aktualizace bezpecnostnich protokolu',
        'content': 'Vsichni ridici si prosim prostudujte nove bezpecnostni smernice v priloze.',
        'content_full': 'Všichni řidiči si prosím prostudujte nové bezpečnostní směrnice.\n\nKlíčové změny:\n- Nové postupy při nakládce nebezpečného nákladu\n- Aktualizované formuláře pro hlášení nehod\n- Povinné kontroly před jízdou\n\nDokumenty najdete v sekci Dokumenty.',
        'author': 'Administrator Systemu',
        'created': '2024-11-08 14:15',
        'featured': False,
        'image': '',
        'read_by': [],
        'comments': [
            {'author': 'Jan Novak', 'text': 'Dokumenty jsem prostudoval', 'time': '2024-11-09 08:00'}
        ]
    }
]

MESSAGES = []

# Načtení zpráv z JSON
if os.path.exists('data_messages.json'):
    with open('data_messages.json', 'r', encoding='utf-8') as f:
        MESSAGES = json.load(f)
else:
    MESSAGES = [
        {
            'id': 1,
            'from_user_id': 1,
            'from_name': 'Administrátor Systému',
            'subject': 'Vítejte v systému',
            'content': 'Vítejte v novém firemním portálu European Transport CZ!',
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'recipient_type': 'all',  # all, ridic, administrativa, single
            'recipient_user_id': None,  # pouze pokud recipient_type = single
            'read_by': []  # seznam {'user_id': X, 'read_at': 'timestamp'}
        }
    ]

APPLICATIONS = [
    {'id': 1, 'name': 'Sprava vozidel', 'icon': '🚛', 'status': 'planned', 'description': 'Modul pro spravu vozoveho parku', 'visible_for_ridic': True},
    {'id': 2, 'name': 'GPS tracking', 'icon': '📍', 'status': 'planned', 'description': 'Sledovani pozice vozidel', 'visible_for_ridic': True},
    {'id': 3, 'name': 'Sklady', 'icon': '📦', 'status': 'planned', 'description': 'Sprava skladovych zasob', 'visible_for_ridic': False},
    {'id': 4, 'name': 'Ucetnictvi', 'icon': '💰', 'status': 'planned', 'description': 'Financni modul', 'visible_for_ridic': False},
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
                {% if session.user_id %}
                    <span class="navbar-text me-3">
                        👤 {{ session.full_name }}
                        <span class="badge ms-1 {{ 'admin-badge' if session.role == 'admin' else 'user-badge' }}">
                            {{ {'admin': 'Admin', 'ridic': 'Řidič', 'administrativa': 'Administrativa'}.get(session.role, session.role|title) }}
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
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" name="visible_for_ridic" id="visibleForRidic" checked>
                            <label class="form-check-label" for="visibleForRidic">
                                Viditelné pro profil Řidič
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
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" id="editVisibleForRidic" name="visible_for_ridic">
                            <label class="form-check-label" for="editVisibleForRidic">
                                Viditelné pro profil Řidič
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
    
    <!-- Modal pro editaci novinky -->
    <div class="modal fade" id="editNewsModal" tabindex="-1" data-bs-backdrop="static">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-pencil"></i> Upravit novinku</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="editNewsForm" method="POST">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Název</label>
                            <input type="text" class="form-control" id="editNewsTitle" name="title" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Krátký obsah (náhled)</label>
                            <textarea class="form-control" id="editNewsContent" name="content" rows="2" required placeholder="Zobrazí se na hlavní stránce..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Plný obsah (detail)</label>
                            <textarea class="form-control" id="editNewsContentFull" name="content_full" rows="6" placeholder="Zobrazí se po kliknutí na novinku..."></textarea>
                            <small class="text-muted">Můžete použít více řádků pro lepší formátování.</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">URL obrázku (volitelné)</label>
                            <input type="text" class="form-control" id="editNewsImage" name="image" placeholder="https://example.com/obrazek.jpg">
                        </div>
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="editNewsFeatured" name="featured">
                            <label class="form-check-label" for="editNewsFeatured">⭐ Důležitá novinka (zvýrazněná)</label>
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
    
    <!-- Modal pro přidání novinky -->
    <div class="modal fade" id="addNewsModal" tabindex="-1" data-bs-backdrop="static">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-plus-circle"></i> Přidat novinku</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="/add_news">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Název</label>
                            <input type="text" class="form-control" name="title" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Krátký obsah (náhled)</label>
                            <textarea class="form-control" name="content" rows="2" required placeholder="Zobrazí se na hlavní stránce..."></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Plný obsah (detail)</label>
                            <textarea class="form-control" name="content_full" rows="6" placeholder="Zobrazí se po kliknutí na novinku..."></textarea>
                            <small class="text-muted">Můžete použít více řádků pro lepší formátování.</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">URL obrázku (volitelné)</label>
                            <input type="text" class="form-control" name="image" placeholder="https://example.com/obrazek.jpg">
                        </div>
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" name="featured" id="addNewsFeatured">
                            <label class="form-check-label" for="addNewsFeatured">⭐ Důležitá novinka (zvýrazněná)</label>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-success"><i class="bi bi-check-lg"></i> Přidat novinku</button>
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
        
        function editNews(newsId, title, content, contentFull, image, featured) {
            document.getElementById('editNewsForm').action = '/admin/edit_news/' + newsId;
            document.getElementById('editNewsTitle').value = title;
            document.getElementById('editNewsContent').value = content;
            document.getElementById('editNewsContentFull').value = contentFull || content;
            document.getElementById('editNewsImage').value = image || '';
            document.getElementById('editNewsFeatured').checked = featured;
            
            const modal = new bootstrap.Modal(document.getElementById('editNewsModal'));
            modal.show();
        }
        
        function deleteNews(newsId, title) {
            if (confirm('Opravdu chcete smazat novinku "' + title + '"? Tato akce je nevratná!')) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/admin/delete_news/' + newsId;
                
                document.body.appendChild(form);
                form.submit();
            }
        }
        
        function showAddNewsModal() {
            const modal = new bootstrap.Modal(document.getElementById('addNewsModal'));
            modal.show();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Hlavni dashboard - vse na jedne strance."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = USERS.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    is_admin = user['role'] == 'admin'
    
    # Pocitani statistik
    unread_messages = 0
    for msg in MESSAGES:
        # Zpráva je nepřečtená pokud user_id není v read_by
        if user_id not in [r.get('user_id') for r in msg.get('read_by', [])]:
            # A zároveň je zpráva určená pro tento uživatele
            recipient_type = msg.get('recipient_type', 'all')
            recipient_user_id = msg.get('recipient_user_id')
            
            if recipient_type == 'all' or \
               (recipient_type == 'single' and recipient_user_id == user_id) or \
               (recipient_type == user['role']):
                unread_messages += 1
    
    total_users = len(USERS)
    total_news = len(NEWS)
    
    # Počet nepřečtených novinek pro aktuálního uživatele
    unread_news = 0
    for news in NEWS:
        # Novinka je nepřečtená, pokud uživatel není v seznamu read_by
        readers = [r['user_id'] for r in news.get('read_by', [])]
        if user_id not in readers:
            unread_news += 1
    
    # Kompaktní verze novinek pro sidebar - zobrazit pouze 3 nejnovější
    news_cards_html = ""
    display_limit = 3
    total_news_count = len(NEWS)
    
    def count_all_comments(comments):
        """Rekurzivně spočítá všechny komentáře včetně odpovědí."""
        count = len(comments)
        for comment in comments:
            if comment.get('replies'):
                count += count_all_comments(comment['replies'])
        return count
    
    for idx, news in enumerate(NEWS[:display_limit]):
        featured_class = "border-danger" if news.get('featured', False) else "border-primary"
        comments_count = count_all_comments(news.get('comments', []))
        star = "⭐ " if news.get('featured', False) else ""
        read_count = len(news.get('read_by', []))
        
        admin_buttons = ''
        if is_admin:
            # Escapování pro JavaScript
            title_escaped = news['title'].replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            content_escaped = news['content'].replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            content_full_escaped = news.get('content_full', news['content']).replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            image_escaped = news.get('image', '').replace("'", "\\'").replace('"', '\\"')
            
            admin_buttons = f'''
            <div class="btn-group btn-group-sm mt-2" onclick="event.stopPropagation();">
                <button class="btn btn-outline-primary btn-sm" onclick="editNews({news['id']}, '{title_escaped}', '{content_escaped}', '{content_full_escaped}', '{image_escaped}', {str(news.get('featured', False)).lower()}); event.stopPropagation();">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteNews({news['id']}, '{title_escaped}'); event.stopPropagation();">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            '''
        
        news_cards_html += f'''
        <div class="card {featured_class} mb-2" style="border-left: 4px solid; cursor: pointer;" onclick="window.location.href='/news/{news['id']}'">
            <div class="card-body p-2">
                <h6 class="card-title mb-1" style="font-size: 0.9rem;">{star}{news["title"]}</h6>
                <p class="card-text small mb-2"><strong>{news["content"][:100]}{'...' if len(news['content']) > 100 else ''}</strong></p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted" style="font-size: 0.75rem;">
                        {news["author"]} • {news["created"][:10]}
                    </small>
                    <div>
                        {'<span class="badge bg-success me-1" style="font-size: 0.7rem;"><i class="bi bi-eye"></i> ' + str(read_count) + '</span>' if is_admin and read_count > 0 else ''}
                        <span class="badge bg-info" style="font-size: 0.7rem;">💬 {comments_count}</span>
                    </div>
                </div>
                {admin_buttons}
            </div>
        </div>
        '''
    
    # Přidání tlačítka pro archiv novinek, pokud je jich víc než 3
    if total_news_count > display_limit:
        news_cards_html += f'''
        <div class="text-center mt-2">
            <a href="/news/archive" class="btn btn-outline-primary btn-sm w-100">
                <i class="bi bi-archive"></i> Archiv novinek ({total_news_count - display_limit} starších)
            </a>
        </div>
        '''
    
    # Originální news_html pro kompatibilitu
    news_html = news_cards_html
    
    # Zprávy - zobrazit pouze ty relevantní pro uživatele
    messages_html = ""
    for message in MESSAGES:
        # Zkontrolovat jestli je zpráva určená pro tohoto uživatele
        recipient_type = message.get('recipient_type', 'all')
        recipient_user_id = message.get('recipient_user_id')
        
        is_for_user = False
        if recipient_type == 'all':
            is_for_user = True
        elif recipient_type == 'single' and recipient_user_id == user_id:
            is_for_user = True
        elif recipient_type == user['role']:
            is_for_user = True
        
        if not is_for_user:
            continue
        
        # Zkontrolovat jestli už je přečtená
        is_read = user_id in [r.get('user_id') for r in message.get('read_by', [])]
        unread_class = "" if is_read else "unread"
        unread_badge = '' if is_read else '<span class="badge bg-danger">Nová</span>'
        
        # Určit příjemce pro zobrazení
        recipient_text = ''
        if recipient_type == 'all':
            recipient_text = 'Pro všechny'
        elif recipient_type == 'single':
            recipient_text = 'Pouze pro vás'
        elif recipient_type == 'ridic':
            recipient_text = 'Pro řidiče'
        elif recipient_type == 'administrativa':
            recipient_text = 'Pro administrativu'
        
        messages_html += f'''
        <div class="card mb-2 message-item {unread_class}">
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1" style="font-size: 0.9rem;">
                            {message.get('subject', 'Bez předmětu')} {unread_badge}
                        </h6>
                        <p class="mb-1 small">{message.get('content', '')[:80]}{'...' if len(message.get('content', '')) > 80 else ''}</p>
                        <small class="text-muted">
                            <i class="bi bi-person"></i> {message.get('from_name', 'Systém')} | 
                            <i class="bi bi-clock"></i> {message.get('created', '')[:16]}
                        </small><br>
                        <small class="text-muted"><i class="bi bi-envelope"></i> {recipient_text}</small>
                    </div>
                    {f'<button class="btn btn-sm btn-outline-success" onclick="markMessageRead({message['id']})"><i class="bi bi-check"></i></button>' if not is_read else '<small class="text-success"><i class="bi bi-check2-circle"></i> Přečteno</small>'}
                </div>
            </div>
        </div>
        '''
    
    if not messages_html:
        messages_html = '<p class="text-muted small">Žádné zprávy</p>'
    
    # Aplikace pro levy panel - filtrujeme podle role
    apps_html = ""
    filtered_apps = APPLICATIONS
    if user['role'] == 'ridic':
        filtered_apps = [app for app in APPLICATIONS if app.get('visible_for_ridic', False)]
    
    for app in filtered_apps:
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
        for user_id, usr in USERS.items():
            role_badge = "admin-badge" if usr["role"] == "admin" else "user-badge"
            status_badge = "success" if usr.get("active", True) else "secondary"
            action_btn = "Deaktivovat" if usr.get("active", True) else "Aktivovat"
            status_text = "Aktivní" if usr.get("active", True) else "Neaktivní"
            
            users_html += f'''
            <tr>
                <td><img src="{usr.get('avatar', 'https://via.placeholder.com/40')}" alt="Avatar" class="rounded-circle me-2" width="30" height="30">{usr["full_name"]}</td>
                <td>{usr["email"]}</td>
                <td><span class="badge {role_badge}">{usr["role"]}</span></td>
                <td><span class="badge bg-{status_badge}">{status_text}</span></td>
                <td>
                    <a href="/users" class="btn btn-sm btn-outline-primary">Spravovat</a>
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
                        <h6>{user["full_name"]}</h6>
                        <p class="text-muted small mb-2">{'Administrátor' if user["role"] == 'admin' else 'Řidič' if user["role"] == 'ridic' else 'Administrativa' if user["role"] == 'administrativa' else user["role"].title()} účet</p>
                        <button class="btn btn-outline-primary btn-sm" onclick="toggleSection('edit-profile')">
                            <i class="bi bi-pencil"></i> Editovat profil
                        </button>
                    </div>
                </div>

                <!-- Statistiky -->
                <div class="mb-4">
                    <h6><i class="bi bi-bar-chart"></i> Statistiky</h6>
                    <ul class="list-unstyled small">
                        <li><i class="bi bi-newspaper"></i> Nepřečtené novinky: {unread_news}</li>
                        <li><i class="bi bi-envelope"></i> Nepřečtené zprávy: {unread_messages}</li>
                        <li><i class="bi bi-clock"></i> Online: {datetime.now().strftime("%H:%M")}</li>
                    </ul>
                    {f'''<div class="mt-2">
                        <a href="/users" class="btn btn-outline-primary btn-sm w-100 mb-2"><i class="bi bi-people"></i> Správa uživatelů</a>
                        <a href="/admin/deleted-comments" class="btn btn-outline-danger btn-sm w-100"><i class="bi bi-trash"></i> Smazané komentáře</a>
                    </div>''' if is_admin else ''}
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
                                <input type="text" class="form-control" name="first_name" value="{user['full_name'].split()[0] if ' ' in user['full_name'] else user['full_name']}" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Prijmeni</label>
                                <input type="text" class="form-control" name="last_name" value="{user['full_name'].split()[1] if ' ' in user['full_name'] and len(user['full_name'].split()) > 1 else ''}">
                            </div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" name="email" value="{user['email']}" required>
                    </div>
                    {'<div class="mb-3"><label class="form-label">Avatar URL</label><input type="url" class="form-control" name="avatar" value="' + user.get('avatar', 'https://via.placeholder.com/50') + '" placeholder="URL obrázku avatara"></div>' if is_admin else ''}
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
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h6 class="mb-0"><i class="bi bi-newspaper"></i> Firemní novinky</h6>
                                {f'<button class="btn btn-primary btn-sm" onclick="showAddNewsModal()"><i class="bi bi-plus"></i> Přidat</button>' if is_admin else ''}
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
    
    <script>
    function markMessageRead(messageId) {{
        fetch('/message/' + messageId + '/mark_read', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }}
        }}).then(() => {{
            location.reload();
        }});
    }}
    </script>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Dashboard", content=content)

@app.route('/add_news', methods=['POST'])
def add_news():
    """Pridani nove novinky."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    content_full = request.form.get('content_full', content)
    image = request.form.get('image', '')
    featured = 'featured' in request.form
    
    new_news = {
        'id': max([n['id'] for n in NEWS], default=0) + 1,
        'title': title,
        'content': content,
        'content_full': content_full,
        'image': image,
        'author': session.get('full_name', 'Neznámý'),
        'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'featured': featured,
        'read_by': [],
        'comments': []
    }
    
    NEWS.insert(0, new_news)
    save_news()  # Uloží změny do JSON
    flash('Novinka byla uspesne pridana!', 'success')
    return redirect(url_for('index'))

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    """Editace profilu uzivatele."""
    if 'user_id' not in session:
        flash('Nejste prihlaseni!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = USERS.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    username = request.form.get('username', '').strip()
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').lower().strip()
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validace
    if not username:
        flash('Uživatelské jméno je povinné!', 'error')
        return redirect(url_for('index'))
    
    if not full_name:
        flash('Celé jméno je povinné!', 'error')
        return redirect(url_for('index'))
        
    if not email:
        flash('Email je povinný!', 'error')
        return redirect(url_for('index'))
    
    # Kontrola duplicit (kromě současného uživatele)
    for uid, u in USERS.items():
        if uid != user_id:
            if u['username'] == username:
                flash('Toto uživatelské jméno už používá jiný uživatel!', 'error')
                return redirect(url_for('index'))
            if u['email'] == email:
                flash('Tento email už používá jiný uživatel!', 'error')
                return redirect(url_for('index'))
    
    # Změna hesla
    if new_password:
        if not current_password:
            flash('Pro změnu hesla musíte zadat současné heslo!', 'error')
            return redirect(url_for('index'))
        
        if not check_password_hash(user['password'], current_password):
            flash('Současné heslo je neplatné!', 'error')
            return redirect(url_for('index'))
        
        if new_password != confirm_password:
            flash('Nová hesla se neshodují!', 'error')
            return redirect(url_for('index'))
        
        if len(new_password) < 6:
            flash('Heslo musí mít alespoň 6 znaků!', 'error')
            return redirect(url_for('index'))
    
    # Aktualizace dat
    USERS[user_id].update({
        'username': username,
        'full_name': full_name,
        'email': email
    })
    
    if new_password:
        USERS[user_id]['password'] = generate_password_hash(new_password)
    
    # Aktualizace session
    session['username'] = username
    session['full_name'] = full_name
    
    flash('Profil byl úspěšně aktualizován!', 'success')
    return redirect(url_for('index'))

# Starý admin_edit_user route byl nahrazen novým systémem uživatelů

# Starý admin_add_user route byl odstraněn

@app.route('/admin/toggle_user_status', methods=['POST'])
def admin_toggle_user_status():
    """Prepnuti statusu uzivatele."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    user_id = int(request.form.get('user_id', 0))
    
    if user_id not in USERS:
        flash('Uzivatel nenalezen!', 'error')
        return redirect(url_for('index'))
    
    # Prepnuti statusu
    current_active = USERS[user_id].get('active', True)
    new_active = not current_active
    USERS[user_id]['active'] = new_active
    
    status_text = 'aktivovan' if new_active else 'deaktivovan'
    flash(f'Uzivatel byl uspesne {status_text}!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/add_app', methods=['POST'])
def add_app():
    """Pridani nove aplikace."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    name = request.form.get('name')
    icon = request.form.get('icon')
    description = request.form.get('description', '')
    url = request.form.get('url', '')
    require_password = 'require_password' in request.form
    access_password = request.form.get('access_password', '')
    visible_for_ridic = 'visible_for_ridic' in request.form
    
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
        'access_password': access_password,
        'visible_for_ridic': visible_for_ridic
    }
    
    APPLICATIONS.append(new_app)
    save_applications()  # Uloží změny do JSON
    flash('Aplikace byla uspesne pridana!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/edit_app', methods=['POST'])
def edit_app():
    """Editace existujici aplikace."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    app_id = int(request.form.get('app_id'))
    name = request.form.get('name')
    icon = request.form.get('icon')
    description = request.form.get('description', '')
    url = request.form.get('url', '')
    require_password = 'require_password' in request.form
    access_password = request.form.get('access_password', '')
    visible_for_ridic = 'visible_for_ridic' in request.form
    
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
        'access_password': access_password,
        'visible_for_ridic': visible_for_ridic
    })
    save_applications()  # Uloží změny do JSON
    
    flash('Aplikace byla uspesne aktualizovana!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/delete_app', methods=['POST'])
def delete_app():
    """Smazani aplikace."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemate opravneni!', 'error')
        return redirect(url_for('index'))
    
    app_id = int(request.form.get('app_id'))
    
    # Najdeme a smazeme aplikaci
    global APPLICATIONS
    APPLICATIONS = [app for app in APPLICATIONS if app['id'] != app_id]
    save_applications()  # Uloží změny do JSON
    
    flash('Aplikace byla uspesne smazana!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Prihlasovaci stranka."""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        
        # Najdeme uživatele podle emailu - email je klíč v USERS dictionary
        user_found = USERS.get(email)
        
        if user_found and check_password_hash(user_found['password'], password):
            if not user_found.get('active', True):
                flash('Váš účet je deaktivován. Kontaktujte administrátora.', 'error')
            else:
                session['user_id'] = email  # Use email as user_id since that's the key
                session['full_name'] = user_found['name']
                session['role'] = user_found['role']
                flash(f'Vítejte, {user_found["name"]}!', 'success')
                return redirect(url_for('index'))
        else:
            flash('Neplatné přihlašovací údaje!', 'error')
    
    login_form = '''
    <div class="row justify-content-center">
        <div class="col-md-4">
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
    name = session.get('full_name', 'Uživatel')
    session.clear()
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

@app.route('/users')
def users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Parametr pro zobrazení smazaných
    show_deleted = request.args.get('show_deleted') == 'true'
    
    # Seznam avatarů
    avatar_options = [
        'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix',
        'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka',
        'https://api.dicebear.com/7.x/avataaars/svg?seed=Bob',
        'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice',
        'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
        'https://api.dicebear.com/7.x/avataaars/svg?seed=Emma',
        'https://api.dicebear.com/7.x/bottts/svg?seed=Robot1',
        'https://api.dicebear.com/7.x/bottts/svg?seed=Robot2',
    ]
    
    # Vygenerování HTML pro seznam uživatelů
    users_html = ''
    deleted_users_html = ''
    
    for user in USERS.values():
        is_deleted = user.get('deleted', False)
        
        # Pokud je smazaný a nechceme zobrazit smazané, přeskočíme
        if is_deleted and not show_deleted:
            continue
        
        # Pokud není smazaný a chceme zobrazit pouze smazané, přeskočíme
        if not is_deleted and show_deleted:
            continue
            
        status_badge = '<span class="badge bg-success">Aktivní</span>' if user.get('active', True) and not is_deleted else '<span class="badge bg-danger">Neaktivní</span>' if not is_deleted else '<span class="badge bg-secondary">Smazán</span>'
        role_badge_class = 'admin-badge' if user['role'] == 'admin' else 'user-badge'
        role_name = {'admin': 'Admin', 'ridic': 'Řidič', 'administrativa': 'Administrativa'}.get(user['role'], user['role'].title())
        
        if is_deleted:
            # Tlačítka pro smazané uživatele
            action_buttons = f'''
                <button class="btn btn-success btn-sm" onclick="restoreUser({user['id']}, '{user['username']}')">
                    <i class="bi bi-arrow-counterclockwise"></i> Obnovit
                </button>
            '''
        else:
            # Tlačítka pro aktivní uživatele
            message_button = f'<button class="btn btn-outline-info btn-sm" onclick="sendMessageToUser({user['id']}, \\"{user['full_name']}\\")"><i class="bi bi-envelope"></i></button>'
            delete_button = f'<button class="btn btn-outline-danger btn-sm" onclick="deleteUser({user['id']}, \\"{user['username']}\\")"><i class="bi bi-trash"></i></button>' if user['id'] != session.get('user_id') else '<span class="text-muted small">Vlastní</span>'
            
            action_buttons = f'''
                <div class="btn-group btn-group-sm">
                    {message_button}
                    <button class="btn btn-outline-primary btn-sm" onclick="editUser({user['id']}, \\'{user['username']}\\', \\'{user['email']}\\', \\'{user['full_name']}\\', \\'{user['role']}\\', \\'{user.get('avatar', '')}\\', {str(user.get('active', True)).lower()})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    {delete_button}
                </div>
            '''
        
        user_row = f'''
        <tr class="{'table-secondary' if is_deleted else ''}">
            <td><img src="{user.get('avatar', 'https://via.placeholder.com/40')}" alt="Avatar" class="rounded-circle" width="40" height="40"></td>
            <td>
                <strong>{user['full_name']}</strong><br>
                <small class="text-muted">{user['username']}</small>
                {f'<br><small class="text-danger">Smazán: {user.get("deleted_at", "")}</small>' if is_deleted else ''}
            </td>
            <td>{user['email']}</td>
            <td><span class="badge {role_badge_class}">{role_name}</span></td>
            <td>{status_badge}</td>
            <td>{action_buttons}</td>
        </tr>
        '''
        
        if is_deleted:
            deleted_users_html += user_row
        else:
            users_html += user_row
    
    # Vygenerování HTML pro avatary
    avatars_html = ''
    for av in avatar_options:
        avatars_html += f'<div class="col-3"><img src="{av}" class="img-thumbnail avatar-option" style="cursor: pointer; width: 100%;" onclick="selectAvatar(\'{av}\')" data-avatar="{av}"></div>'
    
    content = f'''
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-4">
                <div class="sidebar p-3">
                    <h5><i class="bi bi-people-fill"></i> Správa uživatelů</h5>
                    <hr>
                    
                    <!-- Statistiky -->
                    <div class="mb-4">
                        <h6>Statistiky</h6>
                        <div class="row text-center">
                            <div class="col-4">
                                <div class="border rounded p-2">
                                    <h4>{len([u for u in USERS.values() if not u.get('deleted', False)])}</h4>
                                    <small>Aktivní</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="border rounded p-2">
                                    <h4>{len([u for u in USERS.values() if u.get('deleted', False)])}</h4>
                                    <small>Smazaní</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="border rounded p-2">
                                    <h4>{len([u for u in USERS.values() if u['role'] == 'admin' and not u.get('deleted', False)])}</h4>
                                    <small>Admini</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Filtry -->
                    <div class="mb-3">
                        <a href="/users" class="btn btn-outline-primary btn-sm w-100 mb-2 {'active' if not show_deleted else ''}">
                            <i class="bi bi-people"></i> Aktivní uživatelé
                        </a>
                        <a href="/users?show_deleted=true" class="btn btn-outline-danger btn-sm w-100 {'active' if show_deleted else ''}">
                            <i class="bi bi-trash"></i> Smazaní uživatelé
                        </a>
                    </div>
                    
                    <!-- Tlačítko pro přidání uživatele -->
                    <button class="btn btn-success w-100" data-bs-toggle="modal" data-bs-target="#addUserModal">
                        <i class="bi bi-person-plus"></i> Přidat uživatele
                    </button>
                    <button class="btn btn-primary w-100 mt-2" data-bs-toggle="modal" data-bs-target="#sendMessageModal">
                        <i class="bi bi-envelope"></i> Odeslat zprávu skupině
                    </button>
                </div>
            </div>
            
            <!-- Hlavní obsah -->
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="bi bi-people"></i> Seznam uživatelů</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Avatar</th>
                                        <th>Jméno</th>
                                        <th>Email</th>
                                        <th>Role</th>
                                        <th>Status</th>
                                        <th>Akce</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {users_html}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <!-- Návrat na dashboard -->
                <div class="mt-3">
                    <a href="/" class="btn btn-outline-primary">
                        <i class="bi bi-arrow-left"></i> Zpět na dashboard
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal pro přidání uživatele -->
    <div class="modal fade" id="addUserModal" tabindex="-1" data-bs-backdrop="static">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-person-plus"></i> Přidat nového uživatele</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="/admin/add_user">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Uživatelské jméno</label>
                            <input type="text" class="form-control" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Celé jméno</label>
                            <input type="text" class="form-control" name="full_name" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Heslo</label>
                            <input type="password" class="form-control" name="password" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Role</label>
                            <select class="form-control" name="role" required>
                                <option value="ridic">Řidič</option>
                                <option value="administrativa">Administrativa</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-success">Vytvořit uživatele</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Modal pro editaci uživatele -->
    <div class="modal fade" id="editUserModal" tabindex="-1" data-bs-backdrop="static">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-pencil"></i> Upravit uživatele</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="editUserForm" method="POST">
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Uživatelské jméno</label>
                                    <input type="text" class="form-control" id="editUsername" name="username" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Celé jméno</label>
                                    <input type="text" class="form-control" id="editFullName" name="full_name" required>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" id="editUserEmail" name="email" required>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Role</label>
                                    <select class="form-control" id="editUserRole" name="role" required>
                                        <option value="ridic">Řidič</option>
                                        <option value="administrativa">Administrativa</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Nové heslo (ponechte prázdné)</label>
                                    <input type="password" class="form-control" name="password">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Avatar</label>
                            <div class="row g-2">
                                {avatars_html}
                            </div>
                            <input type="hidden" id="editUserAvatar" name="avatar" value="">
                            <small class="text-muted">Klikněte na avatar pro výběr</small>
                        </div>
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="editUserActive" name="active" checked>
                            <label class="form-check-label" for="editUserActive">Účet je aktivní</label>
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
    
    <!-- Modal pro odeslání zprávy uživateli -->
    <div class="modal fade" id="sendUserMessageModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-envelope"></i> Odeslat zprávu uživateli</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="sendUserMessageForm" method="POST" action="/admin/send_message">
                    <input type="hidden" id="messageRecipientId" name="recipient_user_id">
                    <input type="hidden" name="recipient_type" value="single">
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <i class="bi bi-info-circle"></i> Odesílá se uživateli: <strong id="messageRecipientName"></strong>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Předmět</label>
                            <input type="text" class="form-control" name="subject" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Zpráva</label>
                            <textarea class="form-control" name="content" rows="5" required></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-primary">Odeslat zprávu</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <!-- Modal pro odeslání zprávy skupině -->
    <div class="modal fade" id="sendMessageModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-broadcast"></i> Odeslat zprávu skupině</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="/admin/send_message">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Příjemci</label>
                            <select class="form-control" name="recipient_type" required>
                                <option value="all">Všichni uživatelé</option>
                                <option value="ridic">Pouze řidiči</option>
                                <option value="administrativa">Pouze administrativa</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Předmět</label>
                            <input type="text" class="form-control" name="subject" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Zpráva</label>
                            <textarea class="form-control" name="content" rows="5" required></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-primary">Odeslat zprávu</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script>
    function selectAvatar(url) {{
        document.getElementById('editUserAvatar').value = url;
        document.querySelectorAll('.avatar-option').forEach(img => {{
            img.style.border = '';
        }});
        document.querySelector(`[data-avatar="${{url}}"]`).style.border = '3px solid #007bff';
    }}
    
    function editUser(id, username, email, fullName, role, avatar, active) {{
        document.getElementById('editUserForm').action = '/admin/edit_user/' + id;
        document.getElementById('editUsername').value = username;
        document.getElementById('editUserEmail').value = email;
        document.getElementById('editFullName').value = fullName;
        document.getElementById('editUserRole').value = role;
        document.getElementById('editUserActive').checked = active;
        document.getElementById('editUserAvatar').value = avatar;
        
        // Zvýraznit vybraný avatar
        document.querySelectorAll('.avatar-option').forEach(img => {{
            if (img.getAttribute('data-avatar') === avatar) {{
                img.style.border = '3px solid #007bff';
            }} else {{
                img.style.border = '';
            }}
        }});
        
        new bootstrap.Modal(document.getElementById('editUserModal')).show();
    }}
    
    function deleteUser(id, username) {{
        if (confirm('Opravdu chcete smazat uživatele ' + username + '?')) {{
            fetch('/admin/delete_user/' + id, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }}
            }}).then(() => {{
                location.reload();
            }});
        }}
    }}
    
    function restoreUser(id, username) {{
        if (confirm('Opravdu chcete obnovit uživatele ' + username + '?')) {{
            fetch('/admin/restore_user/' + id, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }}
            }}).then(() => {{
                location.reload();
            }});
        }}
    }}
    
    function sendMessageToUser(id, name) {{
        document.getElementById('messageRecipientId').value = id;
        document.getElementById('messageRecipientName').textContent = name;
        new bootstrap.Modal(document.getElementById('sendUserMessageModal')).show();
    }}
    </script>
    '''
    
    return render_template_string(BASE_TEMPLATE, title="Správa uživatelů", content=content)

@app.route('/admin/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'ridic')
    full_name = request.form.get('full_name', '').strip()
    
    # Validace
    if not all([username, email, password, full_name]):
        flash('Všechna pole jsou povinná.', 'error')
        return redirect(url_for('users'))
    
    # Kontrola duplicit
    for user in USERS.values():
        if user['username'] == username:
            flash('Uživatelské jméno již existuje.', 'error')
            return redirect(url_for('users'))
        if user['email'] == email:
            flash('Email již existuje.', 'error')
            return redirect(url_for('users'))
    
    # Vytvoření nového uživatele
    new_id = max(USERS.keys()) + 1
    USERS[new_id] = {
        'id': new_id,
        'username': username,
        'email': email,
        'password': generate_password_hash(password),
        'full_name': full_name,
        'role': role,
        'avatar': 'https://via.placeholder.com/50',
        'active': True
    }
    
    save_users()  # Uložit do JSON
    flash(f'Uživatel {username} byl úspěšně vytvořen.', 'success')
    return redirect(url_for('users'))

@app.route('/admin/edit_user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if user_id not in USERS:
        flash('Uživatel nebyl nalezen.', 'error')
        return redirect(url_for('users'))
    
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    role = request.form.get('role', 'ridic')
    full_name = request.form.get('full_name', '').strip()
    password = request.form.get('password', '').strip()
    avatar = request.form.get('avatar', '').strip()
    active = 'active' in request.form
    full_name = request.form.get('full_name', '').strip()
    password = request.form.get('password', '').strip()
    active = 'active' in request.form
    
    # Validace
    if not all([username, email, full_name]):
        flash('Uživatelské jméno, email a celé jméno jsou povinné.', 'error')
        return redirect(url_for('users'))
    
    # Kontrola duplicit (kromě současného uživatele)
    for uid, user in USERS.items():
        if uid != user_id:
            if user['username'] == username:
                flash('Uživatelské jméno již existuje.', 'error')
                return redirect(url_for('users'))
            if user['email'] == email:
                flash('Email již existuje.', 'error')
                return redirect(url_for('users'))
    
    # Aktualizace uživatele
    USERS[user_id].update({
        'username': username,
        'email': email,
        'full_name': full_name,
        'role': role,
        'active': active
    })
    
    # Změna hesla pokud je zadáno
    if password:
        USERS[user_id]['password'] = generate_password_hash(password)
    
    save_users()  # Uložit do JSON
    flash(f'Uživatel {username} byl úspěšně aktualizován.', 'success')
    return redirect(url_for('users'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Zamezení mazání vlastního účtu
    if user_id == session.get('user_id'):
        flash('Nelze smazat vlastní účet.', 'error')
        return redirect(url_for('users'))
    
    if user_id in USERS:
        username = USERS[user_id]['username']
        # Soft delete - pouze označíme jako smazaného
        USERS[user_id]['deleted'] = True
        USERS[user_id]['deleted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        USERS[user_id]['deleted_by'] = session.get('full_name', 'Admin')
        USERS[user_id]['active'] = False
        save_users()  # Uložit do JSON
        flash(f'Uživatel {username} byl úspěšně smazán.', 'success')
    else:
        flash('Uživatel nebyl nalezen.', 'error')
    
    return redirect(url_for('users'))

@app.route('/admin/restore_user/<int:user_id>', methods=['POST'])
def restore_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if user_id in USERS and USERS[user_id].get('deleted'):
        USERS[user_id]['deleted'] = False
        USERS[user_id]['deleted_at'] = ''
        USERS[user_id]['deleted_by'] = ''
        USERS[user_id]['active'] = True
        save_users()
        flash(f'Uživatel {USERS[user_id]["username"]} byl obnoven.', 'success')
    else:
        flash('Uživatel nebyl nalezen.', 'error')
    
    return redirect(url_for('users'))

@app.route('/admin/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    subject = request.form.get('subject', '').strip()
    content = request.form.get('content', '').strip()
    recipient_type = request.form.get('recipient_type', 'all')  # all, ridic, administrativa, single
    recipient_user_id = request.form.get('recipient_user_id')
    
    if not subject or not content:
        flash('Předmět a obsah zprávy jsou povinné.', 'error')
        return redirect(url_for('users'))
    
    # Vytvoření nové zprávy
    new_id = max([m['id'] for m in MESSAGES], default=0) + 1
    from_user = USERS[session['user_id']]
    
    new_message = {
        'id': new_id,
        'from_user_id': session['user_id'],
        'from_name': from_user['full_name'],
        'subject': subject,
        'content': content,
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'recipient_type': recipient_type,
        'recipient_user_id': int(recipient_user_id) if recipient_user_id else None,
        'read_by': []
    }
    
    MESSAGES.append(new_message)
    save_messages()
    
    # Zpráva o úspěchu
    if recipient_type == 'all':
        flash('Zpráva byla odeslána všem uživatelům.', 'success')
    elif recipient_type == 'single':
        recipient = USERS.get(int(recipient_user_id))
        if recipient:
            flash(f'Zpráva byla odeslána uživateli {recipient["full_name"]}.', 'success')
    else:
        role_names = {'ridic': 'řidičům', 'administrativa': 'administrativě'}
        flash(f'Zpráva byla odeslána {role_names.get(recipient_type, "skupině")}.', 'success')
    
    return redirect(url_for('users'))

@app.route('/message/<int:message_id>/mark_read', methods=['POST'])
def mark_message_read(message_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    for msg in MESSAGES:
        if msg['id'] == message_id:
            # Zkontrolovat jestli už není přečteno
            if user_id not in [r.get('user_id') for r in msg.get('read_by', [])]:
                msg['read_by'].append({
                    'user_id': user_id,
                    'read_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                save_messages()
            break
    
    return redirect(url_for('index'))

@app.route('/admin/edit_news/<int:news_id>', methods=['POST'])
def edit_news(news_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    content_full = request.form.get('content_full', content).strip()
    image = request.form.get('image', '').strip()
    featured = 'featured' in request.form
    
    if not title or not content:
        flash('Název a obsah novinky jsou povinné.', 'error')
        return redirect(url_for('index'))
    
    # Najdeme novinku podle ID
    news_found = None
    for i, news in enumerate(NEWS):
        if news['id'] == news_id:
            news_found = i
            break
    
    if news_found is not None:
        NEWS[news_found].update({
            'title': title,
            'content': content,
            'content_full': content_full,
            'image': image,
            'featured': featured
        })
        save_news()  # Uloží změny do JSON
        flash('Novinka byla úspěšně aktualizována.', 'success')
    else:
        flash('Novinka nebyla nalezena.', 'error')
    
    return redirect(url_for('index'))

@app.route('/admin/delete_news/<int:news_id>', methods=['POST'])
def delete_news(news_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Najdeme a smazeme novinku podle ID
    global NEWS
    original_count = len(NEWS)
    NEWS = [news for news in NEWS if news['id'] != news_id]
    save_news()  # Uloží změny do JSON
    
    if len(NEWS) < original_count:
        flash('Novinka byla úspěšně smazána.', 'success')
    else:
        flash('Novinka nebyla nalezena.', 'error')
    
    return redirect(url_for('index'))

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    """Zobrazení detailu novinky."""
    if 'user_id' not in session:
        flash('Nejste přihlášeni!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = USERS.get(user_id)
    
    # Najdeme novinku
    news_item = None
    for news in NEWS:
        if news['id'] == news_id:
            news_item = news
            break
    
    if not news_item:
        flash('Novinka nebyla nalezena.', 'error')
        return redirect(url_for('index'))
    
    # Zaznamenáme čtení
    if 'read_by' not in news_item:
        news_item['read_by'] = []
    
    # Přidáme uživatele do seznamu čtenářů, pokud tam ještě není
    reader_info = {
        'user_id': user_id,
        'full_name': user.get('full_name', 'Neznámý'),
        'read_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Kontrola, zda uživatel již četl
    already_read = False
    for reader in news_item['read_by']:
        if reader['user_id'] == user_id:
            already_read = True
            # Aktualizujeme čas posledního čtení
            reader['read_at'] = reader_info['read_at']
            break
    
    if not already_read:
        news_item['read_by'].append(reader_info)
    
    save_news()  # Uložíme změny
    
    # Vytvoříme HTML pro seznam čtenářů (jen pro admina)
    readers_html = ''
    if session.get('role') == 'admin' and news_item.get('read_by'):
        readers_html = '<div class="card mt-4"><div class="card-header"><h6><i class="bi bi-eye"></i> Přečetli (' + str(len(news_item['read_by'])) + ')</h6></div><div class="card-body"><ul class="list-unstyled">'
        for reader in news_item['read_by']:
            readers_html += f"<li><i class='bi bi-person-check'></i> {reader['full_name']} - <small class='text-muted'>{reader['read_at']}</small></li>"
        readers_html += '</ul></div></div>'
    
    content_full = news_item.get('content_full', news_item.get('content', ''))
    image_html = ''
    if news_item.get('image'):
        image_html = f'<div class="text-center mb-4"><img src="{news_item["image"]}" class="img-fluid" style="max-width: 100%; max-height: 500px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" alt="Obrázek novinky"></div>'
    
    # Systém komentářů
    if 'comments' not in news_item:
        news_item['comments'] = []
    
    def render_comment(comment, depth=0):
        """Rekurzivní renderování komentáře a jeho odpovědí."""
        comment_id = comment.get('id', 0)
        is_deleted = comment.get('deleted', False)
        is_owner = comment.get('user_id') == user_id
        is_admin_user = session.get('role') == 'admin'
        
        margin_left = f"margin-left: {depth * 30}px;" if depth > 0 else ""
        
        if is_deleted:
            restore_button = ''
            if is_admin_user:
                restore_button = f'''
                <form method="POST" action="/news/{news_id}/comment/{comment_id}/restore" style="display: inline;" class="mt-2">
                    <button type="submit" class="btn btn-success btn-sm" onclick="return confirm('Opravdu chcete obnovit tento komentář?')">
                        <i class="bi bi-arrow-counterclockwise"></i> Obnovit komentář
                    </button>
                </form>
                '''
            return f'''
            <div class="card mb-2 bg-light" style="{margin_left}">
                <div class="card-body p-2">
                    <small class="text-muted"><i class="bi bi-trash"></i> Komentář od <strong>{comment.get('author', 'Neznámý')}</strong> byl smazán administrátorem</small>
                    <div class="mt-1"><small class="text-muted">Původní datum: {comment.get('created', '')}</small></div>
                    <div class="mt-1"><small class="text-danger"><strong>Důvod smazání:</strong> {comment.get('delete_reason', 'Nezadán')}</small></div>
                    <small class="text-muted">Smazal: {comment.get('deleted_by', 'Admin')} | {comment.get('deleted_at', '')}</small>
                    {restore_button}
                </div>
            </div>
            '''
        
        edit_time = f" (upraveno {comment.get('edited_at', '')})" if comment.get('edited') else ""
        
        comment_html = f'''
        <div class="card mb-2" style="{margin_left}" id="comment-{comment_id}">
            <div class="card-body p-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <strong>{comment['author']}</strong> 
                        <small class="text-muted">• {comment['created']}{edit_time}</small>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary btn-sm" onclick="showReplyForm({comment_id}, '{comment['author']}')">
                            <i class="bi bi-reply"></i>
                        </button>
                        {f'<button class="btn btn-outline-secondary btn-sm" onclick="editComment({comment_id}, \'{comment["text"].replace("'", "\\'").replace(chr(10), "\\n")}\')"><i class="bi bi-pencil"></i></button>' if is_owner else ''}
                        {f'<button class="btn btn-outline-danger btn-sm" onclick="showDeleteModal({comment_id})"><i class="bi bi-trash"></i></button>' if is_admin_user else ''}
                    </div>
                </div>
                <div class="mt-2" id="comment-text-{comment_id}">
                    <p class="mb-0" style="white-space: pre-wrap;">{comment['text']}</p>
                </div>
                {f'''
                <button class="btn btn-sm btn-link text-decoration-none p-0 mt-1" onclick="toggleReplies({comment_id})" id="toggle-btn-{comment_id}">
                    <i class="bi bi-chevron-down" id="toggle-icon-{comment_id}"></i> {len(comment.get('replies', []))} {'odpověď' if len(comment.get('replies', [])) == 1 else 'odpovědi' if len(comment.get('replies', [])) < 5 else 'odpovědí'}
                </button>
                ''' if comment.get('replies') and len(comment.get('replies', [])) > 0 else ''}
                <div id="edit-form-{comment_id}" style="display: none;">
                    <form method="POST" action="/news/{news_id}/comment/{comment_id}/edit">
                        <textarea class="form-control form-control-sm mb-2" name="text" rows="3" required>{comment['text']}</textarea>
                        <button type="submit" class="btn btn-primary btn-sm">Uložit</button>
                        <button type="button" class="btn btn-secondary btn-sm" onclick="cancelEdit({comment_id})">Zrušit</button>
                    </form>
                </div>
                <div id="reply-form-{comment_id}" style="display: none;" class="mt-2">
                    <form method="POST" action="/news/{news_id}/comment/add">
                        <input type="hidden" name="parent_id" value="{comment_id}">
                        <textarea class="form-control form-control-sm mb-2" name="text" rows="2" placeholder="Napište odpověď..." required></textarea>
                        <button type="submit" class="btn btn-success btn-sm">Odeslat odpověď</button>
                        <button type="button" class="btn btn-secondary btn-sm" onclick="hideReplyForm({comment_id})">Zrušit</button>
                    </form>
                </div>
            </div>
        </div>
        '''
        
        # Přidání odpovědí
        replies_html = ''
        if comment.get('replies'):
            replies_html = f'<div id="replies-{comment_id}" style="display: none;">'
            for reply in comment.get('replies', []):
                replies_html += render_comment(reply, depth + 1)
            replies_html += '</div>'
        
        return comment_html + replies_html
    
    comments_html = ''
    for comment in news_item['comments']:
        comments_html += render_comment(comment)
    
    if not comments_html:
        comments_html = '<p class="text-muted">Zatím žádné komentáře. Buďte první!</p>'
    
    content = f'''
    <div class="container-fluid">
        <div class="mb-3">
            <a href="/" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> Zpět na dashboard</a>
        </div>
        
        <div class="row">
            <!-- Levá část - Obsah novinky -->
            <div class="col-lg-7">
                <div class="card sticky-top" style="top: 20px;">
                    <div class="card-header" style="background: {'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)' if news_item.get('featured') else 'linear-gradient(135deg, #2c5aa0 0%, #1e3a72 100%)'}; color: white;">
                        <h3 class="mb-0">{news_item['title']}</h3>
                        <small><i class="bi bi-person"></i> {news_item['author']} | <i class="bi bi-calendar"></i> {news_item['created']}</small>
                    </div>
                    <div class="card-body" style="max-height: 70vh; overflow-y: auto;">
                        {image_html}
                        <div style="white-space: pre-wrap; line-height: 1.8;">
                            {content_full}
                        </div>
                    </div>
                </div>
                
                {readers_html}
            </div>
            
            <!-- Pravá část - Komentáře -->
            <div class="col-lg-5">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="bi bi-chat-left-text"></i> Komentáře ({len(news_item['comments'])})</h5>
                    </div>
                    <div class="card-body p-3">
                        <!-- Formulář pro nový komentář -->
                        <form method="POST" action="/news/{news_id}/comment/add" class="mb-3">
                            <textarea class="form-control mb-2" name="text" rows="2" placeholder="Napište komentář..." required></textarea>
                            <button type="submit" class="btn btn-primary btn-sm w-100"><i class="bi bi-send"></i> Přidat komentář</button>
                        </form>
                        
                        <hr>
                        
                        <!-- Seznam komentářů -->
                        <div style="max-height: 60vh; overflow-y: auto;">
                            {comments_html}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modál pro smazání komentáře -->
    <div class="modal fade" id="deleteCommentModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-trash"></i> Smazat komentář</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="deleteCommentForm" method="POST">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Důvod smazání (povinné)</label>
                            <textarea class="form-control" name="delete_reason" rows="3" required placeholder="Uveďte důvod smazání komentáře..."></textarea>
                        </div>
                        <div class="alert alert-warning">
                            <i class="bi bi-exclamation-triangle"></i> Komentář bude označen jako smazaný a všem uživatelům se zobrazí důvod smazání.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-danger">Smazat komentář</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        function showReplyForm(commentId, author) {{
            document.getElementById('reply-form-' + commentId).style.display = 'block';
        }}
        
        function hideReplyForm(commentId) {{
            document.getElementById('reply-form-' + commentId).style.display = 'none';
        }}
        
        function editComment(commentId, text) {{
            document.getElementById('comment-text-' + commentId).style.display = 'none';
            document.getElementById('edit-form-' + commentId).style.display = 'block';
        }}
        
        function cancelEdit(commentId) {{
            document.getElementById('comment-text-' + commentId).style.display = 'block';
            document.getElementById('edit-form-' + commentId).style.display = 'none';
        }}
        
        function showDeleteModal(commentId) {{
            const form = document.getElementById('deleteCommentForm');
            form.action = '/news/{news_id}/comment/' + commentId + '/delete';
            const modal = new bootstrap.Modal(document.getElementById('deleteCommentModal'));
            modal.show();
        }}
        
        function toggleReplies(commentId) {{
            const repliesDiv = document.getElementById('replies-' + commentId);
            const icon = document.getElementById('toggle-icon-' + commentId);
            
            if (repliesDiv.style.display === 'none') {{
                repliesDiv.style.display = 'block';
                icon.className = 'bi bi-chevron-up';
            }} else {{
                repliesDiv.style.display = 'none';
                icon.className = 'bi bi-chevron-down';
            }}
        }}
    </script>
    '''
    
    return render_template_string(BASE_TEMPLATE, title=news_item['title'], content=content)

@app.route('/news/<int:news_id>/comment/add', methods=['POST'])
def add_comment(news_id):
    """Přidání komentáře k novince."""
    if 'user_id' not in session:
        flash('Nejste přihlášeni!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = USERS.get(user_id)
    text = request.form.get('text', '').strip()
    parent_id = request.form.get('parent_id', '')
    
    if not text:
        flash('Komentář nesmí být prázdný!', 'error')
        return redirect(url_for('news_detail', news_id=news_id))
    
    # Najdeme novinku
    news_item = None
    for news in NEWS:
        if news['id'] == news_id:
            news_item = news
            break
    
    if not news_item:
        flash('Novinka nebyla nalezena.', 'error')
        return redirect(url_for('index'))
    
    if 'comments' not in news_item:
        news_item['comments'] = []
    
    # Vytvoření nového komentáře
    new_comment = {
        'id': max([c.get('id', 0) for c in news_item['comments']], default=0) + 1,
        'user_id': user_id,
        'author': user.get('full_name', 'Neznámý'),
        'text': text,
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'edited': False,
        'deleted': False,
        'replies': []
    }
    
    # Pokud je to odpověď na jiný komentář
    if parent_id:
        parent_id = int(parent_id)
        
        def add_reply_to_comment(comments):
            for comment in comments:
                if comment['id'] == parent_id:
                    if 'replies' not in comment:
                        comment['replies'] = []
                    comment['replies'].append(new_comment)
                    return True
                if comment.get('replies'):
                    if add_reply_to_comment(comment['replies']):
                        return True
            return False
        
        if not add_reply_to_comment(news_item['comments']):
            # Pokud se nepodařilo najít rodičovský komentář, přidáme jako hlavní
            news_item['comments'].append(new_comment)
    else:
        # Hlavní komentář
        news_item['comments'].append(new_comment)
    
    save_news()
    flash('Komentář byl přidán!', 'success')
    return redirect(url_for('news_detail', news_id=news_id))

@app.route('/news/<int:news_id>/comment/<int:comment_id>/edit', methods=['POST'])
def edit_comment(news_id, comment_id):
    """Editace komentáře."""
    if 'user_id' not in session:
        flash('Nejste přihlášeni!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    text = request.form.get('text', '').strip()
    
    if not text:
        flash('Komentář nesmí být prázdný!', 'error')
        return redirect(url_for('news_detail', news_id=news_id))
    
    # Najdeme novinku
    news_item = None
    for news in NEWS:
        if news['id'] == news_id:
            news_item = news
            break
    
    if not news_item:
        flash('Novinka nebyla nalezena.', 'error')
        return redirect(url_for('index'))
    
    # Najdeme a upravíme komentář
    def update_comment(comments):
        for comment in comments:
            if comment['id'] == comment_id:
                if comment['user_id'] == user_id:
                    comment['text'] = text
                    comment['edited'] = True
                    comment['edited_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    return True
                else:
                    flash('Nemůžete upravovat cizí komentáře!', 'error')
                    return False
            if comment.get('replies'):
                if update_comment(comment['replies']):
                    return True
        return False
    
    if update_comment(news_item.get('comments', [])):
        save_news()
        flash('Komentář byl upraven!', 'success')
    else:
        flash('Komentář nebyl nalezen!', 'error')
    
    return redirect(url_for('news_detail', news_id=news_id))

@app.route('/news/<int:news_id>/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(news_id, comment_id):
    """Smazání komentáře (pouze admin)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemáte oprávnění!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = USERS.get(user_id)
    delete_reason = request.form.get('delete_reason', '').strip()
    
    if not delete_reason:
        flash('Musíte uvést důvod smazání!', 'error')
        return redirect(url_for('news_detail', news_id=news_id))
    
    # Najdeme novinku
    news_item = None
    for news in NEWS:
        if news['id'] == news_id:
            news_item = news
            break
    
    if not news_item:
        flash('Novinka nebyla nalezena.', 'error')
        return redirect(url_for('index'))
    
    # Najdeme a označíme komentář jako smazaný
    def mark_deleted(comments):
        for comment in comments:
            if comment['id'] == comment_id:
                comment['deleted'] = True
                comment['delete_reason'] = delete_reason
                comment['deleted_by'] = user.get('full_name', 'Admin')
                comment['deleted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return True
            if comment.get('replies'):
                if mark_deleted(comment['replies']):
                    return True
        return False
    
    if mark_deleted(news_item.get('comments', [])):
        save_news()
        flash('Komentář byl smazán!', 'success')
    else:
        flash('Komentář nebyl nalezen!', 'error')
    
    return redirect(url_for('news_detail', news_id=news_id))

@app.route('/news/<int:news_id>/comment/<int:comment_id>/restore', methods=['POST'])
def restore_comment(news_id, comment_id):
    """Obnovení smazaného komentáře (pouze admin)."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemáte oprávnění!', 'error')
        return redirect(url_for('login'))
    
    # Najdeme novinku
    news_item = None
    for news in NEWS:
        if news['id'] == news_id:
            news_item = news
            break
    
    if not news_item:
        flash('Novinka nebyla nalezena.', 'error')
        return redirect(url_for('index'))
    
    # Najdeme a obnovíme komentář
    def restore(comments):
        for comment in comments:
            if comment['id'] == comment_id:
                comment['deleted'] = False
                comment['delete_reason'] = ''
                comment['deleted_by'] = ''
                comment['deleted_at'] = ''
                return True
            if comment.get('replies'):
                if restore(comment['replies']):
                    return True
        return False
    
    if restore(news_item.get('comments', [])):
        save_news()
        flash('Komentář byl obnoven!', 'success')
    else:
        flash('Komentář nebyl nalezen!', 'error')
    
    # Vrátit na stránku odkud přišel (referer) nebo na detail novinky
    referer = request.referrer
    if referer and 'deleted-comments' in referer:
        return redirect(url_for('admin_deleted_comments'))
    else:
        return redirect(url_for('news_detail', news_id=news_id))

@app.route('/admin/deleted-comments')
def admin_deleted_comments():
    """Admin panel pro správu smazaných komentářů."""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Nemáte oprávnění!', 'error')
        return redirect(url_for('login'))
    
    # Najdeme všechny smazané komentáře
    deleted_comments = []
    
    def find_deleted(comments, news_title, news_id):
        for comment in comments:
            if comment.get('deleted'):
                deleted_comments.append({
                    'comment': comment,
                    'news_title': news_title,
                    'news_id': news_id
                })
            if comment.get('replies'):
                find_deleted(comment['replies'], news_title, news_id)
    
    for news in NEWS:
        find_deleted(news.get('comments', []), news['title'], news['id'])
    
    # Seřadit podle data smazání (nejnovější první)
    deleted_comments.sort(key=lambda x: x['comment'].get('deleted_at', ''), reverse=True)
    
    # Generování tabulky
    comments_html = ''
    if deleted_comments:
        for item in deleted_comments:
            comment = item['comment']
            comments_html += f'''
            <tr>
                <td><a href="/news/{item['news_id']}" class="text-decoration-none">{item['news_title']}</a></td>
                <td><strong>{comment.get('author', 'Neznámý')}</strong></td>
                <td><small>{comment.get('created', '')}</small></td>
                <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{comment.get('text', '')[:100]}...</td>
                <td><span class="text-danger">{comment.get('delete_reason', 'Nezadán')}</span></td>
                <td><small>{comment.get('deleted_by', 'Admin')}<br>{comment.get('deleted_at', '')}</small></td>
                <td>
                    <form method="POST" action="/news/{item['news_id']}/comment/{comment['id']}/restore" style="display: inline;">
                        <button type="submit" class="btn btn-success btn-sm" onclick="return confirm('Opravdu chcete obnovit tento komentář?')">
                            <i class="bi bi-arrow-counterclockwise"></i> Obnovit
                        </button>
                    </form>
                </td>
            </tr>
            '''
    else:
        comments_html = '<tr><td colspan="7" class="text-center text-muted">Žádné smazané komentáře</td></tr>'
    
    content = f'''
    <div class="container-fluid mt-4">
        <div class="mb-3">
            <a href="/" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> Zpět na dashboard</a>
        </div>
        
        <div class="card">
            <div class="card-header bg-danger text-white">
                <h4 class="mb-0"><i class="bi bi-trash"></i> Správa smazaných komentářů</h4>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> Zde můžete zobrazit všechny smazané komentáře a případně je obnovit.
                </div>
                
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Novinka</th>
                                <th>Autor</th>
                                <th>Vytvořeno</th>
                                <th>Text komentáře</th>
                                <th>Důvod smazání</th>
                                <th>Smazal</th>
                                <th>Akce</th>
                            </tr>
                        </thead>
                        <tbody>
                            {comments_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title='Smazané komentáře', content=content)

@app.route('/news/archive')
def news_archive():
    """Archiv všech novinek s filtrováním podle roku a měsíce."""
    if 'user_id' not in session:
        flash('Nejste přihlášeni!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'
    
    # Získání filtru z URL parametrů
    year_filter = request.args.get('year', '')
    month_filter = request.args.get('month', '')
    
    # Získání seznamu dostupných roků a měsíců
    available_dates = {}
    for news in NEWS:
        created_date = news['created'][:10]  # YYYY-MM-DD
        year = created_date[:4]
        month = created_date[5:7]
        
        if year not in available_dates:
            available_dates[year] = set()
        available_dates[year].add(month)
    
    # Seřazení roků sestupně
    sorted_years = sorted(available_dates.keys(), reverse=True)
    
    # Filtrování novinek
    filtered_news = NEWS
    if year_filter:
        filtered_news = [n for n in filtered_news if n['created'][:4] == year_filter]
    if month_filter:
        filtered_news = [n for n in filtered_news if n['created'][5:7] == month_filter]
    
    # Vytvoření filtrovacího formuláře
    month_names = {
        '01': 'Leden', '02': 'Únor', '03': 'Březen', '04': 'Duben',
        '05': 'Květen', '06': 'Červen', '07': 'Červenec', '08': 'Srpen',
        '09': 'Září', '10': 'Říjen', '11': 'Listopad', '12': 'Prosinec'
    }
    
    year_options = '<option value="">Všechny roky</option>'
    for year in sorted_years:
        selected = 'selected' if year == year_filter else ''
        year_options += f'<option value="{year}" {selected}>{year}</option>'
    
    month_options = '<option value="">Všechny měsíce</option>'
    if year_filter and year_filter in available_dates:
        for month in sorted(available_dates[year_filter]):
            selected = 'selected' if month == month_filter else ''
            month_options += f'<option value="{month}" {selected}>{month_names.get(month, month)}</option>'
    
    filter_html = f'''
    <div class="card mb-3">
        <div class="card-body">
            <form method="GET" class="row g-2">
                <div class="col-md-4">
                    <label class="form-label">Rok</label>
                    <select name="year" class="form-select" onchange="this.form.submit()">
                        {year_options}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Měsíc</label>
                    <select name="month" class="form-select" onchange="this.form.submit()">
                        {month_options}
                    </select>
                </div>
                <div class="col-md-4 d-flex align-items-end">
                    <a href="/news/archive" class="btn btn-secondary w-100">Zrušit filtr</a>
                </div>
            </form>
        </div>
    </div>
    '''
    
    # Generování HTML pro novinky
    def count_all_comments(comments):
        """Rekurzivně spočítá všechny komentáře včetně odpovědí."""
        count = len(comments)
        for comment in comments:
            if comment.get('replies'):
                count += count_all_comments(comment['replies'])
        return count
    
    news_list_html = ''
    for news in filtered_news:
        featured_class = "border-danger" if news.get('featured', False) else "border-primary"
        star = "⭐ " if news.get('featured', False) else ""
        read_count = len(news.get('read_by', []))
        comments_count = count_all_comments(news.get('comments', []))
        
        admin_buttons = ''
        if is_admin:
            title_escaped = news['title'].replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            content_escaped = news['content'].replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            content_full_escaped = news.get('content_full', news['content']).replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            image_escaped = news.get('image', '').replace("'", "\\'").replace('"', '\\"')
            
            admin_buttons = f'''
            <div class="btn-group btn-group-sm mt-2" onclick="event.stopPropagation();">
                <button class="btn btn-outline-primary btn-sm" onclick="editNews({news['id']}, '{title_escaped}', '{content_escaped}', '{content_full_escaped}', '{image_escaped}', {str(news.get('featured', False)).lower()}); event.stopPropagation();">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteNews({news['id']}, '{title_escaped}'); event.stopPropagation();">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            '''
        
        news_list_html += f'''
        <div class="card {featured_class} mb-3" style="border-left: 4px solid; cursor: pointer;" onclick="window.location.href='/news/{news['id']}'">
            <div class="card-body">
                <h5 class="card-title">{star}{news["title"]}</h5>
                <p class="card-text"><strong>{news["content"]}</strong></p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">
                        <i class="bi bi-person"></i> {news["author"]} | <i class="bi bi-calendar"></i> {news["created"]}
                    </small>
                    <div>
                        {'<span class="badge bg-success me-1"><i class="bi bi-eye"></i> ' + str(read_count) + '</span>' if is_admin and read_count > 0 else ''}
                        <span class="badge bg-info">💬 {comments_count}</span>
                    </div>
                </div>
                {admin_buttons}
            </div>
        </div>
        '''
    
    if not news_list_html:
        news_list_html = '<div class="alert alert-info">Žádné novinky nenalezeny pro vybrané filtry.</div>'
    
    content = f'''
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="mb-3">
                <a href="/" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> Zpět na dashboard</a>
            </div>
            
            <div class="card mb-4">
                <div class="card-header" style="background: linear-gradient(135deg, #2c5aa0 0%, #1e3a72 100%); color: white;">
                    <h4 class="mb-0"><i class="bi bi-archive"></i> Archiv novinek</h4>
                    <small>Celkem {len(filtered_news)} novinek{f" (filtrováno)" if year_filter or month_filter else ""}</small>
                </div>
            </div>
            
            {filter_html}
            
            {news_list_html}
        </div>
    </div>
    '''
    
    return render_template_string(BASE_TEMPLATE, title='Archiv novinek', content=content)

# Funkce pro perzistentní uložení dat
def save_users():
    """Uloží uživatele do JSON souboru."""
    users_list = list(USERS.values())
    with open('data_users.json', 'w', encoding='utf-8') as f:
        json.dump(users_list, f, ensure_ascii=False, indent=2)

def save_applications():
    """Uloží aplikace do JSON souboru."""
    with open('data_applications.json', 'w', encoding='utf-8') as f:
        json.dump(APPLICATIONS, f, ensure_ascii=False, indent=2)

def save_news():
    """Uloží novinky do JSON souboru."""
    with open('data_news.json', 'w', encoding='utf-8') as f:
        json.dump(NEWS, f, ensure_ascii=False, indent=2)

def save_messages():
    """Uloží zprávy do JSON souboru."""
    with open('data_messages.json', 'w', encoding='utf-8') as f:
        json.dump(MESSAGES, f, ensure_ascii=False, indent=2)

def load_data():
    """Načte data ze souborů při startu aplikace."""
    global USERS, APPLICATIONS, NEWS, MESSAGES
    
    # Načítání uživatelů
    if os.path.exists('data_users.json'):
        try:
            with open('data_users.json', 'r', encoding='utf-8') as f:
                users_list = json.load(f)
                USERS = {user['id']: user for user in users_list}
                print(f"✅ Načteno {len(USERS)} uživatelů z data_users.json")
        except Exception as e:
            print(f"⚠️ Chyba při načítání uživatelů: {e}")
    
    # Načítání aplikací
    if os.path.exists('data_applications.json'):
        try:
            with open('data_applications.json', 'r', encoding='utf-8') as f:
                APPLICATIONS[:] = json.load(f)
                print(f"✅ Načteno {len(APPLICATIONS)} aplikací z data_applications.json")
        except Exception as e:
            print(f"⚠️ Chyba při načítání aplikací: {e}")
    
    # Načítání novinek
    if os.path.exists('data_news.json'):
        try:
            with open('data_news.json', 'r', encoding='utf-8') as f:
                NEWS[:] = json.load(f)
                print(f"✅ Načteno {len(NEWS)} novinek z data_news.json")
        except Exception as e:
            print(f"⚠️ Chyba při načítání novinek: {e}")
    
    # Načítání zpráv
    if os.path.exists('data_messages.json'):
        try:
            with open('data_messages.json', 'r', encoding='utf-8') as f:
                MESSAGES[:] = json.load(f)
                print(f"✅ Načteno {len(MESSAGES)} zpráv z data_messages.json")
        except Exception as e:
            print(f"⚠️ Chyba při načítání zpráv: {e}")

if __name__ == '__main__':
    # Načtení dat při startu
    load_data()
    
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