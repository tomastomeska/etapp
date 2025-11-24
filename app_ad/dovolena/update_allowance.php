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

$userId = $_POST['user_id'] ?? null;
$hours = intval($_POST['hours'] ?? 0);

if (!$userId || $hours < 0) {
    header('Location: admin.php?error=invalid_data');
    exit;
}

$allowancesFile = __DIR__ . '/data/allowances.json';

// Načtení dat
$allowances = [];
if (file_exists($allowancesFile)) {
    $allowances = json_decode(file_get_contents($allowancesFile), true) ?: [];
}

// Aktualizace přídělu
$allowances[$userId] = [
    'hours_per_year' => $hours,
    'updated_by' => $userData['id'],
    'updated_by_name' => $userData['full_name'],
    'updated_at' => date('Y-m-d H:i:s')
];

// Zajistit, že složka data existuje
$dataDir = __DIR__ . '/data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0777, true);
}

// Uložit
file_put_contents($allowancesFile, json_encode($allowances, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

header('Location: admin.php?success=allowance_updated');
exit;
