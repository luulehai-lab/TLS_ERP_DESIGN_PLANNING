# Tên file: ui/login_window.py
# CHỨC NĂNG: Giao diện và luồng xử lý xác thực đăng nhập Google OAuth2 của hệ thống.
# CHANGELOG:
# - 15:01:02 13/07/2026: [UPDATE] feat(drawing-service): sort drawings by project section code and drawing id for grouping (Antigravity)
# - 17:07:38 11/07/2026: [UPDATE] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 15:17:43 11/07/2026: [UPDATE] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 15:14:00 11/07/2026: [UPDATE] Chặn email không đăng ký (whitelist check) không cho vào app (Antigravity)
# - 17:29:28 10/07/2026: [FIX] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 18:03:18 08/07/2026: [UPDATE] feat(ui): support Google Drive folder URLs for drawing packages (Antigravity)
# - 18:00:00 08/07/2026: [UPDATE] Cập nhật màu sắc nhãn phiên bản sáng lên để dễ nhìn trên nền tối (Antigravity)
# - 17:37:32 08/07/2026: [FIX] fix(ui): synchronize drawing status between Design and Planning views with manual and auto refresh (Antigravity)
# - 17:30:00 08/07/2026: [FIX] Khắc phục lỗi chữ trắng trên nền trắng trong các ô nhập liệu, bảng dữ liệu và nút bấm hộp thoại cảnh báo trên các máy chạy Windows Dark Mode (Antigravity)
# - 16:40:16 08/07/2026: [UPDATE] feat(auth): add Google OAuth2 login with department-based access control (Antigravity)
# - 16:35:00 08/07/2026: [FIX] Trì hoãn việc shutdown auth_manager bằng QTimer để tránh deadlock socket (Lê Thanh Vân/Antigravity)
# - 14:13:50 08/07/2026: [NEW] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 14:20:00 08/07/2026: [NEW] Khởi tạo giao diện đăng nhập Google (Lê Thanh Vân/Antigravity)
# - 17:52:00 10/07/2026: [REFACTOR] Thay thế styles thô bằng TLSTheme dùng chung (Lê Thanh Vân/Antigravity)


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
from PyQt6.QtGui import QDesktopServices, QPixmap

from ui.styles.theme import TLSTheme
from core.services.auth_service import GoogleAuthManager
from core.services.project_service import is_email_authorized

logger = logging.getLogger(__name__)


class AuthWorkerThread(QThread):
    """Luồng phụ xử lý máy chủ HTTP callback cục bộ và lắng nghe kết quả."""

    finished: pyqtSignal = pyqtSignal(str)
    error: pyqtSignal = pyqtSignal(str)

    def __init__(self, auth_manager: GoogleAuthManager) -> None:
        """Khởi tạo luồng phụ xác thực đăng nhập Google.

        Args:
            auth_manager: Đối tượng quản lý kết nối OAuth2 backend.
        """
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
        """Khởi tạo cửa sổ Đăng nhập LoginWindow."""
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

        self._setup_branding(card, card_layout)
        self._setup_login_controls(card, card_layout)

        layout.addWidget(card)

        # Áp dụng stylesheet
        self._apply_styles()

    def _setup_branding(self, card: QFrame, card_layout: QVBoxLayout) -> None:
        """Thiết lập logo và tiêu đề thương hiệu TLS.

        Args:
            card: Khung Card chứa nhãn.
            card_layout: Bố cục dọc của Card.
        """
        import os
        logo_label = QLabel(card)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_path, "LOGO.JPG")

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale logo về chiều rộng 110px cho màn hình Login
            scaled_pixmap = pixmap.scaledToWidth(110, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(logo_label)

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

    def _setup_login_controls(self, card: QFrame, card_layout: QVBoxLayout) -> None:
        """Thiết lập các nút đăng nhập và phiên bản ở dưới Card.

        Args:
            card: Khung Card chứa.
            card_layout: Bố cục dọc của Card.
        """
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
        version_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(version_label)

    def _apply_styles(self) -> None:
        """Áp dụng bộ CSS QSS Premium Dark Slate từ TLSTheme."""
        self.setStyleSheet(TLSTheme.login_stylesheet())

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

        # Kiểm tra email có quyền truy cập hệ thống không
        if not is_email_authorized(email):
            logger.warning(
                "Email '%s' không có quyền truy cập hệ thống. Từ chối đăng nhập.",
                email,
            )
            self.lbl_status.setText("❌ Email chưa được đăng ký trong hệ thống.")
            self.btn_login.setEnabled(True)
            QMessageBox.warning(
                self,
                "Truy Cập Bị Từ Chối",
                f"Email '{email}' chưa được đăng ký trong hệ thống ERP.\n\n"
                f"Vui lòng liên hệ Quản trị viên (Anh Lưu) để được cấp quyền.",
            )
            return

        # Phân quyền phòng ban
        from core.services.project_service import get_staff_role

        role = get_staff_role(email)
        department = "Kế hoạch"
        if role in ["Thiết kế", "Admin", "Kinh doanh"]:
            department = "Thiết kế"

        logger.info(
            "Người dùng %s (Vai trò: %s) được gán vào phòng ban: %s",
            email,
            role,
            department,
        )

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
