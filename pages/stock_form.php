<?php
$id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
$item = ['name' => '', 'unit' => 'g', 'quantity' => 0, 'low_stock_threshold' => 0, 'notes' => ''];

if ($id) {
    $stmt = $pdo->prepare('SELECT * FROM ingredients WHERE id = ?');
    $stmt->execute([$id]);
    $found = $stmt->fetch();
    if (!$found) {
        set_flash('error', 'Không tìm thấy nguyên liệu.');
        redirect('stock');
    }
    $item = $found;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $name = trim($_POST['name'] ?? '');
    $unit = trim($_POST['unit'] ?? '');
    $quantity = (float) ($_POST['quantity'] ?? 0);
    $threshold = (float) ($_POST['low_stock_threshold'] ?? 0);
    $notes = trim($_POST['notes'] ?? '');

    if ($name === '' || $unit === '') {
        set_flash('error', 'Vui lòng nhập tên và đơn vị tính.');
    } else {
        if ($id) {
            $stmt = $pdo->prepare('UPDATE ingredients SET name=?, unit=?, quantity=?, low_stock_threshold=?, notes=? WHERE id=?');
            $stmt->execute([$name, $unit, $quantity, $threshold, $notes, $id]);
            set_flash('success', 'Đã cập nhật nguyên liệu.');
        } else {
            $stmt = $pdo->prepare('INSERT INTO ingredients (name, unit, quantity, low_stock_threshold, notes) VALUES (?,?,?,?,?)');
            $stmt->execute([$name, $unit, $quantity, $threshold, $notes]);
            set_flash('success', 'Đã thêm nguyên liệu mới.');
        }
        redirect('stock');
    }
}
?>
<h1 class="page-title"><?= $id ? 'Sửa nguyên liệu' : 'Thêm nguyên liệu' ?></h1>

<div class="card card-form">
    <form method="post">
        <?= csrf_field() ?>
        <label>Tên nguyên liệu</label>
        <input type="text" name="name" value="<?= e($item['name']) ?>" required>

        <label>Đơn vị tính (g, ml, kg, l, cái...)</label>
        <input type="text" name="unit" value="<?= e($item['unit']) ?>" required>

        <label>Số lượng tồn kho</label>
        <input type="number" step="0.01" name="quantity" value="<?= e($item['quantity']) ?>" required>

        <label>Ngưỡng cảnh báo sắp hết</label>
        <input type="number" step="0.01" name="low_stock_threshold" value="<?= e($item['low_stock_threshold']) ?>" required>

        <label>Ghi chú</label>
        <textarea name="notes" rows="2"><?= e($item['notes']) ?></textarea>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Lưu</button>
            <a href="index.php?page=stock" class="btn btn-secondary">Huỷ</a>
        </div>
    </form>
</div>
