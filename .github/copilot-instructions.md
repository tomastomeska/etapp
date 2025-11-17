# European Transport CZ s.r.o. - Firemní Aplikační Server

## Obecné informace o projektu

Tento projekt je firemní aplikační server vyvinutý pro společnost European Transport CZ s.r.o. Slouží jako centrální portál pro správu firemních aplikací, uživatelů a komunikaci.

## Technická architektura

- **Backend**: Python 3.12+ s Flask frameworkem
- **Databáze**: SQLite (development) / PostgreSQL (production)  
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Real-time**: Socket.IO pro živou komunikaci
- **Autentifikace**: Flask-Login s bcrypt hashováním

## Struktura projektu

```
euapp/
├── app/                    # Hlavní Flask aplikace
│   ├── __init__.py        # Factory pattern a konfigurace
│   ├── models/            # SQLAlchemy databázové modely
│   ├── auth/              # Autentifikační blueprint
│   ├── main/              # Hlavní routes a views
│   ├── admin/             # Administrační panel
│   ├── api/               # REST API endpoints
│   ├── static/            # CSS, JS, obrázky
│   └── templates/         # Jinja2 HTML šablony
├── applications/          # Modulární firemní aplikace
├── migrations/           # Flask-Migrate databázové migrace
├── tests/                # Unit a integration testy
├── config.py             # Konfigurace prostředí
└── run.py               # Spouštěcí skript
```

## Klíčové funkce

### Bezpečnost
- Robustní autentifikační systém s Flask-Login
- Bcrypt hashování hesel
- CSRF ochrana přes Flask-WTF
- Rate limiting na přihlašovací endpointy
- Session management s bezpečnými cookies
- Monitoring uživatelských aktivit

### Správa uživatelů
- Hierarchický systém rolí a oprávnění
- Aktivace/deaktivace účtů
- Sledování online statusu
- Profily uživatelů s fotkami
- Historie aktivit

### Komunikační systém
- Zprávy mezi uživateli
- Hromadné oznámení od administrátorů
- Real-time notifikace přes Socket.IO
- Systém novinek s komentáři a hodnocením

### Modularita
- Blueprint architektura pro škálovatelnost
- Pluginový systém pro externí aplikace
- REST API pro integraci s jinými systémy
- Administrační rozhraní pro správu

## Vývojové pokyny

### Databázové modely
Všechny modely jsou v `app/models/__init__.py` s následující konvencí:
- Používej SQLAlchemy ORM
- Vztahy definuj pomocí `db.relationship()`
- Pro časové značky použij `datetime.utcnow`
- Validace přes SQLAlchemy constraints

### Blueprinty
Každý funkční celek má vlastní blueprint:
- `auth` - přihlašování, registrace, profily
- `main` - dashboard, novinky, zprávy
- `admin` - administrační panel
- `api` - REST endpoints

### Formuláře
Všechny formuláře používají Flask-WTF:
- CSRF ochrana je povinná
- Custom validátory pro business logiku
- Bootstrap styling pro konzistentní vzhled

### Šablony
- Jinja2 templating engine
- Base template s navigací a flash zprávami
- Responsive design s Bootstrap 5
- Custom CSS ve `static/css/main.css`

## Bezpečnostní požadavky

- Všechny hesla musí být hashovaná pomocí bcrypt
- Sensitive operace vyžadují reautentifikaci
- Logování všech bezpečnostních událostí
- Regular security audits
- Input sanitization a validation

## Provozní informace

### Development
```bash
# Aktivace virtuálního prostředí
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Spuštění aplikace
python run.py

# Aplikace bude dostupná na http://localhost:5000
```

### Výchozí účty
- **Admin**: admin@europeantransport.cz / admin123
- **User**: user@europeantransport.cz / user123

### Environment variables
- `SECRET_KEY` - Pro session a CSRF ochranu
- `DATABASE_URL` - Připojení k databázi
- `MAIL_*` - SMTP konfigurace pro emaily

## Rozšiřování

### Přidání nové aplikace
1. Vytvořte složku v `applications/`
2. Implementujte Flask blueprint
3. Zaregistrujte v `app/__init__.py`
4. Přidejte do administrace

### Nové databázové modely
1. Definujte model v `app/models/`
2. Vytvořte migraci: `flask db migrate -m "popis"`
3. Aplikujte: `flask db upgrade`

### API endpointy
- Přidejte do `app/api/routes.py`
- Používejte JSON response format
- Implementujte proper error handling
- Dokumentujte v docstrings

## Coding Standards

- Python PEP 8 styling
- Descriptive variable and function names
- Comprehensive docstrings
- Type hints where appropriate
- Error handling s proper logging
- Unit tests pro critical functions