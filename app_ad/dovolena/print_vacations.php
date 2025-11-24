<?php
// Autentifikace uživatele
require_once __DIR__ . '/auth.php';

// Kontrola oprávnění - pouze admin
if (!$isAdmin) {
    header('Location: index.php');
    exit;
}

// Získat filtr statusu
$filterStatus = $_GET['status'] ?? 'all';

// Načtení dat
$vacationsFile = __DIR__ . '/data/vacations.json';

function loadJsonFile($file, $default = []) {
    if (file_exists($file)) {
        return json_decode(file_get_contents($file), true) ?: $default;
    }
    return $default;
}

$vacations = loadJsonFile($vacationsFile, []);

// Filtrovat podle statusu
$filteredVacations = [];
foreach ($vacations as $vac) {
    if ($filterStatus === 'all' || $vac['status'] === $filterStatus) {
        $filteredVacations[] = $vac;
    }
}

// Seřadit podle data podání
usort($filteredVacations, function($a, $b) {
    return strtotime($b['submitted_at']) - strtotime($a['submitted_at']);
});

// Nadpis podle filtru
$title = 'Všechny žádosti o dovolenou';
switch ($filterStatus) {
    case 'pending':
        $title = 'Žádosti ke schválení';
        break;
    case 'approved':
        $title = 'Schválené dovolené';
        break;
    case 'rejected':
        $title = 'Zamítnuté žádosti';
        break;
}

// Typy dovolené
function getVacationType($type) {
    switch ($type) {
        case 'vacation': return 'Dovolená';
        case 'paid_leave': return 'Placené volno';
        case 'unpaid_leave': return 'Neplacené volno';
        default: return $type;
    }
}

// Status badge
function getStatusText($status) {
    switch ($status) {
        case 'pending': return 'Ke schválení';
        case 'approved': return 'Schválená';
        case 'rejected': return 'Zamítnutá';
        default: return $status;
    }
}
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($title) ?> - Tisk</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @media print {
            .no-print { display: none; }
            body { padding: 20px; }
        }
        
        body {
            font-family: Arial, sans-serif;
            padding: 30px;
        }
        
        .header {
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        
        .vacation-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .vacation-table th {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 10px;
            text-align: left;
            font-weight: bold;
        }
        
        .vacation-table td {
            border: 1px solid #dee2e6;
            padding: 10px;
        }
        
        .vacation-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .status-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status-pending {
            background: #fef3c7;
            color: #92400e;
        }
        
        .status-approved {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-rejected {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            font-size: 0.9em;
            color: #6b7280;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><?= htmlspecialchars($title) ?></h1>
        <p class="mb-0">
            <strong>European Transport CZ s.r.o.</strong><br>
            Vytištěno: <?= date('d.m.Y H:i') ?><br>
            Vytiskl: <?= htmlspecialchars($userName) ?>
        </p>
    </div>
    
    <div class="no-print mb-3">
        <button onclick="window.print()" class="btn btn-primary">
            <i class="bi bi-printer"></i> Tisknout
        </button>
        <button onclick="window.close()" class="btn btn-secondary">
            Zavřít
        </button>
    </div>
    
    <?php if (empty($filteredVacations)): ?>
        <div class="alert alert-info">
            <strong>Žádné záznamy</strong><br>
            Nebyly nalezeny žádné žádosti o dovolenou pro vybraný filtr.
        </div>
    <?php else: ?>
        <p><strong>Celkem záznamů: <?= count($filteredVacations) ?></strong></p>
        
        <table class="vacation-table">
            <thead>
                <tr>
                    <th style="width: 5%;">ID</th>
                    <th style="width: 15%;">Zaměstnanec</th>
                    <th style="width: 12%;">Typ</th>
                    <th style="width: 12%;">Od</th>
                    <th style="width: 12%;">Do</th>
                    <th style="width: 8%;">Hodin</th>
                    <th style="width: 10%;">Status</th>
                    <th style="width: 12%;">Podáno</th>
                    <th style="width: 14%;">Poznámka</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($filteredVacations as $vac): ?>
                    <tr>
                        <td><?= substr($vac['id'], 0, 8) ?></td>
                        <td><?= htmlspecialchars($vac['user_name']) ?></td>
                        <td><?= getVacationType($vac['type']) ?><?= $vac['half_day'] ? ' (½)' : '' ?></td>
                        <td><?= date('d.m.Y', strtotime($vac['start_date'])) ?></td>
                        <td><?= date('d.m.Y', strtotime($vac['end_date'])) ?></td>
                        <td><?= $vac['hours'] ?> h</td>
                        <td>
                            <span class="status-badge status-<?= $vac['status'] ?>">
                                <?= getStatusText($vac['status']) ?>
                            </span>
                        </td>
                        <td><?= date('d.m.Y', strtotime($vac['submitted_at'])) ?></td>
                        <td style="font-size: 0.85em;">
                            <?php if (!empty($vac['note'])): ?>
                                <?= htmlspecialchars(substr($vac['note'], 0, 50)) ?>
                            <?php endif; ?>
                            <?php if ($vac['status'] === 'rejected' && !empty($vac['reject_reason'])): ?>
                                <br><strong>Důvod zamítnutí:</strong> <?= htmlspecialchars(substr($vac['reject_reason'], 0, 50)) ?>
                            <?php endif; ?>
                            <?php if ($vac['status'] === 'approved' && !empty($vac['change_note'])): ?>
                                <br><strong>Úprava:</strong> <?= htmlspecialchars(substr($vac['change_note'], 0, 50)) ?>
                            <?php endif; ?>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        
        <?php if ($filterStatus === 'approved'): ?>
            <div class="mt-4">
                <h5>Statistiky schválených dovolených</h5>
                <?php
                $totalHours = 0;
                $userStats = [];
                
                foreach ($filteredVacations as $vac) {
                    $totalHours += $vac['hours'];
                    if (!isset($userStats[$vac['user_name']])) {
                        $userStats[$vac['user_name']] = ['count' => 0, 'hours' => 0];
                    }
                    $userStats[$vac['user_name']]['count']++;
                    $userStats[$vac['user_name']]['hours'] += $vac['hours'];
                }
                ?>
                <p><strong>Celkový počet hodin:</strong> <?= $totalHours ?> h</p>
                <p><strong>Průměrná délka:</strong> <?= round($totalHours / count($filteredVacations), 1) ?> h</p>
            </div>
        <?php endif; ?>
    <?php endif; ?>
    
    <div class="footer">
        <p>
            <strong>European Transport CZ s.r.o.</strong><br>
            Systém správy dovolené | Vytištěno automaticky ze systému
        </p>
    </div>
    
    <script>
        // Automaticky otevřít tiskové okno po načtení
        window.addEventListener('load', function() {
            // Počkat chvíli na načtení stylů
            setTimeout(function() {
                // Nezobrazovat dialog, pokud není potřeba
                // window.print();
            }, 500);
        });
    </script>
</body>
</html>
