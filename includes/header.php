<?php $user = current_user(); ?>
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title><?= e(APP_NAME) ?></title>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="app">
    <header class="topbar">
        <button class="menu-toggle" id="menuToggle" aria-label="Menu">&#9776;</button>
        <div class="topbar-title">☕ <?= e(APP_NAME) ?></div>
        <?php if ($user): ?>
        <div class="topbar-user">
            <span><?= e($user['name']) ?> (<?= $user['role'] === 'admin' ? 'Quản lý' : 'Nhân viên' ?>)</span>
            <a href="index.php?page=logout" class="btn-logout">Đăng xuất</a>
        </div>
        <?php endif; ?>
    </header>
    <div class="app-body">
