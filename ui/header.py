# Tên file: ui/header.py
# CHỨC NĂNG: Thanh Header nằm ngang phía trên điều phối đăng xuất và chuyển đổi các màn hình nghiệp vụ
# CHANGELOG:
# - 17:26:45 13/07/2026: [UPDATE] feat(ui): restrict drawing release form to admin and planning users only (Antigravity)
# - 18:49:30 11/07/2026: [UPDATE] feat(drawing-version-qr): implement drawing revision logic and dynamic QR code panel (Antigravity)
# - 18:18:00 11/07/2026: [UPDATE] Bổ sung nút chuyển tab Báo cáo Thống kê công khai cho mọi vai trò (Lê Thanh Vân/Antigravity)
# - 17:07:38 11/07/2026: [UPDATE] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 16:59:00 11/07/2026: [UPDATE] Tích hợp tab Quản lý Nhân sự dành riêng cho Admin (Antigravity)
# - 18:28:01 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:29:28 10/07/2026: [NEW] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 17:30:00 10/07/2026: [NEW] Tách HeaderWidget từ MainWindow phục vụ tối ưu hóa cấu trúc (Lê Thanh Vân/Antigravity)

import logging
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QWidget,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal

from ui.styles.theme import TLSTheme

logger = logging.getLogger(__name__)


class HeaderWidget(QFrame):
    """Thanh công cụ điều hướng Header phía trên.

    Hiển thị dự án đang chọn, các nút chuyển tab nghiệp vụ, thông tin người dùng
    và nút đăng xuất.
    """

    view_switched: pyqtSignal = pyqtSignal(int)  # Phát đi: (index)
    logout_clicked: pyqtSignal = pyqtSignal()  # Phát đi khi nhấn Đăng xuất

    def __init__(
        self, parent: QWidget | None = None, user_email: str = "", user_dept: str = ""
    ) -> None:
        """Khởi tạo HeaderWidget.

        Args:
            parent: Widget cha.
            user_email: Email người dùng đăng nhập.
            user_dept: Phòng ban của người dùng đăng nhập.
        """
        super().__init__(parent)
        self.setObjectName("headerBar")
        self.user_email: str = user_email
        self.user_dept: str = user_dept

        self._init_ui()

    def _init_ui(self) -> None:
        """Khởi tạo các thành phần giao diện của Header."""
        header_layout = QHBoxLayout(self)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # 1. Thiết lập hiển thị dự án hiện hành và các tab điều hướng
        self._setup_project_and_navigation(header_layout)

        # Spacer đẩy các tab điều hướng sang phải
        header_layout.addStretch()

        # Thêm đường phân tách nhỏ
        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: #E2E8F0; margin: 0px 15px;")
        header_layout.addWidget(sep)

        # 2. Thiết lập thông tin người dùng và đăng xuất
        self._setup_user_profile(header_layout)

    def _setup_project_and_navigation(self, header_layout: QHBoxLayout) -> None:
        """Thiết lập phần hiển thị tên dự án hiện hành và các nút tab nghiệp vụ.

        Args:
            header_layout: Layout chính của Header để gắn các nút điều hướng.
        """
        # Tên dự án hiện hành bên trái
        self.lbl_header_project = QLabel("DỰ ÁN HIỆN HÀNH: Chưa chọn", self)
        self.lbl_header_project.setObjectName("headerProjectLabel")
        self.lbl_header_project.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        header_layout.addWidget(self.lbl_header_project)

        # Group button quản lý trạng thái checked độc quyền cho tab ngang
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Nút chuyển màn hình Dự án
        self.btn_du_an = QPushButton("🏢 QUẢN LÝ DỰ ÁN", self)
        self.btn_du_an.setObjectName("navButton")
        self.btn_du_an.setCheckable(True)
        self.btn_du_an.clicked.connect(lambda: self.view_switched.emit(0))
        self.button_group.addButton(self.btn_du_an)
        header_layout.addWidget(self.btn_du_an)

        # Nút chuyển màn hình Thiết kế
        self.btn_thiet_ke = QPushButton("📂 BAN HÀNH BẢN VẼ", self)
        self.btn_thiet_ke.setObjectName("navButton")
        self.btn_thiet_ke.setCheckable(True)
        self.btn_thiet_ke.clicked.connect(lambda: self.view_switched.emit(1))
        self.button_group.addButton(self.btn_thiet_ke)
        header_layout.addWidget(self.btn_thiet_ke)

        # Nút chuyển màn hình Kế hoạch
        self.btn_ke_hoach = QPushButton("⚙️ TIẾP NHẬN SẢN XUẤT", self)
        self.btn_ke_hoach.setObjectName("navButton")
        self.btn_ke_hoach.setCheckable(True)
        self.btn_ke_hoach.clicked.connect(lambda: self.view_switched.emit(2))
        self.button_group.addButton(self.btn_ke_hoach)
        header_layout.addWidget(self.btn_ke_hoach)

        # Nút chuyển màn hình Báo cáo (Hiển thị công khai)
        self.btn_bao_cao = QPushButton("📊 BÁO CÁO THỐNG KÊ", self)
        self.btn_bao_cao.setObjectName("navButton")
        self.btn_bao_cao.setCheckable(True)
        self.btn_bao_cao.clicked.connect(lambda: self.view_switched.emit(4))
        self.button_group.addButton(self.btn_bao_cao)
        header_layout.addWidget(self.btn_bao_cao)

        # Nút chuyển màn hình Nhân sự (chỉ Admin thấy)
        self.btn_nhan_su = QPushButton("👥 QUẢN LÝ NHÂN SỰ", self)
        self.btn_nhan_su.setObjectName("navButton")
        self.btn_nhan_su.setCheckable(True)
        self.btn_nhan_su.clicked.connect(lambda: self.view_switched.emit(3))
        self.button_group.addButton(self.btn_nhan_su)
        header_layout.addWidget(self.btn_nhan_su)
        self.btn_nhan_su.hide()

        # Phân quyền hiển thị nút điều hướng
        is_planning = (
            self.user_dept == "Kế hoạch"
            or self.user_email.lower() == "phongkehoachkythuat25@gmail.com"
        )
        if is_planning:
            self.btn_du_an.hide()
            self.btn_thiet_ke.hide()

        if self.user_email.lower() == "luu.lehai@gmail.com":
            self.btn_nhan_su.show()

    def _setup_user_profile(self, header_layout: QHBoxLayout) -> None:
        """Thiết lập phần hiển thị thông tin người dùng đăng nhập và nút đăng xuất.

        Args:
            header_layout: Layout chính của Header để gắn thông tin user.
        """
        user_info_widget = QWidget(self)
        user_info_layout = QHBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(10)

        # Avatar tròn giả lập bằng chữ cái đầu của email
        first_char = self.user_email[0].upper() if self.user_email else "U"
        self.lbl_avatar = QLabel(first_char, user_info_widget)
        self.lbl_avatar.setStyleSheet(TLSTheme.avatar_stylesheet())
        user_info_layout.addWidget(self.lbl_avatar)

        # Label email và vai trò
        dept_display = "Thiết Kế" if self.user_dept == "Thiết kế" else "Kế Hoạch"
        self.lbl_user = QLabel(f"{self.user_email}\n({dept_display})", user_info_widget)
        self.lbl_user.setStyleSheet(
            "font-size: 11px; color: #475569; font-weight: 600;"
        )
        user_info_layout.addWidget(self.lbl_user)

        # Nút đăng xuất
        self.btn_logout = QPushButton("🚪 Đăng xuất", user_info_widget)
        self.btn_logout.setStyleSheet(TLSTheme.logout_button_stylesheet())
        self.btn_logout.clicked.connect(self.logout_clicked.emit)
        user_info_layout.addWidget(self.btn_logout)

        header_layout.addWidget(user_info_widget)

    def set_project_text(self, text: str) -> None:
        """Cập nhật text hiển thị tên dự án hiện hành bên trái header.

        Args:
            text: Nội dung chuỗi hiển thị.
        """
        self.lbl_header_project.setText(text)

    def set_active_tab(self, index: int) -> None:
        """Đồng bộ tab đang được chọn từ ngoài.

        Args:
            index: Chỉ số tab điều hướng.
        """
        if index == 0:
            self.btn_du_an.setChecked(True)
        elif index == 1:
            self.btn_thiet_ke.setChecked(True)
        elif index == 2:
            self.btn_ke_hoach.setChecked(True)
        elif index == 3:
            self.btn_nhan_su.setChecked(True)
        elif index == 4:
            self.btn_bao_cao.setChecked(True)
