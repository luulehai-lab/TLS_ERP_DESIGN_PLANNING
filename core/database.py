# Tên file: core/database.py
# CHỨC NĂNG: Cấu hình SQLAlchemy kết nối PostgreSQL (hoặc SQLite dự phòng)
# CHANGELOG:
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:43:00 02/07/2026: [FIX] Bổ sung Type Hints kiểu trả về cho hàm get_db (Lê Thanh Vân/Antigravity)
# - 10:58:00 02/07/2026: [NEW] Thiết lập kết nối cơ sở dữ liệu SQLAlchemy (Lê Thanh Vân/Antigravity)

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Cấu hình logging cơ bản cho sql
logging.basicConfig(level=logging.INFO)

# Khởi tạo engine kết nối
# Đối với PostgreSQL, ta tăng kích thước pool kết nối để đảm bảo tính chịu tải
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )
else:
    # Đối với SQLite local
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Khởi tạo session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo Base class cho các Model kế thừa
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Generator tạo session kết nối DB và tự động đóng sau khi hoàn thành.

    Yields:
        SessionLocal: Session kết nối database hiện thời.

    Returns:
        Generator[Session, None, None]: Generator quản lý phiên kết nối DB.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
