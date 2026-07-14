# Tên file: tests/test_release_evidence.py
# CHỨC NĂNG: Unit test kiểm thử chức năng sinh ảnh bằng chứng ban hành bản vẽ
# CHANGELOG:
# - 16:43:18 14/07/2026: [UPDATE] feat(drawing-evidence): auto generate release evidence image in local folder (Antigravity)
# - 16:30:00 14/07/2026: [UPDATE] Cập nhật dữ liệu test đầy đủ Mã dự án, Hạng mục, Ghi chú và test kích thước ảnh mới (Lê Thanh Vân/Antigravity)
# - 14:05:01 14/07/2026: [NEW] fix(ui): remove format argument from qr image save for PyPNGImage compatibility (Antigravity)
# - 13:55:00 14/07/2026: [NEW] Khởi tạo unit test cho release_evidence_service (Lê Thanh Vân/Antigravity)

import os
import shutil
import unittest
from datetime import datetime
from PIL import Image

from core.services.release_evidence_service import generate_release_evidence_image


class TestReleaseEvidenceService(unittest.TestCase):
    """Lớp kiểm thử cho dịch vụ sinh ảnh bằng chứng ban hành bản vẽ."""

    def setUp(self) -> None:
        """Thiết lập thư mục tạm phục vụ kiểm thử."""
        self.test_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "temp_evidence_test")
        )
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

        self.dummy_drawing_data = {
            "project_id": "TLS-2026-PRJ01",
            "project_name": "DỰ ÁN NHÀ XƯỞNG TUẤN LONG STEEL - GIAI ĐOẠN 2",
            "section_name": "Hạng mục Khung Kèo thép chính",
            "drawing_id": "TLS-100-DWG-001",
            "drawing_name": "Mặt bằng kết cấu cột và dầm sàn tầng 1",
            "current_version": "V1.0",
            "performed_by": "engineer.van@tuanlongsteel.com.vn",
            "notes": "Ban hành bản vẽ thiết kế cột chi tiết",
            "timestamp": "2026-07-14 13:55:00",
        }

    def tearDown(self) -> None:
        """Dọn dẹp thư mục tạm sau khi chạy test."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_image_success(self) -> None:
        """Kiểm tra sinh ảnh thành công và đúng kích thước, định dạng."""
        # Thực thi sinh ảnh
        filepath = generate_release_evidence_image(
            self.dummy_drawing_data, self.test_dir
        )

        # 1. Đảm bảo file được tạo ra và không rỗng
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".png"))

        # 2. Đảm bảo tên file được đặt đúng quy chuẩn
        filename = os.path.basename(filepath)
        today_str = datetime.now().strftime("%Y%m%d")
        expected_filename = f"_DA_BAN_HANH_REVV1.0_{today_str}.png"
        self.assertEqual(filename, expected_filename)

        # 3. Đảm bảo kích thước ảnh là 800x550
        with Image.open(filepath) as img:
            self.assertEqual(img.size, (800, 550))
            self.assertEqual(img.format, "PNG")


if __name__ == "__main__":
    unittest.main()
