<?php
$from = $_GET['from'] ?? date('Y-m-d', strtotime('-6 day'));
$to = $_GET['to'] ?? date('Y-m-d');

$stmt = $pdo->prepare("SELECT DATE(created_at) AS d, COUNT(*) AS cnt, SUM(total_amount) AS total
    FROM orders WHERE status = 'completed' AND DATE(created_at) BETWEEN ? AND ?
    GROUP BY DATE(created_at) ORDER BY d ASC");
$stmt->execute([$from, $to]);
$byDay = $stmt->fetchAll();

$totalOrders = array_sum(array_column($byDay, 'cnt'));
$totalRevenue = array_sum(array_column($byDay, 'total'));

$stmt = $pdo->prepare("SELECT oi.recipe_name, SUM(oi.quantity) AS qty, SUM(oi.subtotal) AS revenue
    FROM order_items oi JOIN orders o ON o.id = oi.order_id
    WHERE o.status = 'completed' AND DATE(o.created_at) BETWEEN ? AND ?
    GROUP BY oi.recipe_name ORDER BY qty DESC LIMIT 10");
$stmt->execute([$from, $to]);
$topItems = $stmt->fetchAll();
?>
<h1 class="page-title">Báo cáo doanh thu &amp; đơn hàng</h1>

<form method="get" class="card card-form inline-form">
    <input type="hidden" name="page" value="reports_daily">
    <label>Từ ngày</label>
    <input type="date" name="from" value="<?= e($from) ?>">
    <label>Đến ngày</label>
    <input type="date" name="to" value="<?= e($to) ?>">
    <button type="submit" class="btn btn-primary">Lọc</button>
</form>

<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-value"><?= (int) $totalOrders ?></div>
        <div class="stat-label">Tổng số đơn</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?= format_money($totalRevenue) ?></div>
        <div class="stat-label">Tổng doanh thu</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?= $totalOrders ? format_money($totalRevenue / $totalOrders) : format_money(0) ?></div>
        <div class="stat-label">Giá trị đơn trung bình</div>
    </div>
</div>

<div class="grid-2">
    <div class="card">
        <h2>Theo ngày</h2>
        <table class="table">
            <thead><tr><th>Ngày</th><th>Số đơn</th><th>Doanh thu</th></tr></thead>
            <tbody>
            <?php foreach ($byDay as $row): ?>
                <tr><td><?= format_date($row['d']) ?></td><td><?= (int) $row['cnt'] ?></td><td><?= format_money($row['total']) ?></td></tr>
            <?php endforeach; ?>
            <?php if (empty($byDay)): ?><tr><td colspan="3" class="muted">Không có dữ liệu.</td></tr><?php endif; ?>
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>Món bán chạy</h2>
        <table class="table">
            <thead><tr><th>Món</th><th>SL bán</th><th>Doanh thu</th></tr></thead>
            <tbody>
            <?php foreach ($topItems as $row): ?>
                <tr><td><?= e($row['recipe_name']) ?></td><td><?= (int) $row['qty'] ?></td><td><?= format_money($row['revenue']) ?></td></tr>
            <?php endforeach; ?>
            <?php if (empty($topItems)): ?><tr><td colspan="3" class="muted">Không có dữ liệu.</td></tr><?php endif; ?>
            </tbody>
        </table>
    </div>
</div>
