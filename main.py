# Tên file: main.py
# CHỨC NĂNG: Điểm khởi chạy ứng dụng PyQt6 ERP TK-KH (Tuấn Long Steel)
# CHANGELOG:
# - 13:38:53 08/07/2026: [UPDATE] feat(db): add script to enable Row-Level Security and update code graph (Antigravity)
# - 13:32:00 08/07/2026: [UPDATE] Cấu hình logging lên đầu file và sử dụng RotatingFileHandler trong thư mục logs/ để tránh lỗi mất log và phình file (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:40:00 02/07/2026: [NEW] Khởi tạo tệp khởi chạy chính của ứng dụng PyQt6 (Lê Thanh Vân/Antigravity)

import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Cấu hình logging toàn cục sớm nhất có thể trước khi các module khác được import
BASE_DIR = Path(__file__).parent.resolve()
log_dir = BASE_DIR / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app_run.log"

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = RotatingFileHandler(
    log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[stream_handler, file_handler],
)
logger = logging.getLogger("main")

from PyQt6.QtWidgets import QApplication  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


def main() -> None:
    """Hàm khởi động chính của chương trình.

    Thiết lập đối tượng ứng dụng PyQt6, nạp giao diện chính
    và bắt đầu vòng lặp xử lý sự kiện giao diện.
    """
    logger.info("Khởi động ứng dụng ERP TK-KH TLS...")
    try:
        app = QApplication(sys.argv)

        # Thiết lập style tổng thể của hệ thống cho đồng bộ
        app.setStyle("Fusion")

        window = MainWindow()
        window.show()

        logger.info("Ứng dụng PyQt6 hiển thị thành công. Bắt đầu vòng lặp sự kiện.")
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(
            "Ứng dụng dừng đột ngột do lỗi nghiêm trọng: %s", str(e), exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
