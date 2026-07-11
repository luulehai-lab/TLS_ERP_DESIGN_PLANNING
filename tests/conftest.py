# Tên file: tests/conftest.py
# CHỨC NĂNG: Cấu hình chung và Fixtures cho hệ thống Testing (pytest) của ERP.
# CHANGELOG:
# - 17:07:37 11/07/2026: [UPDATE] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 15:17:43 11/07/2026: [NEW] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 14:18:00 11/07/2026: [NEW] Thiết lập môi trường và cấu hình pytest cho ERP. (Antigravity)

import os
import sys

# Thêm project root vào path để có thể import các module nội bộ của ERP
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ghi đè DATABASE_URL sang SQLite in-memory trước khi khởi tạo database engine
os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
import config  # noqa: E402

# Đảm bảo config.DATABASE_URL được cập nhật
config.DATABASE_URL = "sqlite://"

import core.database  # noqa: E402

# Định nghĩa lại engine và SessionLocal trỏ tới in-memory SQLite cho quá trình testing
core.database.engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}
)
core.database.SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=core.database.engine
)

from core.database import Base, engine, SessionLocal  # noqa: E402
from core.models import Staff  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> None:
    """Tạo cấu trúc bảng và seed dữ liệu mẫu cho SQLite in-memory khi bắt đầu session testing."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Seed staffs
        staffs = [
            Staff(name="Lê Hải Lưu", email="luu.lehai@gmail.com", role="Admin"),
            Staff(
                name="Nguyễn Văn Quân", email="quanxu23@gmail.com", role="Kinh doanh"
            ),
            Staff(
                name="Trịnh Văn Phúc",
                email="vanphuctrinh2211@gmail.com",
                role="Kinh doanh",
            ),
            Staff(name="Vũ Thanh Hà", email="ha91steel@gmail.com", role="Thiết kế"),
            Staff(
                name="Nguyễn Văn Trịnh", email="trinh58xd2@gmail.com", role="Thiết kế"
            ),
            Staff(name="Trần Mạnh Linh", email="linh.tran@tls.vn", role="Kế hoạch"),
            Staff(name="Nguyễn Hồng Thái", email="thai.nguyen@tls.vn", role="Kế hoạch"),
            Staff(name="Nguyễn Mạnh Tuấn", email="tuan.nguyen@tls.vn", role="Kế hoạch"),
            Staff(name="Lê Viết Hiệu", email="hieu.le@tls.vn", role="Kế hoạch"),
            Staff(
                name="Phòng Kế Hoạch",
                email="phongkehoachkythuat25@gmail.com",
                role="Kế hoạch",
            ),
        ]
        db.add_all(staffs)
        db.commit()
    finally:
        db.close()
