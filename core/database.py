# Tên file: core/database.py
# CHỨC NĂNG: Cấu hình SQLAlchemy kết nối PostgreSQL (hoặc SQLite dự phòng)
# CHANGELOG:
# - 10:57:17 15/07/2026: [REFACTOR] refactor(report): modularize report service and implement visual drawing timeline (Antigravity)
# - 10:45:00 15/07/2026: [UPDATE] Sử dụng Direct Connection (cổng 5432) cho di trú DDL của Supabase Pooler để tránh treo lock (Lê Thanh Vân/Antigravity)
# - 10:27:00 15/07/2026: [UPDATE] Tích hợp lớp SafeSession ghi đè close() để tránh crash app do lỗi rớt kết nối SSL (Lê Thanh Vân/Antigravity)
# - 09:44:00 15/07/2026: [UPDATE] Thêm logic dọn dẹp kết nối cũ và lock_timeout để tránh treo di trú (Lê Thanh Vân/Antigravity)
# - 09:23:00 15/07/2026: [UPDATE] Cấu hình NullPool cho PostgreSQL engine nhằm ngắt kết nối ngay khi đóng session, giải quyết lỗi EMAXCONNSESSION (Lê Thanh Vân/Antigravity)
# - 09:21:00 15/07/2026: [REFACTOR] Đóng gói di trú CSDL vào hàm run_migrations để tránh import-time execution làm treo app (Lê Thanh Vân/Antigravity)
# - 09:08:00 15/07/2026: [UPDATE] Bổ sung tự động di trú cho released_at và factory_transferred_at vào bảng drawings (Lê Thanh Vân/Antigravity)
# - 14:35:51 13/07/2026: [UPDATE] feat(drawing-ui): integrate auto google drive file/folder upload and auto fill link during drawing release (Antigravity)
# - 13:38:53 08/07/2026: [UPDATE] feat(db): add script to enable Row-Level Security and update code graph (Antigravity)
# - 13:30:00 08/07/2026: [REFACTOR] Loại bỏ logging.basicConfig() cục bộ để tránh ghi đè cấu hình logging của file chính (Lê Thanh Vân/Antigravity)
# - 13:21:00 08/07/2026: [UPDATE] Cấu hình connect_timeout cho engine kết nối PostgreSQL để tránh treo vô hạn khi mạng lỗi (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:43:00 02/07/2026: [FIX] Bổ sung Type Hints kiểu trả về cho hàm get_db (Lê Thanh Vân/Antigravity)
# - 10:58:00 02/07/2026: [NEW] Thiết lập kết nối cơ sở dữ liệu SQLAlchemy (Lê Thanh Vân/Antigravity)

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Session as BaseSession,
    Session,
)
from sqlalchemy.pool import NullPool

from config import DATABASE_URL

logger = logging.getLogger(__name__)


# Khởi tạo engine kết nối
# Đối với PostgreSQL, do Supabase giới hạn kết nối nghiêm ngặt (pool_size: 15 trong session mode),
# ta sử dụng NullPool để giải phóng kết nối ngay lập tức sau khi đóng Session,
# tránh hiện tượng tích lũy kết nối gây lỗi EMAXCONNSESSION.
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        connect_args={"connect_timeout": 10},
    )
else:
    # Đối với SQLite local
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# Định nghĩa custom Session để bắt và bỏ qua lỗi đóng kết nối vật lý đã chết
class SafeSession(BaseSession):
    def close(self) -> None:
        """Ghi đè phương thức close để bắt lỗi SSL connection closed unexpectedly."""
        try:
            super().close()
        except Exception as e:
            logger.debug(
                "Database: Bỏ qua lỗi đóng session không mong muốn (SSL closed): %s",
                str(e),
            )


# Khởi tạo session factory dùng SafeSession
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=SafeSession
)

# Khởi tạo Base class cho các Model kế thừa
Base = declarative_base()

# Các biến cờ toàn cục theo dõi xem các cột mới đã được di trú thành công trong database thật hay chưa.
# Nếu chưa được di trú (do tranh chấp lock trên Supabase), ORM listener sẽ tự động defer các cột này để tránh lỗi crash UndefinedColumn.
HAS_RELEASED_AT = False
HAS_FACTORY_TRANSFERRED_AT = False


def get_db() -> Generator[Session, None, None]:
    """Generator tạo session kết nối DB và tự động đóng sau khi hoàn thành.

    Yields:
        Session: Đối tượng Session của SQLAlchemy để thao tác DB.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Chạy các câu lệnh di trú cơ sở dữ liệu gọn nhẹ để cập nhật cấu trúc bảng."""
    global HAS_RELEASED_AT, HAS_FACTORY_TRANSFERRED_AT
    logger.info("Bắt đầu tiến trình kiểm tra và di trú cơ sở dữ liệu...")

    # Tạo connection string trực tiếp qua cổng 5432 nếu là Supabase Pooler để tránh lỗi Transaction Mode DDL
    migration_url = DATABASE_URL
    if "pooler.supabase.com" in migration_url:
        migration_url = migration_url.replace(":6543", ":5432")

    from sqlalchemy import create_engine

    migration_engine = create_engine(migration_url)

    try:
        from sqlalchemy import text

        # Giải phóng các session cũ đang ở trạng thái idle/idle in transaction trên Postgres
        # để dọn dẹp các lock cũ bị treo từ các lần tắt nóng trước đó.
        if migration_url.startswith("postgresql"):
            try:
                with migration_engine.begin() as conn:
                    # Thiết lập lock_timeout ngắn 5 giây cho session di trú này
                    conn.execute(text("SET lock_timeout = '5000';"))
                    # Kill các process cũ của cơ sở dữ liệu hiện tại ngoại trừ process này
                    conn.execute(
                        text(
                            """
                        SELECT pg_terminate_backend(pid)
                        FROM pg_stat_activity
                        WHERE datname = current_database()
                          AND pid <> pg_backend_pid()
                          AND state in ('idle', 'idle in transaction');
                    """
                        )
                    )
                logger.info(
                    "Database migration: Đã dọn dẹp các session cũ bị treo để giải phóng Locks."
                )
            except Exception as e:
                logger.debug(
                    "Database migration: Không thể dọn dẹp session cũ (Hành vi phân quyền bình thường của Supabase): %s",
                    str(e),
                )

        with migration_engine.begin() as conn:
            # Thiết lập lock_timeout ngắn 5 giây cho các câu lệnh trên connection này
            if migration_url.startswith("postgresql"):
                conn.execute(text("SET lock_timeout = '5000';"))

            # Lấy danh sách bảng hiện tại trong DB
            if migration_url.startswith("postgresql"):
                res = conn.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
                    )
                )
                tables = [row[0] for row in res.fetchall()]
            else:
                res = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table';")
                )
                tables = [row[0] for row in res.fetchall()]

            # Kiểm tra bảng projects
            if "projects" in tables:
                if migration_url.startswith("postgresql"):
                    res = conn.execute(
                        text(
                            "SELECT column_name FROM information_schema.columns WHERE table_name = 'projects';"
                        )
                    )
                    proj_cols = [row[0] for row in res.fetchall()]
                else:
                    res = conn.execute(text("PRAGMA table_info(projects);"))
                    proj_cols = [row[1] for row in res.fetchall()]

                if "local_path" not in proj_cols:
                    conn.execute(
                        text("ALTER TABLE projects ADD COLUMN local_path VARCHAR(500);")
                    )
                    logger.info(
                        "Database migration: Đã thêm cột local_path vào bảng projects."
                    )

            # Kiểm tra bảng drawings
            if "drawings" in tables:
                if migration_url.startswith("postgresql"):
                    res = conn.execute(
                        text(
                            "SELECT column_name FROM information_schema.columns WHERE table_name = 'drawings';"
                        )
                    )
                    draw_cols = [row[0] for row in res.fetchall()]
                else:
                    res = conn.execute(text("PRAGMA table_info(drawings);"))
                    draw_cols = [row[1] for row in res.fetchall()]

                # Xử lý cột released_at
                if "released_at" in draw_cols:
                    HAS_RELEASED_AT = True
                else:
                    try:
                        conn.execute(
                            text(
                                "ALTER TABLE drawings ADD COLUMN released_at TIMESTAMP;"
                            )
                        )
                        HAS_RELEASED_AT = True
                        logger.info(
                            "Database migration: Đã thêm cột released_at vào bảng drawings."
                        )
                    except Exception as e:
                        logger.warning(
                            "Database migration: Không thể thêm cột released_at (do dính lock): %s",
                            str(e),
                        )

                # Xử lý cột factory_transferred_at
                if "factory_transferred_at" in draw_cols:
                    HAS_FACTORY_TRANSFERRED_AT = True
                else:
                    try:
                        conn.execute(
                            text(
                                "ALTER TABLE drawings ADD COLUMN factory_transferred_at TIMESTAMP;"
                            )
                        )
                        HAS_FACTORY_TRANSFERRED_AT = True
                        logger.info(
                            "Database migration: Đã thêm cột factory_transferred_at vào bảng drawings."
                        )
                    except Exception as e:
                        logger.warning(
                            "Database migration: Không thể thêm cột factory_transferred_at (do dính lock): %s",
                            str(e),
                        )
        logger.info("Database migration: Hoàn thành tiến trình di trú cơ sở dữ liệu.")
    except Exception as e:
        logger.error("Lỗi khi chạy di trú tự động database: %s", str(e))
    finally:
        migration_engine.dispose()
        logger.info("Đã giải phóng connection pool của migration engine.")
