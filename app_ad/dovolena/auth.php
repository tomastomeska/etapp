<?php
/**
 * Autentifikační modul pro dovolenkovou aplikaci
 * Zpracovává přihlášení z Flask proxy pomocí HTTP headers
 * a udržuje PHP session pro další requesty
 */

// Spustit session s vhodnými parametry
if (session_status() === PHP_SESSION_NONE) {
    // Nastavit session cookie parametry
    session_set_cookie_params([
        'lifetime' => 0, // Session cookie (vyprší po zavření prohlížeče)
        'path' => '/',
        'domain' => 'localhost',
        'secure' => false,
        'httponly' => true,
        'samesite' => 'Lax'
    ]);
    session_start();
}

$userData = null;

// DEBUG - zakomentuj po vyřešení
$debug_info = [];
$debug_info['has_headers'] = isset($_SERVER['HTTP_X_USER_ID']);
$debug_info['has_session'] = isset($_SESSION['user_data']);
$debug_info['session_id'] = session_id();

// Kontrola, zda přišla data z Flask proxy (HTTP headers)
if (isset($_SERVER['HTTP_X_USER_ID']) && isset($_SERVER['HTTP_X_USER_EMAIL'])) {
    // Data přišla z Flask proxy - uložit do session
    $debug_info['source'] = 'flask_proxy';
    $_SESSION['user_data'] = [
        'id' => $_SERVER['HTTP_X_USER_ID'],
        'email' => $_SERVER['HTTP_X_USER_EMAIL'],
        'full_name' => base64_decode($_SERVER['HTTP_X_USER_NAME']),
        'role' => $_SERVER['HTTP_X_USER_ROLE'],
        'username' => $_SERVER['HTTP_X_USER_USERNAME'],
        'last_activity' => time()
    ];
    $userData = $_SESSION['user_data'];
}
// Pokud hlavičky nejsou, zkusit načíst z existující session
elseif (isset($_SESSION['user_data'])) {
    // Zkontrolovat timeout (30 minut neaktivity)
    $debug_info['source'] = 'php_session';
    $timeout = 1800; // 30 minut
    if (time() - $_SESSION['user_data']['last_activity'] < $timeout) {
        // Session je stále platná
        $_SESSION['user_data']['last_activity'] = time();
        $userData = $_SESSION['user_data'];
        $debug_info['session_valid'] = true;
    } else {
        // Session vypršela
        $debug_info['session_valid'] = false;
        $debug_info['session_expired'] = true;
        session_destroy();
        session_start();
        $userData = null;
    }
} else {
    $debug_info['source'] = 'none';
}

// DEBUG výstup - odkomentuj pro debugging
// echo "<!-- DEBUG AUTH: " . json_encode($debug_info) . " -->";

// Pokud není přihlášen ani z proxy ani z session, přesměruj na hlavní aplikaci
if (!$userData) {
    // Pokud request přišel přes Flask proxy (má X-Forwarded hlavičku), ukáže chybu
    // Pokud ne, přesměruje na Flask login
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR']) || isset($_SERVER['HTTP_X_REAL_IP'])) {
        die('Autentifikace selhala. Prosím přihlaste se znovu.');
    }
    header('Location: http://localhost:5004/login');
    exit;
}

// Nastavit globální proměnné pro použití v aplikaci
$isAdmin = in_array($userData['role'], ['admin', 'administrativa']);
$userId = $userData['id'];
$userName = $userData['full_name'];
$userRole = $userData['role'];
$userEmail = $userData['email'];

// Pomocné funkce
function isUserAdmin() {
    global $isAdmin;
    return $isAdmin;
}

function getUserId() {
    global $userId;
    return $userId;
}

function getUserName() {
    global $userName;
    return $userName;
}

function getUserRole() {
    global $userRole;
    return $userRole;
}
