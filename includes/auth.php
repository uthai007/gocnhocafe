<?php
// ============================================================
// Authentication & authorization helpers
// ============================================================

function is_logged_in()
{
    return !empty($_SESSION['user_id']);
}

function current_user()
{
    if (!is_logged_in()) {
        return null;
    }
    return [
        'id' => $_SESSION['user_id'],
        'name' => $_SESSION['user_name'],
        'role' => $_SESSION['user_role'],
    ];
}

function is_admin()
{
    return is_logged_in() && $_SESSION['user_role'] === 'admin';
}

function require_login()
{
    if (!is_logged_in()) {
        redirect('login');
    }
}

function require_admin()
{
    require_login();
    if (!is_admin()) {
        set_flash('error', 'Bạn không có quyền truy cập trang này.');
        redirect('dashboard');
    }
}

function attempt_login(PDO $pdo, $username, $password)
{
    $stmt = $pdo->prepare('SELECT * FROM users WHERE username = ? AND active = 1 LIMIT 1');
    $stmt->execute([$username]);
    $user = $stmt->fetch();

    if ($user && password_verify($password, $user['password'])) {
        session_regenerate_id(true);
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['user_name'] = $user['full_name'];
        $_SESSION['user_role'] = $user['role'];
        return true;
    }
    return false;
}

function do_logout()
{
    $_SESSION = [];
    session_destroy();
}
