<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $action = $_POST['action'] ?? '';

    if ($action === 'add') {
        $type = $_POST['checklist_type'] ?? 'open';
        $itemName = trim($_POST['item_name'] ?? '');
        if ($itemName !== '') {
            $maxOrder = (int) $pdo->query("SELECT COALESCE(MAX(sort_order),0) FROM checklist_templates WHERE checklist_type = " . $pdo->quote($type))->fetchColumn();
            $stmt = $pdo->prepare('INSERT INTO checklist_templates (checklist_type, item_name, sort_order) VALUES (?,?,?)');
            $stmt->execute([$type, $itemName, $maxOrder + 1]);
            set_flash('success', 'Đã thêm mục checklist.');
        }
    } elseif ($action === 'delete') {
        $stmt = $pdo->prepare('DELETE FROM checklist_templates WHERE id = ?');
        $stmt->execute([(int) ($_POST['id'] ?? 0)]);
        set_flash('success', 'Đã xoá mục checklist.');
    } elseif ($action === 'toggle_active') {
        $stmt = $pdo->prepare('UPDATE checklist_templates SET active = 1 - active WHERE id = ?');
        $stmt->execute([(int) ($_POST['id'] ?? 0)]);
    }
    redirect('checklist_templates');
}

$open = $pdo->query("SELECT * FROM checklist_templates WHERE checklist_type = 'open' ORDER BY sort_order")->fetchAll();
$close = $pdo->query("SELECT * FROM checklist_templates WHERE checklist_type = 'close' ORDER BY sort_order")->fetchAll();

function render_template_list($items)
{
    foreach ($items as $item) {
        echo '<li class="' . ($item['active'] ? '' : 'muted') . '">';
        echo '<span>' . e($item['item_name']) . '</span>';
        echo '<span class="row-actions">';
        echo '<form method="post" class="inline-form"><input type="hidden" name="csrf_token" value="' . e(csrf_token()) . '"><input type="hidden" name="action" value="toggle_active"><input type="hidden" name="id" value="' . (int) $item['id'] . '"><button type="submit" class="btn btn-xs btn-secondary">' . ($item['active'] ? 'Ẩn' : 'Hiện') . '</button></form>';
        echo '<form method="post" class="inline-form" onsubmit="return confirm(\'Xoá mục này?\')"><input type="hidden" name="csrf_token" value="' . e(csrf_token()) . '"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="' . (int) $item['id'] . '"><button type="submit" class="btn btn-xs btn-danger">Xoá</button></form>';
        echo '</span></li>';
    }
}
?>
<h1 class="page-title">Mẫu checklist đầu ca / cuối ca</h1>

<div class="grid-2">
    <div class="card">
        <h2>Checklist đầu ca (mở cửa)</h2>
        <ul class="checklist-admin-list">
            <?php render_template_list($open); ?>
        </ul>
        <form method="post" class="inline-form">
            <?= csrf_field() ?>
            <input type="hidden" name="action" value="add">
            <input type="hidden" name="checklist_type" value="open">
            <input type="text" name="item_name" placeholder="Thêm mục mới..." required>
            <button type="submit" class="btn btn-sm btn-primary">Thêm</button>
        </form>
    </div>

    <div class="card">
        <h2>Checklist cuối ca (đóng cửa)</h2>
        <ul class="checklist-admin-list">
            <?php render_template_list($close); ?>
        </ul>
        <form method="post" class="inline-form">
            <?= csrf_field() ?>
            <input type="hidden" name="action" value="add">
            <input type="hidden" name="checklist_type" value="close">
            <input type="text" name="item_name" placeholder="Thêm mục mới..." required>
            <button type="submit" class="btn btn-sm btn-primary">Thêm</button>
        </form>
    </div>
</div>
