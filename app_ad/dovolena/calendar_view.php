<?php
// Kalendářové zobrazení
$firstDayOfMonth = strtotime("$currentYear-$currentMonth-01");
$daysInMonth = date('t', $firstDayOfMonth);
$firstDayWeekday = date('N', $firstDayOfMonth); // 1 = pondělí, 7 = neděle

// Navigace měsíců
$prevMonth = $currentMonth - 1;
$prevYear = $currentYear;
if ($prevMonth < 1) {
    $prevMonth = 12;
    $prevYear--;
}

$nextMonth = $currentMonth + 1;
$nextYear = $currentYear;
if ($nextMonth > 12) {
    $nextMonth = 1;
    $nextYear++;
}

$monthNames = [
    1 => 'Leden', 2 => 'Únor', 3 => 'Březen', 4 => 'Duben',
    5 => 'Květen', 6 => 'Červen', 7 => 'Červenec', 8 => 'Srpen',
    9 => 'Září', 10 => 'Říjen', 11 => 'Listopad', 12 => 'Prosinec'
];
?>

<div class="calendar">
    <div class="calendar-header">
        <div class="d-flex justify-content-between align-items-center">
            <a href="?year=<?= $prevYear ?>&month=<?= $prevMonth ?>" class="btn btn-sm btn-outline-primary">
                <i class="bi bi-chevron-left"></i> Předchozí
            </a>
            <h4 class="mb-0"><?= $monthNames[$currentMonth] ?> <?= $currentYear ?></h4>
            <a href="?year=<?= $nextYear ?>&month=<?= $nextMonth ?>" class="btn btn-sm btn-outline-primary">
                Následující <i class="bi bi-chevron-right"></i>
            </a>
        </div>
    </div>
    
    <div class="table-responsive">
        <table class="table table-bordered mb-0">
            <thead>
                <tr class="text-center">
                    <th style="width: 14.28%;">Pondělí</th>
                    <th style="width: 14.28%;">Úterý</th>
                    <th style="width: 14.28%;">Středa</th>
                    <th style="width: 14.28%;">Čtvrtek</th>
                    <th style="width: 14.28%;">Pátek</th>
                    <th style="width: 14.28%;" class="bg-light">Sobota</th>
                    <th style="width: 14.28%;" class="bg-light">Neděle</th>
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
                            echo '<div class="fw-bold">' . $dayCounter . '</div>';
                            
                            // Najít dovolené pro tento den
                            $vacationsForDay = [];
                            foreach ($vacations as $vacation) {
                                $vStart = $vacation['start_date'];
                                $vEnd = $vacation['end_date'];
                                
                                if ($currentDate >= $vStart && $currentDate <= $vEnd) {
                                    // Zobrazit pouze vlastní dovolené nebo všechny pro admina
                                    if (!$isAdmin && $vacation['user_id'] != $userId) {
                                        continue;
                                    }
                                    
                                    $vacationsForDay[] = $vacation;
                                }
                            }
                            
                            // Najít celozávodní události pro tento den
                            $eventsForDay = [];
                            foreach ($visibleEvents as $event) {
                                $eStart = $event['start_date'];
                                $eEnd = $event['end_date'];
                                
                                if ($currentDate >= $eStart && $currentDate <= $eEnd) {
                                    $eventsForDay[] = $event;
                                }
                            }
                            
                            // Zobrazit celozávodní události
                            foreach ($eventsForDay as $evt) {
                                $eventColor = '#2563eb'; // Default modrá
                                $eventIcon = 'ℹ️';
                                $eventBorder = '#1e40af';
                                
                                if ($evt['type'] === 'vacation') {
                                    $eventColor = '#dc2626'; // Červená
                                    $eventBorder = '#991b1b';
                                    $eventIcon = '🏖️';
                                } elseif ($evt['type'] === 'company_event') {
                                    $eventColor = '#16a34a'; // Zelená
                                    $eventBorder = '#15803d';
                                    $eventIcon = '🎉';
                                }
                                
                                // Spočítat počet přihlášených pro tuto událost
                                $eventAttendingCount = 0;
                                if (isset($attendance[$evt['id']])) {
                                    foreach ($attendance[$evt['id']] as $att) {
                                        if ($att['status'] === 'attending') {
                                            $eventAttendingCount++;
                                        }
                                    }
                                }
                                
                                echo '<div class="small px-2 py-2 mb-1 rounded text-white fw-bold" style="background: linear-gradient(135deg, ' . $eventColor . ' 0%, ' . $eventBorder . ' 100%); font-size: 0.75rem; border-left: 4px solid ' . $eventBorder . '; box-shadow: 0 2px 4px rgba(0,0,0,0.15);">';
                                echo $eventIcon . ' ' . htmlspecialchars($evt['title']);
                                if ($eventAttendingCount > 0) {
                                    echo ' <span class="badge bg-white text-dark" style="font-size: 0.65rem;">👥 ' . $eventAttendingCount . '</span>';
                                }
                                echo '</div>';
                            }
                            
                            // Zobrazit dovolené
                            foreach ($vacationsForDay as $vac) {
                                $statusClass = 'vacation-' . $vac['status'];
                                if ($vac['type'] === 'paid_leave') {
                                    $statusClass = 'vacation-paid-leave';
                                } elseif ($vac['type'] === 'unpaid_leave') {
                                    $statusClass = 'vacation-unpaid-leave';
                                }
                                
                                $label = '';
                                if ($vac['type'] === 'vacation') $label = 'D';
                                elseif ($vac['type'] === 'paid_leave') $label = 'PV';
                                elseif ($vac['type'] === 'unpaid_leave') $label = 'NV';
                                
                                if ($vac['half_day']) {
                                    $label .= ' (½)';
                                }
                                
                                if ($isAdmin && $vac['user_id'] != $userId) {
                                    $label .= ' - ' . substr($vac['user_name'], 0, 15);
                                }
                                
                                echo '<div class="vacation-indicator ' . $statusClass . '" title="' . htmlspecialchars($vac['user_name']) . '">' . $label . '</div>';
                                
                                // Pokud je víkend nebo svátek, přidat poznámku
                                if ($isWeekend || $isHolidayDay) {
                                    echo '<div class="weekend-note">⚠️ Neodečítá se z fondu</div>';
                                }
                            }
                            
                            // Zobrazit svátek
                            if ($isHolidayDay) {
                                if (isset($holidays[$currentDate])) {
                                    echo '<small class="text-warning"><i class="bi bi-star-fill"></i> ' . substr($holidays[$currentDate], 0, 20) . '</small>';
                                }
                            }
                            
                            // Upozornění na kolize (pro adminy)
                            if ($isAdmin && count($vacationsForDay) > 1) {
                                $approvedCount = 0;
                                foreach ($vacationsForDay as $vac) {
                                    if ($vac['status'] === 'approved') $approvedCount++;
                                }
                                if ($approvedCount > 1) {
                                    echo '<div class="mt-1"><small class="badge bg-warning text-dark"><i class="bi bi-exclamation-triangle"></i> Kolize!</small></div>';
                                }
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
    </div>
    
    <div class="p-3 bg-light">
        <div class="row">
            <div class="col-md-6">
                <h6>Legenda:</h6>
                <div class="d-flex flex-wrap gap-2">
                    <span class="vacation-indicator vacation-approved">Schválená</span>
                    <span class="vacation-indicator vacation-pending">Čeká na schválení</span>
                    <span class="vacation-indicator vacation-rejected">Zamítnutá</span>
                    <span class="vacation-indicator vacation-paid-leave">Placené volno</span>
                    <span class="vacation-indicator vacation-unpaid-leave">Neplacené volno</span>
                </div>
            </div>
            <?php if ($isAdmin): ?>
            <div class="col-md-6">
                <small class="text-muted">
                    <i class="bi bi-info-circle"></i> D = Dovolená, PV = Placené volno, NV = Neplacené volno, (½) = Půl dne
                </small>
            </div>
            <?php endif; ?>
        </div>
    </div>
</div>
