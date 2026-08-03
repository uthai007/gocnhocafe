<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST' && is_admin()) {
    verify_csrf();
    $ingredientId = (int) ($_POST['ingredient_id'] ?? 0);
    $type = $_POST['type'] ?? 'import';
    $amount = (float) ($_POST['amount'] ?? 0);
    $note = trim($_POST['note'] ?? '');

    $validTypes = ['import', 'export', 'adjustment'];
    if ($ingredientId && $amount > 0 && in_array($type, $validTypes, true)) {
        $changeAmount = $type === 'export' ? -$amount : $amount;

        $pdo->beginTransaction();
        $stmt = $pdo->prepare('UPDATE ingredients SET quantity = quantity + ? WHERE id = ?');
        $stmt->execute([$changeAmount, $ingredientId]);

        $stmt = $pdo->prepare('INSERT INTO stock_transactions (ingredient_id, type, change_amount, note, created_by) VALUES (?,?,?,?,?)');
        $stmt->execute([$ingredientId, $type, $changeAmount, $note, current_user()['id']]);
        $pdo->commit();

        set_flash('success', 'Đã ghi nhận giao dịch kho.');
    } else {
        set_flash('error', 'Vui lòng nhập đầy đủ thông tin hợp lệ.');
    }
    redirect('stock_transactions');
}

$ingredients = $pdo->query("SELECT id, name, unit FROM ingredients ORDER BY name ASC")->fetchAll();

$history = $pdo->query("SELECT t.*, i.name AS ingredient_name, i.unit, u.full_name
    FROM stock_transactions t
    JOIN ingredients i ON i.id = t.ingredient_id
    LEFT JOIN users u ON u.id = t.created_by
    ORDER BY t.created_at DESC LIMIT 100")->fetchAll();

$typeLabels = ['import' => 'Nhập kho', 'export' => 'Xuất kho', 'adjustment' => 'Điều chỉnh', 'order_deduct' => 'Trừ theo đơn hàng'];
?>
<div class="page-header">
    <h1 class="page-title">Lịch sử xuất / nhập kho</h1>
    <a href="index.php?page=stock" class="btn btn-secondary">&larr; Về kho nguyên liệu</a>
</div>

<?php if (is_admin()): ?>
<div class="card card-form">
    <h2>Ghi nhận giao dịch mới</h2>
    <form method="post">
        <?= csrf_field() ?>
        <div class="form-row">
            <div>
                <label>Nguyên liệu</label>
                <select name="ingredient_id" required>
                    <option value="">-- Chọn --</option>
                    <?php foreach ($ingredients as $ing): ?>
                        <option value="<?= (int) $ing['id'] ?>"><?= e($ing['name']) ?> (<?= e($ing['unit']) ?>)</option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div>
                <label>Loại giao dịch</label>
                <select name="type" required>
                    <option value="import">Nhập kho (+)</option>
                    <option value="export">Xuất kho (-)</option>
                    <option value="adjustment">Điều chỉnh (+)</option>
                </select>
            </div>
            <div>
                <label>Số lượng</label>
                <input type="number" step="0.01" min="0.01" name="amount" required>
            </div>
        </div>
        <label>Ghi chú</label>
        <input type="text" name="note" placeholder="VD: Nhập hàng từ nhà cung cấp...">
        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Ghi nhận</button>
        </div>
    </form>
</div>
<?php endif; ?>

<div class="card">
    <table class="table">
        <thead><tr><th>Thời gian</th><th>Nguyên liệu</th><th>Loại</th><th>Thay đổi</th><th>Người thực hiện</th><th>Ghi chú</th></tr></thead>
        <tbody>
        <?php foreach ($history as $h): ?>
            <tr>
                <td><?= format_date($h['created_at'], true) ?></td>
                <td><?= e($h['ingredient_name']) ?></td>
                <td><?= e($typeLabels[$h['type']] ?? $h['type']) ?></td>
                <td class="<?= $h['change_amount'] < 0 ? 'text-danger' : 'text-success' ?>">
                    <?= $h['change_amount'] > 0 ? '+' : '' ?><?= (float) $h['change_amount'] ?> <?= e($h['unit']) ?>
                </td>
                <td><?= e($h['full_name'] ?? '—') ?></td>
                <td><?= e($h['note']) ?></td>
            </tr>
        <?php endforeach; ?>
        <?php if (empty($history)): ?>
            <tr><td colspan="6" class="muted">Chưa có giao dịch nào.</td></tr>
        <?php endif; ?>
        </tbody>
    </table>
</div>
