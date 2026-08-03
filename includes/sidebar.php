<?php
$current = $_GET['page'] ?? 'dashboard';
$isAdmin = is_admin();

function nav_link($page, $label, $icon, $current, $activePages = null)
{
    $activePages = $activePages ?? [$page];
    $active = in_array($current, $activePages, true) ? ' active' : '';
    echo '<a href="index.php?page=' . e($page) . '" class="nav-link' . $active . '"><span class="nav-icon">' . $icon . '</span>' . e($label) . '</a>';
}
?>
<nav class="sidebar" id="sidebar">
    <?php nav_link('dashboard', 'Tổng quan', '📊', $current); ?>
    <?php nav_link('stock', 'Kho nguyên liệu', '📦', $current, ['stock', 'stock_form', 'stock_transactions']); ?>
    <?php nav_link('recipes', 'Công thức / Menu', '📖', $current, ['recipes', 'recipe_form', 'recipe_view']); ?>
    <?php nav_link('orders', 'Đơn hàng', '🧾', $current, ['orders', 'order_new', 'order_view']); ?>
    <?php nav_link('checklist', 'Checklist ca làm', '✅', $current); ?>
    <?php nav_link('shift_schedule', 'Lịch làm ca', '🗓️', $current); ?>
    <?php if ($isAdmin): ?>
        <div class="nav-section">Quản lý</div>
        <?php nav_link('checklist_templates', 'Mẫu checklist', '📝', $current); ?>
        <?php nav_link('reports_daily', 'Báo cáo', '📈', $current); ?>
        <?php nav_link('users', 'Tài khoản nhân viên', '👥', $current, ['users', 'user_form']); ?>
    <?php endif; ?>
</nav>
