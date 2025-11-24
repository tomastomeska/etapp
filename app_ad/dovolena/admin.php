<?php
// Autentifikace uživatele
require_once __DIR__ . '/auth.php';

// Kontrola oprávnění - pouze admin
if (!$isAdmin) {
    header('Location: index.php');
    exit;
}

// Načtení dat
$vacationsFile = __DIR__ . '/data/vacations.json';
$allowancesFile = __DIR__ . '/data/allowances.json';

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
$allowances = loadJsonFile($allowancesFile, []);

// Načtení všech uživatelů
$allUsers = [];
$usersDataFile = __DIR__ . '/../../data_users.json';
if (file_exists($usersDataFile)) {
    $allUsers = json_decode(file_get_contents($usersDataFile), true);
}

// Statistiky
$pendingCount = 0;
$approvedCount = 0;
$rejectedCount = 0;

foreach ($vacations as $vac) {
    if ($vac['status'] === 'pending') $pendingCount++;
    elseif ($vac['status'] === 'approved') $approvedCount++;
    elseif ($vac['status'] === 'rejected') $rejectedCount++;
}
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Administrace dovolené - European Transport CZ</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        :root {
            --primary-blue: #2563eb;
        }
        
        body {
            background: #f8fafc;
        }
        
        .admin-header {
            background: linear-gradient(135deg, var(--primary-blue), #1e40af);
            color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
        }
        
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .vacation-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #ddd;
        }
        
        .vacation-card.pending {
            border-left-color: #f59e0b;
        }
        
        .vacation-card.approved {
            border-left-color: #10b981;
        }
        
        .vacation-card.rejected {
            border-left-color: #ef4444;
        }
        
        .conflict-badge {
            background: #fef3c7;
            color: #92400e;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>

<div class="container-fluid p-4">
    <div class="admin-header">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h2><i class="bi bi-gear"></i> Administrace dovolené</h2>
                <p class="mb-0">Správa žádostí a přídělů dovolené</p>
            </div>
            <div>
                <a href="print_vacations.php?status=pending" target="_blank" class="btn btn-outline-primary me-2">
                    <i class="bi bi-printer"></i> Tisk ke schválení
                </a>
                <a href="print_vacations.php?status=approved" target="_blank" class="btn btn-outline-success me-2">
                    <i class="bi bi-printer"></i> Tisk schválených
                </a>
                <a href="print_vacations.php?status=rejected" target="_blank" class="btn btn-outline-danger me-2">
                    <i class="bi bi-printer"></i> Tisk zamítnutých
                </a>
                <a href="index.php" class="btn btn-light">
                    <i class="bi bi-arrow-left"></i> Zpět na přehled
                </a>
            </div>
        </div>
    </div>
    
    <!-- Statistiky -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="stat-card">
                <h3 class="text-warning"><?= $pendingCount ?></h3>
                <p class="mb-0">Čeká na schválení</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card">
                <h3 class="text-success"><?= $approvedCount ?></h3>
                <p class="mb-0">Schválených</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card">
                <h3 class="text-danger"><?= $rejectedCount ?></h3>
                <p class="mb-0">Zamítnutých</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card">
                <h3 class="text-primary"><?= count($allUsers) ?></h3>
                <p class="mb-0">Celkem uživatelů</p>
            </div>
        </div>
    </div>
    
    <!-- Notifikace -->
    <?php if (isset($_GET['success'])): ?>
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <?php
            switch ($_GET['success']) {
                case 'approved':
                    echo '<i class="bi bi-check-circle"></i> Žádost byla úspěšně schválena.';
                    break;
                case 'approved_modified':
                    echo '<i class="bi bi-check-circle"></i> Žádost byla schválena s úpravou termínu.';
                    break;
                case 'rejected':
                    echo '<i class="bi bi-x-circle"></i> Žádost byla zamítnuta.';
                    break;
                case 'allowance_updated':
                    echo '<i class="bi bi-check-circle"></i> Příděl dovolené byl aktualizován.';
                    break;
                default:
                    echo '<i class="bi bi-check-circle"></i> Operace byla úspěšně dokončena.';
            }
            ?>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    <?php endif; ?>
    
    <?php if (isset($_GET['error'])): ?>
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <?php
            switch ($_GET['error']) {
                case 'missing_reason':
                    echo '<i class="bi bi-exclamation-triangle"></i> Musíte zadat důvod zamítnutí!';
                    break;
                case 'invalid_dates':
                    echo '<i class="bi bi-exclamation-triangle"></i> Neplatné datum. Datum konce musí být po datu začátku.';
                    break;
                default:
                    echo '<i class="bi bi-exclamation-triangle"></i> Nastala chyba při zpracování.';
            }
            ?>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    <?php endif; ?>
    
    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4" role="tablist">
        <li class="nav-item">
            <a class="nav-link active" data-bs-toggle="tab" href="#pending">
                <i class="bi bi-clock"></i> Čekající žádosti (<?= $pendingCount ?>)
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link" data-bs-toggle="tab" href="#all">
                <i class="bi bi-list"></i> Všechny žádosti
            </a>
        </li>
        <li class="nav-item">
            <a class="nav-link" data-bs-toggle="tab" href="#allowances">
                <i class="bi bi-people"></i> Příděly dovolené
            </a>
        </li>
    </ul>
    
    <div class="tab-content">
        <!-- Čekající žádosti -->
        <div class="tab-pane fade show active" id="pending">
            <?php
            $pendingVacations = array_filter($vacations, function($v) {
                return $v['status'] === 'pending';
            });
            
            usort($pendingVacations, function($a, $b) {
                return strtotime($a['start_date']) - strtotime($b['start_date']);
            });
            
            if (empty($pendingVacations)): ?>
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> Žádné čekající žádosti.
                </div>
            <?php else: ?>
                <?php foreach ($pendingVacations as $vac): 
                    // Kontrola kolizí
                    $conflicts = [];
                    foreach ($vacations as $other) {
                        if ($other['id'] !== $vac['id'] && 
                            $other['status'] === 'approved' &&
                            $other['start_date'] <= $vac['end_date'] && 
                            $other['end_date'] >= $vac['start_date']) {
                            $conflicts[] = $other;
                        }
                    }
                ?>
                <div class="vacation-card pending">
                    <div class="row align-items-center">
                        <div class="col-md-4">
                            <h5 class="mb-1"><?= htmlspecialchars($vac['user_name']) ?></h5>
                            <p class="mb-0">
                                <?php
                                    if ($vac['type'] === 'vacation') echo '<span class="badge bg-primary">Dovolená</span>';
                                    elseif ($vac['type'] === 'paid_leave') echo '<span class="badge bg-info">Placené volno</span>';
                                    else echo '<span class="badge bg-secondary">Neplacené volno</span>';
                                ?>
                                <?php if ($vac['half_day']): ?>
                                    <span class="badge bg-light text-dark">Půl dne</span>
                                <?php endif; ?>
                            </p>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted">Období:</small><br>
                            <strong><?= date('d.m.Y', strtotime($vac['start_date'])) ?></strong> -
                            <strong><?= date('d.m.Y', strtotime($vac['end_date'])) ?></strong>
                            <br>
                            <small><?= $vac['hours'] ?> hodin (<?= ($vac['hours'] / 8) ?> dní)</small>
                        </div>
                        <div class="col-md-2">
                            <?php if (!empty($conflicts)): ?>
                                <div class="conflict-badge">
                                    <i class="bi bi-exclamation-triangle"></i> Kolize!
                                    <small class="d-block">Počet: <?= count($conflicts) ?></small>
                                </div>
                            <?php endif; ?>
                        </div>
                        <div class="col-md-3 text-end">
                            <button type="button" class="btn btn-success btn-sm" 
                                    onclick="approveVacation(<?= $vac['id'] ?>, '<?= htmlspecialchars($vac['start_date']) ?>', '<?= htmlspecialchars($vac['end_date']) ?>')">
                                <i class="bi bi-check-circle"></i> Schválit
                            </button>
                            <button type="button" class="btn btn-warning btn-sm" 
                                    onclick="approveWithChanges(<?= $vac['id'] ?>, '<?= htmlspecialchars($vac['start_date']) ?>', '<?= htmlspecialchars($vac['end_date']) ?>')">
                                <i class="bi bi-pencil"></i> Schválit s úpravou
                            </button>
                            <button type="button" class="btn btn-danger btn-sm" 
                                    onclick="rejectVacation(<?= $vac['id'] ?>)">
                                <i class="bi bi-x-circle"></i> Zamítnout
                            </button>
                        </div>
                    </div>
                    <?php if ($vac['note']): ?>
                        <div class="mt-2 pt-2 border-top">
                            <small class="text-muted">Poznámka: <?= htmlspecialchars($vac['note']) ?></small>
                        </div>
                    <?php endif; ?>
                    <?php if (!empty($conflicts)): ?>
                        <div class="mt-2 pt-2 border-top">
                            <small class="text-warning fw-bold">⚠️ Kolize s:</small>
                            <?php foreach ($conflicts as $conf): ?>
                                <br><small>• <?= htmlspecialchars($conf['user_name']) ?> 
                                (<?= date('d.m.', strtotime($conf['start_date'])) ?> - <?= date('d.m.', strtotime($conf['end_date'])) ?>)</small>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>
                </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
        
        <!-- Všechny žádosti -->
        <div class="tab-pane fade" id="all">
            <div class="table-responsive bg-white rounded shadow-sm">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Uživatel</th>
                            <th>Typ</th>
                            <th>Od - Do</th>
                            <th>Hodiny</th>
                            <th>Stav</th>
                            <th>Schválil</th>
                            <th>Datum žádosti</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php 
                        $sortedVacations = $vacations;
                        usort($sortedVacations, function($a, $b) {
                            return strtotime($b['created_at']) - strtotime($a['created_at']);
                        });
                        
                        foreach ($sortedVacations as $vac): ?>
                        <tr>
                            <td><?= htmlspecialchars($vac['user_name']) ?></td>
                            <td>
                                <?php
                                    if ($vac['type'] === 'vacation') echo 'Dovolená';
                                    elseif ($vac['type'] === 'paid_leave') echo 'Placené volno';
                                    else echo 'Neplacené volno';
                                ?>
                            </td>
                            <td>
                                <?= date('d.m.Y', strtotime($vac['start_date'])) ?> -
                                <?= date('d.m.Y', strtotime($vac['end_date'])) ?>
                            </td>
                            <td><?= $vac['hours'] ?> h</td>
                            <td>
                                <?php if ($vac['status'] === 'approved'): ?>
                                    <span class="badge bg-success">Schváleno</span>
                                <?php elseif ($vac['status'] === 'pending'): ?>
                                    <span class="badge bg-warning">Čeká</span>
                                <?php else: ?>
                                    <span class="badge bg-danger">Zamítnuto</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?php if ($vac['approved_by_name']): ?>
                                    <small><?= htmlspecialchars($vac['approved_by_name']) ?></small>
                                <?php else: ?>
                                    <small class="text-muted">-</small>
                                <?php endif; ?>
                            </td>
                            <td><small><?= date('d.m.Y H:i', strtotime($vac['created_at'])) ?></small></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Příděly dovolené -->
        <div class="tab-pane fade" id="allowances">
            <div class="bg-white rounded shadow-sm p-4">
                <h5 class="mb-3">Správa přídělů dovolené</h5>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>Uživatel</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Příděl (hodiny/rok)</th>
                                <th>Příděl (dny/rok)</th>
                                <th>Akce</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($allUsers as $user): 
                                $userAllowance = $allowances[$user['id']] ?? null;
                                $hours = $userAllowance ? $userAllowance['hours_per_year'] : 160;
                            ?>
                            <tr>
                                <td><?= htmlspecialchars($user['full_name']) ?></td>
                                <td><?= htmlspecialchars($user['email']) ?></td>
                                <td>
                                    <?php
                                        if ($user['role'] === 'admin') echo '<span class="badge bg-danger">Admin</span>';
                                        elseif ($user['role'] === 'ridic') echo '<span class="badge bg-primary">Řidič</span>';
                                        else echo '<span class="badge bg-info">Administrativa</span>';
                                    ?>
                                </td>
                                <td><?= $hours ?> h</td>
                                <td><?= ($hours / 8) ?> dní</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" 
                                            data-bs-toggle="modal" 
                                            data-bs-target="#editAllowanceModal"
                                            data-user-id="<?= $user['id'] ?>"
                                            data-user-name="<?= htmlspecialchars($user['full_name']) ?>"
                                            data-hours="<?= $hours ?>">
                                        <i class="bi bi-pencil"></i> Upravit
                                    </button>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal pro úpravu přídělu -->
<div class="modal fade" id="editAllowanceModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">Upravit příděl dovolené</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <form action="update_allowance.php" method="POST">
                <div class="modal-body">
                    <input type="hidden" name="user_id" id="editUserId">
                    <div class="mb-3">
                        <label class="form-label">Uživatel:</label>
                        <p class="fw-bold" id="editUserName"></p>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Počet hodin za kalendářní rok</label>
                        <input type="number" class="form-control" name="hours" id="editHours" min="0" step="8" required>
                        <small class="text-muted">Výchozí: 160 hodin (20 dní)</small>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Odpovídá dnům:</label>
                        <p class="fw-bold text-primary"><span id="daysCalculated">0</span> dní</p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                    <button type="submit" class="btn btn-primary">Uložit</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Modal pro zamítnutí s důvodem -->
<div class="modal fade" id="rejectModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <form action="process_vacation.php" method="POST" id="rejectForm">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title">Zamítnutí žádosti o dovolenou</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" name="vacation_id" id="rejectVacationId">
                    <input type="hidden" name="action" value="reject">
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> Pozor! Tato akce zamítne žádost a uživatel bude informován.
                    </div>
                    <div class="mb-3">
                        <label class="form-label fw-bold">Důvod zamítnutí *</label>
                        <textarea class="form-control" name="reject_reason" id="rejectReason" 
                                  rows="4" required placeholder="Uveďte důvod zamítnutí žádosti..."></textarea>
                        <small class="text-muted">Tento důvod uvidí uživatel.</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                    <button type="submit" class="btn btn-danger">
                        <i class="bi bi-x-circle"></i> Zamítnout žádost
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Modal pro schválení s úpravou -->
<div class="modal fade" id="approveWithChangesModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <form action="process_vacation.php" method="POST" id="approveWithChangesForm">
                <div class="modal-header bg-warning text-dark">
                    <h5 class="modal-title">Schválení s úpravou termínu</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" name="vacation_id" id="modifyVacationId">
                    <input type="hidden" name="action" value="approve_with_changes">
                    
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle"></i> Upravte termín dovolené podle potřeby.
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label fw-bold">Původní žádost:</label>
                        <p class="mb-0" id="originalDates"></p>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Nové datum od *</label>
                            <input type="date" class="form-control" name="new_start_date" id="newStartDate" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Nové datum do *</label>
                            <input type="date" class="form-control" name="new_end_date" id="newEndDate" required>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Poznámka ke změně (volitelné)</label>
                        <textarea class="form-control" name="change_note" id="changeNote" 
                                  rows="3" placeholder="Důvod úpravy termínu..."></textarea>
                        <small class="text-muted">Uživatel uvidí tuto poznámku.</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zrušit</button>
                    <button type="submit" class="btn btn-warning">
                        <i class="bi bi-pencil"></i> Schválit s úpravou
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
    // Schválení bez úpravy
    function approveVacation(id, startDate, endDate) {
        if (confirm('Opravdu chcete schválit tuto žádost?')) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = 'process_vacation.php';
            
            const idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'vacation_id';
            idInput.value = id;
            
            const actionInput = document.createElement('input');
            actionInput.type = 'hidden';
            actionInput.name = 'action';
            actionInput.value = 'approve';
            
            form.appendChild(idInput);
            form.appendChild(actionInput);
            document.body.appendChild(form);
            form.submit();
        }
    }
    
    // Zamítnutí s důvodem
    function rejectVacation(id) {
        document.getElementById('rejectVacationId').value = id;
        document.getElementById('rejectReason').value = '';
        const modal = new bootstrap.Modal(document.getElementById('rejectModal'));
        modal.show();
    }
    
    // Schválení s úpravou
    function approveWithChanges(id, startDate, endDate) {
        document.getElementById('modifyVacationId').value = id;
        document.getElementById('newStartDate').value = startDate;
        document.getElementById('newEndDate').value = endDate;
        document.getElementById('changeNote').value = '';
        
        const start = new Date(startDate).toLocaleDateString('cs-CZ');
        const end = new Date(endDate).toLocaleDateString('cs-CZ');
        document.getElementById('originalDates').textContent = `${start} - ${end}`;
        
        const modal = new bootstrap.Modal(document.getElementById('approveWithChangesModal'));
        modal.show();
    }
    
    // Modal pro editaci přídělu
    const editModal = document.getElementById('editAllowanceModal');
    editModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const userId = button.getAttribute('data-user-id');
        const userName = button.getAttribute('data-user-name');
        const hours = button.getAttribute('data-hours');
        
        document.getElementById('editUserId').value = userId;
        document.getElementById('editUserName').textContent = userName;
        document.getElementById('editHours').value = hours;
        document.getElementById('daysCalculated').textContent = (hours / 8);
    });
    
    // Kalkulace dnů
    document.getElementById('editHours').addEventListener('input', function() {
        const days = this.value / 8;
        document.getElementById('daysCalculated').textContent = days.toFixed(1);
    });
</script>

</body>
</html>
