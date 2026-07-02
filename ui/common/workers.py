# Tên file: ui/common/workers.py
# CHỨC NĂNG: Khai báo các luồng phụ xử lý bất đồng bộ (QThread Workers)
# CHANGELOG:
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:32:00 02/07/2026: [NEW] Khởi tạo luồng phụ tải bản vẽ ngầm tránh block UI Thread (Lê Thanh Vân/Antigravity)

import logging
from PyQt6.QtCore import QThread, pyqtSignal

from core.database import SessionLocal
from core.services import drawing_service

logger = logging.getLogger(__name__)


class DrawingLoaderThread(QThread):
    """Luồng phụ chuyên trách tải danh sách bản vẽ từ cơ sở dữ liệu cloud.

    Giúp giao diện người dùng (UI Thread) luôn mượt mà và phản hồi ngay lập tức
    khi thay đổi dự án được chọn trên Sidebar.
    """

    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, project_id: str) -> None:
        """Khởi tạo luồng tải bản vẽ ngầm.

        Args:
            project_id: Mã dự án cần truy vấn danh sách bản vẽ.
        """
        super().__init__()
        self.project_id = project_id

    def run(self) -> None:
        """Thực thi câu lệnh truy vấn ở luồng phụ."""
        logger.info("Bắt đầu tải bản vẽ ngầm cho dự án: %s", self.project_id)
        db = SessionLocal()
        try:
            drawings = drawing_service.get_project_drawings(db, self.project_id)

            # Bóc tách sang danh sách dict thô để truyền an toàn qua Signal,
            # tránh DetachedInstanceError khi session bị đóng.
            raw_drawings = []
            for d in drawings:
                raw_drawings.append(
                    {
                        "drawing_id": d.drawing_id,
                        "drawing_name": d.drawing_name,
                        "status": d.status,
                        "current_version": d.current_version,
                        "drive_link": d.drive_link,
                        "updated_at": d.updated_at,
                    }
                )

            logger.info(
                "Tải xong bản vẽ ngầm cho dự án: %s (Tìm thấy %d bản vẽ)",
                self.project_id,
                len(raw_drawings),
            )
            self.finished.emit(raw_drawings)
        except Exception as e:
            logger.error(
                "Lỗi trong lúc truy vấn bản vẽ ở luồng phụ cho dự án '%s': %s",
                self.project_id,
                str(e),
                exc_info=True,
            )
            self.error.emit(str(e))
        finally:
            db.close()
