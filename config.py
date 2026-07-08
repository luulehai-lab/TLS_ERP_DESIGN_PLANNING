# Tên file: config.py
# CHỨC NĂNG: Quản lý cấu hình dự án (Database, API, Thư mục)
# CHANGELOG:
# - 17:15:26 08/07/2026: [FIX] fix(auth): fix socket deadlock, redirect issues and optimize DB connection performance (Antigravity)
# - 14:13:50 08/07/2026: [UPDATE] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 14:05:00 08/07/2026: [UPDATE] Bổ sung cấu hình OAuth và phân quyền email phòng ban (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 10:56:00 02/07/2026: [NEW] Khởi tạo tệp cấu hình dự án (Lê Thanh Vân/Antigravity)

import os
from pathlib import Path
from dotenv import load_dotenv

import sys

# Thư mục gốc của dự án (tương thích cả khi đóng gói PyInstaller và chạy code trực tiếp)
if getattr(sys, "frozen", False):
    BASE_DIR: Path = Path(sys.executable).parent.resolve()
else:
    BASE_DIR: Path = Path(__file__).parent.resolve()

# Load file .env nếu có
env_path: Path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Cấu hình Database
DATABASE_URL: str | None = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Dự phòng SQLite local nếu không có cấu hình Database URL
    DATABASE_URL = f"sqlite:///{BASE_DIR}/erp_local.db"

# Cấu hình Google Drive (nếu có dùng API tự động sau này)
GOOGLE_DRIVE_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")

# Cấu hình Google OAuth
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Cấu hình danh sách email được truy cập phòng Thiết kế
raw_emails: str = os.getenv("DESIGN_DEPARTMENT_EMAILS", "luu.lehai@gmail.com")
DESIGN_DEPARTMENT_EMAILS: list[str] = [
    email.strip() for email in raw_emails.split(",") if email.strip()
]
