# Tên file: tests/test_revise_drawing.py
# CHỨC NĂNG: Unit test cho tính năng nâng cấp phiên bản bản vẽ (Revise Drawing) và ghi logs
# CHANGELOG:
# - 18:09:38 11/07/2026: [NEW] feat(drawing-ui): add version input field to drawing release form and update backend (Antigravity)
# - 18:15:00 11/07/2026: [NEW] Viết unit tests kiểm thử hàm revise_drawing ở backend (Lê Thanh Vân/Antigravity)

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models import Project, DrawingLog
from core.services.drawing_service import create_drawing, revise_drawing


class TestDrawingRevision(unittest.TestCase):
    """Kiểm thử tính năng Revise (cập nhật phiên bản) bản vẽ."""

    def setUp(self) -> None:
        """Thiết lập database SQLite in-memory cho môi trường test."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.db = self.SessionLocal()

        # Tạo dự án giả lập
        self.project_id = "PROJ_TEST"
        db_proj = Project(
            project_id=self.project_id,
            project_name="Dự án Test",
            status="Đang chạy",
        )
        self.db.add(db_proj)
        self.db.commit()

    def tearDown(self) -> None:
        """Dọn dẹp database sau khi test xong."""
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_create_and_revise_drawing(self) -> None:
        """Kiểm thử chu trình ban hành V1 và nâng cấp lên V2."""
        # 1. Ban hành V1
        draw_data = {
            "drawing_id": "TLS-D01",
            "drawing_name": "Mặt bằng cột",
            "current_version": "V1",
            "notes": "Ban hành ban đầu",
            "drive_link": "https://drive.google.com/file1",
        }
        draw = create_drawing(self.db, self.project_id, draw_data)
        self.assertIsNotNone(draw)
        self.assertEqual(draw.current_version, "V1")

        # Kiểm tra log khởi tạo
        logs = self.db.query(DrawingLog).filter_by(drawing_id="TLS-D01").all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].version, "V1")
        self.assertEqual(logs[0].action, "Ban hành")

        # 2. Thực hiện Revise lên V2
        revise_data = {
            "current_version": "V2",
            "notes": "Thay đổi chiều cao cột",
            "drive_link": "https://drive.google.com/file2",
            "performed_by": "ha91steel@gmail.com",
        }
        updated_draw = revise_drawing(self.db, "TLS-D01", revise_data)
        self.assertIsNotNone(updated_draw)
        self.assertEqual(updated_draw.current_version, "V2")
        self.assertEqual(updated_draw.drive_link, "https://drive.google.com/file2")

        # Kiểm tra log cập nhật
        logs = (
            self.db.query(DrawingLog)
            .filter_by(drawing_id="TLS-D01")
            .order_by(DrawingLog.log_id.asc())
            .all()
        )
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[1].version, "V2")
        self.assertEqual(logs[1].action, "Nâng cấp phiên bản: V1 -> V2")
        self.assertEqual(logs[1].performed_by, "ha91steel@gmail.com")
        self.assertIn("Link cũ: https://drive.google.com/file1", logs[1].note)
        self.assertIn("Ghi chú mới: Thay đổi chiều cao cột", logs[1].note)
