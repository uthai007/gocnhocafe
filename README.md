# ☕ Coffee Shop Manager

Web app quản lý quán cà phê: kho nguyên liệu, công thức pha chế, đơn hàng, checklist đầu/cuối ca và lịch làm việc của nhân viên.

Viết bằng **PHP thuần + MySQL** (không cần framework, không cần bước build) để có thể upload trực tiếp lên **Hostinger Shared Hosting** qua File Manager hoặc FTP.

## Tính năng

- **Đăng nhập phân quyền**: Quản lý (admin) và Nhân viên (staff).
- **Kho nguyên liệu**: theo dõi tồn kho, cảnh báo sắp hết hàng, lịch sử nhập/xuất kho.
- **Công thức / Menu**: khai báo nguyên liệu cần dùng và các bước pha chế cho từng món.
- **Đơn hàng**: nhân viên tạo đơn, hệ thống tự động trừ kho theo công thức, xem lịch sử & chi tiết đơn.
- **Checklist ca làm**: mẫu checklist đầu ca / cuối ca do quản lý thiết lập, nhân viên đánh dấu hoàn thành theo từng ca.
- **Lịch làm ca**: quản lý xếp ca theo tuần cho từng nhân viên.
- **Báo cáo**: số đơn, doanh thu theo ngày, món bán chạy.

## Yêu cầu hệ thống

- PHP 7.4 trở lên (khuyến nghị PHP 8.x — mặc định trên Hostinger hiện nay)
- MySQL 5.7+ hoặc MariaDB
- Không cần Composer, không cần Node.js

## Cài đặt & chạy thử ở máy local

1. Cài [XAMPP](https://www.apachefriends.org/) hoặc [Laragon](https://laragon.org/).
2. Copy thư mục dự án vào `htdocs` (XAMPP) hoặc `www` (Laragon).
3. Tạo database MySQL tên `coffee_shop`, import file [`database/schema.sql`](database/schema.sql).
4. File `config/database.php` mặc định đã cấu hình sẵn cho local (`root` / không mật khẩu). Nếu khác, hãy sửa lại.
5. Mở trình duyệt: `http://localhost/<ten-thu-muc>/`

## Tài khoản mặc định (đổi ngay sau khi cài đặt)

| Vai trò  | Tên đăng nhập | Mật khẩu |
|----------|---------------|----------|
| Quản lý  | `admin`       | `123456` |
| Nhân viên| `staff1`      | `123456` |

## Triển khai lên Hostinger (Shared Hosting)

1. **Tạo database**: hPanel → *Databases* → *MySQL Databases* → tạo database + user, ghi lại tên database, username, password, host (thường là `localhost`).
2. **Import schema**: vào *phpMyAdmin* từ hPanel, chọn database vừa tạo → tab *Import* → chọn file `database/schema.sql` → Go.
3. **Chuẩn bị file cấu hình**:
   - Copy `config/database.example.php` thành `config/database.php`.
   - Điền đúng `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS` theo thông tin ở bước 1.
4. **Upload code**: dùng *File Manager* trong hPanel hoặc FTP (FileZilla) để upload toàn bộ nội dung thư mục dự án vào `public_html` (hoặc thư mục con nếu dùng subdomain).
5. **Tắt hiển thị lỗi ở production**: mở `config/config.php`, đổi:
   ```php
   ini_set('display_errors', '0');
   ```
6. Truy cập domain của bạn, đăng nhập bằng tài khoản admin mặc định và **đổi mật khẩu ngay** (mục *Tài khoản nhân viên*).

## Cấu trúc thư mục

```
config/          Cấu hình kết nối DB & bootstrap ứng dụng
includes/        Header, sidebar, footer, hàm dùng chung, xác thực
pages/           Các trang chức năng (được index.php nạp theo ?page=...)
assets/css, js/  Giao diện & script phía client
database/schema.sql   Cấu trúc bảng + dữ liệu mẫu
index.php        Front controller (router chính, mọi request đi qua đây)
```

## Bảo mật

- File `config/database.php` chứa thông tin nhạy cảm và đã được thêm vào `.gitignore` — không commit file này lên Git với thông tin thật.
- Mật khẩu người dùng được băm bằng `password_hash()` (bcrypt).
- Toàn bộ truy vấn dùng PDO prepared statements để chống SQL Injection.
- Form có CSRF token bảo vệ.
- Sau khi đưa lên production, luôn đổi mật khẩu tài khoản mặc định và tắt `display_errors`.
