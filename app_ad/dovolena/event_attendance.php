<?php
// Zpracování přihlášek na celozávodní události

// Autentifikace uživatele
require_once __DIR__ . '/auth.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: index.php');
    exit;
}

$eventId = $_POST['event_id'] ?? '';
$action = $_POST['action'] ?? '';

if (empty($eventId) || !in_array($action, ['attend', 'not_attend'])) {
    header('Location: index.php?error=invalid_request');
    exit;
}

// Cesta k souboru s přihláškami
$attendanceFile = __DIR__ . '/../../data/event_attendance.json';

// Načíst přihlášky
$attendance = [];
if (file_exists($attendanceFile)) {
    $attendance = json_decode(file_get_contents($attendanceFile), true) ?: [];
}

// Inicializovat pole pro událost, pokud neexistuje
if (!isset($attendance[$eventId])) {
    $attendance[$eventId] = [];
}

// Najít existující přihlášku uživatele
$existingIndex = null;
foreach ($attendance[$eventId] as $index => $att) {
    if ($att['user_id'] === $userData['id']) {
        $existingIndex = $index;
        break;
    }
}

if ($action === 'attend') {
    // Přihláška na událost
    $newAttendance = [
        'user_id' => $userData['id'],
        'user_name' => $userData['full_name'],
        'user_role' => $userData['role'],
        'status' => 'attending',
        'timestamp' => date('Y-m-d H:i:s')
    ];
    
    if ($existingIndex !== null) {
        // Aktualizovat existující
        $attendance[$eventId][$existingIndex] = $newAttendance;
    } else {
        // Přidat novou
        $attendance[$eventId][] = $newAttendance;
    }
    
    // Uložit
    $dir = dirname($attendanceFile);
    if (!is_dir($dir)) {
        mkdir($dir, 0777, true);
    }
    file_put_contents($attendanceFile, json_encode($attendance, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    
    header('Location: index.php?success=event_attend');
    exit;
    
} elseif ($action === 'not_attend') {
    // Odhlášení z události - vyžaduje důvod
    $reason = trim($_POST['reason'] ?? '');
    
    if (empty($reason)) {
        header('Location: index.php?error=missing_reason');
        exit;
    }
    
    $newAttendance = [
        'user_id' => $userData['id'],
        'user_name' => $userData['full_name'],
        'user_role' => $userData['role'],
        'status' => 'not_attending',
        'reason' => $reason,
        'timestamp' => date('Y-m-d H:i:s')
    ];
    
    if ($existingIndex !== null) {
        // Aktualizovat existující
        $attendance[$eventId][$existingIndex] = $newAttendance;
    } else {
        // Přidat novou
        $attendance[$eventId][] = $newAttendance;
    }
    
    // Uložit
    $dir = dirname($attendanceFile);
    if (!is_dir($dir)) {
        mkdir($dir, 0777, true);
    }
    file_put_contents($attendanceFile, json_encode($attendance, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    
    header('Location: index.php?success=event_not_attend');
    exit;
}

header('Location: index.php');
exit;
