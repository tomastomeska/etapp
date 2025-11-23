<?php
echo "PHP funguje!<br>";
echo "PHP verze: " . phpversion() . "<br>";
echo "Document root: " . $_SERVER['DOCUMENT_ROOT'] . "<br>";
echo "Script filename: " . $_SERVER['SCRIPT_FILENAME'] . "<br>";

// Test session
session_start();
echo "Session ID: " . session_id() . "<br>";

// Test cesty k souborům
$dataFile = __DIR__ . '/../../data_users.json';
echo "Data users cesta: $dataFile<br>";
echo "Existuje data_users.json: " . (file_exists($dataFile) ? "ANO" : "NE") . "<br>";

if (file_exists($dataFile)) {
    $users = json_decode(file_get_contents($dataFile), true);
    echo "Počet uživatelů: " . count($users) . "<br>";
}
?>
