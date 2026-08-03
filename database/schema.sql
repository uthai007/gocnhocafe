-- ============================================================
-- Coffee Shop Manager - Database Schema
-- Compatible with MySQL 5.7+ / MariaDB (Hostinger shared hosting)
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- Users (Admin / Staff)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','staff') NOT NULL DEFAULT 'staff',
    phone VARCHAR(20) DEFAULT NULL,
    active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Ingredients (Stock items)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingredients (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'g',
    quantity DECIMAL(12,2) NOT NULL DEFAULT 0,
    low_stock_threshold DECIMAL(12,2) NOT NULL DEFAULT 0,
    notes VARCHAR(255) DEFAULT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Stock transactions (import / export / adjustment / order deduction)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock_transactions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ingredient_id INT UNSIGNED NOT NULL,
    type ENUM('import','export','adjustment','order_deduct') NOT NULL,
    change_amount DECIMAL(12,2) NOT NULL,
    note VARCHAR(255) DEFAULT NULL,
    created_by INT UNSIGNED DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Recipes (Menu items)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) DEFAULT NULL,
    price DECIMAL(12,2) NOT NULL DEFAULT 0,
    description VARCHAR(255) DEFAULT NULL,
    active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Recipe ingredients (BOM - bill of materials per drink)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT UNSIGNED NOT NULL,
    ingredient_id INT UNSIGNED NOT NULL,
    quantity_needed DECIMAL(12,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Recipe steps (preparation workflow)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recipe_steps (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    recipe_id INT UNSIGNED NOT NULL,
    step_number INT UNSIGNED NOT NULL DEFAULT 1,
    instruction VARCHAR(500) NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Orders
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_code VARCHAR(30) NOT NULL UNIQUE,
    staff_id INT UNSIGNED DEFAULT NULL,
    status ENUM('completed','cancelled') NOT NULL DEFAULT 'completed',
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    note VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Order items
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id INT UNSIGNED NOT NULL,
    recipe_id INT UNSIGNED DEFAULT NULL,
    recipe_name VARCHAR(100) NOT NULL,
    quantity INT UNSIGNED NOT NULL DEFAULT 1,
    unit_price DECIMAL(12,2) NOT NULL DEFAULT 0,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Shifts (work schedule)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shifts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    staff_id INT UNSIGNED NOT NULL,
    shift_date DATE NOT NULL,
    shift_type ENUM('sang','chieu','toi') NOT NULL DEFAULT 'sang',
    start_time TIME DEFAULT NULL,
    end_time TIME DEFAULT NULL,
    note VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Checklist templates (defined by admin, per shift type + open/close)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS checklist_templates (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    checklist_type ENUM('open','close') NOT NULL DEFAULT 'open',
    item_name VARCHAR(255) NOT NULL,
    sort_order INT UNSIGNED NOT NULL DEFAULT 0,
    active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Checklist completions (per shift, tracks which items done)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS checklist_completions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    shift_id INT UNSIGNED NOT NULL,
    template_id INT UNSIGNED NOT NULL,
    is_done TINYINT(1) NOT NULL DEFAULT 0,
    completed_by INT UNSIGNED DEFAULT NULL,
    completed_at TIMESTAMP NULL DEFAULT NULL,
    UNIQUE KEY uniq_shift_template (shift_id, template_id),
    FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES checklist_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (completed_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- Seed data
-- ============================================================

-- Default accounts (password for both = "123456")
-- Hash generated with bcrypt, compatible with PHP password_verify()
INSERT INTO users (full_name, username, password, role, phone) VALUES
('Quản trị viên', 'admin', '$2y$12$wnbuZRBFaRRtdl8BiJHs1.RD060WxxoTE8FIilhpL3.6AONHw0tj2', 'admin', '0900000000'),
('Nhân viên A', 'staff1', '$2y$12$wnbuZRBFaRRtdl8BiJHs1.RD060WxxoTE8FIilhpL3.6AONHw0tj2', 'staff', '0900000001');

-- Sample ingredients
INSERT INTO ingredients (name, unit, quantity, low_stock_threshold, notes) VALUES
('Cà phê hạt Robusta', 'g', 5000, 1000, 'Kho lạnh'),
('Sữa đặc', 'ml', 3000, 500, NULL),
('Sữa tươi', 'ml', 4000, 1000, 'Bảo quản lạnh'),
('Đường', 'g', 5000, 500, NULL),
('Đá viên', 'g', 20000, 2000, NULL),
('Trà đen', 'g', 1000, 200, NULL),
('Bột matcha', 'g', 500, 100, NULL),
('Syrup caramel', 'ml', 1000, 200, NULL),
('Ly nhựa 500ml', 'cái', 200, 50, NULL);

-- Sample recipes
INSERT INTO recipes (name, category, price, description) VALUES
('Cà phê sữa đá', 'Cà phê', 25000, 'Cà phê phin truyền thống pha cùng sữa đặc và đá'),
('Bạc xỉu', 'Cà phê', 27000, 'Cà phê ít, nhiều sữa'),
('Trà đào cam sả', 'Trà trái cây', 35000, 'Trà đen ủ lạnh, đào, cam, sả'),
('Matcha sữa tươi đá', 'Trà xanh', 32000, 'Bột matcha Nhật pha cùng sữa tươi');

-- Recipe ingredients (BOM)
INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity_needed) VALUES
(1, 1, 20), (1, 2, 30), (1, 5, 150),
(2, 1, 15), (2, 2, 20), (2, 3, 60), (2, 5, 150),
(3, 6, 10), (3, 4, 20), (3, 5, 200),
(4, 7, 15), (4, 3, 100), (4, 4, 10), (4, 5, 150);

-- Recipe steps
INSERT INTO recipe_steps (recipe_id, step_number, instruction) VALUES
(1, 1, 'Cho 30ml sữa đặc vào ly'),
(1, 2, 'Pha 20g cà phê phin, lấy khoảng 40ml nước cốt'),
(1, 3, 'Khuấy đều cà phê với sữa đặc'),
(1, 4, 'Thêm đá viên đầy ly và khuấy nhẹ'),
(2, 1, 'Cho 20ml sữa đặc và 60ml sữa tươi vào ly'),
(2, 2, 'Pha 15g cà phê phin, lấy khoảng 30ml nước cốt'),
(2, 3, 'Rót cà phê nhẹ nhàng lên lớp sữa'),
(2, 4, 'Thêm đá viên'),
(3, 1, 'Ủ trà đen với nước sôi trong 5 phút, để nguội'),
(3, 2, 'Cắt đào, cam, sả cho vào ly'),
(3, 3, 'Thêm đường và trà đã ủ'),
(3, 4, 'Cho đá viên và khuấy đều'),
(4, 1, 'Đánh tan bột matcha với một ít nước ấm'),
(4, 2, 'Thêm đường vào khuấy đều'),
(4, 3, 'Cho đá viên vào ly, rót sữa tươi'),
(4, 4, 'Rót hỗn hợp matcha lên trên cùng');

-- Checklist templates
INSERT INTO checklist_templates (checklist_type, item_name, sort_order) VALUES
('open', 'Bật máy pha cà phê, máy xay', 1),
('open', 'Kiểm tra tồn kho nguyên liệu chính', 2),
('open', 'Chuẩn bị đá viên', 3),
('open', 'Vệ sinh quầy pha chế, mặt bàn khách', 4),
('open', 'Kiểm tra tiền quỹ đầu ca', 5),
('close', 'Vệ sinh máy pha cà phê, dụng cụ pha chế', 1),
('close', 'Bảo quản nguyên liệu còn dư vào tủ lạnh', 2),
('close', 'Đổ rác, lau dọn khu vực pha chế và quầy', 3),
('close', 'Kiểm đếm tiền quỹ cuối ca', 4),
('close', 'Tắt các thiết bị điện, khóa cửa', 5);

-- Sample shift (today, staff1, morning) - adjust date as needed after import
INSERT INTO shifts (staff_id, shift_date, shift_type, start_time, end_time) VALUES
(2, CURDATE(), 'sang', '07:00:00', '13:00:00');
