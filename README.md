<!--
File: README.md
CHỨC NĂNG: Tài liệu giới thiệu tổng quan, hướng dẫn cài đặt và vận hành hệ thống ERP Thiết kế - Kế hoạch (TLS)
CHANGELOG:
- 12:05:00 02/07/2026: [NEW] Khởi tạo file README giới thiệu dự án (Lê Thanh Vân/Antigravity)
-->

# 🏗️ TLS ERP DESIGN PLANNING

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-PyQt6-orange.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-green.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Hệ thống **ERP Thiết kế - Kế hoạch (TLS ERP Design Planning)** là ứng dụng máy tính (Desktop App) được xây dựng dành riêng cho **Tuấn Long Steel (TLS)** nhằm tối ưu hóa và thông suốt luồng công việc giữa phòng **Thiết kế** (Ban hành bản vẽ) và phòng **Kế hoạch** (Tiếp nhận & In ấn sản xuất).

Hệ thống kết hợp sức mạnh lưu trữ dữ liệu trạng thái thời gian thực của **Supabase Cloud DB** và giải pháp lưu trữ tài liệu bản vẽ kỹ thuật nặng của **Google Shared Drive**.

---

## 🚀 Tính Năng Chính (Giai đoạn 1)

*   **Phòng Thiết Kế (Design Department)**:
    *   Ban hành bản vẽ kỹ thuật mới kèm các thông tin thuộc tính (Mã bản vẽ, tên bản vẽ, dự án).
    *   Liên kết trực tiếp tệp tin PDF thiết kế thông qua URL chia sẻ từ Google Drive.
    *   Quản lý danh sách bản vẽ đã phát hành và theo dõi trạng thái.
*   **Phòng Kế Hoạch (Planning Department)**:
    *   Tiếp nhận thông tin bản vẽ được ban hành theo thời gian thực.
    *   Truy cập nhanh để xem và in ấn bản vẽ PDF trực tiếp từ Google Drive.
    *   Xác nhận bàn giao bản vẽ xuống xưởng sản xuất, tự động cập nhật trạng thái sang "Đang sản xuất".

---

## 🛠️ Công Nghệ Sử Dụng

*   **Ngôn ngữ lập trình**: Python 3.12+
*   **Giao diện người dùng**: PyQt6 (hỗ trợ xử lý đa luồng `QThread` đảm bảo UI mượt mà, không bị đơ lag khi gọi API).
*   **Cơ sở dữ liệu**: PostgreSQL hosted trên Supabase Cloud.
*   **ORM**: SQLAlchemy kết hợp DB Driver để truy cập và quản lý dữ liệu.
*   **Quản lý cấu hình**: `python-dotenv` quản lý bảo mật API keys và thông tin kết nối.

---

## 📂 Cấu Trúc Mã Nguồn

Dự án tuân thủ nghiêm ngặt nguyên lý **Phân tách Trách nhiệm (Separation of Concerns)**:

```
TLS_ERP_DESIGN_PLANNING/
├── main.py                  # Điểm khởi chạy chính của ứng dụng PyQt6
├── config.py                # Đọc cấu hình từ .env và thiết lập môi trường
├── core/                    # TẦNG CORE LOGIC (Tuyệt đối cấm import PyQt6 tại đây)
│   ├── database.py          # Kết nối PostgreSQL và khởi tạo SQLAlchemy session
│   ├── models.py            # Khai báo cấu trúc bảng (Projects, Drawings, BOM...)
│   └── services/            # Lớp xử lý nghiệp vụ (ProjectService, DrawingService)
├── ui/                      # TẦNG GIAO DIỆN (PyQt6 - Cấm truy vấn trực tiếp cơ sở dữ liệu)
│   ├── main_window.py       # Layout chính và định tuyến sidebar điều hướng
│   ├── common/              # Các Widget dùng chung và luồng phụ (workers.py)
│   └── views/               # Giao diện nghiệp vụ (thiet_ke_view.py, ke_hoach_view.py)
├── docs/                    # Tài liệu đặc tả kiến trúc và lịch sử phát triển
└── scripts/                 # Các công cụ kiểm toán chất lượng mã nguồn tự động
```

---

## 💻 Hướng Dẫn Cài Đặt & Chạy Thử

### 1. Chuẩn bị môi trường
Yêu cầu máy tính cài đặt sẵn **Python 3.12 trở lên**.

### 2. Tải mã nguồn và cài đặt thư viện
Mở Terminal/PowerShell tại thư mục dự án và chạy các lệnh sau:

```bash
# Cài đặt các thư viện cần thiết
pip install PyQt6 supabase sqlalchemy psycopg2-binary python-dotenv ruff
```

### 3. Cấu hình biến môi trường
Tạo file `.env` tại thư mục gốc của dự án với nội dung cấu hình kết nối của bạn:

```env
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
DATABASE_URL=postgresql://postgres:password@db.your-supabase.supabase.co:5432/postgres
```

### 4. Khởi chạy ứng dụng
Chạy ứng dụng bằng lệnh:

```bash
python main.py
```

---

## 📐 Tiêu Chuẩn Chất Lượng Mã Nguồn (Strict Limits)

Để đảm bảo mã nguồn luôn sạch, dễ bảo trì và tránh nợ kỹ thuật, dự án tích hợp hệ thống kiểm soát chất lượng tự động **Git Guard** tại local. Mọi commit bắt buộc phải vượt qua:

1.  **Độ dài tệp**: Tối đa 800 dòng (Khuyến nghị chia tách module khi đạt 500 dòng).
2.  **Độ dài hàm**: Tối đa 100 dòng (Khuyến nghị dưới 50 dòng).
3.  **Đối số của hàm**: Tối đa 4 đối số thực tế (nếu nhiều hơn bắt buộc gom nhóm thành Data Class hoặc Dictionary).
4.  **Type Hints & Docstrings**: Bắt buộc khai báo đầy đủ kiểu dữ liệu và ghi chú chuẩn Google-Style cho tất cả các hàm/class mới hoặc sửa đổi.
5.  **Xử lý lỗi**: Nghiêm cấm nuốt lỗi im lặng (`except: pass`), bắt buộc phải ghi log lỗi thông qua `logger.error`.

---

## 📄 Tài Liệu Liên Quan
*   [Bản đồ kiến trúc chi tiết (Master Map)](docs/architecture/ARCHITECTURE_MAP.md)
*   [Sơ đồ liên kết mã nguồn (Codebase Graph)](docs/architecture/MAP_GRAPH.md)
