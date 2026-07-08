# Tên file: scripts/migrate_sections.py
# CHỨC NĂNG: Cập nhật schema database (tạo bảng project_sections, ALTER TABLE drawings)
# CHANGELOG:
# - 18:19:45 08/07/2026: [NEW] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [NEW] Khởi tạo script SQL Migration cho Hạng mục Dự án (Antigravity)

import sys
import os
import logging
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, SessionLocal
from core.models import Base, ProjectSection  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("migrate_sections")


def run_migration() -> bool:
    """Thực thi cập nhật cấu trúc cơ sở dữ liệu cloud.

    Returns:
        bool: True nếu thành công, False nếu thất bại.
    """
    logger.info("Bắt đầu chạy migration cho Hạng mục Dự án...")

    # 1. Tạo các bảng mới nếu chưa có (như bảng project_sections)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tạo bảng project_sections thành công hoặc đã tồn tại.")
    except Exception as e:
        logger.error("Lỗi khi chạy create_all: %s", str(e), exc_info=True)
        return False

    # 2. ALTER TABLE drawings để thêm cột section_id nếu chưa có
    db = SessionLocal()
    try:
        is_postgres = engine.dialect.name == "postgresql"

        if is_postgres:
            check_sql = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='drawings' AND column_name='section_id';
            """
            res = db.execute(text(check_sql)).fetchone()
            if not res:
                logger.info(
                    "Thêm cột section_id và constraint khóa ngoại vào bảng drawings (PostgreSQL)..."
                )
                db.execute(text("ALTER TABLE drawings ADD COLUMN section_id INTEGER;"))
                db.execute(
                    text(
                        """
                    ALTER TABLE drawings
                    ADD CONSTRAINT fk_drawings_section_id
                    FOREIGN KEY (section_id)
                    REFERENCES project_sections(section_id)
                    ON DELETE SET NULL;
                """
                    )
                )
                db.commit()
                logger.info("Thêm cột section_id thành công.")
            else:
                logger.info("Cột section_id đã tồn tại trong bảng drawings.")
        else:
            # SQLite local
            res = db.execute(text("PRAGMA table_info(drawings);")).fetchall()
            cols = [r[1] for r in res]
            if "section_id" not in cols:
                logger.info("Thêm cột section_id vào bảng drawings (SQLite)...")
                db.execute(
                    text(
                        "ALTER TABLE drawings ADD COLUMN section_id INTEGER REFERENCES project_sections(section_id) ON DELETE SET NULL;"
                    )
                )
                db.commit()
                logger.info("Thêm cột section_id thành công.")
            else:
                logger.info("Cột section_id đã tồn tại trong bảng drawings.")

        return True
    except Exception as e:
        db.rollback()
        logger.error("Lỗi khi ALTER TABLE drawings: %s", str(e), exc_info=True)
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
