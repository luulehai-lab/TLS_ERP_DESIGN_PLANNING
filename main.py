# Tên file: main.py
# CHỨC NĂNG: Điểm khởi chạy ứng dụng PyQt6 ERP TK-KH (Tuấn Long Steel)
# CHANGELOG:
# - 16:40:16 08/07/2026: [UPDATE] feat(auth): add Google OAuth2 login with department-based access control (Antigravity)
# - 16:35:00 08/07/2026: [UPDATE] Khởi chạy DatabasePrewarmerThread ngay khi bật app để tối ưu hiệu năng kết nối (Lê Thanh Vân/Antigravity)
# - 14:13:50 08/07/2026: [UPDATE] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 14:25:00 08/07/2026: [UPDATE] Tích hợp màn hình LoginWindow và định tuyến đăng nhập/phân quyền/đăng xuất (Lê Thanh Vân/Antigravity)
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
from ui.login_window import LoginWindow  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


def main() -> None:
    """Hàm khởi động chính của chương trình.

    Thiết lập đối tượng ứng dụng PyQt6, nạp giao diện đăng nhập (LoginWindow)
    và điều phối chuyển đổi sang giao diện chính (MainWindow) khi xác thực thành công.
    """
    logger.info("Khởi động ứng dụng ERP TK-KH TLS...")
    try:
        app = QApplication(sys.argv)

        # Thiết lập style tổng thể của hệ thống cho đồng bộ
        app.setStyle("Fusion")

        # Khởi chạy tiến trình làm nóng Connection Pool database ngầm ở background
        from ui.common.workers import DatabasePrewarmerThread

        prewarmer = DatabasePrewarmerThread()
        prewarmer.start()
        # Giữ tham chiếu của thread để tránh bị bộ thu gom rác giải phóng sớm
        app.db_prewarmer = prewarmer  # type: ignore

        login_win = LoginWindow()
        main_win: MainWindow | None = None

        def on_login_success(email: str, dept: str) -> None:
            """Callback xử lý khi đăng nhập thành công từ LoginWindow."""
            nonlocal main_win
            logger.info("Nhận callback đăng nhập thành công. Khởi tạo MainWindow...")

            # Khởi tạo MainWindow với email và phòng ban đã được xác thực
            main_win = MainWindow(user_email=email, user_dept=dept)
            main_win.logout_clicked.connect(on_logout_requested)

            login_win.hide()
            main_win.show()

        def on_logout_requested() -> None:
            """Callback xử lý khi người dùng click đăng xuất từ MainWindow."""
            nonlocal main_win
            logger.info("Nhận yêu cầu đăng xuất. Quay về LoginWindow...")
            if main_win:
                main_win.close()
                main_win = None
            login_win.show()

        # Kết nối sự kiện đăng nhập thành công
        login_win.login_success.connect(on_login_success)
        login_win.show()

        logger.info(
            "Ứng dụng PyQt6 hiển thị cửa sổ Đăng nhập thành công. Bắt đầu vòng lặp sự kiện."
        )
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(
            "Ứng dụng dừng đột ngột do lỗi nghiêm trọng: %s", str(e), exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
