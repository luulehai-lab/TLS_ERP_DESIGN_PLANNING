# Tên file: scripts/migrate_drawing_notes.py
# CHỨC NĂNG: Thêm cột notes (ghi chú) vào bảng drawings trong database
# CHANGELOG:
# - 14:34:36 11/07/2026: [NEW] refactor(ui-modularity): complete modular refactoring of codebase graph tools and adopt UI-Backend Separation rules (Antigravity)
# - 14:30:00 11/07/2026: [NEW] Migration thêm cột notes cho Drawing (Antigravity)

import sys
import os
import logging
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, SessionLocal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("migrate_drawing_notes")


def run_migration() -> bool:
    """Thêm cột notes VARCHAR(500) vào bảng drawings nếu chưa tồn tại.

    Returns:
        bool: True nếu thành công, False nếu thất bại.
    """
    logger.info("Bắt đầu migration: Thêm cột notes vào bảng drawings...")

    db = SessionLocal()
    try:
        is_postgres = engine.dialect.name == "postgresql"

        if is_postgres:
            check_sql = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='drawings' AND column_name='notes';
            """
            res = db.execute(text(check_sql)).fetchone()
            if not res:
                logger.info("Thêm cột notes vào bảng drawings (PostgreSQL)...")
                db.execute(
                    text("ALTER TABLE drawings ADD COLUMN notes VARCHAR(500);")
                )
                db.commit()
                logger.info("Thêm cột notes thành công.")
            else:
                logger.info("Cột notes đã tồn tại trong bảng drawings.")
        else:
            # SQLite local
            res = db.execute(text("PRAGMA table_info(drawings);")).fetchall()
            cols = [r[1] for r in res]
            if "notes" not in cols:
                logger.info("Thêm cột notes vào bảng drawings (SQLite)...")
                db.execute(
                    text(
                        "ALTER TABLE drawings ADD COLUMN notes VARCHAR(500);"
                    )
                )
                db.commit()
                logger.info("Thêm cột notes thành công.")
            else:
                logger.info("Cột notes đã tồn tại trong bảng drawings.")

        return True
    except Exception as e:
        db.rollback()
        logger.error(
            "Lỗi khi ALTER TABLE drawings: %s", str(e), exc_info=True
        )
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
