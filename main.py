# Tên file: main.py
# CHỨC NĂNG: Điểm khởi chạy ứng dụng PyQt6 ERP TK-KH (Tuấn Long Steel)
# CHANGELOG:
# - 10:57:17 15/07/2026: [REFACTOR] refactor(report): modularize report service and implement visual drawing timeline (Antigravity)
# - 09:34:00 15/07/2026: [UPDATE] Gọi run_migrations() đồng bộ ngay khi khởi chạy app để tránh race condition thiếu cột (Lê Thanh Vân/Antigravity)
# - 09:42:18 13/07/2026: [FIX] feat(report): add visual report dashboard with charts, fix combobox/permission bugs and install global exception hook (Antigravity)
# - 18:49:30 11/07/2026: [UPDATE] feat(drawing-version-qr): implement drawing revision logic and dynamic QR code panel (Antigravity)
# - 18:40:00 11/07/2026: [FIX] Thêm sys.excepthook toàn cục để ghi mọi unhandled exception vào app_run.log (Lê Thanh Vân/Antigravity)
# - 18:24:00 11/07/2026: [UPDATE] Cải tiến cơ chế log: Di chuyển import vào try/except block của main() và bắt lỗi module-level để ghi vào app_run.log (Lê Thanh Vân/Antigravity)
# - 17:07:37 11/07/2026: [UPDATE] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 15:17:43 11/07/2026: [UPDATE] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 12:35:53 10/07/2026: [FIX] fix(ui): convert database UTC time representation to GMT+7 local time for display (Antigravity)
# - 15:14:00 11/07/2026: [UPDATE] Kiểm tra whitelist email khi auto-login từ session cũ (Antigravity)
# - 12:40:00 10/07/2026: [UPDATE] Tích hợp SessionManager hỗ trợ tự động đăng nhập và đăng xuất (Lê Thanh Vân/Antigravity)
# - 16:40:16 08/07/2026: [UPDATE] feat(auth): add Google OAuth2 login with department-based access control (Antigravity)
# - 16:35:00 08/07/2026: [UPDATE] Khởi chạy DatabasePrewarmerThread ngay khi bật app để tối ưu hiệu năng kết nối (Lê Thanh Vân/Antigravity)
# - 14:13:50 08/07/2026: [UPDATE] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 14:25:00 08/07/2026: [UPDATE] Tích hợp màn hình LoginWindow và định tuyến đăng nhập/phân quyền/đăng xuất (Lê Thanh Vân/Antigravity)
# - 13:38:53 08/07/2026: [UPDATE] feat(db): add script to enable Row-Level Security and update code graph (Antigravity)
# - 13:32:00 08/07/2026: [UPDATE] Cấu hình logging lên đầu file và sử dụng RotatingFileHandler trong thư mục logs/ để tránh lỗi mất log và phình file (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:40:00 02/07/2026: [NEW] Khởi tạo tệp khởi chạy chính của ứng dụng PyQt6 (Lê Thanh Vân/Antigravity)

import logging
import sys
from core.logging_bootstrap import bootstrap_logging

# Khởi tạo hệ thống logging toàn cục sớm nhất, bắt unhandled crash và redirect stdout/stderr
bootstrap_logging(log_file="app_run.log")

logger = logging.getLogger("main")


def main() -> None:
    """Hàm khởi động chính của chương trình.

    Thiết lập đối tượng ứng dụng PyQt6, nạp giao diện đăng nhập (LoginWindow)
    và điều phối chuyển đổi sang giao diện chính (MainWindow) khi xác thực thành công.
    """
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.login_window import LoginWindow
        from ui.main_window import MainWindow
        from core.services.session_manager import SessionManager
        from core.services.project_service import is_email_authorized

        logger.info("Khởi động ứng dụng ERP TK-KH TLS...")
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

            # Lưu phiên đăng nhập
            SessionManager.save_session(email, dept)

            # Khởi tạo MainWindow với email và phòng ban đã được xác thực
            main_win = MainWindow(user_email=email, user_dept=dept)
            main_win.logout_clicked.connect(on_logout_requested)

            login_win.hide()
            main_win.show()

        def on_logout_requested() -> None:
            """Callback xử lý khi người dùng click đăng xuất từ MainWindow."""
            nonlocal main_win
            logger.info("Nhận yêu cầu đăng xuất. Quay về LoginWindow...")

            # Xóa phiên đăng nhập
            SessionManager.clear_session()

            if main_win:
                main_win.close()
                main_win = None
            login_win.show()

        # Kết nối sự kiện đăng nhập thành công
        login_win.login_success.connect(on_login_success)

        session = SessionManager.load_session()
        if session and is_email_authorized(session["email"]):
            from core.services.project_service import get_staff_role

            role = get_staff_role(session["email"])
            dept = "Kế hoạch"
            if role in ["Thiết kế", "Admin", "Kinh doanh"]:
                dept = "Thiết kế"

            logger.info(
                "Phát hiện phiên đăng nhập cũ (%s, Vai trò: %s). Tự động đăng nhập...",
                session["email"],
                role,
            )
            main_win = MainWindow(user_email=session["email"], user_dept=dept)
            main_win.logout_clicked.connect(on_logout_requested)
            main_win.show()
        else:
            if session:
                logger.warning(
                    "Email '%s' không còn quyền truy cập. Xóa session cũ.",
                    session["email"],
                )
                SessionManager.clear_session()
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
    try:
        main()
    except Exception as e:
        logger.critical(
            "Lỗi nghiêm trọng ở cấp độ module khởi chạy: %s", str(e), exc_info=True
        )
        sys.exit(1)
