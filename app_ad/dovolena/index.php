<?php
// Autentifikace uživatele
require_once __DIR__ . '/auth.php';

// Cesty k datovým souborům
$vacationsFile = __DIR__ . '/data/vacations.json';
$allowancesFile = __DIR__ . '/data/allowances.json';
$holidaysFile = __DIR__ . '/data/czech_holidays.json';
$eventsFile = __DIR__ . '/../../data/company_events.json';

// Načtení dat
function loadJsonFile($file, $default = []) {
    if (file_exists($file)) {
        return json_decode(file_get_contents($file), true) ?: $default;
    }
    return $default;
}

$vacations = loadJsonFile($vacationsFile, []);
$allowances = loadJsonFile($allowancesFile, []);
$holidays = loadJsonFile($holidaysFile, []);
$companyEvents = loadJsonFile($eventsFile, []);

// Filtr celozávodních událostí podle role uživatele
$visibleEvents = [];
foreach ($companyEvents as $event) {
    // Pokud je pro všechny, zobrazit
    if ($event['visible_for_all']) {
        $visibleEvents[] = $event;
        continue;
    }
    
    // Kontrola podle role
    if ($userRole === 'admin' && $event['visible_for_admin']) {
        $visibleEvents[] = $event;
    } elseif ($userRole === 'administrativa' && $event['visible_for_administrativa']) {
        $visibleEvents[] = $event;
    } elseif ($userRole === 'ridic' && $event['visible_for_ridic']) {
        $visibleEvents[] = $event;
    }
}

// Získání přídělu pro uživatele
$userAllowance = $allowances[$userId] ?? null;
$totalHours = $userAllowance ? $userAllowance['hours_per_year'] : 160;

// Výpočet statistik
$usedHours = 0;
$pendingHours = 0;

foreach ($vacations as $vac) {
    if ($vac['user_id'] != $userId) continue;
    
    if ($vac['status'] === 'approved') {
        $usedHours += $vac['hours'];
    } elseif ($vac['status'] === 'pending') {
        $pendingHours += $vac['hours'];
    }
}

$availableHours = $totalHours - $usedHours;

// Filtr žádostí podle role
$userVacations = [];
foreach ($vacations as $vac) {
    if ($isAdmin || $vac['user_id'] == $userId) {
        $userVacations[] = $vac;
    }
}

// Seřadit podle data
usort($userVacations, function($a, $b) {
    return strtotime($b['created_at']) - strtotime($a['created_at']);
});

// Kalendář - aktuální měsíc a rok
$currentMonth = isset($_GET['month']) ? intval($_GET['month']) : date('n');
$currentYear = isset($_GET['year']) ? intval($_GET['year']) : date('Y');

// Pomocná funkce pro kontrolu svátků
function isHoliday($date, $holidays) {
    return isset($holidays[$date]);
}
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Správa dovolené - European Transport CZ</title>
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
        }

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
        }
        
        body {
            background: var(--bg-light);
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
            color: var(--text-dark);
        }
        
        .main-card {
            background: var(--bg-white);
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            margin: 2rem auto;
            max-width: 1400px;
        }
        
        .header-section {
            background: linear-gradient(135deg, var(--primary-blue), var(--primary-blue-dark));
            color: white;
            padding: 2rem;
            border-radius: 12px 12px 0 0;
        }
        
        .stats-card {
            background: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            transition: all 0.2s;
        }
        
        .stats-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        .btn-primary {
            background: var(--primary-blue);
            border-color: var(--primary-blue);
        }
        
        .btn-primary:hover {
            background: var(--primary-blue-dark);
            border-color: var(--primary-blue-dark);
        }
        
        .view-toggle {
            background: var(--bg-light);
            border-radius: 8px;
            padding: 0.25rem;
        }
        
        .view-toggle .btn {
            border-radius: 6px;
        }
        
        .badge {
            padding: 0.35rem 0.65rem;
            font-weight: 500;
        }
        
        /* Kalendář */
        .calendar td {
            height: 120px;
            vertical-align: top;
            padding: 8px;
        }
        
        .calendar .calendar-day {
            position: relative;
            min-height: 100px;
        }
        
        .calendar .today {
            background-color: #dbeafe;
        }
        
        .calendar .weekend {
            background-color: #f8f9fa;
        }
        
        .calendar .holiday {
            background-color: #fef2f2;
        }
        
        /* Indikátory dovolené */
        .vacation-indicator {
            display: inline-block;
            padding: 4px 8px;
            margin: 2px 0;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            width: 100%;
            text-align: center;
        }
        
        /* Čeká na schválení - ORANŽOVÁ */
        .vacation-pending {
            background-color: #f59e0b;
            color: white;
            border-left: 4px solid #d97706;
        }
        
        /* Schválená - ZELENÁ */
        .vacation-approved {
            background-color: #10b981;
            color: white;
            border-left: 4px solid #059669;
        }
        
        /* Zamítnutá - ČERVENÁ */
        .vacation-rejected {
            background-color: #ef4444;
            color: white;
            border-left: 4px solid #dc2626;
        }
        
        /* Placené volno - MODRÁ */
        .vacation-paid-leave {
            background-color: #3b82f6;
            color: white;
            border-left: 4px solid #2563eb;
        }
        
        /* Neplacené volno - ŠEDÁ */
        .vacation-unpaid-leave {
            background-color: #6b7280;
            color: white;
            border-left: 4px solid #4b5563;
        }
        
        .weekend-note {
            font-size: 0.65rem;
            color: #6b7280;
            font-style: italic;
            margin-top: 2px;
        }
    </style>
</head>
<body>

<div class="container-fluid p-4">
    <div class="main-card">
        <!-- Header -->
        <div class="header-section">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h2><i class="bi bi-calendar-heart"></i> Správa dovolené</h2>
                    <p class="mb-0">European Transport CZ s.r.o. - <?= htmlspecialchars($userName) ?></p>
                </div>
                <div>
                    <?php if ($isAdmin): ?>
                        <a href="manage_events.php" class="btn btn-info me-2">
                            <i class="bi bi-calendar-event"></i> Celozávodní události
                        </a>
                        <a href="admin.php" class="btn btn-warning me-2">
                            <i class="bi bi-gear"></i> Administrace
                        </a>
                    <?php endif; ?>
                    <a href="http://localhost:5004/" class="btn btn-light me-2">
                        <i class="bi bi-arrow-left"></i> Odejít z aplikace
                    </a>
                    <a href="http://localhost:5004/logout" class="btn btn-outline-light">
                        <i class="bi bi-box-arrow-right"></i> Odhlásit
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Stats -->
        <div class="p-4">
            <!-- Notifikace -->
            <?php if (isset($_GET['success'])): ?>
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <?php
                    switch ($_GET['success']) {
                        case 'vacation_submitted':
                            echo '<i class="bi bi-check-circle"></i> Žádost o dovolenou byla úspěšně odeslána ke schválení.';
                            break;
                        case 'cancelled':
                            echo '<i class="bi bi-check-circle"></i> Žádost byla úspěšně zrušena.';
                            break;
                        default:
                            echo '<i class="bi bi-check-circle"></i> Operace byla úspěšně dokončena.';
                    }
                    ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            <?php endif; ?>
            
            <?php if (isset($_GET['error'])): ?>
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <?php
                    switch ($_GET['error']) {
                        case 'missing_fields':
                            echo '<i class="bi bi-exclamation-triangle"></i> Vyplňte prosím všechna povinná pole.';
                            break;
                        case 'invalid_dates':
                            echo '<i class="bi bi-exclamation-triangle"></i> Datum konce musí být po datu začátku.';
                            break;
                        case 'cannot_cancel':
                            echo '<i class="bi bi-exclamation-triangle"></i> Žádost nelze zrušit.';
                            break;
                        case 'save_failed':
                            echo '<i class="bi bi-exclamation-triangle"></i> Nepodařilo se uložit žádost. Zkontrolujte oprávnění k zápisu do složky data/.';
                            break;
                        default:
                            echo '<i class="bi bi-exclamation-triangle"></i> Nastala chyba při zpracování požadavku.';
                    }
                    ?>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            <?php endif; ?>
            
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-primary mb-0"><?= $totalHours ?> h</h3>
                        <small class="text-muted">Celkový příděl</small>
                        <div class="mt-1"><small>(<?= ($totalHours / 8) ?> dní)</small></div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-success mb-0"><?= $availableHours ?> h</h3>
                        <small class="text-muted">Dostupné</small>
                        <div class="mt-1"><small>(<?= ($availableHours / 8) ?> dní)</small></div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-info mb-0"><?= $usedHours ?> h</h3>
                        <small class="text-muted">Čerpáno</small>
                        <div class="mt-1"><small>(<?= ($usedHours / 8) ?> dní)</small></div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card text-center">
                        <h3 class="text-warning mb-0"><?= $pendingHours ?> h</h3>
                        <small class="text-muted">Čeká na schválení</small>
                        <div class="mt-1"><small>(<?= ($pendingHours / 8) ?> dní)</small></div>
                    </div>
                </div>
            </div>
            
            <!-- Toolbar -->
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#newVacationModal">
                        <i class="bi bi-plus-lg"></i> Nová žádost
                    </button>
                    <?php if ($isAdmin): ?>
                        <a href="print_calendar.php?year=<?= $currentYear ?>&month=<?= $currentMonth ?>" target="_blank" class="btn btn-outline-secondary">
                            <i class="bi bi-printer"></i> Tisknout kalendář
                        </a>
                    <?php endif; ?>
                </div>
                <div class="view-toggle btn-group" role="group">
                    <input type="radio" class="btn-check" name="viewMode" id="viewCalendar" checked>
                    <label class="btn btn-outline-primary" for="viewCalendar">
                        <i class="bi bi-calendar3"></i> Kalendář
                    </label>
                    <input type="radio" class="btn-check" name="viewMode" id="viewList">
                    <label class="btn btn-outline-primary" for="viewList">
                        <i class="bi bi-list-ul"></i> Seznam
                    </label>
                </div>
            </div>
            
            <!-- Celozávodní události - oznámení -->
            <?php
            // Zobrazit nadcházející události (od dnes do 30 dnů)
            $today = date('Y-m-d');
            $futureDate = date('Y-m-d', strtotime('+30 days'));
            $upcomingEvents = [];
            
            foreach ($visibleEvents as $event) {
                if ($event['start_date'] >= $today && $event['start_date'] <= $futureDate) {
                    $upcomingEvents[] = $event;
                }
            }
            
            // Seřadit podle data
            usort($upcomingEvents, function($a, $b) {
                return strtotime($a['start_date']) - strtotime($b['start_date']);
            });
            
            if (!empty($upcomingEvents)):
            ?>
                <div class="alert alert-light border mb-4" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);">
                    <h5 class="mb-3"><i class="bi bi-calendar-event text-primary"></i> Nadcházející celozávodní události</h5>
                    <?php 
                    // Načíst přihlášky
                    $attendanceFile = __DIR__ . '/../../data/event_attendance.json';
                    $attendance = [];
                    if (file_exists($attendanceFile)) {
                        $attendance = json_decode(file_get_contents($attendanceFile), true) ?: [];
                    }
                    
                    foreach (array_slice($upcomingEvents, 0, 3) as $evt): 
                        $eventIcon = 'ℹ️';
                        $eventColor = '#2563eb';
                        $bgGradient = 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)';
                        
                        if ($evt['type'] === 'vacation') {
                            $eventIcon = '🏖️';
                            $eventColor = '#dc2626';
                            $bgGradient = 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)';
                        } elseif ($evt['type'] === 'company_event') {
                            $eventIcon = '🎉';
                            $eventColor = '#16a34a';
                            $bgGradient = 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)';
                        }
                        
                        // Zjistit stav přihlášky uživatele
                        $userStatus = null;
                        $userReason = '';
                        if (isset($attendance[$evt['id']])) {
                            foreach ($attendance[$evt['id']] as $att) {
                                if ($att['user_id'] === $userId) {
                                    $userStatus = $att['status'];
                                    $userReason = $att['reason'] ?? '';
                                    break;
                                }
                            }
                        }
                        
                        $attendingCount = 0;
                        $notAttendingCount = 0;
                        if (isset($attendance[$evt['id']])) {
                            foreach ($attendance[$evt['id']] as $att) {
                                if ($att['status'] === 'attending') $attendingCount++;
                                elseif ($att['status'] === 'not_attending') $notAttendingCount++;
                            }
                        }
                    ?>
                        <div class="card mb-3" style="background: <?= $bgGradient ?>; border-left: 4px solid <?= $eventColor ?>;">
                            <div class="card-body">
                                <div class="row align-items-center">
                                    <div class="col-md-8">
                                        <h6 class="mb-1"><strong><?= $eventIcon ?> <?= htmlspecialchars($evt['title']) ?></strong></h6>
                                        <small class="text-muted">
                                            📅 <?= date('d.m.Y', strtotime($evt['start_date'])) ?> - <?= date('d.m.Y', strtotime($evt['end_date'])) ?>
                                        </small>
                                        <?php if (!empty($evt['description'])): ?>
                                            <p class="mb-1 mt-1"><small><?= htmlspecialchars($evt['description']) ?></small></p>
                                        <?php endif; ?>
                                        <small class="text-muted">
                                            👥 Zúčastní se: <strong class="text-success"><?= $attendingCount ?></strong>
                                        </small>
                                    </div>
                                    <div class="col-md-4 text-end">
                                        <?php if ($userStatus === 'attending'): ?>
                                            <span class="badge bg-success mb-2"><i class="bi bi-check-circle"></i> Zúčastním se</span><br>
                                            <button class="btn btn-sm btn-outline-danger" onclick="notAttendEvent('<?= $evt['id'] ?>', '<?= htmlspecialchars(addslashes($evt['title'])) ?>')">
                                                <i class="bi bi-x-circle"></i> Zrušit účast
                                            </button>
                                        <?php elseif ($userStatus === 'not_attending'): ?>
                                            <span class="badge bg-danger mb-2"><i class="bi bi-x-circle"></i> Nezúčastním se</span><br>
                                            <small class="text-muted d-block mb-2">Důvod: <?= htmlspecialchars($userReason) ?></small>
                                            <button class="btn btn-sm btn-outline-success" onclick="attendEvent('<?= $evt['id'] ?>')">
                                                <i class="bi bi-check-circle"></i> Přeci jen se zúčastním
                                            </button>
                                        <?php else: ?>
                                            <button class="btn btn-sm btn-success" onclick="attendEvent('<?= $evt['id'] ?>')">
                                                <i class="bi bi-check-circle"></i> Zúčastním se
                                            </button>
                                            <button class="btn btn-sm btn-outline-secondary" onclick="notAttendEvent('<?= $evt['id'] ?>', '<?= htmlspecialchars(addslashes($evt['title'])) ?>')">
                                                <i class="bi bi-x-circle"></i> Nezúčastním se
                                            </button>
                                        <?php endif; ?>
                                    </div>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                    <?php if (count($upcomingEvents) > 3): ?>
                        <small class="text-muted">... a další <?= count($upcomingEvents) - 3 ?> události</small>
                    <?php endif; ?>
                </div>
            <?php endif; ?>
            
            <!-- Content -->
            <div id="contentArea">
                <div id="calendarView">
                    <?php include 'calendar_view.php'; ?>
                </div>
                <div id="listView" style="display: none;">
                    <?php include 'list_view.php'; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal pro důvod neúčasti -->
<div class="modal fade" id="notAttendModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <form action="event_attendance.php" method="POST" id="notAttendForm">
                <div class="modal-header bg-warning">
                    <h5 class="modal-title">Důvod neúčasti na události</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" name="event_id" id="notAttendEventId">
                    <input type="hidden" name="action" value="not_attend">
                    
                    <div class="alert alert-info">
                        <strong>Událost:</strong> <span id="notAttendEventTitle"></span>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label fw-bold">Důvod neúčasti *</label>
                        <textarea class="form-control" name="reason" id="notAttendReason" 
                                  rows="4" required placeholder="Uveďte prosím důvod, proč se nemůžete zúčastnit..."></textarea>
                        <small class="text-muted">Tento důvod uvidí administrátor.</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                    <button type="submit" class="btn btn-warning">
                        <i class="bi bi-x-circle"></i> Potvrdit neúčast
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Modal pro novou dovolenou -->
<div class="modal fade" id="newVacationModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">Nová žádost o dovolenou</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <form action="submit_vacation.php" method="POST">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Typ</label>
                        <select class="form-select" name="type" required>
                            <option value="vacation">Dovolená</option>
                            <option value="paid_leave">Placené volno</option>
                            <option value="unpaid_leave">Neplacené volno</option>
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Datum od</label>
                        <input type="date" class="form-control" name="start_date" id="startDate" required>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Datum do</label>
                        <input type="date" class="form-control" name="end_date" id="endDate" required>
                    </div>
                    
                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="halfDay" name="half_day">
                            <label class="form-check-label" for="halfDay">
                                Půl dne (4 hodiny)
                            </label>
                        </div>
                    </div>
                    
                    <div class="mb-3" id="halfDayTime" style="display: none;">
                        <label class="form-label">Část dne</label>
                        <select class="form-select" name="half_day_period">
                            <option value="morning">Dopoledne (8:00 - 12:00)</option>
                            <option value="afternoon">Odpoledne (12:00 - 16:00)</option>
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Poznámka (nepovinná)</label>
                        <textarea class="form-control" name="note" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                    <button type="submit" class="btn btn-primary">Odeslat ke schválení</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
    // Přihláška na událost
    function attendEvent(eventId) {
        if (confirm('Opravdu se chcete zúčastnit této události?')) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = 'event_attendance.php';
            
            const eventInput = document.createElement('input');
            eventInput.type = 'hidden';
            eventInput.name = 'event_id';
            eventInput.value = eventId;
            
            const actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = 'attend';
            
            form.appendChild(eventInput);
            form.appendChild(actionInput);
            document.body.appendChild(form);
            form.submit();
        }
    }
    
    // Odhlášení z události s důvodem
    function notAttendEvent(eventId, eventTitle) {
        document.getElementById('notAttendEventId').value = eventId;
        document.getElementById('notAttendEventTitle').textContent = eventTitle;
        document.getElementById('notAttendReason').value = '';
        const modal = new bootstrap.Modal(document.getElementById('notAttendModal'));
        modal.show();
    }
    
    // View toggle
    document.getElementById('viewCalendar').addEventListener('change', function() {
        if (this.checked) {
            document.getElementById('calendarView').style.display = 'block';
            document.getElementById('listView').style.display = 'none';
        }
    });
    
    document.getElementById('viewList').addEventListener('change', function() {
        if (this.checked) {
            document.getElementById('calendarView').style.display = 'none';
            document.getElementById('listView').style.display = 'block';
        }
    });
    
    // Half day toggle
    document.getElementById('halfDay').addEventListener('change', function() {
        const halfDayTime = document.getElementById('halfDayTime');
        const endDate = document.getElementById('endDate');
        
        if (this.checked) {
            halfDayTime.style.display = 'block';
            endDate.disabled = true;
            endDate.value = document.getElementById('startDate').value;
        } else {
            halfDayTime.style.display = 'none';
            endDate.disabled = false;
        }
    });
    
    // Sync dates for half day
    document.getElementById('startDate').addEventListener('change', function() {
        if (document.getElementById('halfDay').checked) {
            document.getElementById('endDate').value = this.value;
        }
    });
    
    // Theme support
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
</script>

</body>
</html>
