<?php
// ============================================================
// Core application bootstrap: session, error display, DB connection
// ============================================================

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Show errors while developing; turn OFF (set to 0) once live on production.
error_reporting(E_ALL);
ini_set('display_errors', '1');

date_default_timezone_set('Asia/Ho_Chi_Minh');

define('APP_NAME', 'Coffee Shop Manager');
define('ROOT_PATH', dirname(__DIR__));

require_once __DIR__ . '/database.php';

try {
    $pdo = new PDO(
        'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4',
        DB_USER,
        DB_PASS,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]
    );
} catch (PDOException $e) {
    die('Không thể kết nối cơ sở dữ liệu. Vui lòng kiểm tra config/database.php. (' . htmlspecialchars($e->getMessage()) . ')');
}
