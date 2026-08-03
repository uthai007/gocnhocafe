<?php
$user = current_user();
$date = $_GET['date'] ?? date('Y-m-d');
$shiftId = isset($_GET['shift_id']) ? (int) $_GET['shift_id'] : 0;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $shiftId = (int) ($_POST['shift_id'] ?? 0);
    $templateId = (int) ($_POST['template_id'] ?? 0);

    // Ownership check: staff can only tick their own shift's checklist
    $stmt = $pdo->prepare('SELECT * FROM shifts WHERE id = ?');
    $stmt->execute([$shiftId]);
    $shift = $stmt->fetch();

    if ($shift && ($shift['staff_id'] == $user['id'] || $user['role'] === 'admin')) {
        $stmt = $pdo->prepare('SELECT * FROM checklist_completions WHERE shift_id = ? AND template_id = ?');
        $stmt->execute([$shiftId, $templateId]);
        $existing = $stmt->fetch();

        $newState = $existing ? (1 - $existing['is_done']) : 1;

        if ($existing) {
            $stmt = $pdo->prepare('UPDATE checklist_completions SET is_done = ?, completed_by = ?, completed_at = ? WHERE id = ?');
            $stmt->execute([$newState, $user['id'], $newState ? date('Y-m-d H:i:s') : null, $existing['id']]);
        } else {
            $stmt = $pdo->prepare('INSERT INTO checklist_completions (shift_id, template_id, is_done, completed_by, completed_at) VALUES (?,?,?,?,?)');
            $stmt->execute([$shiftId, $templateId, $newState, $user['id'], $newState ? date('Y-m-d H:i:s') : null]);
        }
    }
    redirect('checklist', ['date' => $date, 'shift_id' => $shiftId]);
}

// Find candidate shifts for this date
if ($user['role'] === 'admin') {
    $stmt = $pdo->prepare("SELECT s.*, u.full_name FROM shifts s JOIN users u ON u.id = s.staff_id WHERE s.shift_date = ? ORDER BY FIELD(s.shift_type,'sang','chieu','toi')");
    $stmt->execute([$date]);
} else {
    $stmt = $pdo->prepare("SELECT s.*, u.full_name FROM shifts s JOIN users u ON u.id = s.staff_id WHERE s.shift_date = ? AND s.staff_id = ? ORDER BY FIELD(s.shift_type,'sang','chieu','toi')");
    $stmt->execute([$date, $user['id']]);
}
$candidateShifts = $stmt->fetchAll();

if (!$shiftId && count($candidateShifts) === 1) {
    $shiftId = $candidateShifts[0]['id'];
}

$activeShift = null;
foreach ($candidateShifts as $s) {
    if ($s['id'] == $shiftId) {
        $activeShift = $s;
        break;
    }
}
?>
<div class="page-header">
    <h1 class="page-title">Checklist ca làm</h1>
    <form method="get" class="inline-form">
        <input type="hidden" name="page" value="checklist">
        <input type="date" name="date" value="<?= e($date) ?>" onchange="this.form.submit()">
    </form>
</div>

<?php if (empty($candidateShifts)): ?>
    <div class="card"><p class="muted">Không có ca làm nào vào ngày này.</p></div>
<?php elseif (!$activeShift): ?>
    <div class="card">
        <h2>Chọn ca làm việc</h2>
        <ul class="plain-list">
        <?php foreach ($candidateShifts as $s): ?>
            <li><a href="index.php?page=checklist&date=<?= e($date) ?>&shift_id=<?= (int) $s['id'] ?>"><?= e($s['full_name']) ?> - <?= shift_type_label($s['shift_type']) ?></a></li>
        <?php endforeach; ?>
        </ul>
    </div>
<?php else: ?>
    <?php
    $stmt = $pdo->prepare("SELECT c.*, cc.is_done, cc.completed_at, cc.completed_by
        FROM checklist_templates c
        LEFT JOIN checklist_completions cc ON cc.template_id = c.id AND cc.shift_id = ?
        WHERE c.checklist_type = ? AND c.active = 1
        ORDER BY c.sort_order");

    $stmt->execute([$activeShift['id'], 'open']);
    $openItems = $stmt->fetchAll();

    $stmt->execute([$activeShift['id'], 'close']);
    $closeItems = $stmt->fetchAll();

    function render_checklist_section($items, $shiftId)
    {
        if (empty($items)) {
            echo '<p class="muted">Chưa có mục nào.</p>';
            return;
        }
        echo '<ul class="checklist-list">';
        foreach ($items as $item) {
            $checked = !empty($item['is_done']);
            echo '<li class="' . ($checked ? 'done' : '') . '">';
            echo '<form method="post" class="checklist-form">';
            echo csrf_field();
            echo '<input type="hidden" name="shift_id" value="' . (int) $shiftId . '">';
            echo '<input type="hidden" name="template_id" value="' . (int) $item['id'] . '">';
            echo '<button type="submit" class="checklist-check">' . ($checked ? '✅' : '⬜') . '</button>';
            echo '<span>' . e($item['item_name']) . '</span>';
            echo '</form></li>';
        }
        echo '</ul>';
    }
    ?>
    <div class="card">
        <h2><?= e($activeShift['full_name']) ?> - <?= shift_type_label($activeShift['shift_type']) ?> - <?= format_date($activeShift['shift_date']) ?></h2>
    </div>

    <div class="grid-2">
        <div class="card">
            <h2>Đầu ca (mở cửa)</h2>
            <?php render_checklist_section($openItems, $activeShift['id']); ?>
        </div>
        <div class="card">
            <h2>Cuối ca (đóng cửa)</h2>
            <?php render_checklist_section($closeItems, $activeShift['id']); ?>
        </div>
    </div>
<?php endif; ?>
