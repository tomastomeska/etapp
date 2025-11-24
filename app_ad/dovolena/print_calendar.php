<?php
// Autentifikace uživatele
require_once __DIR__ . '/auth.php';

// Kontrola oprávnění - pouze admin
if (!$isAdmin) {
    header('Location: index.php');
    exit;
}

// Získat měsíc a rok
$currentYear = isset($_GET['year']) ? (int)$_GET['year'] : date('Y');
$currentMonth = isset($_GET['month']) ? (int)$_GET['month'] : date('n');

// Načtení dat
$vacationsFile = __DIR__ . '/data/vacations.json';
$holidaysFile = __DIR__ . '/data/czech_holidays.json';
$eventsFile = __DIR__ . '/../../data/company_events.json';
$attendanceFile = __DIR__ . '/../../data/event_attendance.json';

function loadJsonFile($file, $default = []) {
    if (file_exists($file)) {
        $content = file_get_contents($file);
        if (empty($content)) {
            return $default;
        }
        $result = json_decode($content, true);
        return $result ?: $default;
    }
    return $default;
}

$vacations = loadJsonFile($vacationsFile, []);
$holidays = loadJsonFile($holidaysFile, []);
$allEvents = loadJsonFile($eventsFile, []);
$attendance = loadJsonFile($attendanceFile, []);

// Filtrovat pouze schválené dovolené pro tisk
$approvedVacations = array_filter($vacations, function($v) {
    return $v['status'] === 'approved';
});

// Filtrovat události pro aktuální měsíc
$visibleEvents = [];
foreach ($allEvents as $event) {
    $eventStart = strtotime($event['start_date']);
    $eventEnd = strtotime($event['end_date']);
    $monthStart = strtotime("$currentYear-$currentMonth-01");
    $monthEnd = strtotime(date('Y-m-t', $monthStart));
    
    if ($eventEnd >= $monthStart && $eventStart <= $monthEnd) {
        $visibleEvents[] = $event;
    }
}

// Funkce pro kontrolu svátku
function isHoliday($date, $holidays) {
    return isset($holidays[$date]);
}

// Kalendář
$firstDayOfMonth = strtotime("$currentYear-$currentMonth-01");
$daysInMonth = date('t', $firstDayOfMonth);
$firstDayWeekday = date('N', $firstDayOfMonth);

$monthNames = [
    1 => 'Leden', 2 => 'Únor', 3 => 'Březen', 4 => 'Duben',
    5 => 'Květen', 6 => 'Červen', 7 => 'Červenec', 8 => 'Srpen',
    9 => 'Září', 10 => 'Říjen', 11 => 'Listopad', 12 => 'Prosinec'
];
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kalendář dovolených - <?= $monthNames[$currentMonth] ?> <?= $currentYear ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @media print {
            .no-print { display: none; }
            body { 
                padding: 5mm; 
                font-size: 8pt;
            }
            .header {
                padding-bottom: 5px;
                margin-bottom: 10px;
            }
            .header h1 {
                font-size: 14pt;
                margin: 0;
            }
            .header p {
                font-size: 8pt;
            }
            .calendar-day { 
                height: 85px; 
                font-size: 7pt;
                padding: 3px;
            }
            .day-number {
                font-size: 9pt;
            }
            .vacation-item {
                font-size: 6.5pt;
                padding: 1px 2px;
                margin: 1px 0;
            }
            .event-item {
                font-size: 6pt;
                padding: 1px 2px;
                margin: 1px 0;
            }
            .holiday-text {
                font-size: 6pt;
            }
            .legend {
                margin-top: 8px;
                padding: 5px;
                font-size: 7pt;
            }
            .legend-item {
                margin-right: 10px;
                font-size: 7pt;
            }
            .legend-box {
                width: 10px;
                height: 10px;
            }
            .calendar th {
                padding: 4px;
                font-size: 8pt;
            }
        }
        
        @page {
            size: A4 portrait;
            margin: 10mm;
        }
        
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            font-size: 0.9em;
        }
        
        .header {
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        .calendar {
            width: 100%;
            border-collapse: collapse;
        }
        
        .calendar th {
            background: #2563eb;
            color: white;
            padding: 8px;
            text-align: center;
            border: 1px solid #1e40af;
        }
        
        .calendar-day {
            border: 1px solid #ddd;
            padding: 5px;
            vertical-align: top;
            height: 120px;
            position: relative;
        }
        
        .calendar-day.weekend {
            background: #f8f9fa;
        }
        
        .calendar-day.holiday {
            background: #fef3c7;
        }
        
        .calendar-day.today {
            background: #dbeafe;
        }
        
        .day-number {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 3px;
        }
        
        .vacation-item {
            font-size: 0.75em;
            padding: 2px 4px;
            margin: 2px 0;
            border-radius: 3px;
            border-left: 3px solid;
        }
        
        .vacation-approved {
            background: #d1fae5;
            border-left-color: #10b981;
        }
        
        .event-item {
            font-size: 0.7em;
            padding: 2px 4px;
            margin: 2px 0;
            border-radius: 3px;
            color: white;
            font-weight: bold;
        }
        
        .event-vacation {
            background: #dc2626;
        }
        
        .event-info {
            background: #2563eb;
        }
        
        .event-company {
            background: #16a34a;
        }
        
        .holiday-text {
            font-size: 0.7em;
            color: #d97706;
            font-style: italic;
        }
        
        .legend {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .legend-item {
            display: inline-block;
            margin-right: 20px;
            font-size: 0.85em;
        }
        
        .legend-box {
            display: inline-block;
            width: 15px;
            height: 15px;
            margin-right: 5px;
            border-radius: 3px;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Kalendář dovolených - <?= $monthNames[$currentMonth] ?> <?= $currentYear ?></h1>
        <p class="mb-0">
            <strong>European Transport CZ s.r.o.</strong> | 
            Vytištěno: <?= date('d.m.Y H:i') ?> | 
            Vytiskl: <?= htmlspecialchars($userName) ?>
        </p>
    </div>
    
    <div class="no-print mb-3">
        <button onclick="window.print()" class="btn btn-primary">
            <i class="bi bi-printer"></i> Tisknout
        </button>
        <button onclick="window.close()" class="btn btn-secondary">
            Zavřít
        </button>
    </div>
    
    <table class="calendar">
        <thead>
            <tr>
                <th style="width: 14.28%;">Pondělí</th>
                <th style="width: 14.28%;">Úterý</th>
                <th style="width: 14.28%;">Středa</th>
                <th style="width: 14.28%;">Čtvrtek</th>
                <th style="width: 14.28%;">Pátek</th>
                <th style="width: 14.28%;">Sobota</th>
                <th style="width: 14.28%;">Neděle</th>
            </tr>
        </thead>
        <tbody>
            <?php
            $dayCounter = 1;
            $weeksToShow = ceil(($daysInMonth + $firstDayWeekday - 1) / 7);
            
            for ($week = 0; $week < $weeksToShow; $week++) {
                echo '<tr>';
                
                for ($dayOfWeek = 1; $dayOfWeek <= 7; $dayOfWeek++) {
                    $shouldShowDay = ($week === 0 && $dayOfWeek >= $firstDayWeekday) || 
                                    ($week > 0 && $dayCounter <= $daysInMonth);
                    
                    if ($shouldShowDay && $dayCounter <= $daysInMonth) {
                        $currentDate = sprintf("%04d-%02d-%02d", $currentYear, $currentMonth, $dayCounter);
                        $isToday = $currentDate === date('Y-m-d');
                        $isWeekend = $dayOfWeek >= 6;
                        $isHolidayDay = isHoliday($currentDate, $holidays);
                        
                        $classes = ['calendar-day'];
                        if ($isToday) $classes[] = 'today';
                        if ($isWeekend) $classes[] = 'weekend';
                        if ($isHolidayDay) $classes[] = 'holiday';
                        
                        echo '<td class="' . implode(' ', $classes) . '">';
                        echo '<div class="day-number">' . $dayCounter . '</div>';
                        
                        // Najít dovolené pro tento den
                        foreach ($approvedVacations as $vac) {
                            if ($currentDate >= $vac['start_date'] && $currentDate <= $vac['end_date']) {
                                $label = substr($vac['user_name'], 0, 15);
                                if ($vac['half_day']) {
                                    $label .= ' (½)';
                                }
                                echo '<div class="vacation-item vacation-approved">' . htmlspecialchars($label) . '</div>';
                            }
                        }
                        
                        // Najít události pro tento den
                        foreach ($visibleEvents as $evt) {
                            if ($currentDate >= $evt['start_date'] && $currentDate <= $evt['end_date']) {
                                $eventClass = 'event-info';
                                if ($evt['type'] === 'vacation') {
                                    $eventClass = 'event-vacation';
                                } elseif ($evt['type'] === 'company_event') {
                                    $eventClass = 'event-company';
                                }
                                
                                $attendingCount = 0;
                                if (isset($attendance[$evt['id']])) {
                                    foreach ($attendance[$evt['id']] as $att) {
                                        if ($att['status'] === 'attending') {
                                            $attendingCount++;
                                        }
                                    }
                                }
                                
                                $eventLabel = htmlspecialchars(substr($evt['title'], 0, 20));
                                if ($attendingCount > 0) {
                                    $eventLabel .= ' (' . $attendingCount . ')';
                                }
                                
                                echo '<div class="event-item ' . $eventClass . '">' . $eventLabel . '</div>';
                            }
                        }
                        
                        // Zobrazit svátek
                        if ($isHolidayDay) {
                            echo '<div class="holiday-text">' . htmlspecialchars(substr($holidays[$currentDate], 0, 15)) . '</div>';
                        }
                        
                        echo '</td>';
                        $dayCounter++;
                    } else {
                        echo '<td class="calendar-day"></td>';
                    }
                }
                
                echo '</tr>';
            }
            ?>
        </tbody>
    </table>
    
    <div class="legend">
        <strong>Legenda:</strong><br>
        <div class="mt-2">
            <div class="legend-item">
                <span class="legend-box" style="background: #d1fae5; border-left: 3px solid #10b981;"></span>
                Schválená dovolená
            </div>
            <div class="legend-item">
                <span class="legend-box" style="background: #dc2626;"></span>
                Celozávodní dovolená
            </div>
            <div class="legend-item">
                <span class="legend-box" style="background: #2563eb;"></span>
                Informace
            </div>
            <div class="legend-item">
                <span class="legend-box" style="background: #16a34a;"></span>
                Firemní akce
            </div>
            <div class="legend-item">
                <span class="legend-box" style="background: #fef3c7;"></span>
                Státní svátek
            </div>
        </div>
        <div class="mt-2">
            <small>(½) = Půl dne | Číslo v závorce u události = počet přihlášených</small>
        </div>
    </div>
    
    <script>
        // Automaticky otevřít tiskové okno po načtení
        window.addEventListener('load', function() {
            setTimeout(function() {
                // window.print();
            }, 500);
        });
    </script>
</body>
</html>
