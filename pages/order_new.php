<?php
$recipes = $pdo->query("SELECT id, name, price FROM recipes WHERE active = 1 ORDER BY category, name")->fetchAll();

function recipe_options($recipes, $selectedId = null)
{
    $html = '<option value="">-- Chọn món --</option>';
    foreach ($recipes as $r) {
        $sel = $selectedId == $r['id'] ? 'selected' : '';
        $html .= '<option value="' . (int) $r['id'] . '" data-price="' . (float) $r['price'] . '" ' . $sel . '>' . e($r['name']) . ' - ' . number_format($r['price'], 0, ',', '.') . 'đ</option>';
    }
    return $html;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $recipeIds = $_POST['recipe_id'] ?? [];
    $quantities = $_POST['quantity'] ?? [];
    $note = trim($_POST['note'] ?? '');

    $items = [];
    foreach ($recipeIds as $i => $rid) {
        $rid = (int) $rid;
        $qty = (int) ($quantities[$i] ?? 0);
        if ($rid && $qty > 0) {
            $items[] = ['recipe_id' => $rid, 'quantity' => $qty];
        }
    }

    if (empty($items)) {
        set_flash('error', 'Vui lòng chọn ít nhất một món.');
    } else {
        $pdo->beginTransaction();

        $orderCode = generate_order_code($pdo);
        $stmt = $pdo->prepare('INSERT INTO orders (order_code, staff_id, total_amount, note) VALUES (?,?,0,?)');
        $stmt->execute([$orderCode, current_user()['id'], $note]);
        $orderId = (int) $pdo->lastInsertId();

        $total = 0;
        $lowStockWarnings = [];

        $recipeStmt = $pdo->prepare('SELECT * FROM recipes WHERE id = ?');
        $itemStmt = $pdo->prepare('INSERT INTO order_items (order_id, recipe_id, recipe_name, quantity, unit_price, subtotal) VALUES (?,?,?,?,?,?)');
        $bomStmt = $pdo->prepare('SELECT ri.ingredient_id, ri.quantity_needed, i.name, i.unit, i.quantity AS stock_qty
            FROM recipe_ingredients ri JOIN ingredients i ON i.id = ri.ingredient_id WHERE ri.recipe_id = ?');
        $deductStmt = $pdo->prepare('UPDATE ingredients SET quantity = quantity - ? WHERE id = ?');
        $txnStmt = $pdo->prepare('INSERT INTO stock_transactions (ingredient_id, type, change_amount, note, created_by) VALUES (?, "order_deduct", ?, ?, ?)');

        foreach ($items as $item) {
            $recipeStmt->execute([$item['recipe_id']]);
            $recipe = $recipeStmt->fetch();
            if (!$recipe) {
                continue;
            }
            $subtotal = $recipe['price'] * $item['quantity'];
            $total += $subtotal;
            $itemStmt->execute([$orderId, $recipe['id'], $recipe['name'], $item['quantity'], $recipe['price'], $subtotal]);

            $bomStmt->execute([$recipe['id']]);
            foreach ($bomStmt->fetchAll() as $bom) {
                $needed = $bom['quantity_needed'] * $item['quantity'];
                $deductStmt->execute([$needed, $bom['ingredient_id']]);
                $txnStmt->execute([$bom['ingredient_id'], -$needed, 'Đơn hàng ' . $orderCode, current_user()['id']]);

                if ($bom['stock_qty'] - $needed < 0) {
                    $lowStockWarnings[] = $bom['name'];
                }
            }
        }

        $stmt = $pdo->prepare('UPDATE orders SET total_amount = ? WHERE id = ?');
        $stmt->execute([$total, $orderId]);

        $pdo->commit();

        $msg = 'Đã tạo đơn hàng ' . $orderCode . ' (' . format_money($total) . ').';
        if (!empty($lowStockWarnings)) {
            $msg .= ' Lưu ý: nguyên liệu có thể đã âm kho: ' . implode(', ', array_unique($lowStockWarnings));
        }
        set_flash(empty($lowStockWarnings) ? 'success' : 'error', $msg);
        redirect('order_view', ['id' => $orderId]);
    }
}
?>
<h1 class="page-title">Tạo đơn hàng mới</h1>

<form method="post" class="card card-form">
    <?= csrf_field() ?>
    <h3 class="section-title">Món hàng</h3>
    <div id="orderRows">
        <div class="dynamic-row">
            <select name="recipe_id[]"><?= recipe_options($recipes) ?></select>
            <input type="number" min="1" name="quantity[]" value="1" placeholder="Số lượng">
            <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">X</button>
        </div>
    </div>
    <button type="button" class="btn btn-sm btn-secondary" onclick="addOrderRow()">+ Thêm món</button>
    <template id="orderRowTemplate">
        <div class="dynamic-row">
            <select name="recipe_id[]"><?= recipe_options($recipes) ?></select>
            <input type="number" min="1" name="quantity[]" value="1" placeholder="Số lượng">
            <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">X</button>
        </div>
    </template>

    <label>Ghi chú đơn hàng</label>
    <input type="text" name="note" placeholder="VD: Ít đá, mang đi...">

    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Tạo đơn hàng</button>
        <a href="index.php?page=orders" class="btn btn-secondary">Huỷ</a>
    </div>
</form>
