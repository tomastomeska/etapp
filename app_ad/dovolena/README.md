# Aplikace Dovolená

Kompletní systém pro správu dovolené a pracovního volna v rámci European Transport CZ s.r.o.

## Funkce

### Pro všechny uživatele:
- ✅ **Žádosti o dovolenou** - vytváření nových žádostí s výběrem data od-do
- ✅ **Kalendářní pohled** - vizualizace dovolených v měsíčním kalendáři
- ✅ **Seznamový pohled** - tabulkový přehled všech žádostí
- ✅ **Statistiky** - přehled celkového přídělu, čerpaného, zbývajícího a čekajícího
- ✅ **Půl dne dovolené** - možnost žádat 4 hodiny (dopoledne/odpoledne)
- ✅ **Typy volna** - dovolená, placené volno, neplacené volno
- ✅ **České svátky** - automatické vynechání svátků z výpočtu
- ✅ **Víkendy** - automatické vynechání soboty a neděle
- ✅ **Zrušení žádosti** - možnost zrušit čekající žádost

### Pro administrátory:
- ✅ **Schvalování žádostí** - schválení/zamítnutí čekajících žádostí
- ✅ **Detekce kolizí** - upozornění na současně schválené dovolené
- ✅ **Přehled všech žádostí** - vidí žádosti všech uživatelů
- ✅ **Správa přídělů** - nastavení individuálního ročního přídělu pro každého uživatele
- ✅ **Statistiky** - globální přehled čekajících, schválených a zamítnutých žádostí

## Technické specifikace

### Struktura souborů:
```
app_ad/dovolena/
├── index.php                   # Hlavní rozhraní (uživatelský pohled)
├── admin.php                   # Administrační rozhraní
├── calendar_view.php           # Komponenta měsíčního kalendáře
├── list_view.php               # Komponenta seznamového pohledu
├── submit_vacation.php         # Zpracování žádostí
├── cancel_vacation.php         # Zrušení žádosti
├── process_vacation.php        # Schválení/zamítnutí (admin)
├── update_allowance.php        # Úprava přídělů (admin)
├── generate_holidays.php       # Generátor českých svátků
├── data/
│   ├── vacations.json         # Databáze žádostí
│   ├── allowances.json        # Příděly uživatelů
│   └── czech_holidays.json    # České svátky 2024-2035
└── README.md                   # Tato dokumentace
```

### Výchozí nastavení:
- **Roční příděl**: 160 hodin (20 dní)
- **Pracovní den**: 8 hodin
- **Půl dne**: 4 hodiny
- **Časové rozpětí**: 2024-2035

### Výpočet pracovních hodin:
Systém automaticky vypočítává skutečné pracovní hodiny:
- Vynechává soboty a neděle
- Vynechává české státní svátky
- Podporuje půldenní režim (4h dopoledne nebo odpoledne)
- Při výběru více dní počítá každý den zvlášť

Příklad: Žádost od 1.12.2024 do 5.12.2024 (čtvrtek-středa)
- 1.12. neděle - VYNECHÁNO
- 2.12. pondělí - 8h ✓
- 3.12. úterý - 8h ✓
- 4.12. středa - 8h ✓
- 5.12. čtvrtek - 8h ✓
**Celkem: 32 hodin (4 dny)**

### Stavy žádostí:
- **pending** 🟡 - Čeká na schválení
- **approved** 🟢 - Schváleno
- **rejected** 🔴 - Zamítnuto

### Role a oprávnění:
| Funkce | Všichni | Admin | Administrativa |
|--------|---------|-------|----------------|
| Žádat o dovolenou | ✅ | ✅ | ✅ |
| Zobrazit vlastní žádosti | ✅ | ✅ | ✅ |
| Zrušit čekající žádost | ✅ | ✅ | ✅ |
| Schvalovat žádosti | ❌ | ✅ | ✅ |
| Vidět všechny žádosti | ❌ | ✅ | ✅ |
| Měnit příděly | ❌ | ✅ | ✅ |

## Datové struktury

### vacations.json
```json
{
  "id": "unique_id",
  "user_id": "user_id",
  "user_name": "Jméno Příjmení",
  "type": "vacation|paid_leave|unpaid_leave",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "hours": 32,
  "half_day": false,
  "half_day_period": "morning|afternoon",
  "note": "Poznámka",
  "status": "pending|approved|rejected",
  "approved_by": "admin_id",
  "approved_by_name": "Admin Jméno",
  "approved_at": "YYYY-MM-DD HH:MM:SS",
  "created_at": "YYYY-MM-DD HH:MM:SS"
}
```

### allowances.json
```json
{
  "user_id": {
    "hours_per_year": 160,
    "updated_by": "admin_id",
    "updated_by_name": "Admin Jméno",
    "updated_at": "YYYY-MM-DD HH:MM:SS"
  }
}
```

### czech_holidays.json
```json
{
  "2024-01-01": "Nový rok / Den obnovy samostatného českého státu",
  "2024-03-29": "Velký pátek",
  "2024-04-01": "Velikonoční pondělí",
  ...
}
```

## Instalace a první spuštění

1. **Automatické**: Aplikace vytvoří složku `data/` a potřebné soubory při prvním spuštění

2. **Manuální** (pokud je potřeba předgenerovat):
   ```bash
   cd c:\wamp64\www\euapp\app_ad\dovolena
   mkdir data
   php generate_holidays.php
   ```

3. **Oprávnění**: Zajistěte, že webový server má práva zápisu do složky `data/`

## Přístup k aplikaci

- **Uživatelské rozhraní**: `/app_ad/dovolena/index.php`
- **Administrace**: `/app_ad/dovolena/admin.php` (pouze admin/administrativa)

## Integrace s hlavní aplikací

Aplikace je zaregistrována v `data_applications.json`:
```json
{
  "id": 7,
  "name": "Dovolená",
  "icon": "🏖️",
  "status": "available",
  "description": "Správa dovolené a pracovního volna - žádosti, schvalování, kalendář",
  "url": "/app_ad/dovolena/index.php",
  "visible_for_ridic": true,
  "visible_for_admin": true,
  "type": "php"
}
```

## Často kladené otázky (FAQ)

**Q: Jak změnit výchozí příděl 160 hodin?**  
A: Admin může v administraci upravit individuální příděl každého uživatele.

**Q: Počítá systém svátky během dovolené?**  
A: Ano, svátky jsou automaticky vyloučeny z výpočtu hodin.

**Q: Můžu vzít půl dne?**  
A: Ano, zaškrtněte "Půldenní dovolená" a zvolte dopoledne nebo odpoledne.

**Q: Co se stane s kolizemi?**  
A: Systém upozorní, ale neumožňuje zamezení - rozhodnutí je na administrátorovi.

**Q: Jak daleko dopředu mohu plánovat?**  
A: Aplikace podporuje svátky a dovolené do roku 2035.

## Budoucí rozšíření (možné)

- 📧 Emailové notifikace při schválení/zamítnutí
- 📊 Export statistik do Excel/PDF
- 📱 API pro mobilní aplikaci
- 🔔 Push notifikace
- 📅 Synchronizace s Outlook/Google Calendar
- 🌍 Podpora více jazyků
- 📈 Grafy čerpání dovolené

## Technická podpora

Pro otázky a problémy kontaktujte správce aplikace.

---
**Verze**: 1.0  
**Datum vydání**: 23.11.2024  
**Autor**: European Transport CZ IT tým
