<?php
$date = $_GET['date'] ?? date('Y-m-d');

$stmt = $pdo->prepare("SELECT o.*, u.full_name FROM orders o
    LEFT JOIN users u ON u.id = o.staff_id
    WHERE DATE(o.created_at) = ?
    ORDER BY o.created_at DESC");
$stmt->execute([$date]);
$orders = $stmt->fetchAll();

$totalToday = array_sum(array_column(array_filter($orders, fn($o) => $o['status'] === 'completed'), 'total_amount'));
?>
<div class="page-header">
    <h1 class="page-title">Đơn hàng</h1>
    <div class="page-actions">
        <form method="get" class="inline-form">
            <input type="hidden" name="page" value="orders">
            <input type="date" name="date" value="<?= e($date) ?>" onchange="this.form.submit()">
        </form>
        <a href="index.php?page=order_new" class="btn btn-primary">+ Tạo đơn hàng</a>
    </div>
</div>

<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-value"><?= count($orders) ?></div>
        <div class="stat-label">Số đơn ngày <?= e(format_date($date)) ?></div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?= format_money($totalToday) ?></div>
        <div class="stat-label">Tổng doanh thu</div>
    </div>
</div>

<div class="card">
<table class="table">
    <thead><tr><th>Mã đơn</th><th>Giờ</th><th>Nhân viên</th><th>Tổng tiền</th><th>Trạng thái</th><th></th></tr></thead>
    <tbody>
    <?php foreach ($orders as $order): ?>
        <tr>
            <td><?= e($order['order_code']) ?></td>
            <td><?= date('H:i', strtotime($order['created_at'])) ?></td>
            <td><?= e($order['full_name'] ?? '—') ?></td>
            <td><?= format_money($order['total_amount']) ?></td>
            <td><span class="badge <?= $order['status'] === 'completed' ? 'badge-success' : 'badge-danger' ?>"><?= $order['status'] === 'completed' ? 'Hoàn thành' : 'Đã huỷ' ?></span></td>
            <td><a href="index.php?page=order_view&id=<?= (int) $order['id'] ?>" class="btn btn-sm btn-secondary">Chi tiết</a></td>
        </tr>
    <?php endforeach; ?>
    <?php if (empty($orders)): ?>
        <tr><td colspan="6" class="muted">Không có đơn hàng nào trong ngày này.</td></tr>
    <?php endif; ?>
    </tbody>
</table>
</div>
