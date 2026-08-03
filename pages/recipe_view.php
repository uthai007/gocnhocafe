<?php
$id = (int) ($_GET['id'] ?? 0);
$stmt = $pdo->prepare('SELECT * FROM recipes WHERE id = ?');
$stmt->execute([$id]);
$recipe = $stmt->fetch();

if (!$recipe) {
    set_flash('error', 'Không tìm thấy công thức.');
    redirect('recipes');
}

$stmt = $pdo->prepare("SELECT ri.quantity_needed, i.name, i.unit
    FROM recipe_ingredients ri JOIN ingredients i ON i.id = ri.ingredient_id
    WHERE ri.recipe_id = ?");
$stmt->execute([$id]);
$ingredients = $stmt->fetchAll();

$stmt = $pdo->prepare('SELECT * FROM recipe_steps WHERE recipe_id = ? ORDER BY step_number ASC');
$stmt->execute([$id]);
$steps = $stmt->fetchAll();
?>
<div class="page-header">
    <h1 class="page-title"><?= e($recipe['name']) ?></h1>
    <a href="index.php?page=recipes" class="btn btn-secondary">&larr; Về danh sách</a>
</div>

<div class="grid-2">
    <div class="card">
        <h2>Thông tin món</h2>
        <p><strong>Danh mục:</strong> <?= e($recipe['category'] ?: '—') ?></p>
        <p><strong>Giá bán:</strong> <?= format_money($recipe['price']) ?></p>
        <p><?= e($recipe['description']) ?></p>

        <h3 class="section-title">Nguyên liệu cần dùng (1 ly)</h3>
        <ul class="plain-list">
        <?php foreach ($ingredients as $ing): ?>
            <li><?= e($ing['name']) ?>: <strong><?= (float) $ing['quantity_needed'] ?> <?= e($ing['unit']) ?></strong></li>
        <?php endforeach; ?>
        <?php if (empty($ingredients)): ?><li class="muted">Chưa khai báo nguyên liệu.</li><?php endif; ?>
        </ul>
    </div>

    <div class="card">
        <h2>Quy trình pha chế</h2>
        <?php if (empty($steps)): ?>
            <p class="muted">Chưa có bước pha chế nào.</p>
        <?php else: ?>
        <ol class="step-list">
            <?php foreach ($steps as $step): ?>
                <li><?= e($step['instruction']) ?></li>
            <?php endforeach; ?>
        </ol>
        <?php endif; ?>
    </div>
</div>
