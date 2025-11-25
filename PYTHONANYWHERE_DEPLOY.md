# European Transport CZ - Firemní Portál

Firemní aplikační server pro European Transport CZ s.r.o.

## Nasazení na PythonAnywhere

### 1. Nahrání souborů
```bash
# Nahrát celý projekt do /home/tomastomeska/euapp/
```

### 2. Instalace závislostí
```bash
cd /home/tomastomeska/euapp
pip3.10 install --user flask werkzeug
```

### 3. Konfigurace Web App
V PythonAnywhere dashboard:
- Web → Add a new web app
- Manual configuration (Python 3.10)
- Source code: `/home/tomastomeska/euapp`
- WSGI configuration file: `/var/www/tomastomeska_pythonanywhere_com_wsgi.py`

Obsah WSGI souboru zkopírovat z `wsgi.py`

### 4. Static files
- URL: `/static/`
- Directory: `/home/tomastomeska/euapp/static`

### 5. PHP aplikace (Dovolená)
Pro PHP aplikaci je třeba nastavit:
- URL: `/app_ad/dovolena/`
- Directory: `/home/tomastomeska/euapp/app_ad/dovolena`

## Přihlašovací údaje
- Email: tomeska@european.cz
- Heslo: 20tomeska17

## URL aplikace
https://tomastomeska.pythonanywhere.com
