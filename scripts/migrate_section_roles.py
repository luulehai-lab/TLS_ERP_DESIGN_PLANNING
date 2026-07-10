# Tên file: scripts/migrate_section_roles.py
# CHỨC NĂNG: Cập nhật schema database (thêm cột designer_email vào bảng project_sections)
# CHANGELOG:
# - 15:24:09 10/07/2026: [NEW] feat(auth): support auto login with SessionManager (Antigravity)
# - 15:12:00 10/07/2026: [NEW] Khởi tạo script SQL Migration cho vai trò Hạng mục (Lê Thanh Vân/Antigravity)

import sys
import os
import logging
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, SessionLocal
from core.models import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("migrate_section_roles")


def run_migration() -> bool:
    """Thực thi cập nhật cấu trúc cơ sở dữ liệu cloud.

    Returns:
        bool: True nếu thành công, False nếu thất bại.
    """
    logger.info("Bắt đầu chạy migration bổ sung vai trò Thiết kế phụ trách Hạng mục...")

    # 1. Khởi tạo bảng nếu chưa tồn tại
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Khởi tạo cấu trúc DB SQLAlchemy hoàn tất.")
    except Exception as e:
        logger.error("Lỗi khi chạy create_all: %s", str(e), exc_info=True)
        return False

    # 2. ALTER TABLE project_sections để thêm designer_email nếu chưa có
    db = SessionLocal()
    try:
        is_postgres = engine.dialect.name == "postgresql"

        if is_postgres:
            # PostgreSQL
            check_sql = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='project_sections' AND column_name='designer_email';
            """
            res = db.execute(text(check_sql)).fetchone()
            if not res:
                logger.info("Thêm cột designer_email vào bảng project_sections (PostgreSQL)...")
                db.execute(text("ALTER TABLE project_sections ADD COLUMN designer_email VARCHAR(100);"))
                db.commit()
                logger.info("Thêm cột designer_email thành công.")
            else:
                logger.info("Cột designer_email đã tồn tại trong bảng project_sections.")
        else:
            # SQLite local
            res = db.execute(text("PRAGMA table_info(project_sections);")).fetchall()
            cols = [r[1] for r in res]
            if "designer_email" not in cols:
                logger.info("Thêm cột designer_email vào bảng project_sections (SQLite)...")
                db.execute(text("ALTER TABLE project_sections ADD COLUMN designer_email VARCHAR(100);"))
                db.commit()
                logger.info("Thêm cột designer_email thành công.")
            else:
                logger.info("Cột designer_email đã tồn tại trong bảng project_sections.")

        return True
    except Exception as e:
        db.rollback()
        logger.error("Lỗi khi ALTER TABLE project_sections: %s", str(e), exc_info=True)
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
