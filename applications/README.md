# Aplikace pro European Transport CZ

Tato složka obsahuje modulární aplikace, které se integrují s hlavním systémem.

## Struktura

Každá aplikace by měla mít vlastní podsložku s následující strukturou:

```
nazev_aplikace/
├── __init__.py          # Blueprint registrace
├── routes.py           # URL routes
├── models.py           # Databázové modely (volitelné)
├── forms.py            # Formuláře (volitelné)
├── templates/          # HTML šablony
│   └── nazev_aplikace/
├── static/             # Statické soubory
│   ├── css/
│   ├── js/
│   └── images/
└── README.md           # Dokumentace aplikace
```

## Jak přidat novou aplikaci

1. Vytvořte složku pro aplikaci
2. Implementujte blueprint v `__init__.py`
3. Zaregistrujte blueprint v hlavní aplikaci (`app/__init__.py`)
4. Přidejte odkaz v administračním panelu

## Příklady aplikací

- **Kniha jízd** - Evidence vozidel a cest
- **Skladové hospodářství** - Správa zásob
- **Personalistika** - HR systém
- **Účetnictví** - Finanční moduly
- **CRM** - Správa zákazníků