<?php
$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if ($username === '' || $password === '') {
        $error = 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.';
    } elseif (attempt_login($pdo, $username, $password)) {
        redirect('dashboard');
    } else {
        $error = 'Tên đăng nhập hoặc mật khẩu không đúng.';
    }
}
?>
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Đăng nhập - <?= e(APP_NAME) ?></title>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body class="login-body">
<div class="login-box">
    <h1>☕ <?= e(APP_NAME) ?></h1>
    <p class="login-sub">Đăng nhập để tiếp tục</p>
    <?php if ($error): ?>
        <div class="alert alert-error"><?= e($error) ?></div>
    <?php endif; ?>
    <form method="post" action="index.php?page=login">
        <?= csrf_field() ?>
        <label>Tên đăng nhập</label>
        <input type="text" name="username" required autofocus>
        <label>Mật khẩu</label>
        <input type="password" name="password" required>
        <button type="submit" class="btn btn-primary btn-block">Đăng nhập</button>
    </form>
</div>
</body>
</html>
