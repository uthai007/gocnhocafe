<?php
// ============================================================
// Generic helper functions used across all pages
// ============================================================

function e($value)
{
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}

function redirect($page, $params = [])
{
    $query = array_merge(['page' => $page], $params);
    header('Location: index.php?' . http_build_query($query));
    exit;
}

function set_flash($type, $message)
{
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

function get_flash()
{
    if (empty($_SESSION['flash'])) {
        return null;
    }
    $flash = $_SESSION['flash'];
    unset($_SESSION['flash']);
    return $flash;
}

function csrf_token()
{
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function csrf_field()
{
    return '<input type="hidden" name="csrf_token" value="' . e(csrf_token()) . '">';
}

function verify_csrf()
{
    $token = $_POST['csrf_token'] ?? '';
    if (!hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
        set_flash('error', 'Phiên làm việc đã hết hạn, vui lòng thử lại.');
        redirect($_GET['page'] ?? 'dashboard');
    }
}

function format_money($amount)
{
    return number_format((float) $amount, 0, ',', '.') . ' đ';
}

function format_date($datetime, $withTime = false)
{
    if (empty($datetime)) {
        return '';
    }
    $ts = strtotime($datetime);
    return $withTime ? date('d/m/Y H:i', $ts) : date('d/m/Y', $ts);
}

function generate_order_code(PDO $pdo)
{
    $prefix = 'DH' . date('Ymd');
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM orders WHERE order_code LIKE ?");
    $stmt->execute([$prefix . '%']);
    $count = (int) $stmt->fetchColumn() + 1;
    return $prefix . '-' . str_pad($count, 4, '0', STR_PAD_LEFT);
}

function shift_type_label($type)
{
    $labels = ['sang' => 'Ca sáng', 'chieu' => 'Ca chiều', 'toi' => 'Ca tối'];
    return $labels[$type] ?? $type;
}

function checklist_type_label($type)
{
    return $type === 'open' ? 'Đầu ca (mở cửa)' : 'Cuối ca (đóng cửa)';
}
