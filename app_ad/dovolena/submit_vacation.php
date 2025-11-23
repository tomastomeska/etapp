<?php
// Získání informací o přihlášeném uživateli z Flask proxy (HTTP headers)
$userData = null;

if (isset($_SERVER['HTTP_X_USER_ID'])) {
    $userData = [
        'id' => $_SERVER['HTTP_X_USER_ID'],
        'email' => $_SERVER['HTTP_X_USER_EMAIL'],
        'full_name' => base64_decode($_SERVER['HTTP_X_USER_NAME']),
        'role' => $_SERVER['HTTP_X_USER_ROLE'],
        'username' => $_SERVER['HTTP_X_USER_USERNAME']
    ];
}

if (!$userData) {
    header('Location: index.php');
    exit;
}

// Načtení dat
$vacationsFile = __DIR__ . '/data/vacations.json';
$allowancesFile = __DIR__ . '/data/allowances.json';
$holidaysFile = __DIR__ . '/data/czech_holidays.json';

function loadJsonFile($file, $default = []) {
    if (file_exists($file)) {
        $content = file_get_contents($file);
        if (empty($content)) {
            return $default;
        }
        return json_decode($content, true) ?: $default;
    }
    return $default;
}

function saveJsonFile($file, $data) {
    // Zajistit, že složka existuje
    $dir = dirname($file);
    if (!is_dir($dir)) {
        mkdir($dir, 0777, true);
    }
    return file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

function isWeekend($date) {
    $dayOfWeek = date('N', strtotime($date));
    return $dayOfWeek >= 6;
}

function isHoliday($date, $holidays) {
    return isset($holidays[$date]);
}

function calculateWorkingHours($startDate, $endDate, $holidays, $halfDay = false, $halfDayPeriod = '') {
    if ($halfDay) {
        return 4; // Půl dne = 4 hodiny
    }
    
    $hours = 0;
    $current = strtotime($startDate);
    $end = strtotime($endDate);
    
    while ($current <= $end) {
        $dateStr = date('Y-m-d', $current);
        if (!isWeekend($dateStr) && !isHoliday($dateStr, $holidays)) {
            $hours += 8; // Celý den = 8 hodin
        }
        $current = strtotime('+1 day', $current);
    }
    
    return $hours;
}

$vacations = loadJsonFile($vacationsFile, []);
$holidays = loadJsonFile($holidaysFile, []);

// Zpracování formuláře
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $type = $_POST['type'] ?? '';
    $startDate = $_POST['start_date'] ?? '';
    $endDate = $_POST['end_date'] ?? '';
    $halfDay = isset($_POST['half_day']);
    $halfDayPeriod = $_POST['half_day_period'] ?? '';
    $note = $_POST['note'] ?? '';
    
    // Validace dat
    if (empty($type) || empty($startDate) || empty($endDate)) {
        header('Location: index.php?error=missing_fields');
        exit;
    }
    
    if (strtotime($startDate) > strtotime($endDate)) {
        header('Location: index.php?error=invalid_dates');
        exit;
    }
    
    // Výpočet hodin
    $hours = calculateWorkingHours($startDate, $endDate, $holidays, $halfDay, $halfDayPeriod);
    
    // Vytvoření nové žádosti
    $newId = empty($vacations) ? 1 : max(array_column($vacations, 'id')) + 1;
    
    $newVacation = [
        'id' => $newId,
        'user_id' => $userData['id'],
        'user_name' => $userData['full_name'],
        'type' => $type,
        'start_date' => $startDate,
        'end_date' => $endDate,
        'half_day' => $halfDay,
        'half_day_period' => $halfDayPeriod,
        'hours' => $hours,
        'status' => 'pending',
        'note' => $note,
        'created_at' => date('Y-m-d H:i:s'),
        'approved_by' => null,
        'approved_by_name' => null,
        'approved_at' => null
    ];
    
    $vacations[] = $newVacation;
    
    // Debug - zkontrolovat, jestli můžeme zapisovat
    $result = saveJsonFile($vacationsFile, $vacations);
    
    if ($result === false) {
        header('Location: index.php?error=save_failed');
        exit;
    }
    
    header('Location: index.php?success=vacation_submitted');
    exit;
}

header('Location: index.php');
exit;
?>
