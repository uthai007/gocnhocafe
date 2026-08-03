<?php
$id = isset($_GET['id']) ? (int) $_GET['id'] : 0;
$item = ['full_name' => '', 'username' => '', 'role' => 'staff', 'phone' => '', 'active' => 1];

if ($id) {
    $stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?');
    $stmt->execute([$id]);
    $found = $stmt->fetch();
    if (!$found) {
        set_flash('error', 'Không tìm thấy tài khoản.');
        redirect('users');
    }
    $item = $found;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    verify_csrf();
    $fullName = trim($_POST['full_name'] ?? '');
    $username = trim($_POST['username'] ?? '');
    $role = $_POST['role'] ?? 'staff';
    $phone = trim($_POST['phone'] ?? '');
    $active = isset($_POST['active']) ? 1 : 0;
    $password = $_POST['password'] ?? '';

    if ($fullName === '' || $username === '') {
        set_flash('error', 'Vui lòng nhập đầy đủ họ tên và tên đăng nhập.');
    } elseif (!$id && $password === '') {
        set_flash('error', 'Vui lòng nhập mật khẩu cho tài khoản mới.');
    } else {
        // Check username uniqueness
        $stmt = $pdo->prepare('SELECT id FROM users WHERE username = ? AND id != ?');
        $stmt->execute([$username, $id]);
        if ($stmt->fetch()) {
            set_flash('error', 'Tên đăng nhập đã tồn tại.');
        } elseif ($id) {
            if ($password !== '') {
                $stmt = $pdo->prepare('UPDATE users SET full_name=?, username=?, role=?, phone=?, active=?, password=? WHERE id=?');
                $stmt->execute([$fullName, $username, $role, $phone, $active, password_hash($password, PASSWORD_DEFAULT), $id]);
            } else {
                $stmt = $pdo->prepare('UPDATE users SET full_name=?, username=?, role=?, phone=?, active=? WHERE id=?');
                $stmt->execute([$fullName, $username, $role, $phone, $active, $id]);
            }
            set_flash('success', 'Đã cập nhật tài khoản.');
            redirect('users');
        } else {
            $stmt = $pdo->prepare('INSERT INTO users (full_name, username, password, role, phone, active) VALUES (?,?,?,?,?,?)');
            $stmt->execute([$fullName, $username, password_hash($password, PASSWORD_DEFAULT), $role, $phone, $active]);
            set_flash('success', 'Đã tạo tài khoản mới.');
            redirect('users');
        }
    }
}
?>
<h1 class="page-title"><?= $id ? 'Sửa tài khoản' : 'Thêm tài khoản' ?></h1>

<div class="card card-form">
    <form method="post">
        <?= csrf_field() ?>
        <label>Họ tên</label>
        <input type="text" name="full_name" value="<?= e($item['full_name']) ?>" required>

        <label>Tên đăng nhập</label>
        <input type="text" name="username" value="<?= e($item['username']) ?>" required>

        <label>Mật khẩu <?= $id ? '(để trống nếu không đổi)' : '' ?></label>
        <input type="password" name="password" <?= $id ? '' : 'required' ?>>

        <label>Vai trò</label>
        <select name="role">
            <option value="staff" <?= $item['role'] === 'staff' ? 'selected' : '' ?>>Nhân viên</option>
            <option value="admin" <?= $item['role'] === 'admin' ? 'selected' : '' ?>>Quản lý</option>
        </select>

        <label>Số điện thoại</label>
        <input type="text" name="phone" value="<?= e($item['phone']) ?>">

        <label class="checkbox-label">
            <input type="checkbox" name="active" <?= $item['active'] ? 'checked' : '' ?>> Tài khoản đang hoạt động
        </label>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Lưu</button>
            <a href="index.php?page=users" class="btn btn-secondary">Huỷ</a>
        </div>
    </form>
</div>
