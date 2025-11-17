# European Transport CZ s.r.o. - Firemní Aplikační Server

## Popis
Webový server pro správu firemních aplikací společnosti European Transport CZ s.r.o. 
Postavený na Flask frameworku s důrazem na bezpečnost a modularitu.

## Funkce
- 🔐 Bezpečné uživatelské přihlašování
- 👥 Správa uživatelů a práv
- 📱 Modulární aplikační struktura  
- 📰 Systém novinek a aktualit
- 💬 Komentáře a hodnocení
- 🗳️ Ankety
- 📊 Monitoring uživatelské aktivity
- 💌 Systém zpráv a notifikací
- 🌐 Real-time komunikace

## Technologie
- **Backend**: Python 3.9+ s Flask
- **Databáze**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Real-time**: Socket.IO
- **Autentifikace**: Flask-Login + bcrypt

## Instalace

### Požadavky
- Python 3.9+
- pip
- Git

### Kroky instalace
1. Klonování repozitáře
2. Vytvoření virtuálního prostředí
3. Instalace závislostí
4. Konfigurace prostředí
5. Inicializace databáze
6. Spuštění aplikace

## Spuštění
```bash
python run.py
```

Aplikace bude dostupná na: http://localhost:5000

## Struktura projektu
```
euapp/
├── app/                    # Hlavní aplikace
│   ├── __init__.py        # Flask aplikace a konfigurace
│   ├── models/            # Databázové modely
│   ├── auth/              # Autentifikační modul
│   ├── main/              # Hlavní blueprint
│   ├── admin/             # Administrační panel
│   ├── api/               # REST API
│   ├── static/            # Statické soubory
│   └── templates/         # HTML šablony
├── applications/          # Modulární aplikace
├── migrations/           # Databázové migrace
├── tests/                # Testy
├── config.py             # Konfigurace
├── requirements.txt      # Python závislosti
└── run.py               # Spouštěcí skript
```

## Výchozí přihlašovací údaje
- **Administrátor**: admin@europeantransport.cz / admin123
- **Testovací uživatel**: user@europeantransport.cz / user123

## Vývoj
Pro vývoj nových aplikací vytvořte novou složku v `applications/` a zaregistrujte ji v hlavní aplikaci.

## Bezpečnost
- Hesla jsou hashována pomocí bcrypt
- CSRF ochrana přes Flask-WTF
- Secure session cookies
- Rate limiting na přihlašování
- SQL injection prevence přes SQLAlchemy ORM

## Licence
Proprietární software pro European Transport CZ s.r.o.

---
**Vytvořeno**: Listopad 2025
**Verze**: 1.0.0