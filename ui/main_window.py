# Tên file: ui/main_window.py
# CHỨC NĂNG: Cửa sổ chính điều hướng ứng dụng ERP PyQt6 (Tích hợp Sidebar và Header modular)
# CHANGELOG:
# - 18:28:01 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:29:28 10/07/2026: [FIX] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 17:35:00 10/07/2026: [REFACTOR] Tách logic Sidebar và Header ra các widget con độc lập, áp dụng TLSTheme dùng chung (Lê Thanh Vân/Antigravity)

import logging
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QSplitter,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings

from ui.styles.theme import TLSTheme
from ui.sidebar import SidebarWidget
from ui.header import HeaderWidget
from ui.views.thiet_ke_view import ThietKeView
from ui.views.ke_hoach_view import KeHoachView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng ERP TK-KH TLS.

    Tích hợp SidebarWidget bên trái, HeaderWidget bên phải phía trên,
    và vùng Content QStackedWidget chứa các màn hình nghiệp vụ chính.
    """

    logout_clicked: pyqtSignal = pyqtSignal()

    def __init__(self, user_email: str = "", user_dept: str = "") -> None:
        """Khởi tạo MainWindow.

        Args:
            user_email: Email của người dùng đăng nhập.
            user_dept: Phòng ban của người dùng đăng nhập.
        """
        super().__init__()
        self.setWindowTitle("ERP TK-KH - TUAN LONG STEEL (TLS)")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        self.user_email: str = user_email
        self.user_dept: str = user_dept
        self.current_project_id: str = ""
        self.settings = QSettings("TuanLongSteel", "ERP_TK_KH")

        self._init_ui()

    def _init_ui(self) -> None:
        """Khởi tạo cấu trúc layout Sidebar Dự án bên trái và Content Area + Header bên phải."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout chính chứa splitter
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Tạo QSplitter nằm ngang giữa Sidebar và Content
        self.splitter_main = QSplitter(Qt.Orientation.Horizontal, central_widget)
        self.splitter_main.setHandleWidth(4)
        self.splitter_main.setStyleSheet(TLSTheme.splitter_stylesheet())
        main_layout.addWidget(self.splitter_main)

        # 1. Khởi tạo Sidebar bên trái
        self._setup_left_sidebar()

        # 2. Khởi tạo Vùng bên phải (Header và Content Stack)
        right_container = QWidget(self)
        right_container.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        right_container.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._setup_right_content(right_container, right_layout)

        # Kết nối sự kiện di chuyển splitter để lưu lại trạng thái
        self.splitter_main.splitterMoved.connect(self._save_splitter_state)

        # Khôi phục trạng thái splitter nếu có
        state = self.settings.value("main_splitter_state")
        if state:
            self.splitter_main.restoreState(state)
        else:
            self.splitter_main.setSizes([250, 950])

        # Áp dụng stylesheet tổng thể sử dụng theme chung
        self.setStyleSheet(TLSTheme.main_window_stylesheet())

    def _setup_left_sidebar(self) -> None:
        """Thiết lập Sidebar bên trái của MainWindow."""
        self.sidebar = SidebarWidget(
            self.splitter_main, self.user_email, self.user_dept
        )
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(500)
        self.sidebar.project_selected.connect(self._on_project_selected_by_sidebar)
        self.sidebar.project_deleted.connect(self._on_project_deleted_by_sidebar)
        self.splitter_main.addWidget(self.sidebar)

    def _setup_right_content(
        self, right_container: QWidget, right_layout: QVBoxLayout
    ) -> None:
        """Thiết lập Header và Stacked Widget chứa các View phòng ban.

        Args:
            right_container: Widget chứa nội dung bên phải.
            right_layout: Bố cục dọc của nội dung bên phải.
        """
        # 2a. Header nằm ngang phía trên
        self.header = HeaderWidget(right_container, self.user_email, self.user_dept)
        self.header.view_switched.connect(self._switch_view)
        self.header.logout_clicked.connect(self.logout_clicked.emit)
        right_layout.addWidget(self.header)

        # 2b. QStackedWidget chứa các view chính
        self.content_stack = QStackedWidget(right_container)
        right_layout.addWidget(self.content_stack)

        self.splitter_main.addWidget(right_container)

        # Khởi tạo các Views phòng ban
        from ui.views.du_an_view import DuAnView

        self.du_an_view = DuAnView(self)
        self.thiet_ke_view = ThietKeView(self)
        self.ke_hoach_view = KeHoachView(self)

        # Thêm Views vào Stacked Widget
        self.content_stack.addWidget(self.du_an_view)
        self.content_stack.addWidget(self.thiet_ke_view)
        self.content_stack.addWidget(self.ke_hoach_view)

        # Hiển thị View mặc định dựa vào phân quyền phòng ban
        if self.user_dept == "Kế hoạch":
            self._switch_view(2)
        else:
            self._switch_view(1)

    def load_projects(self) -> None:
        """Wrapper gọi load dự án từ SidebarWidget."""
        self.sidebar.load_projects()

    def _save_splitter_state(self) -> None:
        """Lưu lại trạng thái kích thước thanh kéo Sidebar."""
        self.settings.setValue("main_splitter_state", self.splitter_main.saveState())

    def _on_project_selected_by_sidebar(
        self, project_id: str, display_text: str
    ) -> None:
        """Xử lý sự kiện khi click chọn dự án ở Sidebar.

        Args:
            project_id: ID dự án được chọn.
            display_text: Tên hiển thị dự án.
        """
        logger.info("Main: Chọn dự án %s", project_id)
        self.current_project_id = project_id
        if project_id:
            self.header.set_project_text(f"DỰ ÁN: {display_text}")
        else:
            self.header.set_project_text("DỰ ÁN HIỆN HÀNH: Chưa chọn")

        self._sync_active_view_project()

    def _on_project_deleted_by_sidebar(self, project_id: str) -> None:
        """Xử lý sự kiện khi dự án bị xóa từ Sidebar.

        Args:
            project_id: ID dự án vừa bị xóa.
        """
        logger.info("Main: Nhận tín hiệu xóa dự án %s", project_id)
        if self.current_project_id == project_id:
            self.current_project_id = ""
            self.header.set_project_text("DỰ ÁN HIỆN HÀNH: Chưa chọn")
            self._sync_active_view_project()

        # Reload danh sách dự án của du_an_view nếu có
        if hasattr(self, "du_an_view") and hasattr(self.du_an_view, "reload_projects"):
            self.du_an_view.reload_projects()

    def _switch_view(self, index: int) -> None:
        """Chuyển đổi view hiển thị trên QStackedWidget và đồng bộ nút tab.

        Args:
            index: Chỉ mục của view (0: Quản lý Dự án, 1: Thiết kế, 2: Kế hoạch).
        """
        logger.info("Main: Chuyển màn hình sang index %d", index)
        self.content_stack.setCurrentIndex(index)
        self.header.set_active_tab(index)
        self._sync_active_view_project()

    def _sync_active_view_project(self) -> None:
        """Đồng bộ dự án hiện hành sang View đang được hiển thị."""
        active_idx = self.content_stack.currentIndex()
        if active_idx == 0 and hasattr(self, "du_an_view"):
            self.du_an_view.set_project(self.current_project_id)
        elif active_idx == 1 and hasattr(self, "thiet_ke_view"):
            self.thiet_ke_view.set_project(self.current_project_id)
        elif active_idx == 2 and hasattr(self, "ke_hoach_view"):
            self.ke_hoach_view.set_project(self.current_project_id)
