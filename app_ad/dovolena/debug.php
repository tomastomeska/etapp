<?php
/**
 * Debug stránka pro testování autentifikace
 */

// Spustit session
if (session_status() === PHP_SESSION_NONE) {
    session_set_cookie_params([
        'lifetime' => 0,
        'path' => '/',
        'domain' => 'localhost',
        'secure' => false,
        'httponly' => true,
        'samesite' => 'Lax'
    ]);
    session_start();
}

?>
<!DOCTYPE html>
<html>
<head>
    <title>Debug Autentifikace</title>
    <style>
        body { font-family: monospace; padding: 20px; background: #f5f5f5; }
        .section { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .ok { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
        pre { background: #f0f0f0; padding: 10px; overflow-x: auto; }
        h2 { border-bottom: 2px solid #333; padding-bottom: 5px; }
    </style>
</head>
<body>
    <h1>🔍 Debug Autentifikace - Aplikace Dovolená</h1>
    
    <div class="section">
        <h2>1. PHP Session</h2>
        <p>Session ID: <strong><?php echo session_id(); ?></strong></p>
        <p>Session status: <strong><?php echo session_status() === PHP_SESSION_ACTIVE ? '<span class="ok">AKTIVNÍ</span>' : '<span class="error">NEAKTIVNÍ</span>'; ?></strong></p>
        <p>Session data existují: <strong><?php echo isset($_SESSION['user_data']) ? '<span class="ok">ANO</span>' : '<span class="error">NE</span>'; ?></strong></p>
        <p>Celý $_SESSION obsah:</p>
        <pre><?php print_r($_SESSION); ?></pre>
        <?php if (isset($_SESSION['user_data'])): ?>
            <p class="ok">✅ User data v session:</p>
            <pre><?php print_r($_SESSION['user_data']); ?></pre>
        <?php endif; ?>
    </div>
    
    <div class="section">
        <h2>2. HTTP Headers z Flask Proxy</h2>
        <p>X-User-ID: <strong><?php echo isset($_SERVER['HTTP_X_USER_ID']) ? '<span class="ok">' . $_SERVER['HTTP_X_USER_ID'] . '</span>' : '<span class="error">CHYBÍ</span>'; ?></strong></p>
        <p>X-User-Email: <strong><?php echo isset($_SERVER['HTTP_X_USER_EMAIL']) ? '<span class="ok">' . $_SERVER['HTTP_X_USER_EMAIL'] . '</span>' : '<span class="error">CHYBÍ</span>'; ?></strong></p>
        <p>X-User-Name: <strong><?php echo isset($_SERVER['HTTP_X_USER_NAME']) ? '<span class="ok">' . base64_decode($_SERVER['HTTP_X_USER_NAME']) . '</span>' : '<span class="error">CHYBÍ</span>'; ?></strong></p>
        <p>X-User-Role: <strong><?php echo isset($_SERVER['HTTP_X_USER_ROLE']) ? '<span class="ok">' . $_SERVER['HTTP_X_USER_ROLE'] . '</span>' : '<span class="error">CHYBÍ</span>'; ?></strong></p>
    </div>
    
    <div class="section">
        <h2>3. Jak se dostal request?</h2>
        <?php if (isset($_SERVER['HTTP_X_USER_ID'])): ?>
            <p class="ok">✅ Request přišel přes Flask proxy (hlavičky jsou přítomny)</p>
        <?php elseif (isset($_SESSION['user_data'])): ?>
            <p class="ok">✅ Request přišel přímo na Apache (session je použita)</p>
        <?php else: ?>
            <p class="error">❌ Není přihlášen - ani proxy headers, ani session</p>
        <?php endif; ?>
    </div>
    
    <div class="section">
        <h2>4. Cookies</h2>
        <p>Počet cookies: <strong><?php echo count($_COOKIE); ?></strong></p>
        <p>PHPSESSID cookie: <strong><?php echo isset($_COOKIE['PHPSESSID']) ? '<span class="ok">' . $_COOKIE['PHPSESSID'] . '</span>' : '<span class="error">CHYBÍ</span>'; ?></strong></p>
        <?php if (!empty($_COOKIE)): ?>
            <pre><?php print_r($_COOKIE); ?></pre>
        <?php endif; ?>
    </div>
    
    <div class="section">
        <h2>5. Aktuální URL a způsob přístupu</h2>
        <p>URL: <strong><?php echo $_SERVER['REQUEST_URI']; ?></strong></p>
        <p>HTTP Host: <strong><?php echo $_SERVER['HTTP_HOST']; ?></strong></p>
        <p>Server Port: <strong><?php echo $_SERVER['SERVER_PORT']; ?></strong></p>
    </div>
    
    <div class="section">
        <h2>6. Test odkazy</h2>
        <p><a href="debug.php">🔄 Refresh této stránky</a> (měl by použít session)</p>
        <p><a href="index.php">🏠 Zpět na hlavní stránku aplikace</a></p>
        <p><a href="http://localhost:5004/app_ad/dovolena/debug.php">🔗 Otevřít přes Flask proxy</a></p>
    </div>
    
    <div class="section">
        <h2>7. Diagnostika</h2>
        <?php
        $issues = [];
        
        if (!isset($_SERVER['HTTP_X_USER_ID']) && !isset($_SESSION['user_data'])) {
            $issues[] = "❌ Není přihlášen - musíš přistoupit přes Flask proxy";
        }
        
        if (!isset($_COOKIE['PHPSESSID'])) {
            $issues[] = "⚠️ Session cookie není nastavena - možný problém s cookies";
        }
        
        if (isset($_SESSION['user_data']) && (time() - $_SESSION['user_data']['last_activity']) > 1800) {
            $issues[] = "⚠️ Session vypršela (>30 minut neaktivity)";
        }
        
        if (empty($issues)) {
            echo '<p class="ok">✅ Vše vypadá v pořádku!</p>';
        } else {
            foreach ($issues as $issue) {
                echo '<p>' . $issue . '</p>';
            }
        }
        ?>
    </div>
    
</body>
</html>
