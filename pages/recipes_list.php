<?php
$recipes = $pdo->query("SELECT * FROM recipes ORDER BY category, name")->fetchAll();
?>
<div class="page-header">
    <h1 class="page-title">Công thức / Menu</h1>
    <?php if (is_admin()): ?>
    <div class="page-actions">
        <a href="index.php?page=recipe_form" class="btn btn-primary">+ Thêm món mới</a>
    </div>
    <?php endif; ?>
</div>

<div class="card-grid">
<?php foreach ($recipes as $recipe): ?>
    <div class="recipe-card">
        <div class="recipe-card-body">
            <span class="badge"><?= e($recipe['category'] ?: 'Chưa phân loại') ?></span>
            <h3><?= e($recipe['name']) ?></h3>
            <p class="muted"><?= e($recipe['description']) ?></p>
            <div class="recipe-price"><?= format_money($recipe['price']) ?></div>
        </div>
        <div class="recipe-card-actions">
            <a href="index.php?page=recipe_view&id=<?= (int) $recipe['id'] ?>" class="btn btn-sm btn-secondary">Xem quy trình</a>
            <?php if (is_admin()): ?>
                <a href="index.php?page=recipe_form&id=<?= (int) $recipe['id'] ?>" class="btn btn-sm btn-secondary">Sửa</a>
                <a href="index.php?page=recipe_delete&id=<?= (int) $recipe['id'] ?>" class="btn btn-sm btn-danger" onclick="return confirm('Xoá món này?')">Xoá</a>
            <?php endif; ?>
        </div>
    </div>
<?php endforeach; ?>
<?php if (empty($recipes)): ?>
    <p class="muted">Chưa có công thức nào.</p>
<?php endif; ?>
</div>
