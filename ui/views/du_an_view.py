# CHANGELOG:
# - 17:29:28 10/07/2026: [FIX] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 16:23:44 10/07/2026: [UPDATE] feat(ui): add right click delete project from sidebar with table reload sync (Antigravity)
# - 16:15:00 10/07/2026: [REFACTOR] Thay đổi từ layout 2 cột sang layout xếp dọc, hiển thị ProjectWidget ở trên, SectionWidget ở dưới. Thêm Welcome widget khi chưa chọn dự án. (Lê Thanh Vân/Antigravity)
# - 15:33:00 10/07/2026: [UPDATE] Thêm phương thức reload_projects để cập nhật bảng sau khi xóa dự án (Lê Thanh Vân/Antigravity)
# - 15:24:10 10/07/2026: [UPDATE] feat(auth): support auto login with SessionManager (Antigravity)
# - 17:50:00 10/07/2026: [REFACTOR] Thay thế stylesheet thô bằng TLSTheme dùng chung (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from ui.styles.theme import TLSTheme
from ui.views.du_an.project_widget import ProjectWidget
from ui.views.du_an.section_widget import SectionWidget

logger = logging.getLogger(__name__)


class DuAnView(QWidget):
    """Màn hình nghiệp vụ Quản lý Dự án & Hạng mục của phòng Thiết kế.

    Là Container ghép phối và định tuyến sự kiện xếp lớp dọc giữa ProjectWidget và SectionWidget.
    """

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo DuAnView.

        Args:
            parent: MainWindow chứa view này.
        """
        super().__init__(parent)
        self.main_window = parent
        self.current_project_id: str = ""
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập các thành phần giao diện lắp ghép ProjectWidget và SectionWidget theo chiều dọc."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 1. Phần tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ DỰ ÁN & HẠNG MỤC DỰ ÁN", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        self.main_layout.addWidget(title_label)

        # 2. Widget Chào mừng khi chưa chọn Dự án
        self.welcome_widget = QWidget(self)
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setContentsMargins(20, 100, 20, 100)
        welcome_layout.setSpacing(20)

        welcome_icon = QLabel("🏢", self.welcome_widget)
        welcome_icon.setStyleSheet("font-size: 80px;")
        welcome_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_icon)

        welcome_text = QLabel(
            "Vui lòng chọn một Dự án từ danh sách bên trái Sidebar\nđể xem thông tin chi tiết và quản lý hạng mục.",
            self.welcome_widget,
        )
        welcome_text.setStyleSheet(
            "font-size: 15px; color: #64748B; font-weight: 500; line-height: 1.5;"
        )
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_text)

        self.main_layout.addWidget(self.welcome_widget)

        # 3. Khởi tạo 2 widget con nghiệp vụ
        self.project_widget = ProjectWidget(self)
        self.section_widget = SectionWidget(self)

        # Kết nối tín hiệu cập nhật dự án để load lại Sidebar ở MainWindow
        self.project_widget.project_updated.connect(self._on_project_updated)

        self.main_layout.addWidget(self.project_widget)
        self.main_layout.addWidget(self.section_widget)

        # Áp dụng CSS QSS dùng chung
        self._apply_view_styles()

        # Mặc định ban đầu ẩn các widget nghiệp vụ, chỉ hiện màn hình chào mừng
        self.set_project("")

    def set_project(self, project_id: str) -> None:
        """Thiết lập dự án hiện hành truyền tiếp sang các widget con.

        Args:
            project_id: Mã dự án được chọn từ Sidebar.
        """
        self.current_project_id = project_id if project_id else ""

        if not self.current_project_id:
            # Chưa chọn dự án
            self.welcome_widget.show()
            self.project_widget.hide()
            self.section_widget.hide()
            self.project_widget.set_project_id("")
            self.section_widget.set_project("")
        else:
            # Đã chọn dự án
            self.welcome_widget.hide()
            self.project_widget.show()
            self.section_widget.show()
            self.project_widget.set_project_id(self.current_project_id)
            self.section_widget.set_project(self.current_project_id)

    def reload_projects(self) -> None:
        """Yêu cầu project_widget làm mới lại danh sách dự án trên bảng hiển thị."""
        # Với thiết kế mới, không còn bảng dự án trên ProjectWidget,
        # nên hàm này chỉ cần load lại thông tin dự án hiện hành nếu có thay đổi.
        if self.current_project_id:
            self.project_widget.set_project_id(self.current_project_id)

    def _on_project_updated(self, project_id: str) -> None:
        """Xử lý khi cập nhật dự án thành công."""
        # Gọi làm mới danh sách dự án ở Sidebar của MainWindow
        if self.main_window and hasattr(self.main_window, "load_projects"):
            self.main_window.load_projects()

    def _apply_view_styles(self) -> None:
        """Áp dụng các định dạng giao diện QSS cho view từ TLSTheme."""
        self.setStyleSheet(TLSTheme.content_view_stylesheet())
