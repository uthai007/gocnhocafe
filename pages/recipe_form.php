<?php
$id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
$recipe = ['name' => '', 'category' => '', 'price' => 0, 'description' => ''];
$recipeIngredients = [];
$recipeSteps = [];

if ($id) {
    $stmt = $pdo->prepare('SELECT * FROM recipes WHERE id = ?');
    $stmt->execute([$id]);
    $found = $stmt->fetch();
    if (!$found) {
        set_flash('error', 'Không tìm thấy công thức.');
        redirect('recipes');
    }
    $recipe = $found;

    $stmt = $pdo->prepare('SELECT * FROM recipe_ingredients WHERE recipe_id = ?');
    $stmt->execute([$id]);
    $recipeIngredients = $stmt->fetchAll();

    $stmt = $pdo->prepare('SELECT * FROM recipe_steps WHERE recipe_id = ? ORDER BY step_number ASC');
    $stmt->execute([$id]);
    $recipeSteps = $stmt->fetchAll();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $name = trim($_POST['name'] ?? '');
    $category = trim($_POST['category'] ?? '');
    $price = (float) ($_POST['price'] ?? 0);
    $description = trim($_POST['description'] ?? '');
    $ingredientIds = $_POST['ingredient_id'] ?? [];
    $ingredientQtys = $_POST['ingredient_qty'] ?? [];
    $steps = $_POST['step_text'] ?? [];

    if ($name === '') {
        set_flash('error', 'Vui lòng nhập tên món.');
    } else {
        $pdo->beginTransaction();
        if ($id) {
            $stmt = $pdo->prepare('UPDATE recipes SET name=?, category=?, price=?, description=? WHERE id=?');
            $stmt->execute([$name, $category, $price, $description, $id]);
        } else {
            $stmt = $pdo->prepare('INSERT INTO recipes (name, category, price, description) VALUES (?,?,?,?)');
            $stmt->execute([$name, $category, $price, $description]);
            $id = (int) $pdo->lastInsertId();
        }

        // Replace ingredients
        $pdo->prepare('DELETE FROM recipe_ingredients WHERE recipe_id = ?')->execute([$id]);
        $insIng = $pdo->prepare('INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity_needed) VALUES (?,?,?)');
        foreach ($ingredientIds as $i => $ingId) {
            $ingId = (int) $ingId;
            $qty = (float) ($ingredientQtys[$i] ?? 0);
            if ($ingId && $qty > 0) {
                $insIng->execute([$id, $ingId, $qty]);
            }
        }

        // Replace steps
        $pdo->prepare('DELETE FROM recipe_steps WHERE recipe_id = ?')->execute([$id]);
        $insStep = $pdo->prepare('INSERT INTO recipe_steps (recipe_id, step_number, instruction) VALUES (?,?,?)');
        $stepNumber = 1;
        foreach ($steps as $text) {
            $text = trim($text);
            if ($text !== '') {
                $insStep->execute([$id, $stepNumber, $text]);
                $stepNumber++;
            }
        }

        $pdo->commit();
        set_flash('success', 'Đã lưu công thức.');
        redirect('recipes');
    }
}

$allIngredients = $pdo->query('SELECT id, name, unit FROM ingredients ORDER BY name ASC')->fetchAll();

function ingredient_options($allIngredients, $selectedId = null)
{
    $html = '<option value="">-- Chọn nguyên liệu --</option>';
    foreach ($allIngredients as $ing) {
        $sel = $selectedId == $ing['id'] ? 'selected' : '';
        $html .= '<option value="' . (int) $ing['id'] . '" ' . $sel . '>' . e($ing['name']) . ' (' . e($ing['unit']) . ')</option>';
    }
    return $html;
}
?>
<h1 class="page-title"><?= $id ? 'Sửa công thức' : 'Thêm công thức mới' ?></h1>

<form method="post" class="card card-form">
    <?= csrf_field() ?>
    <div class="form-row">
        <div>
            <label>Tên món</label>
            <input type="text" name="name" value="<?= e($recipe['name']) ?>" required>
        </div>
        <div>
            <label>Danh mục</label>
            <input type="text" name="category" value="<?= e($recipe['category']) ?>" placeholder="VD: Cà phê, Trà trái cây...">
        </div>
        <div>
            <label>Giá bán</label>
            <input type="number" step="1000" name="price" value="<?= e($recipe['price']) ?>" required>
        </div>
    </div>

    <label>Mô tả</label>
    <textarea name="description" rows="2"><?= e($recipe['description']) ?></textarea>

    <h3 class="section-title">Nguyên liệu cần dùng</h3>
    <div id="ingredientRows">
        <?php foreach ($recipeIngredients as $ri): ?>
        <div class="dynamic-row">
            <select name="ingredient_id[]"><?= ingredient_options($allIngredients, $ri['ingredient_id']) ?></select>
            <input type="number" step="0.01" name="ingredient_qty[]" value="<?= e($ri['quantity_needed']) ?>" placeholder="Số lượng cần">
            <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">X</button>
        </div>
        <?php endforeach; ?>
    </div>
    <button type="button" class="btn btn-sm btn-secondary" onclick="addIngredientRow()">+ Thêm nguyên liệu</button>
    <template id="ingredientRowTemplate">
        <div class="dynamic-row">
            <select name="ingredient_id[]"><?= ingredient_options($allIngredients) ?></select>
            <input type="number" step="0.01" name="ingredient_qty[]" placeholder="Số lượng cần">
            <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">X</button>
        </div>
    </template>

    <h3 class="section-title">Các bước pha chế</h3>
    <div id="stepRows">
        <?php if (empty($recipeSteps)): ?>
        <div class="dynamic-row">
            <textarea name="step_text[]" rows="1" placeholder="Mô tả bước thực hiện..."></textarea>
            <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">X</button>
        </div>
        <?php else: ?>
            <?php foreach ($recipeSteps as $step): ?>
            <div class="dynamic-row">
                <textarea name="step_text[]" rows="1"><?= e($step['instruction']) ?></textarea>
                <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">X</button>
            </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>
    <button type="button" class="btn btn-sm btn-secondary" onclick="addStepRow()">+ Thêm bước</button>
    <template id="stepRowTemplate">
        <div class="dynamic-row">
            <textarea name="step_text[]" rows="1" placeholder="Mô tả bước thực hiện..."></textarea>
            <button type="button" class="btn btn-sm btn-danger" onclick="removeRow(this)">X</button>
        </div>
    </template>

    <div class="form-actions">
        <button type="submit" class="btn btn-primary">Lưu công thức</button>
        <a href="index.php?page=recipes" class="btn btn-secondary">Huỷ</a>
    </div>
</form>
