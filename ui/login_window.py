# Tên file: ui/login_window.py
# CHỨC NĂNG: Màn hình Đăng nhập bằng Google cho ứng dụng ERP (Giao diện Slate Premium)
# CHANGELOG:
# - 16:40:16 08/07/2026: [UPDATE] feat(auth): add Google OAuth2 login with department-based access control (Antigravity)
# - 16:35:00 08/07/2026: [FIX] Trì hoãn việc shutdown auth_manager bằng QTimer để tránh deadlock socket (Lê Thanh Vân/Antigravity)
# - 14:13:50 08/07/2026: [NEW] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 14:20:00 08/07/2026: [NEW] Khởi tạo giao diện đăng nhập Google (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import QDesktopServices

from core.services.auth_service import GoogleAuthManager
import config

logger = logging.getLogger(__name__)


class AuthWorkerThread(QThread):
    """Luồng phụ xử lý máy chủ HTTP callback cục bộ và lắng nghe kết quả."""

    finished: pyqtSignal = pyqtSignal(str)
    error: pyqtSignal = pyqtSignal(str)

    def __init__(self, auth_manager: GoogleAuthManager) -> None:
        super().__init__()
        self.auth_manager: GoogleAuthManager = auth_manager
        self._is_running: bool = True

    def run(self) -> None:
        """Thực thi vòng lặp kiểm tra trạng thái đăng nhập từ local server."""
        try:
            self.auth_manager.start_server()

            # Vòng lặp chờ nhận callback từ trình duyệt
            while self._is_running:
                email = self.auth_manager.get_authenticated_email()
                if email:
                    self.finished.emit(email)
                    break
                self.msleep(200)  # Ngủ 200ms để tránh chiếm dụng CPU
        except Exception as e:
            logger.error("Lỗi trong luồng xác thực: %s", str(e), exc_info=True)
            self.error.emit(str(e))

    def stop(self) -> None:
        """Yêu cầu dừng luồng kiểm tra."""
        self._is_running = False
        self.wait()


class LoginWindow(QMainWindow):
    """Cửa sổ Đăng nhập chính của hệ thống ERP TK-KH TLS.

    Thiết kế theo phong cách Premium Dark Slate.
    """

    login_success: pyqtSignal = pyqtSignal(str, str)  # Phát đi: (email, department)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Đăng nhập hệ thống - TUAN LONG STEEL")
        self.resize(450, 550)
        self.setMinimumSize(400, 500)

        self.auth_manager: GoogleAuthManager = GoogleAuthManager(port=8080)
        self.auth_thread: AuthWorkerThread | None = None

        self._init_ui()

    def _init_ui(self) -> None:
        """Khởi tạo giao diện Premium Dark Slate."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout chính
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setSpacing(20)

        # Card container
        card = QFrame(central_widget)
        card.setObjectName("loginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)

        # Tiêu đề thương hiệu
        brand_label = QLabel("TUAN LONG STEEL", card)
        brand_label.setObjectName("brandLabel")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(brand_label)

        sub_brand_label = QLabel("ERP DESIGN & PLANNING SYSTEM", card)
        sub_brand_label.setObjectName("subBrandLabel")
        sub_brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(sub_brand_label)

        # Đường gạch phân tách trang trí
        divider = QFrame(card)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("background-color: #334155; margin: 15px 0px;")
        card_layout.addWidget(divider)

        # Dòng giới thiệu
        intro_label = QLabel("Chào mừng anh đến với hệ thống quản lý.", card)
        intro_label.setObjectName("introLabel")
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(intro_label)

        # Trạng thái chờ
        self.lbl_status = QLabel("Hệ thống đã sẵn sàng.", card)
        self.lbl_status.setObjectName("statusLabel")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        card_layout.addWidget(self.lbl_status)

        # Nút đăng nhập Google
        self.btn_login = QPushButton("🔑 ĐĂNG NHẬP VỚI GOOGLE", card)
        self.btn_login.setObjectName("loginButton")
        self.btn_login.clicked.connect(self._on_login_clicked)
        card_layout.addWidget(self.btn_login)

        # Spacer đẩy xuống chân
        card_layout.addStretch()

        # Phiên bản
        version_label = QLabel("Phiên bản v1.0.0 (Google Login)", card)
        version_label.setStyleSheet("color: #475569; font-size: 11px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(version_label)

        layout.addWidget(card)

        # Áp dụng stylesheet
        self._apply_styles()

    def _apply_styles(self) -> None:
        """Áp dụng bộ CSS QSS Premium Dark Slate."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0F172A; /* Slate 900 */
            }
            #loginCard {
                background-color: #1E293B; /* Slate 800 */
                border: 1px solid #334155;
                border-radius: 12px;
            }
            #brandLabel {
                color: #F8FAFC;
                font-size: 24px;
                font-weight: 800;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1px;
            }
            #subBrandLabel {
                color: #38BDF8; /* Sky 400 */
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            #introLabel {
                color: #94A3B8;
                font-size: 13px;
            }
            #statusLabel {
                color: #64748B;
                font-size: 12px;
                margin-top: 10px;
                min-height: 40px;
            }
            #loginButton {
                background-color: #FFFFFF;
                color: #0F172A;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            #loginButton:hover {
                background-color: #F1F5F9;
            }
            #loginButton:pressed {
                background-color: #CBD5E1;
            }
            #loginButton:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
        """
        )

    def _on_login_clicked(self) -> None:
        """Xử lý khi click vào nút đăng nhập Google."""
        self.btn_login.setEnabled(False)
        self.lbl_status.setText("🔄 Đang khởi động máy chủ xác thực cục bộ...")

        # Tạo luồng xác thực ngầm
        self.auth_thread = AuthWorkerThread(self.auth_manager)
        self.auth_thread.finished.connect(self._on_auth_finished)
        self.auth_thread.error.connect(self._on_auth_error)
        self.auth_thread.start()

        # Mở trình duyệt mặc định trỏ đến Google Auth URL
        auth_url = self.auth_manager.get_auth_url()
        self.lbl_status.setText(
            "🌐 Vui lòng hoàn tất đăng nhập tài khoản Google trên trình duyệt..."
        )
        QDesktopServices.openUrl(QUrl(auth_url))

    def _on_auth_finished(self, email: str) -> None:
        """Xử lý đăng nhập thành công và thực hiện phân quyền phòng ban.

        Args:
            email: Địa chỉ email lấy được từ Google OAuth.
        """
        logger.info("Người dùng đăng nhập thành công email: %s", email)
        self.lbl_status.setText("✔ Xác thực thành công! Đang phân quyền...")

        # Dừng luồng ngầm PyQt trước
        if self.auth_thread:
            self.auth_thread.stop()
            self.auth_thread = None

        # Trì hoãn shutdown local HTTP server 1 giây để đảm bảo socket kết thúc gửi response hoàn toàn
        QTimer.singleShot(1000, self.auth_manager.shutdown)

        # Phân quyền phòng ban
        department = "Kế hoạch"
        if email.lower() in [e.lower() for e in config.DESIGN_DEPARTMENT_EMAILS]:
            department = "Thiết kế"

        logger.info("Người dùng %s được gán vào phòng ban: %s", email, department)

        # Phát tín hiệu báo đăng nhập thành công
        self.login_success.emit(email, department)

    def _on_auth_error(self, err_msg: str) -> None:
        """Xử lý lỗi xác thực từ luồng ngầm.

        Args:
            err_msg: Chi tiết thông điệp lỗi.
        """
        logger.error("Lỗi trong quá trình xác thực: %s", err_msg)
        self.lbl_status.setText("❌ Đăng nhập thất bại. Vui lòng thử lại.")
        self.btn_login.setEnabled(True)

        QMessageBox.critical(
            self,
            "Lỗi Xác Thực",
            f"Không thể hoàn tất đăng nhập Google.\n\nChi tiết: {err_msg}",
        )

        if self.auth_thread:
            self.auth_thread.stop()
            self.auth_thread = None
        self.auth_manager.shutdown()

    def closeEvent(self, event: Any) -> None:
        """Dọn dẹp và dừng server khi đóng cửa sổ đăng nhập.

        Args:
            event: Sự kiện đóng cửa sổ.
        """
        if self.auth_thread:
            self.auth_thread.stop()
            self.auth_thread = None
        self.auth_manager.shutdown()
        event.accept()
