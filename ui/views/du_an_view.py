# Tên file: ui/views/du_an_view.py
# CHỨC NĂNG: Giao diện quản lý Dự án & Hạng mục cho phòng Thiết kế
# CHANGELOG:
# - 18:19:45 08/07/2026: [UPDATE] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [UPDATE] Bổ sung giao diện Quản lý Hạng mục Dự án, bảng danh sách hạng mục và tính năng CRUD Hạng mục (Antigravity)
# - 18:00:00 08/07/2026: [UPDATE] Cho phép form tạo dự án mới dãn tràn hết chiều ngang trang theo yêu cầu (Antigravity)
# - 17:57:00 08/07/2026: [NEW] Khởi tạo giao diện Quản lý dự án, form tạo dự án mới và bảng danh sách dự án (Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtCore import Qt

from core.database import SessionLocal
from core.services import project_service, section_service
from ui.common.workers import ProjectLoaderThread

logger = logging.getLogger(__name__)


class DuAnView(QWidget):
    """Màn hình nghiệp vụ Quản lý Dự án & Hạng mục của phòng Thiết kế.

    Cho phép khởi tạo dự án mới, quản lý danh sách các dự án và hạng mục chi tiết.
    """

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.main_window = parent
        self.current_project_id: str = ""
        self.project_loader_thread: ProjectLoaderThread | None = None
        self._init_ui()
        self.load_projects()

    def _init_ui(self) -> None:
        """Thiết lập các thành phần giao diện của view Quản lý Dự án & Hạng mục."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Phần tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ DỰ ÁN & HẠNG MỤC DỰ ÁN", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Layout ngang chứa 2 form nhập liệu (co giãn tự do)
        forms_layout = QHBoxLayout()
        forms_layout.setSpacing(15)

        # 1. Khung tạo dự án mới
        project_group = self._create_project_group()
        forms_layout.addWidget(project_group)

        # 2. Khung quản lý hạng mục
        section_group = self._create_section_group()
        forms_layout.addWidget(section_group)

        layout.addLayout(forms_layout)

        # Layout ngang chứa 2 bảng thông tin
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(15)

        # Bảng danh sách dự án
        table_proj_group = self._create_table_proj_group()
        tables_layout.addWidget(table_proj_group)

        # Bảng danh sách hạng mục
        table_sect_group = self._create_table_sect_group()
        tables_layout.addWidget(table_sect_group)

        layout.addLayout(tables_layout)

        # Áp dụng CSS QSS cho các controls trong view
        self._apply_view_styles()

    def _create_project_group(self) -> QGroupBox:
        """Tạo panel điều khiển cho nghiệp vụ tạo dự án.

        Returns:
            QGroupBox: Nhóm các ô nhập liệu liên quan tới Dự án.
        """
        group = QGroupBox("Tạo Dự án Mới", self)
        grid = QGridLayout(group)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Mã Dự án:", group), 0, 0)
        self.txt_project_id = QLineEdit(group)
        self.txt_project_id.setPlaceholderText("Ví dụ: TLS-01726")
        grid.addWidget(self.txt_project_id, 0, 1)

        grid.addWidget(QLabel("Tên Dự án:", group), 1, 0)
        self.txt_project_name = QLineEdit(group)
        self.txt_project_name.setPlaceholderText("Nhập tên dự án kết cấu thép...")
        grid.addWidget(self.txt_project_name, 1, 1)

        self.btn_create_proj = QPushButton("➕ Tạo Dự án", group)
        self.btn_create_proj.clicked.connect(self._on_create_project)
        grid.addWidget(self.btn_create_proj, 2, 0, 1, 2)

        return group

    def _create_section_group(self) -> QGroupBox:
        """Tạo panel điều khiển cho nghiệp vụ tạo hạng mục.

        Returns:
            QGroupBox: Nhóm các ô nhập liệu liên quan tới Hạng mục.
        """
        group = QGroupBox("Thêm Hạng mục vào Dự án", self)
        grid = QGridLayout(group)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Dự án hiện hành:", group), 0, 0)
        self.lbl_selected_project_section = QLabel("Chưa chọn dự án ở Sidebar", group)
        self.lbl_selected_project_section.setStyleSheet(
            "font-weight: bold; color: #0284C7; font-size: 13px;"
        )
        grid.addWidget(self.lbl_selected_project_section, 0, 1)

        grid.addWidget(QLabel("Mã Hạng mục:", group), 1, 0)
        self.txt_section_code = QLineEdit(group)
        self.txt_section_code.setPlaceholderText("Ví dụ: NX1, NX2, MN...")
        grid.addWidget(self.txt_section_code, 1, 1)

        grid.addWidget(QLabel("Tên Hạng mục:", group), 2, 0)
        self.txt_section_name = QLineEdit(group)
        self.txt_section_name.setPlaceholderText("Ví dụ: Nhà xưởng 1, Mái lấy sáng...")
        grid.addWidget(self.txt_section_name, 2, 1)

        self.btn_create_sect = QPushButton("➕ Thêm Hạng mục", group)
        self.btn_create_sect.clicked.connect(self._on_create_section)
        grid.addWidget(self.btn_create_sect, 3, 0, 1, 2)

        return group

    def _create_table_proj_group(self) -> QGroupBox:
        """Tạo khung hiển thị bảng danh sách các dự án trong hệ thống.

        Returns:
            QGroupBox: Nhóm bảng hiển thị dữ liệu dự án.
        """
        group = QGroupBox("Danh sách dự án trong hệ thống", self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 15, 10, 10)

        table_actions_layout = QHBoxLayout()
        table_actions_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Làm mới danh sách", group)
        self.btn_refresh.setFixedWidth(150)
        self.btn_refresh.setStyleSheet(
            """
            QPushButton {
                background-color: #0284C7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
            """
        )
        self.btn_refresh.clicked.connect(self._on_manual_refresh)
        table_actions_layout.addWidget(self.btn_refresh)
        layout.addLayout(table_actions_layout)

        self.tbl_projects = QTableWidget(group)
        self.tbl_projects.setColumnCount(3)
        self.tbl_projects.setHorizontalHeaderLabels(
            ["Mã Dự Án", "Tên Dự Án", "Trạng Thái"]
        )

        header = self.tbl_projects.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.tbl_projects.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_projects.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.tbl_projects)
        return group

    def _create_table_sect_group(self) -> QGroupBox:
        """Tạo khung hiển thị bảng danh sách các hạng mục của dự án hiện hành.

        Returns:
            QGroupBox: Nhóm bảng hiển thị dữ liệu hạng mục.
        """
        group = QGroupBox("Danh sách hạng mục dự án", self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 15, 10, 10)

        self.tbl_sections = QTableWidget(group)
        self.tbl_sections.setColumnCount(3)
        self.tbl_sections.setHorizontalHeaderLabels(
            ["Mã Hạng Mục", "Tên Hạng Mục", "Hành Động"]
        )

        header = self.tbl_sections.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.tbl_sections.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_sections.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.tbl_sections)
        return group

    def set_project(self, project_id: str) -> None:
        """Thiết lập dự án hiện hành để quản lý hạng mục.

        Args:
            project_id: Mã dự án được chọn từ Sidebar.
        """
        self.current_project_id = project_id if project_id else ""
        self.lbl_selected_project_section.setText(
            project_id if project_id else "Chưa chọn dự án ở Sidebar"
        )
        self.load_sections()

    def load_projects(self) -> None:
        """Tải danh sách các dự án từ database qua luồng phụ bất đồng bộ."""
        if self.project_loader_thread and self.project_loader_thread.isRunning():
            return

        self.tbl_projects.setRowCount(0)
        self.tbl_projects.setRowCount(1)
        loading_item = QTableWidgetItem("⏳ Đang tải danh sách dự án...")
        loading_item.setFlags(Qt.ItemFlag.NoItemFlags)
        loading_item.setForeground(Qt.GlobalColor.gray)
        self.tbl_projects.setItem(0, 1, loading_item)

        self.project_loader_thread = ProjectLoaderThread()
        self.project_loader_thread.finished.connect(self._on_projects_loaded)
        self.project_loader_thread.error.connect(self._on_load_error)
        self.project_loader_thread.start()

    def _on_projects_loaded(self, projects: list[dict[str, Any]]) -> None:
        """Callback hiển thị danh sách dự án lên bảng.

        Args:
            projects: Danh sách các dự án dạng dict.
        """
        self.tbl_projects.setRowCount(len(projects))
        for r, p in enumerate(projects):
            item_id = QTableWidgetItem(p["project_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_name = QTableWidgetItem(p["project_name"])
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_status = QTableWidgetItem(p["status"])
            item_status.setFlags(item_status.flags() ^ Qt.ItemFlag.ItemIsEditable)

            status_str = p["status"]
            if status_str == "Khởi tạo":
                item_status.setForeground(Qt.GlobalColor.blue)
            elif status_str == "Đang chạy":
                item_status.setForeground(Qt.GlobalColor.darkGreen)
            elif status_str == "Hoàn thành":
                item_status.setForeground(Qt.GlobalColor.gray)

            self.tbl_projects.setItem(r, 0, item_id)
            self.tbl_projects.setItem(r, 1, item_name)
            self.tbl_projects.setItem(r, 2, item_status)

    def _on_load_error(self, error_msg: str) -> None:
        """Callback khi luồng phụ tải dự án gặp lỗi.

        Args:
            error_msg: Thông báo lỗi chi tiết.
        """
        logger.error("Lỗi tải danh sách dự án: %s", error_msg)
        self.tbl_projects.setRowCount(1)
        err_item = QTableWidgetItem("❌ Lỗi tải dữ liệu. Vui lòng click làm mới.")
        err_item.setFlags(Qt.ItemFlag.NoItemFlags)
        err_item.setForeground(Qt.GlobalColor.red)
        self.tbl_projects.setItem(0, 1, err_item)

    def load_sections(self) -> None:
        """Tải danh sách hạng mục của dự án hiện hành từ database (Đồng bộ)."""
        self.tbl_sections.setRowCount(0)
        if not self.current_project_id:
            return

        db = SessionLocal()
        try:
            sections = section_service.list_project_sections(
                db, self.current_project_id
            )
            self.tbl_sections.setRowCount(len(sections))
            for r, s in enumerate(sections):
                item_code = QTableWidgetItem(s.section_code)
                item_code.setFlags(item_code.flags() ^ Qt.ItemFlag.ItemIsEditable)

                item_name = QTableWidgetItem(s.section_name)
                item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

                btn_delete = QPushButton("🗑 Xóa", self.tbl_sections)
                btn_delete.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #EF4444;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 3px 10px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #DC2626;
                    }
                    """
                )
                btn_delete.setProperty("section_id", s.section_id)
                btn_delete.clicked.connect(self._on_delete_section)

                self.tbl_sections.setItem(r, 0, item_code)
                self.tbl_sections.setItem(r, 1, item_name)
                self.tbl_sections.setCellWidget(r, 2, btn_delete)
        except Exception as e:
            logger.error(
                "Lỗi cơ sở dữ liệu khi tải hạng mục: %s", str(e), exc_info=True
            )
        finally:
            db.close()

    def _on_delete_section(self) -> None:
        """Xử lý sự kiện khi click nút [Xóa] hạng mục."""
        btn = self.sender()
        if not btn:
            return
        section_id = btn.property("section_id")
        if not section_id:
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Anh có chắc chắn muốn xóa hạng mục này?\n"
            "Các bản vẽ đang thuộc hạng mục này sẽ được đưa về trạng thái không thuộc hạng mục nào.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            db = SessionLocal()
            try:
                success = section_service.delete_section(db, int(section_id))
                if success:
                    QMessageBox.information(
                        self, "Thông báo", "Đã xóa hạng mục thành công!"
                    )
                    self.load_sections()

                    # Thông báo reload tab Thiết kế để load lại combobox hạng mục
                    if (
                        self.main_window
                        and hasattr(self.main_window, "thiet_ke_view")
                        and hasattr(self.main_window.thiet_ke_view, "load_sections")
                    ):
                        self.main_window.thiet_ke_view.load_sections()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể xóa hạng mục này.")
            except Exception as e:
                logger.error(
                    "Lỗi khi xóa hạng mục ID %d: %s", section_id, str(e), exc_info=True
                )
                QMessageBox.critical(self, "Lỗi", "Lỗi kết nối cơ sở dữ liệu.")
            finally:
                db.close()

    def _on_manual_refresh(self) -> None:
        """Xử lý làm mới thủ công bảng danh sách dự án."""
        logger.info("Yêu cầu làm mới bảng dự án thủ công.")
        self.load_projects()

    def _on_create_project(self) -> None:
        """Xử lý sự kiện click nút [Tạo Dự án]."""
        project_id = self.txt_project_id.text().strip()
        project_name = self.txt_project_name.text().strip()

        if not project_id or not project_name:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập đầy đủ Mã dự án và Tên dự án!"
            )
            return

        created_success = False
        db = SessionLocal()
        try:
            proj = project_service.create_project(db, project_id, project_name)
            if proj:
                created_success = True
        except Exception as e:
            logger.error("Lỗi khi tạo dự án: %s", str(e), exc_info=True)
        finally:
            db.close()

        if created_success:
            QMessageBox.information(
                self, "Thông báo", f"Đã tạo thành công dự án: {project_id}"
            )
            self.txt_project_id.clear()
            self.txt_project_name.clear()
            self.load_projects()

            if self.main_window and hasattr(self.main_window, "load_projects"):
                self.main_window.load_projects()
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                "Tạo dự án thất bại. Vui lòng kiểm tra lại log hệ thống.",
            )

    def _on_create_section(self) -> None:
        """Xử lý sự kiện click nút [Thêm Hạng mục]."""
        project_id = self.current_project_id
        section_code = self.txt_section_code.text().strip()
        section_name = self.txt_section_name.text().strip()

        if not project_id:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn một Dự án bên trái Sidebar trước!"
            )
            return

        if not section_code or not section_name:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập đầy đủ Mã hạng mục và Tên hạng mục!"
            )
            return

        created_success = False
        db = SessionLocal()
        try:
            sect = section_service.create_section(
                db, project_id, section_code, section_name
            )
            if sect:
                created_success = True
        except Exception as e:
            logger.error("Lỗi khi tạo hạng mục: %s", str(e), exc_info=True)
        finally:
            db.close()

        if created_success:
            QMessageBox.information(
                self, "Thông báo", f"Đã thêm thành công hạng mục: {section_code}"
            )
            self.txt_section_code.clear()
            self.txt_section_name.clear()
            self.load_sections()

            # Đồng thời reload combobox hạng mục của thiet_ke_view nếu có
            if (
                self.main_window
                and hasattr(self.main_window, "thiet_ke_view")
                and hasattr(self.main_window.thiet_ke_view, "load_sections")
            ):
                self.main_window.thiet_ke_view.load_sections()
        else:
            QMessageBox.critical(
                self, "Lỗi", "Không thể tạo hạng mục này hoặc lỗi kết nối database."
            )

    def _apply_view_styles(self) -> None:
        """Áp dụng các định dạng giao diện QSS."""
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
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: #F8FAFC;
                color: #0F172A;
            }
            QLineEdit:focus {
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
