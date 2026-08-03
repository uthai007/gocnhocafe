<?php
$users = $pdo->query("SELECT * FROM users ORDER BY role DESC, full_name")->fetchAll();
?>
<div class="page-header">
    <h1 class="page-title">Tài khoản nhân viên</h1>
    <a href="index.php?page=user_form" class="btn btn-primary">+ Thêm tài khoản</a>
</div>

<div class="card">
<table class="table">
    <thead><tr><th>Họ tên</th><th>Tên đăng nhập</th><th>Vai trò</th><th>SĐT</th><th>Trạng thái</th><th></th></tr></thead>
    <tbody>
    <?php foreach ($users as $u): ?>
        <tr>
            <td><?= e($u['full_name']) ?></td>
            <td><?= e($u['username']) ?></td>
            <td><?= $u['role'] === 'admin' ? 'Quản lý' : 'Nhân viên' ?></td>
            <td><?= e($u['phone']) ?></td>
            <td><span class="badge <?= $u['active'] ? 'badge-success' : 'badge-danger' ?>"><?= $u['active'] ? 'Đang hoạt động' : 'Đã khoá' ?></span></td>
            <td class="actions">
                <a href="index.php?page=user_form&id=<?= (int) $u['id'] ?>" class="btn btn-sm btn-secondary">Sửa</a>
                <?php if ($u['id'] != current_user()['id']): ?>
                <a href="index.php?page=user_delete&id=<?= (int) $u['id'] ?>" class="btn btn-sm btn-danger" onclick="return confirm('Xoá tài khoản này?')">Xoá</a>
                <?php endif; ?>
            </td>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
</div>
