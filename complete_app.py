#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
European Transport CZ - Kompletni funkci aplikace
"""

import os
import json
import base64
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_from_directory
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
        'full_name': 'Administrátor systému',
        'role': 'admin',
        'avatar': 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iI2RjMjYyNiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSI1MCIgZm9udC13ZWlnaHQ9ImJvbGQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIj5BPC90ZXh0Pjwvc3ZnPg==',
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
        'avatar': 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iIzI1NjNlYiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSI1MCIgZm9udC13ZWlnaHQ9ImJvbGQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIj7FmjwvdGV4dD48L3N2Zz4=',
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
        'avatar': 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iI2Y5NzMxNiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSI1MCIgZm9udC13ZWlnaHQ9ImJvbGQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIj5BPC90ZXh0Pjwvc3ZnPg==',
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
    {'id': 1, 'name': 'Sprava vozidel', 'icon': '🚛', 'status': 'planned', 'description': 'Modul pro spravu vozoveho parku', 'visible_for_ridic': True, 'visible_for_admin': True},
    {'id': 2, 'name': 'GPS tracking', 'icon': '📍', 'status': 'planned', 'description': 'Sledovani pozice vozidel', 'visible_for_ridic': True, 'visible_for_admin': True},
    {'id': 3, 'name': 'Sklady', 'icon': '📦', 'status': 'planned', 'description': 'Sprava skladovych zasob', 'visible_for_ridic': False, 'visible_for_admin': True},
    {'id': 4, 'name': 'Ucetnictvi', 'icon': '💰', 'status': 'planned', 'description': 'Financni modul', 'visible_for_ridic': False, 'visible_for_admin': True},
    {'id': 5, 'name': 'Dovolená', 'icon': '🏖️', 'status': 'active', 'description': 'Správa dovolené a pracovního volna', 'visible_for_ridic': True, 'visible_for_admin': True, 'url': '/app_ad/dovolena/index.php'},
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
        :root {
            --primary-blue: #2563eb;
            --primary-blue-dark: #1e40af;
            --primary-blue-light: #3b82f6;
            --accent-blue: #60a5fa;
            --bg-light: #f8fafc;
            --bg-white: #ffffff;
            --text-dark: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        
        /* Dark mode */
        [data-theme="dark"] {
            --primary-blue: #3b82f6;
            --primary-blue-dark: #2563eb;
            --primary-blue-light: #60a5fa;
            --accent-blue: #93c5fd;
            --bg-light: #0f172a;
            --bg-white: #1e293b;
            --text-dark: #f1f5f9;
            --text-muted: #cbd5e1;
            --border-color: #334155;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
        }
        
        /* Pink mode */
        [data-theme="pink"] {
            --primary-blue: #ec4899;
            --primary-blue-dark: #db2777;
            --primary-blue-light: #f472b6;
            --accent-blue: #f9a8d4;
            --bg-light: #fdf2f8;
            --bg-white: #ffffff;
            --text-dark: #831843;
            --text-muted: #9f1239;
            --border-color: #fbcfe8;
            --shadow-sm: 0 1px 2px 0 rgba(236, 72, 153, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(236, 72, 153, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(236, 72, 153, 0.1);
        }
        
        body { 
            background: var(--bg-light);
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            color: var(--text-dark);
            line-height: 1.6;
        }
        
        /* Navbar - moderní, plochý design */
        .navbar { 
            background: var(--bg-white) !important;
            border-bottom: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            padding: 1rem 0;
        }
        
        .navbar-brand.logo { 
            font-weight: 600;
            color: var(--primary-blue) !important;
            font-size: 1.25rem;
            letter-spacing: -0.02em;
        }
        
        .navbar .nav-link {
            color: var(--text-muted) !important;
            font-weight: 500;
            transition: color 0.2s;
        }
        
        .navbar .nav-link:hover {
            color: var(--primary-blue) !important;
        }
        
        .navbar-text {
            color: var(--text-dark) !important;
            font-weight: 500;
        }
        
        /* Theme switcher */
        .theme-switcher {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            margin-right: 1rem;
        }
        
        .theme-btn {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 2px solid var(--border-color);
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            background: transparent;
        }
        
        .theme-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .theme-btn.active {
            border-width: 3px;
            box-shadow: 0 0 0 2px var(--bg-light);
        }
        
        .theme-light { color: #2563eb; }\n        .theme-light.active { background: #eff6ff; }
        .theme-dark { color: #60a5fa; }
        .theme-dark.active { background: #1e293b; }
        .theme-pink { color: #ec4899; }
        .theme-pink.active { background: #fce7f3; }
        
        /* Moderní badge design */
        .admin-badge { 
            background: var(--primary-blue);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .user-badge { 
            background: #10b981;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Karty - čistý, minimalistický design */
        .card { 
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
        }
        
        .card:hover { 
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }
        
        .card-header {
            background: var(--bg-white);
            border-bottom: 1px solid var(--border-color);
            padding: 1.25rem 1.5rem;
            font-weight: 600;
            color: var(--text-dark);
        }
        
        .card-body {
            padding: 1.5rem;
        }
        
        /* Tlačítka - moderní, plochý styl */
        .btn-primary { 
            background: var(--primary-blue);
            border: none;
            padding: 0.625rem 1.25rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
            box-shadow: var(--shadow-sm);
        }
        
        .btn-primary:hover { 
            background: var(--primary-blue-dark);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .btn-outline-primary {
            border: 1.5px solid var(--primary-blue);
            color: var(--primary-blue);
            background: transparent;
            padding: 0.625rem 1.25rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .btn-outline-primary:hover {
            background: var(--primary-blue);
            color: white;
            transform: translateY(-1px);
        }
        
        /* Aplikační dlaždice - moderní grid design */
        .app-tile { 
            background: var(--bg-white);
            border: 1.5px solid var(--border-color);
            border-radius: 10px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .app-tile:hover { 
            border-color: var(--primary-blue);
            background: #eff6ff;
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
        }
        
        .app-tile h6 {
            color: var(--text-dark);
            font-weight: 600;
        }
        
        .app-tile .small {
            color: var(--text-muted);
        }
        
        /* Novinky - čistý design */
        .news-card { 
            border-left: 3px solid var(--primary-blue);
            background: var(--bg-white);
        }
        
        .featured-news { 
            border-left: 3px solid var(--primary-blue-light);
            background: linear-gradient(to right, #eff6ff, var(--bg-white));
        }
        
        /* Zprávy */
        .message-item { 
            border-left: 3px solid var(--accent-blue);
            background: var(--bg-white);
            transition: all 0.2s;
        }
        
        .message-item:hover {
            background: var(--bg-light);
        }
        
        .unread { 
            background: #eff6ff;
            border-left-color: var(--primary-blue);
            font-weight: 500;
        }
        
        /* Sidebar a sekce */
        .sidebar { 
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
        }
        
        .content-section { 
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.75rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow-sm);
        }
        
        .admin-panel { 
            background: linear-gradient(to right, #eff6ff, var(--bg-white));
            border: 1.5px solid var(--accent-blue);
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        /* Typografie */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-dark);
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        .text-muted {
            color: var(--text-muted) !important;
        }
        
        /* Formuláře */
        .form-control, .form-select {
            border: 1.5px solid var(--border-color);
            border-radius: 8px;
            padding: 0.625rem 0.875rem;
            transition: all 0.2s;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        /* Badges */
        .badge {
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.8rem;
        }
        
        .bg-success {
            background: #10b981 !important;
        }
        
        .bg-warning {
            background: #f59e0b !important;
        }
        
        .bg-info {
            background: var(--accent-blue) !important;
        }
        
        .bg-secondary {
            background: var(--text-muted) !important;
        }
        
        /* Alert messages */
        .alert {
            border: none;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            border-left: 3px solid;
        }
        
        .alert-success {
            background: #d1fae5;
            border-left-color: #10b981;
            color: #065f46;
        }
        
        .alert-info {
            background: #dbeafe;
            border-left-color: var(--primary-blue);
            color: #1e40af;
        }
        
        .alert-danger {
            background: #fee2e2;
            border-left-color: #ef4444;
            color: #991b1b;
        }
        
        /* Animace */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .card, .app-tile, .content-section {
            animation: fadeIn 0.4s ease-out;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-light);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }
        
        /* Admin sidebar buttons */
        .btn-light:hover {
            background: var(--bg-light) !important;
            border-color: var(--primary-blue) !important;
            transform: translateX(4px);
        }
        
        .btn-light:hover i {
            transform: scale(1.1);
        }
        
        /* Dark mode specific fixes */
        [data-theme="dark"] .btn-light {
            background: var(--bg-white);
            color: var(--text-dark);
        }
        
        [data-theme="dark"] .navbar {
            border-bottom-color: var(--border-color);
        }
        
        [data-theme="dark"] .alert-success {
            background: #134e4a;
            border-left-color: #10b981;
            color: #d1fae5;
        }
        
        [data-theme="dark"] .alert-info {
            background: #1e3a8a;
            border-left-color: var(--primary-blue);
            color: #dbeafe;
        }
        
        [data-theme="dark"] .alert-danger {
            background: #7f1d1d;
            border-left-color: #ef4444;
            color: #fee2e2;
        }
        
        [data-theme="dark"] .form-control,
        [data-theme="dark"] .form-select {
            background: var(--bg-light);
            color: var(--text-dark);
            border-color: var(--border-color);
        }
        
        [data-theme="dark"] .form-control::placeholder {
            color: var(--text-muted);
        }
        
        [data-theme="dark"] .text-muted {
            color: var(--text-muted) !important;
        }
    </style>
    <script>
        // Theme switcher logic
        function setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            updateThemeButtons();
        }
        
        function updateThemeButtons() {
            const currentTheme = localStorage.getItem('theme') || 'light';
            document.querySelectorAll('.theme-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.theme === currentTheme) {
                    btn.classList.add('active');
                }
            });
        }
        
        // Load theme on page load
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeButtons();
        });
    </script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light">
        <div class="container-fluid px-4">
            <a class="navbar-brand logo" href="/">🚛 European Transport CZ</a>
            <div class="navbar-nav ms-auto d-flex align-items-center">
                <div class="theme-switcher">
                    <button class="theme-btn theme-light" data-theme="light" onclick="setTheme('light')" title="Světlý režim">
                        <i class="bi bi-sun-fill"></i>
                    </button>
                    <button class="theme-btn theme-dark" data-theme="dark" onclick="setTheme('dark')" title="Tmavý režim">
                        <i class="bi bi-moon-stars-fill"></i>
                    </button>
                    <button class="theme-btn theme-pink" data-theme="pink" onclick="setTheme('pink')" title="Růžový režim">
                        <i class="bi bi-heart-fill"></i>
                    </button>
                </div>
                {% if session.user_id %}
                    <span class="navbar-text me-3">
                        <i class="bi bi-person-circle"></i> {{ session.full_name }}
                        <span class="badge ms-2 {{ 'admin-badge' if session.role == 'admin' else 'user-badge' }}">
                            {{ {'admin': 'Admin', 'ridic': 'Řidič', 'administrativa': 'Administrativa'}.get(session.role, session.role|title) }}
                        </span>
                    </span>
                    <a class="nav-link" href="/logout"><i class="bi bi-box-arrow-right"></i> Odhlásit</a>
                {% else %}
                    <a class="nav-link" href="/login"><i class="bi bi-box-arrow-in-right"></i> Přihlásit</a>
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
    
    <!-- Modal pro přidání aplikace -->
    <div class="modal fade" id="addAppModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Přidat novou aplikaci</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="addAppForm" method="POST" action="/admin/add_application">
                    <div class="modal-body">
                        <input type="hidden" id="addAppFolder" name="folder">
                        <div class="mb-3">
                            <label class="form-label">Název aplikace</label>
                            <input type="text" class="form-control" id="addAppName" name="name" required>
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
                            <input type="text" class="form-control" id="addAppUrl" name="url" placeholder="/app_ad/nazev/">
                            <small class="text-muted">Relativní cesta od root nebo plná URL</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Stav</label>
                            <select class="form-control" id="addAppStatus" name="status" required>
                                <option value="available">Dostupná</option>
                                <option value="planned">Plánovaná</option>
                            </select>
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
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" name="visible_for_admin" id="visibleForAdmin" checked>
                            <label class="form-check-label" for="visibleForAdmin">
                                Viditelné pro profil Administrativa
                            </label>
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
                <form id="editAppForm" method="POST" action="/admin/edit_application">
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
                            <input type="text" class="form-control" id="editAppUrl" name="url" placeholder="/app_ad/nazev/">
                            <small class="text-muted">Relativní cesta od root nebo plná URL</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Stav</label>
                            <select class="form-control" id="editAppStatus" name="status" required>
                                <option value="available">Dostupná</option>
                                <option value="planned">Plánovaná</option>
                            </select>
                        </div>
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" id="editAppRequirePassword" name="require_password">
                            <label class="form-check-label" for="editAppRequirePassword">
                                Vyžadovat heslo před přechodem
                            </label>
                        </div>
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" id="editAppVisibleForRidic" name="visible_for_ridic">
                            <label class="form-check-label" for="editAppVisibleForRidic">
                                Viditelné pro profil Řidič
                            </label>
                        </div>
                        <div class="form-check mb-3">
                            <input type="checkbox" class="form-check-input" id="editAppVisibleForAdmin" name="visible_for_admin">
                            <label class="form-check-label" for="editAppVisibleForAdmin">
                                Viditelné pro profil Administrativa
                            </label>
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
                        <div class="form-check mb-2">
                            <input type="checkbox" class="form-check-input" id="editNewsFeatured" name="featured">
                            <label class="form-check-label" for="editNewsFeatured">⭐ Důležitá novinka (zvýrazněná)</label>
                        </div>
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="editNewsPinned" name="pinned">
                            <label class="form-check-label" for="editNewsPinned">📌 Připnout (zobrazí se i po přečtení)</label>
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
    
    <!-- Modal pro editaci zprávy -->
    <div class="modal fade" id="editMessageModal" tabindex="-1" data-bs-backdrop="static">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="bi bi-pencil"></i> Upravit zprávu</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form id="editMessageForm" method="POST">
                    <input type="hidden" id="editMessageId" name="message_id">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Předmět</label>
                            <input type="text" class="form-control" id="editMessageSubject" name="subject" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Obsah zprávy</label>
                            <textarea class="form-control" id="editMessageContent" name="content" rows="8" required></textarea>
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
                        <div class="form-check mb-2">
                            <input type="checkbox" class="form-check-input" name="featured" id="addNewsFeatured">
                            <label class="form-check-label" for="addNewsFeatured">⭐ Důležitá novinka (zvýrazněná)</label>
                        </div>
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" name="pinned" id="addNewsPinned">
                            <label class="form-check-label" for="addNewsPinned">📌 Připnout (zobrazí se i po přečtení)</label>
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
                    // Pokud URL začíná lomítkem, je to relativní cesta
                    if (url.startsWith('/')) {
                        window.location.href = url;
                    } else {
                        window.open(url, '_blank');
                    }
                } else {
                    alert('Přístup zrušen');
                }
            } else {
                // Pokud URL začíná lomítkem, je to relativní cesta
                if (url.startsWith('/')) {
                    window.location.href = url;
                } else {
                    window.open(url, '_blank');
                }
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
        
        function editNews(newsId, title, content, contentFull, image, featured, pinned) {
            document.getElementById('editNewsForm').action = '/admin/edit_news/' + newsId;
            document.getElementById('editNewsTitle').value = title;
            document.getElementById('editNewsContent').value = content;
            document.getElementById('editNewsContentFull').value = contentFull || content;
            document.getElementById('editNewsImage').value = image || '';
            document.getElementById('editNewsFeatured').checked = featured;
            document.getElementById('editNewsPinned').checked = pinned || false;
            
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
    
    # Zobrazit pouze nepřečtené novinky (nebo připnuté) na titulní stránce
    unread_news_list = []
    for news in NEWS:
        readers = [r['user_id'] for r in news.get('read_by', [])]
        # Zobrazit pokud je nepřečtená NEBO je připnutá (pinned)
        if user_id not in readers or news.get('pinned', False):
            unread_news_list.append(news)
    
    news_cards_html = ""
    total_news_count = len(NEWS)  # Celkový počet pro archiv
    
    def count_all_comments(comments):
        """Rekurzivně spočítá všechny komentáře včetně odpovědí."""
        count = len(comments)
        for comment in comments:
            if comment.get('replies'):
                count += count_all_comments(comment['replies'])
        return count
    
    for idx, news in enumerate(unread_news_list):
        featured_class = "border-danger" if news.get('featured', False) else "border-primary"
        comments_count = count_all_comments(news.get('comments', []))
        star = "⭐ " if news.get('featured', False) else ""
        pin = "📌 " if news.get('pinned', False) else ""
        read_count = len(news.get('read_by', []))
        is_read = user_id in [r['user_id'] for r in news.get('read_by', [])]
        read_badge = '<span class="badge bg-secondary">Přečteno</span>' if is_read else '<span class="badge bg-success">Nepřečteno</span>'
        
        admin_buttons = ''
        if is_admin:
            # Escapování pro JavaScript
            title_escaped = news['title'].replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            content_escaped = news['content'].replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            content_full_escaped = news.get('content_full', news['content']).replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            image_escaped = news.get('image', '').replace("'", "\\'").replace('"', '\\"')
            
            admin_buttons = f'''
            <div class="btn-group btn-group-sm mt-2" onclick="event.stopPropagation();">
                <button class="btn btn-outline-primary btn-sm" onclick="editNews({news['id']}, '{title_escaped}', '{content_escaped}', '{content_full_escaped}', '{image_escaped}', {str(news.get('featured', False)).lower()}, {str(news.get('pinned', False)).lower()}); event.stopPropagation();">
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
                <h6 class="card-title mb-1" style="font-size: 0.9rem;">{pin}{star}{news["title"]} {read_badge if news.get('pinned', False) else ''}</h6>
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
    
    # Přidání tlačítka pro archiv přečtených novinek
    read_news_count = total_news_count - len(unread_news_list)
    if read_news_count > 0:
        news_cards_html += f'''
        <div class="text-center mt-2">
            <a href="/news/archive" class="btn btn-outline-primary btn-sm w-100">
                <i class="bi bi-archive"></i> Archiv přečtených novinek ({read_news_count})
            </a>
        </div>
        '''
    
    if not news_cards_html:
        news_cards_html = '<p class="text-muted small">Žádné nepřečtené novinky</p>'
    
    # Originální news_html pro kompatibilitu
    news_html = news_cards_html
    
    # Zprávy - zobrazit pouze ty relevantní pro uživatele
    # Nejdříve filtrujeme zprávy
    filtered_messages = []
    for message in MESSAGES:
        # Zkontrolovat jestli je zpráva určená pro tohoto uživatele
        recipient_type = message.get('recipient_type', 'all')
        recipient_user_id = message.get('recipient_user_id')
        
        is_for_user = False
        # Admin vidí všechny zprávy
        if is_admin:
            is_for_user = True
        elif recipient_type == 'all':
            is_for_user = True
        elif recipient_type == 'single' and recipient_user_id == user_id:
            is_for_user = True
        elif recipient_type == user['role']:
            is_for_user = True
        
        if is_for_user:
            filtered_messages.append(message)
    
    # Seřadit zprávy podle data vytvoření (nejnovější první)
    filtered_messages.sort(key=lambda x: x.get('created', ''), reverse=True)
    
    # Zobrazit pouze nepřečtené zprávy na dashboardu
    unread_messages_list = []
    for message in filtered_messages:
        is_read = user_id in [r.get('user_id') for r in message.get('read_by', [])]
        if not is_read:
            unread_messages_list.append(message)
    
    total_messages_count = len(filtered_messages)
    messages_html = ""
    
    for message in unread_messages_list:
        
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
        
        # Admin tlačítka pro editaci a mazání
        admin_buttons = ''
        if is_admin:
            subject_escaped = message.get('subject', '').replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            content_escaped = message.get('content', '').replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
            admin_buttons = f'''
            <div class="btn-group btn-group-sm mt-2">
                <button class="btn btn-outline-primary btn-sm" onclick="editMessage({message['id']}, '{subject_escaped}', '{content_escaped}'); event.stopPropagation();">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteMessage({message['id']}, '{subject_escaped}'); event.stopPropagation();">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            '''
        
        messages_html += f'''
        <div class="card mb-2 message-item {unread_class}" style="cursor: pointer;" onclick="window.location.href='/message/{message['id']}'">
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
                        {admin_buttons}
                    </div>
                    <div onclick="event.stopPropagation();">
                        {f'<button class="btn btn-sm btn-outline-success" onclick="markMessageRead({message['id']})"><i class="bi bi-check"></i></button>' if not is_read else '<small class="text-success"><i class="bi bi-check2-circle"></i> Přečteno</small>'}
                    </div>
                </div>
            </div>
        </div>
        '''
    
    if not messages_html:
        messages_html = '<p class="text-muted small">Žádné nepřečtené zprávy</p>'
    
    # Přidání tlačítka pro archiv přečtených zpráv
    read_messages_count = total_messages_count - len(unread_messages_list)
    if read_messages_count > 0:
        messages_html += f'''
        <div class="text-center mt-2">
            <a href="/messages/archive" class="btn btn-outline-primary btn-sm w-100">
                <i class="bi bi-archive"></i> Archiv přečtených zpráv ({read_messages_count})
            </a>
        </div>
        '''
    
    # Aplikace pro levy panel - filtrujeme podle role
    apps_html = ""
    filtered_apps = APPLICATIONS
    if user['role'] == 'ridic':
        filtered_apps = [app for app in APPLICATIONS if app.get('visible_for_ridic', False)]
    elif user['role'] == 'administrativa':
        filtered_apps = [app for app in APPLICATIONS if app.get('visible_for_admin', True)]
    
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
        <div class="col-xl-2 col-lg-3 col-md-4 col-6">
            <div class="card app-tile text-center py-3 px-2" onclick="{onclick}" {context_menu} style="{cursor_style} min-height: 160px;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{app["icon"]}</div>
                <h6 style="font-size: 0.85rem; margin-bottom: 0.5rem;">{app["name"]}</h6>
                <span class="badge {status_class}" style="font-size: 0.7rem;">{status_text}</span>
                <p class="small text-muted mt-2 mb-0" style="font-size: 0.7rem; line-height: 1.3;">{app.get('description', '')[:40]}{'...' if len(app.get('description', '')) > 40 else ''}</p>
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
            
            # Generování avataru podle role
            avatar_colors = {
                'admin': '#dc2626',
                'ridic': '#2563eb', 
                'administrativa': '#f97316'
            }
            avatar_letters = {
                'admin': 'A',
                'ridic': 'Ř',
                'administrativa': 'A'
            }
            avatar_color = avatar_colors.get(usr['role'], '#6b7280')
            avatar_letter = avatar_letters.get(usr['role'], '?')
            
            avatar_svg = f'''<svg width="30" height="30" style="border-radius: 50%; vertical-align: middle; margin-right: 8px;">
                <circle cx="15" cy="15" r="15" fill="{avatar_color}"/>
                <text x="15" y="21" font-size="15" font-weight="bold" text-anchor="middle" fill="white">{avatar_letter}</text>
            </svg>'''
            
            users_html += f'''
            <tr>
                <td>{avatar_svg}{usr["full_name"]}</td>
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
    <!-- Firemní aplikace - celá šířka nahoře -->
    <div class="container-fluid mb-4">
        <div class="content-section">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0"><i class="bi bi-grid-3x3-gap"></i> Firemní aplikace</h5>
                {f'<button class="btn btn-primary btn-sm" onclick="showAddAppModal()"><i class="bi bi-plus"></i> Přidat aplikaci</button>' if is_admin else ''}
            </div>
            <div class="row g-3">
                {apps_html}
            </div>
        </div>
    </div>
    
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
                    {f'''<div class="mt-3">
                        <h6 class="text-muted text-uppercase mb-3" style="font-size: 0.7rem; letter-spacing: 0.05em; font-weight: 600;">Administrace</h6>
                        <div class="d-grid gap-2">
                            <a href="/users" class="btn btn-light text-start d-flex align-items-center py-2 px-3" style="border: 1px solid var(--border-color); border-radius: 8px; transition: all 0.2s;">
                                <i class="bi bi-people" style="font-size: 1.1rem; color: var(--primary-blue); width: 24px;"></i>
                                <span class="ms-2" style="font-size: 0.9rem; font-weight: 500;">Správa uživatelů</span>
                            </a>
                            <a href="/admin/applications" class="btn btn-light text-start d-flex align-items-center py-2 px-3" style="border: 1px solid var(--border-color); border-radius: 8px; transition: all 0.2s;">
                                <i class="bi bi-grid-3x3-gap" style="font-size: 1.1rem; color: var(--primary-blue); width: 24px;"></i>
                                <span class="ms-2" style="font-size: 0.9rem; font-weight: 500;">Správa aplikací</span>
                            </a>
                            <a href="/admin/deleted-comments" class="btn btn-light text-start d-flex align-items-center py-2 px-3" style="border: 1px solid var(--border-color); border-radius: 8px; transition: all 0.2s;">
                                <i class="bi bi-trash" style="font-size: 1.1rem; color: #ef4444; width: 24px;"></i>
                                <span class="ms-2" style="font-size: 0.9rem; font-weight: 500;">Smazané komentáře</span>
                            </a>
                        </div>
                    </div>''' if is_admin else ''}
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
    
    function editMessage(id, subject, content) {{
        document.getElementById('editMessageForm').action = '/admin/edit_message/' + id;
        document.getElementById('editMessageId').value = id;
        document.getElementById('editMessageSubject').value = subject;
        document.getElementById('editMessageContent').value = content;
        new bootstrap.Modal(document.getElementById('editMessageModal')).show();
    }}
    
    function deleteMessage(id, subject) {{
        if (confirm('Opravdu chcete smazat zprávu "' + subject + '"?')) {{
            fetch('/admin/delete_message/' + id, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }}
            }}).then(() => {{
                location.reload();
            }});
        }}
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
    pinned = 'pinned' in request.form
    
    new_news = {
        'id': max([n['id'] for n in NEWS], default=0) + 1,
        'title': title,
        'content': content,
        'content_full': content_full,
        'image': image,
        'author': session.get('full_name', 'Neznámý'),
        'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'featured': featured,
        'pinned': pinned,
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
                <div class="card-header text-center" style="background: var(--primary-blue-light); color: white; border-radius: 12px 12px 0 0;">
                    <h3 style="color: white; margin: 0;"><i class="bi bi-shield-lock"></i> Přihlášení do systému</h3>
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

@app.route('/api/current-user')
def api_current_user():
    """API endpoint pro získání informací o přihlášeném uživateli."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session.get('user_id')
    if user_id in USERS:
        user = USERS[user_id]
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role'],
            'avatar': user['avatar'],
            'active': user['active']
        })
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/admin/applications')
def admin_applications():
    """Administrace aplikací v app_ad složce."""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Načíst aktuální seznam aplikací
    applications = load_applications()
    
    # Automaticky skenovat app_ad složku
    app_ad_path = os.path.join(os.path.dirname(__file__), 'app_ad')
    available_apps = []
    
    if os.path.exists(app_ad_path):
        for folder_name in os.listdir(app_ad_path):
            folder_path = os.path.join(app_ad_path, folder_name)
            if os.path.isdir(folder_path):
                # Zkontrolovat jestli už existuje v databázi
                exists_in_db = any(app.get('folder') == folder_name for app in applications)
                
                app_info = {
                    'folder': folder_name,
                    'exists': exists_in_db,
                    'path': f'/app_ad/{folder_name}/'
                }
                
                # Pokusit se načíst README
                readme_path = os.path.join(folder_path, 'README.md')
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Vytáhnout první nadpis jako název
                            lines = content.split('\n')
                            for line in lines:
                                if line.startswith('# '):
                                    app_info['title'] = line.replace('# ', '').split('-')[0].strip()
                                    break
                    except:
                        app_info['title'] = folder_name.title()
                else:
                    app_info['title'] = folder_name.title()
                
                available_apps.append(app_info)
    
    # Generování HTML pro aplikace - moderní kartičkový design
    apps_cards = ''
    for app in applications:
        status_badge = 'bg-success' if app.get('status') == 'available' else 'bg-warning'
        status_text = 'Dostupná' if app.get('status') == 'available' else 'Plánovaná'
        status_icon = '✓' if app.get('status') == 'available' else '⏱'
        
        folder_badge = ''
        if app.get('folder'):
            folder_badge = f'<span class="badge bg-info text-white" style="font-size: 0.7rem;"><i class="bi bi-folder2-open"></i> {app["folder"]}</span>'
        
        name_escaped = app['name'].replace("'", "\\'").replace('"', '\\"')
        desc_escaped = app.get('description', '').replace("'", "\\'").replace('"', '\\"')
        url_escaped = app.get('url', '').replace("'", "\\'").replace('"', '\\"')
        
        # Zkrácení URL pro zobrazení
        display_url = app.get('url', '-')
        if len(display_url) > 50:
            display_url = display_url[:47] + '...'
        
        apps_cards += f'''
        <div class="col-xl-4 col-lg-6 col-md-6 mb-3">
            <div class="card h-100 shadow-sm border-0" style="transition: all 0.3s; border-left: 4px solid var(--primary-blue) !important;">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div class="d-flex align-items-center">
                            <div style="font-size: 2.5rem; margin-right: 15px;">{app['icon']}</div>
                            <div>
                                <h5 class="mb-1" style="font-weight: 600; color: var(--text-dark);">{app['name']}</h5>
                                <span class="badge {status_badge}" style="font-size: 0.75rem;">{status_icon} {status_text}</span>
                            </div>
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-light" type="button" data-bs-toggle="dropdown">
                                <i class="bi bi-three-dots-vertical"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li>
                                    <a class="dropdown-item" href="#" onclick="editApp({app['id']}, '{name_escaped}', '{app['icon']}', '{desc_escaped}', '{url_escaped}', '{app.get('status', 'planned')}', {str(app.get('visible_for_ridic', False)).lower()}, {str(app.get('visible_for_admin', True)).lower()}, {str(app.get('require_password', False)).lower()}); return false;">
                                        <i class="bi bi-pencil text-primary"></i> Upravit
                                    </a>
                                </li>
                                <li><hr class="dropdown-divider"></li>
                                <li>
                                    <a class="dropdown-item text-danger" href="#" onclick="deleteApp({app['id']}, '{name_escaped}'); return false;">
                                        <i class="bi bi-trash"></i> Smazat
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                    
                    <p class="text-muted small mb-3" style="min-height: 40px;">{app.get('description', 'Bez popisu')}</p>
                    
                    <div class="d-flex flex-wrap gap-2 mb-3">
                        {folder_badge}
                        <span class="badge {'bg-success' if app.get('visible_for_ridic') else 'bg-secondary'}" style="font-size: 0.7rem;">
                            <i class="bi bi-{'check-circle' if app.get('visible_for_ridic') else 'x-circle'}"></i> 
                            {'Pro řidiče' if app.get('visible_for_ridic') else 'Ne pro řidiče'}
                        </span>
                        <span class="badge {'bg-info' if app.get('visible_for_admin') else 'bg-secondary'}" style="font-size: 0.7rem;">
                            <i class="bi bi-{'check-circle' if app.get('visible_for_admin') else 'x-circle'}"></i> 
                            {'Pro administrativu' if app.get('visible_for_admin') else 'Ne pro administrativu'}
                        </span>
                        {'<span class="badge bg-warning text-dark" style="font-size: 0.7rem;"><i class="bi bi-lock"></i> Vyžaduje heslo</span>' if app.get('require_password') else ''}
                    </div>
                    
                    <div class="border-top pt-2">
                        <small class="text-muted">
                            <i class="bi bi-link-45deg"></i> 
                            <code style="font-size: 0.7rem;">{display_url}</code>
                        </small>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    # Generování seznamu dostupných aplikací v app_ad - modernější design
    available_apps_html = ''
    for app_info in available_apps:
        if not app_info['exists']:
            available_apps_html += f'''
            <div class="card mb-2 border-0 shadow-sm" style="transition: all 0.3s; cursor: pointer;" onmouseover="this.style.transform='translateX(5px)'" onmouseout="this.style.transform='translateX(0)'">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div style="flex: 1;">
                            <h6 class="mb-1" style="font-weight: 600; color: var(--primary-blue);">
                                <i class="bi bi-folder2-open"></i> {app_info['title']}
                            </h6>
                            <small class="text-muted d-block mb-1">📁 {app_info['folder']}</small>
                            <small class="text-info"><code style="font-size: 0.65rem;">{app_info['path']}</code></small>
                        </div>
                        <button class="btn btn-sm btn-success" onclick="addAppFromFolder('{app_info['folder']}', '{app_info['title']}', '{app_info['path']}'); event.stopPropagation();" style="white-space: nowrap;">
                            <i class="bi bi-plus-circle"></i> Přidat
                        </button>
                    </div>
                </div>
            </div>
            '''
    
    if not available_apps_html:
        available_apps_html = '<div class="alert alert-info"><i class="bi bi-info-circle"></i> Žádné nové aplikace v app_ad složce</div>'
    
    content = f'''
    <style>
        .app-admin-card {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .app-admin-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(37, 99, 235, 0.15) !important;
        }}
        .sidebar-scan {{
            position: sticky;
            top: 20px;
        }}
    </style>
    
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-lg-3 col-md-4 mb-4">
                <div class="card border-0 shadow-sm sidebar-scan">
                    <div class="card-header bg-gradient" style="background: linear-gradient(135deg, var(--primary-blue), #1e40af); color: white; border: none;">
                        <h6 class="mb-0"><i class="bi bi-folder2-open"></i> Skenování app_ad</h6>
                    </div>
                    <div class="card-body">
                        <p class="small text-muted mb-3">Automaticky nalezené aplikace ve složce app_ad/</p>
                        {available_apps_html}
                    </div>
                </div>
            </div>
            
            <div class="col-lg-9 col-md-8">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h3 style="font-weight: 700; color: var(--text-dark);">
                            <i class="bi bi-grid-3x3-gap" style="color: var(--primary-blue);"></i> Správa aplikací
                        </h3>
                        <p class="text-muted mb-0">Administrace firemních aplikací a modulů</p>
                    </div>
                    <div>
                        <a href="/" class="btn btn-outline-secondary me-2">
                            <i class="bi bi-arrow-left"></i> Dashboard
                        </a>
                        <button class="btn btn-primary shadow-sm" onclick="showAddAppModal()" style="background: var(--primary-blue); border: none;">
                            <i class="bi bi-plus-circle"></i> Přidat aplikaci
                        </button>
                    </div>
                </div>
                
                <div class="row">
                    {apps_cards}
                </div>
                
                {f'<div class="alert alert-warning"><i class="bi bi-exclamation-triangle"></i> Zatím nejsou přidány žádné aplikace.</div>' if not applications else ''}
            </div>
        </div>
    </div>
    
    <script>
    function editApp(id, name, icon, description, url, status, visibleForRidic, visibleForAdmin, requirePassword) {{
        document.getElementById('editAppId').value = id;
        document.getElementById('editAppName').value = name;
        document.getElementById('editAppIcon').value = icon;
        document.getElementById('editAppDescription').value = description;
        document.getElementById('editAppUrl').value = url;
        document.getElementById('editAppStatus').value = status;
        document.getElementById('editAppVisibleForRidic').checked = visibleForRidic;
        document.getElementById('editAppVisibleForAdmin').checked = visibleForAdmin;
        document.getElementById('editAppRequirePassword').checked = requirePassword;
        
        document.getElementById('editAppForm').action = '/admin/edit_application/' + id;
        new bootstrap.Modal(document.getElementById('editAppModal')).show();
    }}
    
    function deleteApp(id, name) {{
        if (confirm('Opravdu chcete smazat aplikaci "' + name + '"?')) {{
            fetch('/admin/delete_application/' + id, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}}
            }}).then(() => location.reload());
        }}
    }}
    
    function addAppFromFolder(folder, title, path) {{
        document.getElementById('addAppName').value = title;
        document.getElementById('addAppUrl').value = path;
        document.getElementById('addAppFolder').value = folder;
        document.getElementById('addAppStatus').value = 'available';
        new bootstrap.Modal(document.getElementById('addAppModal')).show();
    }}
    
    function showAddAppModal() {{
        document.getElementById('addAppForm').reset();
        new bootstrap.Modal(document.getElementById('addAppModal')).show();
    }}
    </script>
    '''
    
    return render_template_string(BASE_TEMPLATE, title='Správa aplikací', content=content)

@app.route('/admin/add_application', methods=['POST'])
def admin_add_application():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    applications = load_applications()
    
    # Najít maximální ID
    max_id = max([app['id'] for app in applications], default=0)
    
    new_app = {
        'id': max_id + 1,
        'name': request.form.get('name'),
        'icon': request.form.get('icon'),
        'description': request.form.get('description', ''),
        'url': request.form.get('url', ''),
        'status': request.form.get('status', 'planned'),
        'require_password': 'require_password' in request.form,
        'visible_for_ridic': 'visible_for_ridic' in request.form,
        'visible_for_admin': 'visible_for_admin' in request.form,
        'folder': request.form.get('folder', ''),
        'type': 'php' if request.form.get('folder') else 'external'
    }
    
    applications.append(new_app)
    save_applications(applications)
    
    flash('Aplikace byla úspěšně přidána.', 'success')
    return redirect(url_for('admin_applications'))

@app.route('/admin/edit_application/<int:app_id>', methods=['POST'])
def admin_edit_application(app_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    applications = load_applications()
    
    for app in applications:
        if app['id'] == app_id:
            app['name'] = request.form.get('name')
            app['icon'] = request.form.get('icon')
            app['description'] = request.form.get('description', '')
            app['url'] = request.form.get('url', '')
            app['status'] = request.form.get('status', 'planned')
            app['require_password'] = 'require_password' in request.form
            app['visible_for_ridic'] = 'visible_for_ridic' in request.form
            app['visible_for_admin'] = 'visible_for_admin' in request.form
            break
    
    save_applications(applications)
    
    flash('Aplikace byla úspěšně upravena.', 'success')
    return redirect(url_for('admin_applications'))

@app.route('/admin/delete_application/<int:app_id>', methods=['POST'])
def admin_delete_application(app_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    app_id = int(app_id)  # Převod z URL parametru na int
    applications = load_applications()
    applications = [app for app in applications if app['id'] != app_id]
    save_applications(applications)
    
    return jsonify({'success': True})

@app.route('/users')
def users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Parametr pro zobrazení smazaných
    show_deleted = request.args.get('show_deleted') == 'true'
    
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
            username_escaped = user['username'].replace("\\", "\\\\").replace("'", "\\'").replace('"', "&quot;")
            action_buttons = f'''
                <button class="btn btn-success btn-sm" onclick="restoreUser({user['id']}, '{username_escaped}')">
                    <i class="bi bi-arrow-counterclockwise"></i> Obnovit
                </button>
            '''
        else:
            # Tlačítka pro aktivní uživatele
            # Escapování pro JavaScript - nahradit apostrofy a uvozovky
            full_name_escaped = user['full_name'].replace("\\", "\\\\").replace("'", "\\'").replace('"', "&quot;")
            username_escaped = user['username'].replace("\\", "\\\\").replace("'", "\\'").replace('"', "&quot;")
            email_escaped = user['email'].replace("\\", "\\\\").replace("'", "\\'").replace('"', "&quot;")
            avatar_escaped = user.get('avatar', '').replace("\\", "\\\\").replace("'", "\\'").replace('"', "&quot;")
            
            message_button = f'<button class="btn btn-outline-info btn-sm" onclick="sendMessageToUser({user['id']}, \'{full_name_escaped}\')"><i class="bi bi-envelope"></i></button>'
            delete_button = f'<button class="btn btn-outline-danger btn-sm" onclick="deleteUser({user['id']}, \'{username_escaped}\')"><i class="bi bi-trash"></i></button>' if user['id'] != session.get('user_id') else '<span class="text-muted small">Vlastní</span>'
            
            action_buttons = f'''
                <div class="btn-group btn-group-sm">
                    {message_button}
                    <button class="btn btn-outline-primary btn-sm" onclick="editUser({user['id']}, '{username_escaped}', '{email_escaped}', '{full_name_escaped}', '{user['role']}', '{avatar_escaped}', {str(user.get('active', True)).lower()})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    {delete_button}
                </div>
            '''
        
        # Generování avataru podle role
        avatar_colors = {
            'admin': '#dc2626',
            'ridic': '#2563eb', 
            'administrativa': '#f97316'
        }
        avatar_letters = {
            'admin': 'A',
            'ridic': 'Ř',
            'administrativa': 'A'
        }
        avatar_color = avatar_colors.get(user['role'], '#6b7280')
        avatar_letter = avatar_letters.get(user['role'], '?')
        
        avatar_svg = f'''<svg width="40" height="40" style="border-radius: 50%;">
            <circle cx="20" cy="20" r="20" fill="{avatar_color}"/>
            <text x="20" y="28" font-size="20" font-weight="bold" text-anchor="middle" fill="white">{avatar_letter}</text>
        </svg>'''
        
        user_row = f'''
        <tr class="{'table-secondary' if is_deleted else ''}">
            <td>{avatar_svg}</td>
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
    function editUser(id, username, email, fullName, role, avatar, active) {{
        document.getElementById('editUserForm').action = '/admin/edit_user/' + id;
        document.getElementById('editUsername').value = username;
        document.getElementById('editUserEmail').value = email;
        document.getElementById('editFullName').value = fullName;
        document.getElementById('editUserRole').value = role;
        document.getElementById('editUserActive').checked = active;
        
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
        'avatar': get_avatar_by_role(role),
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
        'active': active,
        'avatar': get_avatar_by_role(role)
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

@app.route('/message/<int:message_id>')
def message_detail(message_id):
    """Detail zprávy."""
    if 'user_id' not in session:
        flash('Nejste přihlášeni!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'
    
    # Najít zprávu
    message = None
    for msg in MESSAGES:
        if msg['id'] == message_id:
            message = msg
            break
    
    if not message:
        flash('Zpráva nebyla nalezena.', 'error')
        return redirect(url_for('index'))
    
    # Automaticky označit jako přečtenou
    if user_id not in [r.get('user_id') for r in message.get('read_by', [])]:
        message['read_by'].append({
            'user_id': user_id,
            'read_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_messages()
    
    # Určit příjemce
    recipient_type = message.get('recipient_type', 'all')
    recipient_text = ''
    if recipient_type == 'all':
        recipient_text = 'Pro všechny'
    elif recipient_type == 'single':
        recipient_user_id = message.get('recipient_user_id')
        recipient_user = USERS.get(recipient_user_id)
        recipient_text = f'Pouze pro: {recipient_user["full_name"]}' if recipient_user else 'Pouze pro konkrétního uživatele'
    elif recipient_type == 'ridic':
        recipient_text = 'Pro řidiče'
    elif recipient_type == 'administrativa':
        recipient_text = 'Pro administrativu'
    
    # Admin tlačítka
    admin_buttons = ''
    if is_admin:
        subject_escaped = message.get('subject', '').replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
        content_escaped = message.get('content', '').replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
        admin_buttons = f'''
        <div class="btn-group mt-3">
            <button class="btn btn-outline-primary" onclick="editMessage({message['id']}, '{subject_escaped}', '{content_escaped}')">
                <i class="bi bi-pencil"></i> Upravit
            </button>
            <button class="btn btn-outline-danger" onclick="deleteMessage({message['id']}, '{subject_escaped}')">
                <i class="bi bi-trash"></i> Smazat
            </button>
        </div>
        '''
    
    content = f'''
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="mb-3">
                <a href="/" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> Zpět na dashboard</a>
            </div>
            
            <div class="card">
                <div class="card-header" style="background: linear-gradient(135deg, #2c5aa0 0%, #1e3a72 100%); color: white;">
                    <h4 class="mb-0"><i class="bi bi-envelope-open"></i> {message.get('subject', 'Bez předmětu')}</h4>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <small class="text-muted">
                            <i class="bi bi-person"></i> Od: <strong>{message.get('from_name', 'Systém')}</strong> | 
                            <i class="bi bi-clock"></i> {message.get('created', '')} |
                            <i class="bi bi-envelope"></i> {recipient_text}
                        </small>
                    </div>
                    <hr>
                    <div style="white-space: pre-wrap;">{message.get('content', '')}</div>
                    {admin_buttons}
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function editMessage(id, subject, content) {{
        document.getElementById('editMessageId').value = id;
        document.getElementById('editMessageSubject').value = subject;
        document.getElementById('editMessageContent').value = content;
        new bootstrap.Modal(document.getElementById('editMessageModal')).show();
    }}
    
    function deleteMessage(id, subject) {{
        if (confirm('Opravdu chcete smazat zprávu "' + subject + '"?')) {{
            fetch('/admin/delete_message/' + id, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }}
            }}).then(() => {{
                window.location.href = '/';
            }});
        }}
    }}
    </script>
    '''
    
    return render_template_string(BASE_TEMPLATE, title='Detail zprávy', content=content)

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

@app.route('/admin/edit_message/<int:message_id>', methods=['POST'])
def edit_message(message_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    subject = request.form.get('subject', '').strip()
    content = request.form.get('content', '').strip()
    
    if not subject or not content:
        flash('Předmět a obsah zprávy jsou povinné.', 'error')
        return redirect(url_for('message_detail', message_id=message_id))
    
    # Najít zprávu
    for msg in MESSAGES:
        if msg['id'] == message_id:
            msg['subject'] = subject
            msg['content'] = content
            save_messages()
            flash('Zpráva byla úspěšně upravena.', 'success')
            break
    
    return redirect(url_for('message_detail', message_id=message_id))

@app.route('/admin/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    # Najít a smazat zprávu
    global MESSAGES
    MESSAGES = [msg for msg in MESSAGES if msg['id'] != message_id]
    save_messages()
    flash('Zpráva byla úspěšně smazána.', 'success')
    
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
    pinned = 'pinned' in request.form
    
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
            'featured': featured,
            'pinned': pinned
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

@app.route('/messages/archive')
def messages_archive():
    """Archiv všech zpráv s filtrováním podle roku a měsíce."""
    if 'user_id' not in session:
        flash('Nejste přihlášeni!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = USERS.get(user_id)
    is_admin = session.get('role') == 'admin'
    
    # Získání filtru z URL parametrů
    year_filter = request.args.get('year', '')
    month_filter = request.args.get('month', '')
    
    # Nejdříve filtrujeme zprávy podle příjemce
    filtered_messages = []
    for message in MESSAGES:
        recipient_type = message.get('recipient_type', 'all')
        recipient_user_id = message.get('recipient_user_id')
        
        is_for_user = False
        if is_admin:
            is_for_user = True
        elif recipient_type == 'all':
            is_for_user = True
        elif recipient_type == 'single' and recipient_user_id == user_id:
            is_for_user = True
        elif recipient_type == user['role']:
            is_for_user = True
        
        if is_for_user:
            filtered_messages.append(message)
    
    # Seřadit zprávy podle data vytvoření (nejnovější první)
    filtered_messages.sort(key=lambda x: x.get('created', ''), reverse=True)
    
    # Získání seznamu dostupných roků a měsíců
    available_dates = {}
    for message in filtered_messages:
        created_date = message['created'][:10]  # YYYY-MM-DD
        year = created_date[:4]
        month = created_date[5:7]
        
        if year not in available_dates:
            available_dates[year] = set()
        available_dates[year].add(month)
    
    # Seřazení roků sestupně
    sorted_years = sorted(available_dates.keys(), reverse=True)
    
    # Filtrování zpráv podle data
    if year_filter:
        filtered_messages = [m for m in filtered_messages if m['created'][:4] == year_filter]
    if month_filter:
        filtered_messages = [m for m in filtered_messages if m['created'][5:7] == month_filter]
    
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
                    <a href="/messages/archive" class="btn btn-secondary w-100">Zrušit filtr</a>
                </div>
            </form>
        </div>
    </div>
    '''
    
    # Generování HTML pro zprávy
    messages_list_html = ''
    for message in filtered_messages:
        # Zkontrolovat jestli už je přečtená
        is_read = user_id in [r.get('user_id') for r in message.get('read_by', [])]
        unread_badge = '' if is_read else '<span class="badge bg-danger">Nová</span>'
        
        # Určit příjemce pro zobrazení
        recipient_type = message.get('recipient_type', 'all')
        recipient_text = ''
        if recipient_type == 'all':
            recipient_text = 'Pro všechny'
        elif recipient_type == 'single':
            recipient_text = 'Pouze pro vás'
        elif recipient_type == 'ridic':
            recipient_text = 'Pro řidiče'
        elif recipient_type == 'administrativa':
            recipient_text = 'Pro administrativu'
        
        messages_list_html += f'''
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-envelope"></i> {message.get('subject', 'Bez předmětu')} {unread_badge}
                    </h5>
                    {f'<button class="btn btn-sm btn-outline-success" onclick="markMessageRead({message['id']})"><i class="bi bi-check"></i> Označit jako přečtené</button>' if not is_read else '<small class="text-success"><i class="bi bi-check2-circle"></i> Přečteno</small>'}
                </div>
                <p class="card-text">{message.get('content', '')}</p>
                <div class="d-flex justify-content-between">
                    <small class="text-muted">
                        <i class="bi bi-person"></i> {message.get('from_name', 'Systém')} | 
                        <i class="bi bi-clock"></i> {message.get('created', '')}
                    </small>
                    <small class="text-muted">
                        <i class="bi bi-envelope"></i> {recipient_text}
                    </small>
                </div>
            </div>
        </div>
        '''
    
    if not messages_list_html:
        messages_list_html = '<div class="alert alert-info">Žádné zprávy nenalezeny pro vybrané filtry.</div>'
    
    content = f'''
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="mb-3">
                <a href="/" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> Zpět na dashboard</a>
            </div>
            
            <div class="card mb-4">
                <div class="card-header" style="background: linear-gradient(135deg, #2c5aa0 0%, #1e3a72 100%); color: white;">
                    <h4 class="mb-0"><i class="bi bi-archive"></i> Archiv zpráv</h4>
                    <small>Celkem {len(filtered_messages)} zpráv{f" (filtrováno)" if year_filter or month_filter else ""}</small>
                </div>
            </div>
            
            {filter_html}
            
            {messages_list_html}
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
    
    return render_template_string(BASE_TEMPLATE, title='Archiv zpráv', content=content)

# Funkce pro generování avatarů podle role
def get_avatar_by_role(role):
    """Vygeneruje SVG avatar podle role uživatele."""
    # Base64 encoded SVG avatary pro lepší kompatibilitu
    avatars = {
        'admin': 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iI2RjMjYyNiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSI1MCIgZm9udC13ZWlnaHQ9ImJvbGQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIj5BPC90ZXh0Pjwvc3ZnPg==',
        'ridic': 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iIzI1NjNlYiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSI1MCIgZm9udC13ZWlnaHQ9ImJvbGQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIj7FmjwvdGV4dD48L3N2Zz4=',
        'administrativa': 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iI2Y5NzMxNiIvPjx0ZXh0IHg9IjUwIiB5PSI3MCIgZm9udC1zaXplPSI1MCIgZm9udC13ZWlnaHQ9ImJvbGQiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIj5BPC90ZXh0Pjwvc3ZnPg=='
    }
    return avatars.get(role, avatars['ridic'])

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

# Helper funkce pro práci s aplikacemi
def load_applications():
    """Načte aplikace ze souboru."""
    if os.path.exists('data_applications.json'):
        with open('data_applications.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_applications(applications):
    """Uloží aplikace do souboru a aktualizuje globální proměnnou."""
    global APPLICATIONS
    with open('data_applications.json', 'w', encoding='utf-8') as f:
        json.dump(applications, f, ensure_ascii=False, indent=2)
    APPLICATIONS[:] = applications

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

# Route pro přístup k aplikacím v app_ad složce
@app.route('/app_ad/<path:filename>', methods=['GET', 'POST'])
def app_ad_files(filename):
    """Proxy pro PHP aplikace v app_ad složce - předává session data."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Pro PHP soubory vytvoříme proxy s předáním user dat
    if filename.endswith('.php'):
        import urllib.request
        import urllib.parse
        
        # URL na Apache server
        apache_url = f'http://localhost/euapp/app_ad/{filename}'
        
        # Připravit query string
        query_string = request.query_string.decode('utf-8')
        if query_string:
            apache_url += '?' + query_string
        
        # Získat user data
        user_id = session.get('user_id')
        user = USERS.get(user_id)
        
        if not user:
            return redirect(url_for('login'))
        
        # Připravit headers
        headers = {
            'X-User-ID': str(user['id']),
            'X-User-Email': user['email'],
            'X-User-Name': base64.b64encode(user['full_name'].encode('utf-8')).decode('ascii'),
            'X-User-Role': user['role'],
            'X-User-Username': user['username']
        }
        
        try:
            # POST data
            if request.method == 'POST':
                # Převést ImmutableMultiDict na dict pro urlencode
                form_data = {}
                for key in request.form:
                    # Pokud je více hodnot se stejným klíčem, vezmi všechny
                    values = request.form.getlist(key)
                    if len(values) == 1:
                        form_data[key] = values[0]
                    else:
                        form_data[key] = values
                
                post_data = urllib.parse.urlencode(form_data).encode('utf-8')
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                req = urllib.request.Request(apache_url, data=post_data, headers=headers, method='POST')
            else:
                req = urllib.request.Request(apache_url, headers=headers, method='GET')
            
            # Poslat request
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                content_type = response.headers.get('Content-Type', 'text/html')
                
                return content, 200, {'Content-Type': content_type}
                
        except Exception as e:
            flash(f'Chyba při načítání aplikace: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    # Pro ostatní soubory (CSS, JS, obrázky) jen pošli
    import os
    app_ad_path = os.path.join(os.path.dirname(__file__), 'app_ad')
    return send_from_directory(app_ad_path, filename)

@app.route('/aquany-info')
def aquany_info():
    """Informační stránka pro spuštění Aquany."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    content = '''
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4><i class="bi bi-box"></i> Aquany - Systém správy dopravních zakázek</h4>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <i class="bi bi-info-circle"></i> <strong>PHP Aplikace</strong><br>
                            Aquany je PHP aplikace, která vyžaduje Apache/WAMP server pro svůj běh.
                        </div>
                        
                        <h5>Možnosti spuštění:</h5>
                        
                        <div class="accordion" id="aquanyAccordion">
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#option1">
                                        <strong>1. Přes WAMP Server (doporučeno)</strong>
                                    </button>
                                </h2>
                                <div id="option1" class="accordion-collapse collapse show" data-bs-parent="#aquanyAccordion">
                                    <div class="accordion-body">
                                        <ol>
                                            <li>Spusťte WAMP Server (ikonka v systémové liště)</li>
                                            <li>Počkejte, až ikona zezelená</li>
                                            <li>Klikněte na tlačítko níže</li>
                                        </ol>
                                        <a href="http://localhost/euapp/app_ad/aquany/" target="_blank" class="btn btn-success">
                                            <i class="bi bi-box-arrow-up-right"></i> Otevřít Aquany přes WAMP
                                        </a>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#option2">
                                        <strong>2. Přes PHP Built-in Server</strong>
                                    </button>
                                </h2>
                                <div id="option2" class="accordion-collapse collapse" data-bs-parent="#aquanyAccordion">
                                    <div class="accordion-body">
                                        <p>Spusťte následující příkaz v terminálu:</p>
                                        <div class="bg-dark text-white p-3 rounded">
                                            <code>cd c:\\wamp64\\www\\euapp\\app_ad\\aquany</code><br>
                                            <code>php -S localhost:8080</code>
                                        </div>
                                        <p class="mt-2">Poté otevřete:</p>
                                        <a href="http://localhost:8080" target="_blank" class="btn btn-primary">
                                            <i class="bi bi-box-arrow-up-right"></i> Otevřít Aquany (port 8080)
                                        </a>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#option3">
                                        <strong>3. Automatické spuštění (experimentální)</strong>
                                    </button>
                                </h2>
                                <div id="option3" class="accordion-collapse collapse" data-bs-parent="#aquanyAccordion">
                                    <div class="accordion-body">
                                        <p>Klikněte na tlačítko pro automatické spuštění PHP serveru:</p>
                                        <form action="/start-aquany" method="POST">
                                            <button type="submit" class="btn btn-warning">
                                                <i class="bi bi-play-fill"></i> Spustit Aquany automaticky
                                            </button>
                                        </form>
                                        <small class="text-muted">Spustí PHP server na portu 8080 a otevře aplikaci</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4">
                            <a href="/" class="btn btn-secondary">
                                <i class="bi bi-arrow-left"></i> Zpět na dashboard
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE, title='Aquany - Spuštění', content=content)

@app.route('/start-aquany', methods=['POST'])
def start_aquany():
    """Automaticky spustí PHP server pro Aquany."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    import subprocess
    import os
    
    aquany_path = os.path.join(os.path.dirname(__file__), 'app_ad', 'aquany')
    
    try:
        # Pokusíme se najít PHP v WAMP
        php_paths = [
            r'c:\wamp64\bin\php\php8.3.0\php.exe',
            r'c:\wamp64\bin\php\php8.2.13\php.exe',
            r'c:\wamp64\bin\php\php8.1.0\php.exe',
            r'php'  # Pokud je PHP v PATH
        ]
        
        php_exe = None
        for path in php_paths:
            try:
                if os.path.exists(path) or path == 'php':
                    # Test, zda PHP funguje
                    test = subprocess.run([path, '--version'], capture_output=True, timeout=2)
                    if test.returncode == 0:
                        php_exe = path
                        break
            except:
                continue
        
        if not php_exe:
            flash('PHP nebyl nalezen v systému. Spusťte WAMP server nebo nainstalujte PHP.', 'error')
            return redirect(url_for('aquany_info'))
        
        # Spustíme PHP server na pozadí
        subprocess.Popen(
            [php_exe, '-S', 'localhost:8080'],
            cwd=aquany_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        flash('PHP server byl spuštěn na portu 8080. Otevírám Aquany...', 'success')
        
        # Přesměrujeme na Aquany
        return '''
        <html>
        <head>
            <meta http-equiv="refresh" content="2;url=http://localhost:8080" />
        </head>
        <body>
            <p>Spouštím Aquany... Budete přesměrováni za 2 sekundy.</p>
            <p>Pokud se stránka neotevře automaticky, <a href="http://localhost:8080">klikněte zde</a>.</p>
        </body>
        </html>
        '''
        
    except Exception as e:
        flash(f'Chyba při spouštění PHP serveru: {str(e)}', 'error')
        return redirect(url_for('aquany_info'))

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