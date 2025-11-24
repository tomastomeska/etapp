<?php
/**
 * Odhlášení z aplikace Dovolená
 * Zruší PHP session a přesměruje na Flask logout který zruší i Flask session
 */

// Spustit session
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Zrušit všechny session proměnné
$_SESSION = [];

// Zrušit session cookie
if (isset($_COOKIE[session_name()])) {
    setcookie(session_name(), '', time() - 3600, '/');
}

// Zničit session
session_destroy();

// Přesměrovat přímo na Flask logout endpoint
// Flask logout zruší Flask session a přesměruje na login
header('Location: http://localhost:5004/logout');
exit;
