<?php
$user = current_user();

// Today's order stats
$stmt = $pdo->prepare("SELECT COUNT(*) AS cnt, COALESCE(SUM(total_amount),0) AS total
    FROM orders WHERE status = 'completed' AND DATE(created_at) = CURDATE()");
$stmt->execute();
$todayStats = $stmt->fetch();

// Low stock ingredients
$lowStock = $pdo->query("SELECT * FROM ingredients WHERE quantity <= low_stock_threshold ORDER BY quantity ASC")->fetchAll();

// Today's shifts
$shiftStmt = $pdo->prepare("SELECT s.*, u.full_name FROM shifts s
    JOIN users u ON u.id = s.staff_id
    WHERE s.shift_date = CURDATE()
    ORDER BY FIELD(s.shift_type,'sang','chieu','toi')");
$shiftStmt->execute();
$todayShifts = $shiftStmt->fetchAll();

// Top selling items this week
$topStmt = $pdo->query("SELECT recipe_name, SUM(quantity) AS qty FROM order_items oi
    JOIN orders o ON o.id = oi.order_id
    WHERE o.status = 'completed' AND o.created_at >= (CURDATE() - INTERVAL 7 DAY)
    GROUP BY recipe_name ORDER BY qty DESC LIMIT 5");
$topItems = $topStmt->fetchAll();
?>
<h1 class="page-title">Xin chào, <?= e($user['name']) ?> 👋</h1>

<div class="stat-grid">
    <div class="stat-card">
        <div class="stat-value"><?= (int) $todayStats['cnt'] ?></div>
        <div class="stat-label">Đơn hàng hôm nay</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?= format_money($todayStats['total']) ?></div>
        <div class="stat-label">Doanh thu hôm nay</div>
    </div>
    <div class="stat-card <?= count($lowStock) ? 'stat-warning' : '' ?>">
        <div class="stat-value"><?= count($lowStock) ?></div>
        <div class="stat-label">Nguyên liệu sắp hết</div>
    </div>
    <div class="stat-card">
        <div class="stat-value"><?= count($todayShifts) ?></div>
        <div class="stat-label">Ca làm hôm nay</div>
    </div>
</div>

<div class="grid-2">
    <div class="card">
        <h2>⚠️ Nguyên liệu sắp hết</h2>
        <?php if (empty($lowStock)): ?>
            <p class="muted">Không có nguyên liệu nào dưới ngưỡng cảnh báo.</p>
        <?php else: ?>
        <table class="table">
            <thead><tr><th>Tên</th><th>Tồn kho</th><th>Ngưỡng</th></tr></thead>
            <tbody>
            <?php foreach ($lowStock as $item): ?>
                <tr>
                    <td><?= e($item['name']) ?></td>
                    <td class="text-danger"><?= (float) $item['quantity'] ?> <?= e($item['unit']) ?></td>
                    <td><?= (float) $item['low_stock_threshold'] ?> <?= e($item['unit']) ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
        <?php endif; ?>
    </div>

    <div class="card">
        <h2>🗓️ Ca làm hôm nay</h2>
        <?php if (empty($todayShifts)): ?>
            <p class="muted">Chưa có ca làm nào được xếp cho hôm nay.</p>
        <?php else: ?>
        <table class="table">
            <thead><tr><th>Nhân viên</th><th>Ca</th><th>Giờ</th></tr></thead>
            <tbody>
            <?php foreach ($todayShifts as $shift): ?>
                <tr>
                    <td><?= e($shift['full_name']) ?></td>
                    <td><?= shift_type_label($shift['shift_type']) ?></td>
                    <td><?= e(substr($shift['start_time'] ?? '', 0, 5)) ?> - <?= e(substr($shift['end_time'] ?? '', 0, 5)) ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
        <?php endif; ?>
    </div>
</div>

<div class="card">
    <h2>🔥 Bán chạy 7 ngày qua</h2>
    <?php if (empty($topItems)): ?>
        <p class="muted">Chưa có dữ liệu đơn hàng.</p>
    <?php else: ?>
    <table class="table">
        <thead><tr><th>Món</th><th>Số lượng bán</th></tr></thead>
        <tbody>
        <?php foreach ($topItems as $item): ?>
            <tr><td><?= e($item['recipe_name']) ?></td><td><?= (int) $item['qty'] ?></td></tr>
        <?php endforeach; ?>
        </tbody>
    </table>
    <?php endif; ?>
</div>
