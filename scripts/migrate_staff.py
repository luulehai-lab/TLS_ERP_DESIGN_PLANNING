# Tên file: scripts/migrate_staff.py
# CHỨC NĂNG: Khởi tạo bảng staffs trong cơ sở dữ liệu và seed dữ liệu nhân sự thực tế
# CHANGELOG:
# - 17:07:37 11/07/2026: [NEW] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 16:45:00 11/07/2026: [NEW] Khởi tạo script di cư dữ liệu staffs (Antigravity)

import logging
import sys
from pathlib import Path

# Thêm thư mục gốc vào path để import các module nội bộ
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.database import Base, engine, SessionLocal  # noqa: E402
from core.models import Staff  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrate_staff")


def migrate() -> None:
    """Tạo bảng staffs và seed dữ liệu nhân sự thực tế."""
    logger.info("Đang tạo bảng staffs...")
    # Chỉ tạo bảng staffs nếu chưa có
    Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables["staffs"]])
    logger.info("Đã tạo bảng staffs thành công.")

    db = SessionLocal()
    try:
        # Kiểm tra xem đã có dữ liệu chưa để tránh trùng lặp
        if db.query(Staff).first() is not None:
            logger.info("Bảng staffs đã có dữ liệu. Bỏ qua seeding.")
            return

        logger.info("Bắt đầu seeding dữ liệu nhân sự thực tế...")

        staff_data = [
            # Admin
            {"name": "Lê Hải Lưu", "email": "luu.lehai@gmail.com", "role": "Admin"},
            # Kinh doanh (Sales)
            {
                "name": "Nguyễn Văn Quân",
                "email": "quanxu23@gmail.com",
                "role": "Kinh doanh",
            },
            {
                "name": "Trịnh Văn Phúc",
                "email": "vanphuctrinh2211@gmail.com",
                "role": "Kinh doanh",
            },
            # Thiết kế (Designers)
            {
                "name": "Vũ Thanh Hà",
                "email": "ha91steel@gmail.com",
                "role": "Thiết kế",
            },
            {
                "name": "Nguyễn Văn Trịnh",
                "email": "trinh58xd2@gmail.com",
                "role": "Thiết kế",
            },
            # Kế hoạch (Planning)
            {
                "name": "Trần Mạnh Linh",
                "email": "linh.tran@tls.vn",
                "role": "Kế hoạch",
            },
            {
                "name": "Nguyễn Hồng Thái",
                "email": "thai.nguyen@tls.vn",
                "role": "Kế hoạch",
            },
            {
                "name": "Nguyễn Mạnh Tuấn",
                "email": "tuan.nguyen@tls.vn",
                "role": "Kế hoạch",
            },
            {
                "name": "Lê Viết Hiệu",
                "email": "hieu.le@tls.vn",
                "role": "Kế hoạch",
            },
            # Email chung phòng Kế hoạch
            {
                "name": "Phòng Kế Hoạch",
                "email": "phongkehoachkythuat25@gmail.com",
                "role": "Kế hoạch",
            },
        ]

        for s_dict in staff_data:
            staff = Staff(**s_dict)
            db.add(staff)

        db.commit()
        logger.info("Đã seed thành công %d nhân sự vào database.", len(staff_data))

    except Exception as e:
        db.rollback()
        logger.error("Lỗi trong quá trình di cư dữ liệu: %s", str(e), exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
