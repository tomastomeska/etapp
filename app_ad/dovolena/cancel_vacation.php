<?php
// Autentifikace uživatele
require_once __DIR__ . '/auth.php';

$vacationsFile = __DIR__ . '/data/vacations.json';

function loadJsonFile($file, $default = []) {
    if (file_exists($file)) {
        return json_decode(file_get_contents($file), true) ?: $default;
    }
    return $default;
}

function saveJsonFile($file, $data) {
    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

$vacations = loadJsonFile($vacationsFile, []);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $vacationId = (int)$_POST['vacation_id'];
    
    // Najít žádost
    $found = false;
    foreach ($vacations as $key => $vac) {
        if ($vac['id'] === $vacationId && $vac['user_id'] === $userData['id'] && $vac['status'] === 'pending') {
            unset($vacations[$key]);
            $found = true;
            break;
        }
    }
    
    if ($found) {
        $vacations = array_values($vacations); // Reindex
        saveJsonFile($vacationsFile, $vacations);
        header('Location: index.php?success=cancelled');
    } else {
        header('Location: index.php?error=cannot_cancel');
    }
}

header('Location: index.php');
exit;
?>
