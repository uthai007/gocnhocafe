<?php
$items = $pdo->query("SELECT * FROM ingredients ORDER BY name ASC")->fetchAll();
?>
<div class="page-header">
    <h1 class="page-title">Kho nguyên liệu</h1>
    <?php if (is_admin()): ?>
    <div class="page-actions">
        <a href="index.php?page=stock_transactions" class="btn btn-secondary">Lịch sử xuất/nhập</a>
        <a href="index.php?page=stock_form" class="btn btn-primary">+ Thêm nguyên liệu</a>
    </div>
    <?php endif; ?>
</div>

<div class="card">
<table class="table">
    <thead>
        <tr>
            <th>Tên nguyên liệu</th>
            <th>Tồn kho</th>
            <th>Ngưỡng cảnh báo</th>
            <th>Cập nhật lúc</th>
            <?php if (is_admin()): ?><th>Hành động</th><?php endif; ?>
        </tr>
    </thead>
    <tbody>
    <?php foreach ($items as $item): ?>
        <?php $low = $item['quantity'] <= $item['low_stock_threshold']; ?>
        <tr class="<?= $low ? 'row-warning' : '' ?>">
            <td>
                <?= e($item['name']) ?>
                <?php if ($low): ?><span class="badge badge-danger">Sắp hết</span><?php endif; ?>
            </td>
            <td><?= (float) $item['quantity'] ?> <?= e($item['unit']) ?></td>
            <td><?= (float) $item['low_stock_threshold'] ?> <?= e($item['unit']) ?></td>
            <td><?= format_date($item['updated_at'], true) ?></td>
            <?php if (is_admin()): ?>
            <td class="actions">
                <a href="index.php?page=stock_form&id=<?= (int) $item['id'] ?>" class="btn btn-sm btn-secondary">Sửa</a>
                <a href="index.php?page=stock_delete&id=<?= (int) $item['id'] ?>" class="btn btn-sm btn-danger" onclick="return confirm('Xoá nguyên liệu này?')">Xoá</a>
            </td>
            <?php endif; ?>
        </tr>
    <?php endforeach; ?>
    <?php if (empty($items)): ?>
        <tr><td colspan="5" class="muted">Chưa có nguyên liệu nào.</td></tr>
    <?php endif; ?>
    </tbody>
</table>
</div>
