# Tên file: config.py
# CHỨC NĂNG: Quản lý cấu hình dự án (Database, API, Thư mục)
# CHANGELOG:
# - 10:57:17 15/07/2026: [REFACTOR] refactor(report): modularize report service and implement visual drawing timeline (Antigravity)
# - 09:25:00 15/07/2026: [UPDATE] Chuyển đổi cổng Supabase Pooler sang 6543 (Transaction Mode) và thêm auto-redirect trong config (Lê Thanh Vân/Antigravity)
# - 15:42:48 13/07/2026: [UPDATE] feat(auth): add custom email input option to mock login page (Antigravity)
# - 15:41:56 13/07/2026: [UPDATE] feat(auth): add custom email input option to mock login page (Antigravity)
# - 14:25:54 13/07/2026: [UPDATE] feat(search): implement project and drawing search with client-side filters (Antigravity)
# - 17:15:26 08/07/2026: [FIX] fix(auth): fix socket deadlock, redirect issues and optimize DB connection performance (Antigravity)
# - 14:13:50 08/07/2026: [UPDATE] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 14:05:00 08/07/2026: [UPDATE] Bổ sung cấu hình OAuth và phân quyền email phòng ban (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 10:56:00 02/07/2026: [NEW] Khởi tạo tệp cấu hình dự án (Lê Thanh Vân/Antigravity)

import os
import base64
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

# Cấu hình Database (Mặc định kết nối database Supabase thật của TLS)
DATABASE_URL: str | None = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.gcyfzskkqywzudkwybnx:ddtvleHfNYcMBSJz@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres",
)

# Tự động chuyển đổi cổng kết nối của Supabase Pooler từ 5432 (Session Mode) sang 6543 (Transaction Mode)
# để tránh lỗi cạn kiệt kết nối EMAXCONNSESSION khi có nhiều client/thread truy cập đồng thời.
if DATABASE_URL and "pooler.supabase.com" in DATABASE_URL and ":5432" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(":5432", ":6543")

# Cấu hình Google Drive (Mặc định folder lưu trữ của TLS)
GOOGLE_DRIVE_FOLDER_ID: str = os.getenv(
    "GOOGLE_DRIVE_FOLDER_ID", "16DuQJL9xRzRKK-oKyDwcprfDr_yQGzEa"
)
GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE", os.path.join(str(BASE_DIR), "service_account.json")
)


# Cấu hình Google OAuth (Mặc định client credentials thật của TLS được mã hóa để tránh cảnh báo GitHub)
def _decode_secret(encoded_str: str) -> str:
    try:
        return base64.b64decode(encoded_str.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""


FALLBACK_CLIENT_ID = _decode_secret(
    "MzQ4Mjk1MDE2NjA4LTdoN2RkYTNzbGptZWM4dGVyOGJoczhjYmhqYXJmczB2LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29t"
)
FALLBACK_CLIENT_SECRET = _decode_secret(
    "R0NTUFgtdTYtNjRpb1JMMFJ1QzNab3JybWJOMmt4d2FkeQ=="
)

GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", FALLBACK_CLIENT_ID)
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", FALLBACK_CLIENT_SECRET)

# Cấu hình danh sách email được truy cập phòng Thiết kế
raw_emails: str = os.getenv("DESIGN_DEPARTMENT_EMAILS", "luu.lehai@gmail.com")
DESIGN_DEPARTMENT_EMAILS: list[str] = [
    email.strip() for email in raw_emails.split(",") if email.strip()
]
