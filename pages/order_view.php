<?php
$id = (int) ($_GET['id'] ?? 0);

if ($_SERVER['REQUEST_METHOD'] === 'POST' && is_admin()) {
    verify_csrf();
    if (($_POST['action'] ?? '') === 'cancel') {
        $stmt = $pdo->prepare("UPDATE orders SET status = 'cancelled' WHERE id = ?");
        $stmt->execute([$id]);
        set_flash('success', 'Đã huỷ đơn hàng. Lưu ý: nguyên liệu đã trừ sẽ không tự động hoàn kho, vui lòng điều chỉnh thủ công tại Kho nguyên liệu nếu cần.');
        redirect('order_view', ['id' => $id]);
    }
}

$stmt = $pdo->prepare("SELECT o.*, u.full_name FROM orders o LEFT JOIN users u ON u.id = o.staff_id WHERE o.id = ?");
$stmt->execute([$id]);
$order = $stmt->fetch();

if (!$order) {
    set_flash('error', 'Không tìm thấy đơn hàng.');
    redirect('orders');
}

$stmt = $pdo->prepare('SELECT * FROM order_items WHERE order_id = ?');
$stmt->execute([$id]);
$items = $stmt->fetchAll();
?>
<div class="page-header">
    <h1 class="page-title">Đơn hàng <?= e($order['order_code']) ?></h1>
    <a href="index.php?page=orders" class="btn btn-secondary">&larr; Về danh sách</a>
</div>

<div class="card">
    <p><strong>Thời gian:</strong> <?= format_date($order['created_at'], true) ?></p>
    <p><strong>Nhân viên:</strong> <?= e($order['full_name'] ?? '—') ?></p>
    <p><strong>Trạng thái:</strong> <span class="badge <?= $order['status'] === 'completed' ? 'badge-success' : 'badge-danger' ?>"><?= $order['status'] === 'completed' ? 'Hoàn thành' : 'Đã huỷ' ?></span></p>
    <?php if ($order['note']): ?><p><strong>Ghi chú:</strong> <?= e($order['note']) ?></p><?php endif; ?>

    <table class="table">
        <thead><tr><th>Món</th><th>Số lượng</th><th>Đơn giá</th><th>Thành tiền</th></tr></thead>
        <tbody>
        <?php foreach ($items as $item): ?>
            <tr>
                <td><?= e($item['recipe_name']) ?></td>
                <td><?= (int) $item['quantity'] ?></td>
                <td><?= format_money($item['unit_price']) ?></td>
                <td><?= format_money($item['subtotal']) ?></td>
            </tr>
        <?php endforeach; ?>
        </tbody>
        <tfoot>
            <tr><th colspan="3">Tổng cộng</th><th><?= format_money($order['total_amount']) ?></th></tr>
        </tfoot>
    </table>

    <?php if (is_admin() && $order['status'] === 'completed'): ?>
    <form method="post" onsubmit="return confirm('Huỷ đơn hàng này?')">
        <?= csrf_field() ?>
        <input type="hidden" name="action" value="cancel">
        <button type="submit" class="btn btn-danger">Huỷ đơn hàng</button>
    </form>
    <?php endif; ?>
</div>
