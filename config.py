# Tên file: config.py
# CHỨC NĂNG: Quản lý cấu hình dự án (Database, API, Thư mục)
# CHANGELOG:
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 10:56:00 02/07/2026: [NEW] Khởi tạo tệp cấu hình dự án (Lê Thanh Vân/Antigravity)

import os
from pathlib import Path
from dotenv import load_dotenv

# Thư mục gốc của dự án
BASE_DIR = Path(__file__).parent.resolve()

# Load file .env nếu có
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Cấu hình Database
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Dự phòng SQLite local nếu không có cấu hình Database URL
    DATABASE_URL = f"sqlite:///{BASE_DIR}/erp_local.db"

# Cấu hình Google Drive (nếu có dùng API tự động sau này)
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
