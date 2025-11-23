<?php
// Seznamové zobrazení
$userVacations = [];
foreach ($vacations as $vac) {
    if (!$isAdmin && $vac['user_id'] != $userId) {
        continue;
    }
    $userVacations[] = $vac;
}

// Seřadit podle data
usort($userVacations, function($a, $b) {
    return strtotime($b['start_date']) - strtotime($a['start_date']);
});
?>

<div class="card">
    <div class="card-header bg-light">
        <h5 class="mb-0"><i class="bi bi-list-ul"></i> Seznam žádostí</h5>
    </div>
    <div class="card-body">
        <?php if (empty($userVacations)): ?>
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i> Zatím nemáte žádné záznamy o dovolené.
            </div>
        <?php else: ?>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Typ</th>
                            <?php if ($isAdmin): ?><th>Uživatel</th><?php endif; ?>
                            <th>Od</th>
                            <th>Do</th>
                            <th>Hodiny</th>
                            <th>Stav</th>
                            <?php if ($isAdmin): ?><th>Schválil</th><?php endif; ?>
                            <th>Poznámka</th>
                            <th>Akce</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($userVacations as $vac): 
                            $statusBadge = '';
                            $statusIcon = '';
                            if ($vac['status'] === 'approved') {
                                $statusBadge = 'bg-success';
                                $statusIcon = 'check-circle';
                            } elseif ($vac['status'] === 'pending') {
                                $statusBadge = 'bg-warning';
                                $statusIcon = 'clock';
                            } else {
                                $statusBadge = 'bg-danger';
                                $statusIcon = 'x-circle';
                            }
                            
                            $typeLabel = '';
                            if ($vac['type'] === 'vacation') $typeLabel = 'Dovolená';
                            elseif ($vac['type'] === 'paid_leave') $typeLabel = 'Placené volno';
                            else $typeLabel = 'Neplacené volno';
                        ?>
                        <tr>
                            <td>
                                <strong><?= $typeLabel ?></strong>
                                <?php if ($vac['half_day']): ?>
                                    <br><small class="text-muted">Půl dne (<?= $vac['half_day_period'] === 'morning' ? 'Dopoledne' : 'Odpoledne' ?>)</small>
                                <?php endif; ?>
                            </td>
                            <?php if ($isAdmin): ?>
                                <td><?= htmlspecialchars($vac['user_name']) ?></td>
                            <?php endif; ?>
                            <td><?= date('d.m.Y', strtotime($vac['start_date'])) ?></td>
                            <td><?= date('d.m.Y', strtotime($vac['end_date'])) ?></td>
                            <td>
                                <?= $vac['hours'] ?> h
                                <small class="text-muted">(<?= ($vac['hours'] / 8) ?> dní)</small>
                            </td>
                            <td>
                                <span class="badge <?= $statusBadge ?>">
                                    <i class="bi bi-<?= $statusIcon ?>"></i>
                                    <?php 
                                        if ($vac['status'] === 'approved') echo 'Schváleno';
                                        elseif ($vac['status'] === 'pending') echo 'Čeká na schválení';
                                        else echo 'Zamítnuto';
                                    ?>
                                </span>
                                <?php if (!empty($vac['modified'])): ?>
                                    <br><small class="badge bg-info">Upraveno</small>
                                <?php endif; ?>
                            </td>
                            <?php if ($isAdmin): ?>
                                <td>
                                    <?php if ($vac['approved_by']): ?>
                                        <small><?= htmlspecialchars($vac['approved_by_name']) ?></small>
                                    <?php else: ?>
                                        <small class="text-muted">-</small>
                                    <?php endif; ?>
                                </td>
                            <?php endif; ?>
                            <td>
                                <?php if (!empty($vac['reject_reason'])): ?>
                                    <div class="alert alert-danger alert-sm mb-0 p-2">
                                        <strong>Důvod zamítnutí:</strong><br>
                                        <small><?= htmlspecialchars($vac['reject_reason']) ?></small>
                                    </div>
                                <?php elseif (!empty($vac['modified']) && !empty($vac['change_note'])): ?>
                                    <div class="alert alert-warning alert-sm mb-0 p-2">
                                        <strong>Upraveno z:</strong><br>
                                        <small><?= date('d.m.Y', strtotime($vac['original_start_date'])) ?> - <?= date('d.m.Y', strtotime($vac['original_end_date'])) ?></small>
                                        <?php if ($vac['change_note']): ?>
                                            <br><small><?= htmlspecialchars($vac['change_note']) ?></small>
                                        <?php endif; ?>
                                    </div>
                                <?php elseif ($vac['note']): ?>
                                    <small><?= htmlspecialchars(substr($vac['note'], 0, 50)) ?></small>
                                <?php else: ?>
                                    <small class="text-muted">-</small>
                                <?php endif; ?>
                            </td>
                            <td>
                                <?php if ($vac['status'] === 'pending' && $vac['user_id'] == $userId): ?>
                                    <form action="cancel_vacation.php" method="POST" style="display: inline;" 
                                          onsubmit="return confirm('Opravdu chcete zrušit tuto žádost?');">
                                        <input type="hidden" name="vacation_id" value="<?= $vac['id'] ?>">
                                        <button type="submit" class="btn btn-sm btn-outline-danger">
                                            <i class="bi bi-trash"></i> Zrušit
                                        </button>
                                    </form>
                                <?php endif; ?>
                            </td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        <?php endif; ?>
    </div>
</div>
