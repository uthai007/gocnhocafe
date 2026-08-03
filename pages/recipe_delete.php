<?php
$id = (int) ($_GET['id'] ?? 0);
if ($id) {
    $stmt = $pdo->prepare('DELETE FROM recipes WHERE id = ?');
    $stmt->execute([$id]);
    set_flash('success', 'Đã xoá công thức.');
}
redirect('recipes');
