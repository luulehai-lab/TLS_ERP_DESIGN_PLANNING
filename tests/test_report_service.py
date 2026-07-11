# Tên file: tests/test_report_service.py
# CHỨC NĂNG: Unit test cho tầng nghiệp vụ báo cáo thống kê report_service.py
# CHANGELOG:
# - 18:49:30 11/07/2026: [NEW] feat(drawing-version-qr): implement drawing revision logic and dynamic QR code panel (Antigravity)
# - 18:25:00 11/07/2026: [NEW] Khởi tạo unit tests cho report_service.py có phân quyền dữ liệu (Lê Thanh Vân/Antigravity)

import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models import Project, ProjectSection, Drawing, DrawingLog, Staff
from core.services.report_service import (
    get_drawing_status_stats,
    get_section_drawing_stats,
    get_designer_productivity_stats,
    get_release_timeline_stats,
)


class TestReportService(unittest.TestCase):
    """Kiểm thử tính năng thống kê và phân quyền lọc dữ liệu báo cáo."""

    def setUp(self) -> None:
        """Thiết lập môi trường database giả lập SQLite in-memory."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.db = self.SessionLocal()

        # 1. Khởi tạo danh sách nhân sự staffs
        self.db.add_all(
            [
                Staff(name="Anh Lưu", email="luu.lehai@gmail.com", role="Admin"),
                Staff(
                    name="Kế Hoạch",
                    email="phongkehoachkythuat25@gmail.com",
                    role="Kế hoạch",
                ),
                Staff(name="Trịnh Thiết Kế", email="trinh@tls.vn", role="Thiết kế"),
                Staff(name="Hà Thiết Kế", email="ha@tls.vn", role="Thiết kế"),
                Staff(name="Phúc Sales", email="phuc@tls.vn", role="Kinh doanh"),
            ]
        )

        # 2. Khởi tạo dự án mẫu
        self.project_id = "PROJ_REP"
        self.db.add(
            Project(
                project_id=self.project_id,
                project_name="Dự án Báo Cáo",
                status="Đang chạy",
                sales_email="phuc@tls.vn",
            )
        )
        self.db.commit()

        # 3. Khởi tạo Hạng mục
        self.sec_nx1 = ProjectSection(
            project_id=self.project_id,
            section_code="NX1",
            section_name="Nhà xưởng 1",
            designer_email="trinh@tls.vn",
        )
        self.sec_nx2 = ProjectSection(
            project_id=self.project_id,
            section_code="NX2",
            section_name="Nhà xưởng 2",
            designer_email="ha@tls.vn",
        )
        self.db.add_all([self.sec_nx1, self.sec_nx2])
        self.db.commit()

        # 4. Khởi tạo Bản vẽ mẫu
        # Trịnh phụ trách NX1 có 2 bản vẽ: 1 Chờ triển khai, 1 Đang sản xuất
        # Hà phụ trách NX2 có 1 bản vẽ: Đã hoàn thành
        # Có 1 bản vẽ chung: Chờ triển khai (section_id = None)
        self.db.add_all(
            [
                Drawing(
                    drawing_id="VL-NX1-01",
                    project_id=self.project_id,
                    drawing_name="Mặt bằng NX1",
                    status="Chờ triển khai",
                    section_id=self.sec_nx1.section_id,
                    current_version="V1",
                ),
                Drawing(
                    drawing_id="VL-NX1-02",
                    project_id=self.project_id,
                    drawing_name="Mặt cắt NX1",
                    status="Đang sản xuất",
                    section_id=self.sec_nx1.section_id,
                    current_version="V1",
                ),
                Drawing(
                    drawing_id="VL-NX2-01",
                    project_id=self.project_id,
                    drawing_name="Chi tiết NX2",
                    status="Đã hoàn thành",
                    section_id=self.sec_nx2.section_id,
                    current_version="V1",
                ),
                Drawing(
                    drawing_id="VL-CHUNG-01",
                    project_id=self.project_id,
                    drawing_name="Bản vẽ chung",
                    status="Chờ triển khai",
                    section_id=None,
                    current_version="V1",
                ),
            ]
        )
        self.db.commit()

        # 5. Ghi nhận logs "Ban hành" để phục vụ timeline chart
        self.db.add_all(
            [
                DrawingLog(
                    drawing_id="VL-NX1-01",
                    version="V1",
                    action="Ban hành",
                    performed_by="trinh@tls.vn",
                    timestamp=datetime(2026, 7, 10, 8, 0, 0),
                ),
                DrawingLog(
                    drawing_id="VL-NX1-02",
                    version="V1",
                    action="Ban hành",
                    performed_by="trinh@tls.vn",
                    timestamp=datetime(2026, 7, 11, 9, 0, 0),
                ),
                DrawingLog(
                    drawing_id="VL-NX2-01",
                    version="V1",
                    action="Ban hành",
                    performed_by="ha@tls.vn",
                    timestamp=datetime(2026, 7, 11, 10, 0, 0),
                ),
            ]
        )
        self.db.commit()

    def tearDown(self) -> None:
        """Dọn dẹp database sau kiểm thử."""
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_admin_sees_all_drawing_status_stats(self) -> None:
        """Admin (Anh Lưu) phải thấy toàn bộ trạng thái bản vẽ."""
        stats = get_drawing_status_stats(
            self.db, self.project_id, "luu.lehai@gmail.com"
        )
        self.assertEqual(stats["Chờ triển khai"], 2)  # VL-NX1-01 + VL-CHUNG-01
        self.assertEqual(stats["Đang sản xuất"], 1)  # VL-NX1-02
        self.assertEqual(stats["Đã hoàn thành"], 1)  # VL-NX2-01

    def test_designer_sees_restricted_drawing_status_stats(self) -> None:
        """Designer Trịnh chỉ thấy bản vẽ của mình phụ trách + bản vẽ chung."""
        stats = get_drawing_status_stats(self.db, self.project_id, "trinh@tls.vn")
        # Bản vẽ Trịnh thấy: VL-NX1-01 (Chờ TK), VL-NX1-02 (Đang SX), VL-CHUNG-01 (Chờ TK)
        self.assertEqual(stats["Chờ triển khai"], 2)
        self.assertEqual(stats["Đang sản xuất"], 1)
        self.assertEqual(stats["Đã hoàn thành"], 0)  # NX2 của Hà ➔ 0

    def test_section_stats_filtering_for_designer(self) -> None:
        """Kiểm tra thống kê hạng mục bị lọc theo designer phụ trách."""
        # Trịnh xem hạng mục
        stats_trinh = get_section_drawing_stats(
            self.db, self.project_id, "trinh@tls.vn"
        )
        # Chỉ được trả về hạng mục NX1 + mục CHUNG (nếu có bản vẽ chung)
        codes = [s["section_code"] for s in stats_trinh]
        self.assertIn("NX1", codes)
        self.assertIn("CHUNG", codes)
        self.assertNotIn("NX2", codes)  # Hạng mục NX2 của Hà phải bị lọc bỏ

    def test_designer_productivity_stats(self) -> None:
        """Kiểm tra thống kê năng suất kỹ sư thiết kế."""
        # Admin xem năng suất thiết kế của dự án
        stats_admin = get_designer_productivity_stats(
            self.db, self.project_id, "luu.lehai@gmail.com"
        )
        self.assertEqual(len(stats_admin), 2)  # Trịnh và Hà

        # Designer Trịnh chỉ được xem năng suất của chính mình
        stats_trinh = get_designer_productivity_stats(
            self.db, self.project_id, "trinh@tls.vn"
        )
        self.assertEqual(len(stats_trinh), 1)
        self.assertEqual(stats_trinh[0]["designer_email"], "trinh@tls.vn")
        self.assertEqual(stats_trinh[0]["total"], 2)

    def test_release_timeline_stats_filtering(self) -> None:
        """Kiểm tra thống kê tiến độ ban hành theo thời gian có lọc quyền."""
        # Designer Hà chỉ thấy log ban hành bản vẽ của mình (ngày 11/07)
        timeline_ha = get_release_timeline_stats(self.db, self.project_id, "ha@tls.vn")
        self.assertEqual(len(timeline_ha), 1)
        self.assertEqual(timeline_ha[0]["date"], "2026-07-11")
        self.assertEqual(timeline_ha[0]["count"], 1)
