# Tên file: scripts/migrate_project_roles.py
# CHỨC NĂNG: Cập nhật schema database (thêm cột sales_email và designer_email vào bảng projects)
# CHANGELOG:
# - 15:24:09 10/07/2026: [NEW] feat(auth): support auto login with SessionManager (Antigravity)
# - 14:52:00 10/07/2026: [NEW] Khởi tạo script SQL Migration cho vai trò Dự án (Lê Thanh Vân/Antigravity)

import sys
import os
import logging
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, SessionLocal
from core.models import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("migrate_project_roles")


def run_migration() -> bool:
    """Thực thi cập nhật cấu trúc cơ sở dữ liệu cloud.

    Returns:
        bool: True nếu thành công, False nếu thất bại.
    """
    logger.info("Bắt đầu chạy migration bổ sung vai trò Kinh doanh & Thiết kế cho Dự án...")

    # 1. Khởi tạo bảng nếu chưa tồn tại
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Khởi tạo cấu trúc DB SQLAlchemy hoàn tất.")
    except Exception as e:
        logger.error("Lỗi khi chạy create_all: %s", str(e), exc_info=True)
        return False

    # 2. ALTER TABLE projects để thêm sales_email và designer_email nếu chưa có
    db = SessionLocal()
    try:
        is_postgres = engine.dialect.name == "postgresql"

        if is_postgres:
            # PostgreSQL
            for col_name in ["sales_email", "designer_email"]:
                check_sql = f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='projects' AND column_name='{col_name}';
                """
                res = db.execute(text(check_sql)).fetchone()
                if not res:
                    logger.info("Thêm cột %s vào bảng projects (PostgreSQL)...", col_name)
                    db.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} VARCHAR(100);"))
                    db.commit()
                    logger.info("Thêm cột %s thành công.", col_name)
                else:
                    logger.info("Cột %s đã tồn tại trong bảng projects.", col_name)
        else:
            # SQLite local
            res = db.execute(text("PRAGMA table_info(projects);")).fetchall()
            cols = [r[1] for r in res]
            for col_name in ["sales_email", "designer_email"]:
                if col_name not in cols:
                    logger.info("Thêm cột %s vào bảng projects (SQLite)...", col_name)
                    db.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} VARCHAR(100);"))
                    db.commit()
                    logger.info("Thêm cột %s thành công.", col_name)
                else:
                    logger.info("Cột %s đã tồn tại trong bảng projects.", col_name)

        return True
    except Exception as e:
        db.rollback()
        logger.error("Lỗi khi ALTER TABLE projects: %s", str(e), exc_info=True)
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
