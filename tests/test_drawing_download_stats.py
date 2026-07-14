# Tên file: tests/test_drawing_download_stats.py
# CHỨC NĂNG: Unit test cho tính năng ghi log lượt tải và thống kê lượt tải bản vẽ
# CHANGELOG:
# - 11:39:58 14/07/2026: [NEW] fix(drawing-ui): click on drive link column to open in browser for download (Antigravity)
# - 11:29:00 14/07/2026: [NEW] Khởi tạo tệp tin test kiểm thử thống kê lượt tải bản vẽ (Lê Thanh Vân/Antigravity)

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models import Project, Staff
from core.services.drawing_service import create_drawing, log_drawing_download
from core.services.report_service import (
    get_drawing_download_summary,
    get_drawing_download_details,
)


class TestDrawingDownloadStats(unittest.TestCase):
    """Kiểm thử tính năng ghi log và báo cáo thống kê lượt tải bản vẽ."""

    def setUp(self) -> None:
        """Thiết lập database SQLite in-memory cho môi trường test."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.db = self.SessionLocal()

        # Tạo dự án giả lập
        self.project_id = "PROJ_STATS_TEST"
        db_proj = Project(
            project_id=self.project_id,
            project_name="Dự án Test Thống Kê",
            status="Đang chạy",
        )
        self.db.add(db_proj)

        # Tạo nhân sự giả lập phục vụ phân quyền
        self.user_email = "designer_test@gmail.com"
        db_staff = Staff(
            name="Designer Test",
            email=self.user_email,
            role="Thiết kế",
        )
        self.db.add(db_staff)
        self.db.commit()

        # Tạo bản vẽ mẫu
        draw_data = {
            "drawing_id": "TLS-D01",
            "drawing_name": "Mặt bằng cột",
            "current_version": "V1",
            "notes": "Ban hành ban đầu",
            "drive_link": "https://drive.google.com/file1",
        }
        create_drawing(self.db, self.project_id, draw_data)

    def tearDown(self) -> None:
        """Dọn dẹp database sau khi test xong."""
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_log_drawing_download_and_report(self) -> None:
        """Kiểm thử việc ghi nhận log mở link Drive và tính toán thống kê báo cáo."""
        # 1. Ban đầu lượt tải phải bằng 0
        summary = get_drawing_download_summary(
            self.db, self.project_id, self.user_email
        )
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["drawing_id"], "TLS-D01")
        self.assertEqual(summary[0]["download_count"], 0)

        # 2. Ghi nhận lượt tải thứ nhất
        log_drawing_download(
            self.db, "TLS-D01", self.user_email, "User click Link Drive"
        )

        # 3. Ghi nhận lượt tải thứ hai từ người dùng khác
        log_drawing_download(
            self.db, "TLS-D01", "another_user@gmail.com", "User click Link Drive"
        )

        # 4. Xác nhận tổng lượt tải là 2
        summary = get_drawing_download_summary(
            self.db, self.project_id, self.user_email
        )
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["download_count"], 2)

        # 5. Kiểm tra chi tiết lịch sử tải
        details = get_drawing_download_details(self.db, "TLS-D01")
        self.assertEqual(len(details), 2)
        # Sắp xếp theo timestamp giảm dần nên log gần nhất ở đầu
        self.assertEqual(details[0]["performed_by"], "another_user@gmail.com")
        self.assertEqual(details[0]["version"], "V1")
        self.assertEqual(details[0]["note"], "User click Link Drive")

        self.assertEqual(details[1]["performed_by"], self.user_email)
        self.assertEqual(details[1]["version"], "V1")
        self.assertEqual(details[1]["note"], "User click Link Drive")
