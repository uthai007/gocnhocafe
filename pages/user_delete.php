<?php
$id = (int) ($_GET['id'] ?? 0);
if ($id && $id !== current_user()['id']) {
    $stmt = $pdo->prepare('DELETE FROM users WHERE id = ?');
    $stmt->execute([$id]);
    set_flash('success', 'Đã xoá tài khoản.');
}
redirect('users');
