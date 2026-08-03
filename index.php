<?php
// ============================================================
// Front controller - all requests go through index.php?page=xxx
// ============================================================

require_once __DIR__ . '/config/config.php';
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/auth.php';

$page = $_GET['page'] ?? 'dashboard';

// Map page key => [file, requiresAdmin]
$routes = [
    'login'               => ['pages/login.php', false],
    'dashboard'           => ['pages/dashboard.php', false],

    'stock'               => ['pages/stock_list.php', false],
    'stock_form'          => ['pages/stock_form.php', true],
    'stock_delete'        => ['pages/stock_delete.php', true],
    'stock_transactions'  => ['pages/stock_transactions.php', false],

    'recipes'             => ['pages/recipes_list.php', false],
    'recipe_form'         => ['pages/recipe_form.php', true],
    'recipe_view'         => ['pages/recipe_view.php', false],
    'recipe_delete'       => ['pages/recipe_delete.php', true],

    'orders'              => ['pages/orders_list.php', false],
    'order_new'           => ['pages/order_new.php', false],
    'order_view'          => ['pages/order_view.php', false],

    'checklist'           => ['pages/checklist.php', false],
    'checklist_templates' => ['pages/checklist_templates.php', true],

    'shift_schedule'      => ['pages/shift_schedule.php', false],

    'reports_daily'       => ['pages/reports_daily.php', true],

    'users'               => ['pages/users_list.php', true],
    'user_form'           => ['pages/user_form.php', true],
    'user_delete'         => ['pages/user_delete.php', true],
];

if ($page === 'logout') {
    do_logout();
    redirect('login');
}

if (!array_key_exists($page, $routes)) {
    $page = 'dashboard';
}

[$file, $needsAdmin] = $routes[$page];

if ($page !== 'login') {
    require_login();
}
if ($needsAdmin) {
    require_admin();
}

// Logged-in user visiting login page -> go to dashboard
if ($page === 'login' && is_logged_in()) {
    redirect('dashboard');
}

if ($page === 'login') {
    require __DIR__ . '/' . $file;
    exit;
}

require __DIR__ . '/includes/header.php';
require __DIR__ . '/includes/sidebar.php';
?>
<main class="content">
    <?php $flash = get_flash(); ?>
    <?php if ($flash): ?>
        <div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
    <?php endif; ?>
    <?php require __DIR__ . '/' . $file; ?>
</main>
<?php require __DIR__ . '/includes/footer.php'; ?>
