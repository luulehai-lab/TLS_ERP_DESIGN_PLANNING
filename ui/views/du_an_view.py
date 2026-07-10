# Tên file: ui/views/du_an_view.py
# CHỨC NĂNG: Container kết nối ProjectWidget và SectionWidget của màn hình Quản lý Dự án
# CHANGELOG:
# - 15:33:49 10/07/2026: [UPDATE] feat(ui): add edit mode and designer roles for projects and sections (Antigravity)
# - 15:33:00 10/07/2026: [UPDATE] Thêm phương thức reload_projects để cập nhật bảng sau khi xóa dự án (Lê Thanh Vân/Antigravity)
# - 15:24:10 10/07/2026: [UPDATE] feat(auth): support auto login with SessionManager (Antigravity)
# - 15:05:00 10/07/2026: [REFACTOR] Khắc phục phình code bằng cách tách thành các sub-widgets và đóng vai trò làm Container điều phối (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout

from ui.views.du_an.project_widget import ProjectWidget
from ui.views.du_an.section_widget import SectionWidget

logger = logging.getLogger(__name__)


class DuAnView(QWidget):
    """Màn hình nghiệp vụ Quản lý Dự án & Hạng mục của phòng Thiết kế.

    Là Container ghép phối và định tuyến sự kiện giữa ProjectWidget và SectionWidget.
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
        """Thiết lập các thành phần giao diện lắp ghép ProjectWidget và SectionWidget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Phần tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ DỰ ÁN & HẠNG MỤC DỰ ÁN", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Layout ngang chứa 2 widget con
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # Khởi tạo 2 widget con
        self.project_widget = ProjectWidget(self)
        self.section_widget = SectionWidget(self)

        content_layout.addWidget(self.project_widget)
        content_layout.addWidget(self.section_widget)

        layout.addLayout(content_layout)

        # Đăng ký xử lý sự kiện (Signals)
        self.project_widget.project_selected.connect(self._on_project_selected)
        self.project_widget.project_created.connect(self._on_project_created)

        # Áp dụng CSS QSS dùng chung
        self._apply_view_styles()

    def set_project(self, project_id: str) -> None:
        """Thiết lập dự án hiện hành truyền tiếp sang các widget con.

        Args:
            project_id: Mã dự án được chọn từ Sidebar hoặc bảng danh sách.
        """
        self.current_project_id = project_id if project_id else ""

        # Đồng bộ trạng thái chọn trên bảng dự án của project_widget
        self.project_widget.select_project_by_id(self.current_project_id)

        # Đồng bộ danh sách hạng mục của dự án
        self.section_widget.set_project(self.current_project_id)

    def _on_project_selected(self, project_id: str) -> None:
        """Xử lý khi người dùng chọn dòng dự án trên bảng bên trái.

        Args:
            project_id: Mã dự án được chọn.
        """
        self.current_project_id = project_id
        self.section_widget.set_project(project_id)

    def _on_project_created(self) -> None:
        """Xử lý khi tạo dự án mới thành công."""
        # Gọi làm mới danh sách dự án ở Sidebar của MainWindow
        if self.main_window and hasattr(self.main_window, "load_projects"):
            self.main_window.load_projects()

    def reload_projects(self) -> None:
        """Yêu cầu project_widget làm mới lại danh sách dự án trên bảng hiển thị."""
        if hasattr(self, "project_widget") and hasattr(
            self.project_widget, "load_projects"
        ):
            self.project_widget.load_projects()

    def _apply_view_styles(self) -> None:
        """Áp dụng các định dạng giao diện QSS cho view."""
        self.setStyleSheet(
            """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #334155;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 5px;
            }
            QLabel {
                font-size: 13px;
                color: #475569;
                font-weight: 500;
            }
            QLineEdit, QComboBox {
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: #F8FAFC;
                color: #0F172A;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #38BDF8;
                background-color: #FFFFFF;
                color: #0F172A;
            }
            QPushButton {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E293B;
            }
            QPushButton:pressed {
                background-color: #020617;
            }
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #0F172A;
                gridline-color: #F1F5F9;
                font-size: 13px;
            }
            QTableWidget::item {
                color: #0F172A;
            }
            QTableWidget::item:selected {
                background-color: #38BDF8;
                color: #0F172A;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #475569;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #0F172A;
            }
            QMessageBox QPushButton {
                background-color: #F1F5F9;
                color: #0F172A;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: bold;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #E2E8F0;
            }
            QMessageBox QPushButton:pressed {
                background-color: #CBD5E1;
            }
        """
        )
