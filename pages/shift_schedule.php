<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $action = $_POST['action'] ?? '';

    if ($action === 'add' && is_admin()) {
        $staffId = (int) ($_POST['staff_id'] ?? 0);
        $shiftDate = $_POST['shift_date'] ?? '';
        $shiftType = $_POST['shift_type'] ?? 'sang';
        $startTime = $_POST['start_time'] ?? null;
        $endTime = $_POST['end_time'] ?? null;
        $note = trim($_POST['note'] ?? '');

        if ($staffId && $shiftDate) {
            $stmt = $pdo->prepare('INSERT INTO shifts (staff_id, shift_date, shift_type, start_time, end_time, note) VALUES (?,?,?,?,?,?)');
            $stmt->execute([$staffId, $shiftDate, $shiftType, $startTime ?: null, $endTime ?: null, $note]);
            set_flash('success', 'Đã thêm ca làm việc.');
        } else {
            set_flash('error', 'Vui lòng chọn nhân viên và ngày làm.');
        }
    } elseif ($action === 'delete' && is_admin()) {
        $stmt = $pdo->prepare('DELETE FROM shifts WHERE id = ?');
        $stmt->execute([(int) ($_POST['shift_id'] ?? 0)]);
        set_flash('success', 'Đã xoá ca làm việc.');
    }
    redirect('shift_schedule', isset($_GET['week']) ? ['week' => $_GET['week']] : []);
}

$weekStart = isset($_GET['week']) ? $_GET['week'] : date('Y-m-d', strtotime('monday this week'));
$weekStartTs = strtotime($weekStart);
$days = [];
for ($i = 0; $i < 7; $i++) {
    $days[] = date('Y-m-d', strtotime("+$i day", $weekStartTs));
}
$prevWeek = date('Y-m-d', strtotime('-7 day', $weekStartTs));
$nextWeek = date('Y-m-d', strtotime('+7 day', $weekStartTs));

$stmt = $pdo->prepare("SELECT s.*, u.full_name FROM shifts s JOIN users u ON u.id = s.staff_id
    WHERE s.shift_date BETWEEN ? AND ?
    ORDER BY s.shift_date, FIELD(s.shift_type,'sang','chieu','toi')");
$stmt->execute([$days[0], $days[6]]);
$shifts = $stmt->fetchAll();

$byDate = [];
foreach ($shifts as $shift) {
    $byDate[$shift['shift_date']][] = $shift;
}

$staffList = $pdo->query("SELECT id, full_name FROM users WHERE active = 1 ORDER BY full_name")->fetchAll();
$dayLabels = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật'];
?>
<div class="page-header">
    <h1 class="page-title">Lịch làm ca</h1>
    <div class="page-actions">
        <a href="index.php?page=shift_schedule&week=<?= e($prevWeek) ?>" class="btn btn-secondary">&larr; Tuần trước</a>
        <a href="index.php?page=shift_schedule&week=<?= e($nextWeek) ?>" class="btn btn-secondary">Tuần sau &rarr;</a>
    </div>
</div>

<?php if (is_admin()): ?>
<div class="card card-form">
    <h2>Thêm ca làm việc</h2>
    <form method="post">
        <?= csrf_field() ?>
        <input type="hidden" name="action" value="add">
        <div class="form-row">
            <div>
                <label>Nhân viên</label>
                <select name="staff_id" required>
                    <option value="">-- Chọn --</option>
                    <?php foreach ($staffList as $s): ?>
                        <option value="<?= (int) $s['id'] ?>"><?= e($s['full_name']) ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div>
                <label>Ngày</label>
                <input type="date" name="shift_date" required>
            </div>
            <div>
                <label>Ca</label>
                <select name="shift_type">
                    <option value="sang">Ca sáng</option>
                    <option value="chieu">Ca chiều</option>
                    <option value="toi">Ca tối</option>
                </select>
            </div>
            <div>
                <label>Bắt đầu</label>
                <input type="time" name="start_time">
            </div>
            <div>
                <label>Kết thúc</label>
                <input type="time" name="end_time">
            </div>
        </div>
        <label>Ghi chú</label>
        <input type="text" name="note">
        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Thêm ca</button>
        </div>
    </form>
</div>
<?php endif; ?>

<div class="schedule-grid">
    <?php foreach ($days as $i => $day): ?>
    <div class="schedule-day">
        <div class="schedule-day-header"><?= $dayLabels[$i] ?><br><span class="muted"><?= format_date($day) ?></span></div>
        <?php foreach (($byDate[$day] ?? []) as $shift): ?>
            <div class="schedule-shift">
                <strong><?= e($shift['full_name']) ?></strong>
                <div class="muted"><?= shift_type_label($shift['shift_type']) ?>
                    <?php if ($shift['start_time']): ?>(<?= e(substr($shift['start_time'], 0, 5)) ?>-<?= e(substr($shift['end_time'] ?? '', 0, 5)) ?>)<?php endif; ?>
                </div>
                <?php if ($shift['note']): ?><div class="muted"><?= e($shift['note']) ?></div><?php endif; ?>
                <?php if (is_admin()): ?>
                <form method="post" onsubmit="return confirm('Xoá ca này?')">
                    <?= csrf_field() ?>
                    <input type="hidden" name="action" value="delete">
                    <input type="hidden" name="shift_id" value="<?= (int) $shift['id'] ?>">
                    <button type="submit" class="btn btn-xs btn-danger">Xoá</button>
                </form>
                <?php endif; ?>
            </div>
        <?php endforeach; ?>
    </div>
    <?php endforeach; ?>
</div>
