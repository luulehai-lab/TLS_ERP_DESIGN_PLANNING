# Tên file: scripts/enable_rls.py
# CHỨC NĂNG: Kích hoạt Row-Level Security (RLS) trên các bảng của Supabase để vá lỗ hổng bảo mật
# CHANGELOG:
# - 12:39:43 08/07/2026: [NEW] docs: add project README with overview and setup guide (Antigravity)
# - 12:01:00 08/07/2026: [NEW] Khởi tạo script cấu hình RLS bảo mật database (Lê Thanh Vân/Antigravity)

"""Script tự động bật Row-Level Security (RLS) cho các bảng trong PostgreSQL trên Supabase.

Nhằm bảo vệ dữ liệu dự án khỏi truy cập trái phép qua REST API công cộng của Supabase
nhưng vẫn bảo đảm kết nối direct qua SQLAlchemy hoạt động bình thường.
"""

import logging
import sys
import os
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Thêm thư mục gốc vào PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine

# Thiết lập Logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("enable_rls")

# Danh sách các bảng cần bật RLS
TARGET_TABLES: list[str] = ["projects", "drawings", "drawing_logs", "bom_details"]


def check_rls_status(table_name: str) -> bool:
    """Kiểm tra trạng thái kích hoạt Row-Level Security của một bảng cụ thể.

    Args:
        table_name: Tên của bảng cần kiểm tra trong database.

    Returns:
        bool: True nếu bảng đã được bật RLS, False nếu chưa bật hoặc xảy ra lỗi.
    """
    query = text(
        """
        SELECT relrowsecurity 
        FROM pg_class 
        WHERE oid = :table_name::regclass;
        """
    )
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"table_name": table_name}).scalar()
            return bool(result)
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi kiểm tra trạng thái RLS cho bảng %s: %s",
            table_name,
            str(e),
            exc_info=True,
        )
        return False


def enable_rls_for_tables() -> bool:
    """Thực hiện bật Row-Level Security trên tất cả các bảng đích.

    Returns:
        bool: True nếu tất cả các bảng bật RLS thành công, ngược lại False.
    """
    logger.info("Bắt đầu kích hoạt Row-Level Security (RLS) trên các bảng...")
    all_success = True

    for table in TARGET_TABLES:
        try:
            # Kiểm tra trạng thái hiện tại
            is_enabled = check_rls_status(table)
            if is_enabled:
                logger.info("Bảng '%s' đã được bật RLS từ trước.", table)
                continue

            # Câu lệnh SQL bật RLS
            alter_query = text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

            with engine.connect() as conn:
                # Thực hiện lệnh thay đổi cấu trúc bảng
                conn.execute(alter_query)
                conn.commit()

            # Xác thực lại
            if check_rls_status(table):
                logger.info(
                    "Đã kích hoạt Row-Level Security thành công cho bảng '%s'.",
                    table,
                )
            else:
                logger.error(
                    "Thực thi thành công nhưng kiểm tra lại thấy bảng '%s' vẫn chưa bật RLS.",
                    table,
                )
                all_success = False

        except SQLAlchemyError as e:
            logger.error(
                "Không thể bật Row-Level Security cho bảng '%s': %s",
                table,
                str(e),
                exc_info=True,
            )
            all_success = False

    return all_success


if __name__ == "__main__":
    success = enable_rls_for_tables()
    sys.exit(0 if success else 1)
