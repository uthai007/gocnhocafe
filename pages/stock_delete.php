<?php
$id = (int) ($_GET['id'] ?? 0);
if ($id) {
    $stmt = $pdo->prepare('DELETE FROM ingredients WHERE id = ?');
    $stmt->execute([$id]);
    set_flash('success', 'Đã xoá nguyên liệu.');
}
redirect('stock');
