<?php
// Správa celozávodních událostí

// Ověření přihlášení
if (isset($_SERVER['HTTP_X_USER_ID'])) {
    $userData = [
        'id' => $_SERVER['HTTP_X_USER_ID'],
        'email' => $_SERVER['HTTP_X_USER_EMAIL'],
        'full_name' => base64_decode($_SERVER['HTTP_X_USER_NAME']),
        'role' => $_SERVER['HTTP_X_USER_ROLE'],
        'username' => $_SERVER['HTTP_X_USER_USERNAME']
    ];
} else {
    die('Přístup odepřen');
}

// Kontrola oprávnění - pouze admin nebo administrativa
if ($userData['role'] !== 'admin' && $userData['role'] !== 'administrativa') {
    die('Nemáte oprávnění pro správu událostí');
}

// Načtení událostí
$eventsFile = '../../data/company_events.json';
$events = [];
if (file_exists($eventsFile)) {
    $events = json_decode(file_get_contents($eventsFile), true) ?? [];
}

// Zpracování formuláře
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    if ($action === 'add') {
        $newEvent = [
            'id' => uniqid('event_'),
            'title' => $_POST['title'] ?? '',
            'description' => $_POST['description'] ?? '',
            'type' => $_POST['type'] ?? 'info', // info, vacation, company_event
            'start_date' => $_POST['start_date'] ?? '',
            'end_date' => $_POST['end_date'] ?? '',
            'visible_for_ridic' => isset($_POST['visible_for_ridic']),
            'visible_for_administrativa' => isset($_POST['visible_for_administrativa']),
            'visible_for_admin' => isset($_POST['visible_for_admin']),
            'visible_for_all' => isset($_POST['visible_for_all']),
            'created_by' => $userData['full_name'],
            'created_at' => date('Y-m-d H:i:s')
        ];
        
        $events[] = $newEvent;
        file_put_contents($eventsFile, json_encode($events, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        header('Location: manage_events.php?success=added');
        exit;
    }
    
    if ($action === 'delete') {
        $eventId = $_POST['event_id'] ?? '';
        $events = array_filter($events, function($e) use ($eventId) {
            return $e['id'] !== $eventId;
        });
        $events = array_values($events);
        file_put_contents($eventsFile, json_encode($events, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        header('Location: manage_events.php?success=deleted');
        exit;
    }
    
    if ($action === 'edit') {
        $eventId = $_POST['event_id'] ?? '';
        foreach ($events as &$event) {
            if ($event['id'] === $eventId) {
                $event['title'] = $_POST['title'] ?? $event['title'];
                $event['description'] = $_POST['description'] ?? $event['description'];
                $event['type'] = $_POST['type'] ?? $event['type'];
                $event['start_date'] = $_POST['start_date'] ?? $event['start_date'];
                $event['end_date'] = $_POST['end_date'] ?? $event['end_date'];
                $event['visible_for_ridic'] = isset($_POST['visible_for_ridic']);
                $event['visible_for_administrativa'] = isset($_POST['visible_for_administrativa']);
                $event['visible_for_admin'] = isset($_POST['visible_for_admin']);
                $event['visible_for_all'] = isset($_POST['visible_for_all']);
                $event['updated_at'] = date('Y-m-d H:i:s');
                break;
            }
        }
        file_put_contents($eventsFile, json_encode($events, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        header('Location: manage_events.php?success=updated');
        exit;
    }
}

// Seřazení událostí podle data
usort($events, function($a, $b) {
    return strtotime($a['start_date']) - strtotime($b['start_date']);
});

// Načíst přihlášky
$attendanceFile = '../../data/event_attendance.json';
$attendance = [];
if (file_exists($attendanceFile)) {
    $attendance = json_decode(file_get_contents($attendanceFile), true) ?: [];
}

// Typy událostí pro zobrazení
$eventTypes = [
    'vacation' => ['label' => 'Celozávodní dovolená', 'icon' => '🏖️', 'color' => '#dc2626'],
    'info' => ['label' => 'Informace', 'icon' => 'ℹ️', 'color' => '#2563eb'],
    'company_event' => ['label' => 'Firemní akce', 'icon' => '🎉', 'color' => '#16a34a']
];
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Správa celozávodních událostí</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-blue: #2563eb;
            --dark-bg: #0f172a;
            --dark-card: #1e293b;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
        }
        
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .event-card {
            border-left: 4px solid;
            transition: transform 0.2s;
        }
        
        .event-card:hover {
            transform: translateX(5px);
        }
        
        .event-type-vacation {
            border-left-color: #dc2626;
        }
        
        .event-type-info {
            border-left-color: #2563eb;
        }
        
        .event-type-company_event {
            border-left-color: #16a34a;
        }
        
        .badge-role {
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
        }
        
        .btn-action {
            padding: 0.25rem 0.5rem;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2><i class="bi bi-calendar-event"></i> Správa celozávodních událostí</h2>
                    <div>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addEventModal">
                            <i class="bi bi-plus-circle"></i> Přidat událost
                        </button>
                        <a href="index.php" class="btn btn-secondary">
                            <i class="bi bi-arrow-left"></i> Zpět
                        </a>
                    </div>
                </div>
                
                <?php if (isset($_GET['success'])): ?>
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        <?php
                        switch ($_GET['success']) {
                            case 'added': echo 'Událost byla úspěšně přidána'; break;
                            case 'updated': echo 'Událost byla úspěšně upravena'; break;
                            case 'deleted': echo 'Událost byla úspěšně smazána'; break;
                        }
                        ?>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                <?php endif; ?>
                
                <div class="row">
                    <?php if (empty($events)): ?>
                        <div class="col-12">
                            <div class="alert alert-info">
                                <i class="bi bi-info-circle"></i> Zatím nejsou vytvořeny žádné události.
                            </div>
                        </div>
                    <?php else: ?>
                        <?php foreach ($events as $event): ?>
                            <div class="col-md-6 mb-3">
                                <div class="card event-card event-type-<?php echo $event['type']; ?>">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <h5 class="card-title mb-0">
                                                <?php echo $eventTypes[$event['type']]['icon']; ?>
                                                <?php echo htmlspecialchars($event['title']); ?>
                                            </h5>
                                            <span class="badge" style="background-color: <?php echo $eventTypes[$event['type']]['color']; ?>">
                                                <?php echo $eventTypes[$event['type']]['label']; ?>
                                            </span>
                                        </div>
                                        
                                        <p class="text-muted mb-2">
                                            <?php echo htmlspecialchars($event['description']); ?>
                                        </p>
                                        
                                        <div class="mb-2">
                                            <i class="bi bi-calendar-range"></i>
                                            <strong>Od:</strong> <?php echo date('d.m.Y', strtotime($event['start_date'])); ?>
                                            <strong>Do:</strong> <?php echo date('d.m.Y', strtotime($event['end_date'])); ?>
                                        </div>
                                        
                                        <div class="mb-3">
                                            <small><i class="bi bi-eye"></i> <strong>Viditelné pro:</strong></small><br>
                                            <?php if ($event['visible_for_all']): ?>
                                                <span class="badge bg-primary badge-role">Všichni</span>
                                            <?php else: ?>
                                                <?php if ($event['visible_for_ridic']): ?>
                                                    <span class="badge bg-info badge-role">Řidiči</span>
                                                <?php endif; ?>
                                                <?php if ($event['visible_for_administrativa']): ?>
                                                    <span class="badge bg-warning text-dark badge-role">Administrativa</span>
                                                <?php endif; ?>
                                                <?php if ($event['visible_for_admin']): ?>
                                                    <span class="badge bg-danger badge-role">Administrátoři</span>
                                                <?php endif; ?>
                                            <?php endif; ?>
                                        </div>
                                        
                                        <?php
                                        // Spočítat přihlášky pro tuto událost
                                        $attendingUsers = [];
                                        $notAttendingUsers = [];
                                        if (isset($attendance[$event['id']])) {
                                            foreach ($attendance[$event['id']] as $att) {
                                                if ($att['status'] === 'attending') {
                                                    $attendingUsers[] = $att;
                                                } elseif ($att['status'] === 'not_attending') {
                                                    $notAttendingUsers[] = $att;
                                                }
                                            }
                                        }
                                        ?>
                                        
                                        <?php if (!empty($attendingUsers) || !empty($notAttendingUsers)): ?>
                                            <div class="mb-3 border-top pt-2">
                                                <button class="btn btn-sm btn-outline-info w-100" type="button" 
                                                        data-bs-toggle="collapse" data-bs-target="#attendance-<?php echo $event['id']; ?>">
                                                    <i class="bi bi-people"></i> Přihlášky 
                                                    (✓ <?php echo count($attendingUsers); ?> | ✗ <?php echo count($notAttendingUsers); ?>)
                                                </button>
                                                
                                                <div class="collapse mt-2" id="attendance-<?php echo $event['id']; ?>">
                                                    <?php if (!empty($attendingUsers)): ?>
                                                        <div class="mb-2">
                                                            <strong class="text-success"><i class="bi bi-check-circle"></i> Zúčastní se:</strong>
                                                            <ul class="small mb-0 mt-1">
                                                                <?php foreach ($attendingUsers as $att): ?>
                                                                    <li><?php echo htmlspecialchars($att['user_name']); ?> 
                                                                        <span class="badge bg-secondary"><?php echo $att['user_role']; ?></span>
                                                                        <small class="text-muted">(<?php echo date('d.m. H:i', strtotime($att['timestamp'])); ?>)</small>
                                                                    </li>
                                                                <?php endforeach; ?>
                                                            </ul>
                                                        </div>
                                                    <?php endif; ?>
                                                    
                                                    <?php if (!empty($notAttendingUsers)): ?>
                                                        <div>
                                                            <strong class="text-danger"><i class="bi bi-x-circle"></i> Nezúčastní se:</strong>
                                                            <ul class="small mb-0 mt-1">
                                                                <?php foreach ($notAttendingUsers as $att): ?>
                                                                    <li><?php echo htmlspecialchars($att['user_name']); ?> 
                                                                        <span class="badge bg-secondary"><?php echo $att['user_role']; ?></span>
                                                                        <small class="text-muted">(<?php echo date('d.m. H:i', strtotime($att['timestamp'])); ?>)</small>
                                                                        <?php if (!empty($att['reason'])): ?>
                                                                            <br><small class="text-muted">Důvod: <?php echo htmlspecialchars($att['reason']); ?></small>
                                                                        <?php endif; ?>
                                                                    </li>
                                                                <?php endforeach; ?>
                                                            </ul>
                                                        </div>
                                                    <?php endif; ?>
                                                </div>
                                            </div>
                                        <?php endif; ?>
                                        
                                        <div class="d-flex justify-content-between align-items-center">
                                            <small class="text-muted">
                                                Vytvořil: <?php echo htmlspecialchars($event['created_by']); ?><br>
                                                <?php echo date('d.m.Y H:i', strtotime($event['created_at'])); ?>
                                            </small>
                                            <div>
                                                <button class="btn btn-sm btn-outline-primary btn-action" 
                                                        onclick="editEvent(<?php echo htmlspecialchars(json_encode($event)); ?>)">
                                                    <i class="bi bi-pencil"></i> Upravit
                                                </button>
                                                <form method="POST" style="display: inline;" onsubmit="return confirm('Opravdu smazat tuto událost?');">
                                                    <input type="hidden" name="action" value="delete">
                                                    <input type="hidden" name="event_id" value="<?php echo $event['id']; ?>">
                                                    <button type="submit" class="btn btn-sm btn-outline-danger btn-action">
                                                        <i class="bi bi-trash"></i> Smazat
                                                    </button>
                                                </form>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal pro přidání události -->
    <div class="modal fade" id="addEventModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <form method="POST">
                    <div class="modal-header">
                        <h5 class="modal-title">Přidat novou událost</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <input type="hidden" name="action" value="add">
                        
                        <div class="mb-3">
                            <label class="form-label">Název události *</label>
                            <input type="text" name="title" class="form-control" required>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Popis</label>
                            <textarea name="description" class="form-control" rows="3"></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Typ události *</label>
                            <select name="type" class="form-select" required>
                                <option value="info">ℹ️ Informace</option>
                                <option value="vacation">🏖️ Celozávodní dovolená</option>
                                <option value="company_event">🎉 Firemní akce</option>
                            </select>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Datum od *</label>
                                <input type="date" name="start_date" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Datum do *</label>
                                <input type="date" name="end_date" class="form-control" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Viditelnost *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="visible_all" name="visible_for_all">
                                <label class="form-check-label" for="visible_all">
                                    <strong>Pro všechny</strong> (pokud zaškrtnete, ostatní volby budou ignorovány)
                                </label>
                            </div>
                            <hr>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="visible_ridic" name="visible_for_ridic">
                                <label class="form-check-label" for="visible_ridic">Řidiči</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="visible_administrativa" name="visible_for_administrativa">
                                <label class="form-check-label" for="visible_administrativa">Administrativa</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="visible_admin" name="visible_for_admin">
                                <label class="form-check-label" for="visible_admin">Administrátoři</label>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-primary">Přidat událost</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Modal pro editaci události -->
    <div class="modal fade" id="editEventModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <form method="POST">
                    <div class="modal-header">
                        <h5 class="modal-title">Upravit událost</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <input type="hidden" name="action" value="edit">
                        <input type="hidden" name="event_id" id="edit_event_id">
                        
                        <div class="mb-3">
                            <label class="form-label">Název události *</label>
                            <input type="text" name="title" id="edit_title" class="form-control" required>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Popis</label>
                            <textarea name="description" id="edit_description" class="form-control" rows="3"></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Typ události *</label>
                            <select name="type" id="edit_type" class="form-select" required>
                                <option value="info">ℹ️ Informace</option>
                                <option value="vacation">🏖️ Celozávodní dovolená</option>
                                <option value="company_event">🎉 Firemní akce</option>
                            </select>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Datum od *</label>
                                <input type="date" name="start_date" id="edit_start_date" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Datum do *</label>
                                <input type="date" name="end_date" id="edit_end_date" class="form-control" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Viditelnost *</label>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="edit_visible_all" name="visible_for_all">
                                <label class="form-check-label" for="edit_visible_all">
                                    <strong>Pro všechny</strong>
                                </label>
                            </div>
                            <hr>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="edit_visible_ridic" name="visible_for_ridic">
                                <label class="form-check-label" for="edit_visible_ridic">Řidiči</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="edit_visible_administrativa" name="visible_for_administrativa">
                                <label class="form-check-label" for="edit_visible_administrativa">Administrativa</label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="edit_visible_admin" name="visible_for_admin">
                                <label class="form-check-label" for="edit_visible_admin">Administrátoři</label>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                        <button type="submit" class="btn btn-primary">Uložit změny</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function editEvent(event) {
            document.getElementById('edit_event_id').value = event.id;
            document.getElementById('edit_title').value = event.title;
            document.getElementById('edit_description').value = event.description;
            document.getElementById('edit_type').value = event.type;
            document.getElementById('edit_start_date').value = event.start_date;
            document.getElementById('edit_end_date').value = event.end_date;
            document.getElementById('edit_visible_all').checked = event.visible_for_all;
            document.getElementById('edit_visible_ridic').checked = event.visible_for_ridic;
            document.getElementById('edit_visible_administrativa').checked = event.visible_for_administrativa;
            document.getElementById('edit_visible_admin').checked = event.visible_for_admin;
            
            new bootstrap.Modal(document.getElementById('editEventModal')).show();
        }
    </script>
</body>
</html>
