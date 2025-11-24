<?php
// Autentifikace uživatele
require_once __DIR__ . '/auth.php';

// Kontrola oprávnění - pouze admin
if (!$isAdmin) {
    header('Location: index.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: admin.php');
    exit;
}

$vacationId = intval($_POST['vacation_id'] ?? 0);
$action = $_POST['action'] ?? null;

if (!$vacationId || !in_array($action, ['approve', 'reject', 'approve_with_changes'])) {
    header('Location: admin.php?error=invalid_data');
    exit;
}

$vacationsFile = __DIR__ . '/data/vacations.json';
$allowancesFile = __DIR__ . '/data/allowances.json';

// Načtení dat
$vacations = [];
if (file_exists($vacationsFile)) {
    $vacations = json_decode(file_get_contents($vacationsFile), true) ?: [];
}

$allowances = [];
if (file_exists($allowancesFile)) {
    $allowances = json_decode(file_get_contents($allowancesFile), true) ?: [];
}

// Najít žádost
$vacationIndex = null;
$vacation = null;
foreach ($vacations as $index => $vac) {
    if ($vac['id'] === $vacationId) {
        $vacationIndex = $index;
        $vacation = $vac;
        break;
    }
}

if (!$vacation || $vacation['status'] !== 'pending') {
    header('Location: admin.php?error=not_found');
    exit;
}

// Zpracování podle akce
if ($action === 'approve') {
    // Kontrola kolizí (jen varování, nezakazujeme)
    $conflicts = [];
    foreach ($vacations as $other) {
        if ($other['id'] !== $vacation['id'] && 
            $other['status'] === 'approved' &&
            $other['start_date'] <= $vacation['end_date'] && 
            $other['end_date'] >= $vacation['start_date']) {
            $conflicts[] = $other['user_name'];
        }
    }
    
    // Schválení
    $vacations[$vacationIndex]['status'] = 'approved';
    $vacations[$vacationIndex]['approved_by'] = $userData['id'];
    $vacations[$vacationIndex]['approved_by_name'] = $userData['full_name'];
    $vacations[$vacationIndex]['approved_at'] = date('Y-m-d H:i:s');
    
    // Uložit
    file_put_contents($vacationsFile, json_encode($vacations, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    
    if (!empty($conflicts)) {
        $conflictMsg = urlencode('Schváleno s kolizemi: ' . implode(', ', $conflicts));
        header("Location: admin.php?success=approved&conflicts=$conflictMsg");
    } else {
        header('Location: admin.php?success=approved');
    }
    
} elseif ($action === 'reject') {
    // Zamítnutí - vyžaduje důvod
    $rejectReason = trim($_POST['reject_reason'] ?? '');
    
    if (empty($rejectReason)) {
        header('Location: admin.php?error=missing_reason');
        exit;
    }
    
    $vacations[$vacationIndex]['status'] = 'rejected';
    $vacations[$vacationIndex]['approved_by'] = $userData['id'];
    $vacations[$vacationIndex]['approved_by_name'] = $userData['full_name'];
    $vacations[$vacationIndex]['approved_at'] = date('Y-m-d H:i:s');
    $vacations[$vacationIndex]['reject_reason'] = $rejectReason;
    
    // Uložit
    file_put_contents($vacationsFile, json_encode($vacations, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    
    header('Location: admin.php?success=rejected');
    
} elseif ($action === 'approve_with_changes') {
    // Schválení s úpravou termínu
    $newStartDate = $_POST['new_start_date'] ?? '';
    $newEndDate = $_POST['new_end_date'] ?? '';
    $changeNote = trim($_POST['change_note'] ?? '');
    
    if (empty($newStartDate) || empty($newEndDate)) {
        header('Location: admin.php?error=invalid_dates');
        exit;
    }
    
    if (strtotime($newStartDate) > strtotime($newEndDate)) {
        header('Location: admin.php?error=invalid_dates');
        exit;
    }
    
    // Načíst svátky pro přepočet hodin
    $holidaysFile = __DIR__ . '/data/czech_holidays.json';
    $holidays = [];
    if (file_exists($holidaysFile)) {
        $holidays = json_decode(file_get_contents($holidaysFile), true) ?: [];
    }
    
    // Přepočítat hodiny pro nové datum
    function isWeekend($date) {
        $dayOfWeek = date('N', strtotime($date));
        return $dayOfWeek >= 6;
    }
    
    function isHoliday($date, $holidays) {
        return isset($holidays[$date]);
    }
    
    $newHours = 0;
    $current = strtotime($newStartDate);
    $end = strtotime($newEndDate);
    
    while ($current <= $end) {
        $dateStr = date('Y-m-d', $current);
        if (!isWeekend($dateStr) && !isHoliday($dateStr, $holidays)) {
            $newHours += 8;
        }
        $current = strtotime('+1 day', $current);
    }
    
    // Pokud je půl dne, přepsat na 4 hodiny
    if ($vacation['half_day']) {
        $newHours = 4;
    }
    
    // Uložit původní žádost
    $vacations[$vacationIndex]['original_start_date'] = $vacation['start_date'];
    $vacations[$vacationIndex]['original_end_date'] = $vacation['end_date'];
    $vacations[$vacationIndex]['original_hours'] = $vacation['hours'];
    
    // Aktualizovat s novými daty
    $vacations[$vacationIndex]['start_date'] = $newStartDate;
    $vacations[$vacationIndex]['end_date'] = $newEndDate;
    $vacations[$vacationIndex]['hours'] = $newHours;
    $vacations[$vacationIndex]['status'] = 'approved';
    $vacations[$vacationIndex]['approved_by'] = $userData['id'];
    $vacations[$vacationIndex]['approved_by_name'] = $userData['full_name'];
    $vacations[$vacationIndex]['approved_at'] = date('Y-m-d H:i:s');
    $vacations[$vacationIndex]['modified'] = true;
    $vacations[$vacationIndex]['change_note'] = $changeNote;
    
    // Uložit
    file_put_contents($vacationsFile, json_encode($vacations, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    
    header('Location: admin.php?success=approved_modified');
}

exit;
