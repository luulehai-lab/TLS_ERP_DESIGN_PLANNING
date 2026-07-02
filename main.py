# Tên file: main.py
# CHỨC NĂNG: Điểm khởi chạy ứng dụng PyQt6 ERP TK-KH (Tuấn Long Steel)
# CHANGELOG:
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:40:00 02/07/2026: [NEW] Khởi tạo tệp khởi chạy chính của ứng dụng PyQt6 (Lê Thanh Vân/Antigravity)

import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

# Cấu hình logging toàn cục cho ứng dụng
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app_run.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


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
