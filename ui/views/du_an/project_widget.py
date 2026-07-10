# Tên file: ui/views/du_an/project_widget.py
# CHỨC NĂNG: Giao diện quản lý & hiển thị danh sách Dự án của phòng Thiết kế
# CHANGELOG:
# - 15:24:10 10/07/2026: [NEW] feat(auth): support auto login with SessionManager (Antigravity)
# - 14:56:00 10/07/2026: [NEW] Khởi tạo component ProjectWidget tách từ du_an_view.py (Lê Thanh Vân/Antigravity)

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
    QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.database import SessionLocal
from core.services import project_service
from ui.common.workers import ProjectLoaderThread

logger = logging.getLogger(__name__)


class ProjectWidget(QWidget):
    """Widget quản lý nghiệp vụ Khởi tạo và Hiển thị danh sách Dự án."""

    project_selected = pyqtSignal(str)
    project_created = pyqtSignal()

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo ProjectWidget.

        Args:
            parent: Widget cha của widget này.
        """
        super().__init__(parent)
        self.main_window = parent
        self.project_loader_thread: ProjectLoaderThread | None = None
        self.edit_mode: bool = False
        self.current_projects_data: list[dict[str, Any]] = []
        self._init_ui()
        self.load_projects()

    def _init_ui(self) -> None:
        """Thiết lập giao diện của ProjectWidget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 1. Khung tạo dự án mới
        project_group = self._create_project_group()
        layout.addWidget(project_group)

        # 2. Bảng danh sách dự án
        table_proj_group = self._create_table_proj_group()
        layout.addWidget(table_proj_group)

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

        grid.addWidget(QLabel("Kinh doanh (Sales):", group), 2, 0)
        self.cb_sales = QComboBox(group)
        self.cb_sales.addItem(
            "Nguyễn Văn Quân - quanxu23@gmail.com", "quanxu23@gmail.com"
        )
        self.cb_sales.addItem(
            "Trịnh Văn Phúc - vanphuctrinh2211@gmail.com", "vanphuctrinh2211@gmail.com"
        )
        grid.addWidget(self.cb_sales, 2, 1)

        grid.addWidget(QLabel("Chủ trì Thiết kế:", group), 3, 0)
        self.cb_designer = QComboBox(group)
        self.cb_designer.addItem(
            "Vũ Thanh Hà - ha91steel@gmail.com", "ha91steel@gmail.com"
        )
        self.cb_designer.addItem(
            "Nguyễn Văn Trịnh - trinh58xd2@gmail.com", "trinh58xd2@gmail.com"
        )
        grid.addWidget(self.cb_designer, 3, 1)

        # Layout ngang chứa nút tạo/cập nhật và nút hủy
        btn_layout = QHBoxLayout()
        self.btn_create_proj = QPushButton("➕ Tạo Dự án", group)
        self.btn_create_proj.clicked.connect(self._on_create_project)
        btn_layout.addWidget(self.btn_create_proj)

        self.btn_cancel_edit = QPushButton("❌ Hủy / Tạo mới", group)
        self.btn_cancel_edit.setStyleSheet(
            """
            QPushButton {
                background-color: #64748B;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            """
        )
        self.btn_cancel_edit.clicked.connect(self.clear_form)
        self.btn_cancel_edit.hide()
        btn_layout.addWidget(self.btn_cancel_edit)

        grid.addLayout(btn_layout, 4, 0, 1, 2)

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
        self.btn_refresh.clicked.connect(self.load_projects)
        table_actions_layout.addWidget(self.btn_refresh)
        layout.addLayout(table_actions_layout)

        self.tbl_projects = QTableWidget(group)
        self.tbl_projects.setColumnCount(5)
        self.tbl_projects.setHorizontalHeaderLabels(
            [
                "Mã Dự Án",
                "Tên Dự Án",
                "Kinh doanh (Sales)",
                "Chủ trì Thiết kế",
                "Trạng Thái",
            ]
        )

        header = self.tbl_projects.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.tbl_projects.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_projects.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tbl_projects.itemSelectionChanged.connect(self._on_item_selection_changed)

        layout.addWidget(self.tbl_projects)
        return group

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
        self.current_projects_data = projects
        self.tbl_projects.blockSignals(True)
        self.tbl_projects.setRowCount(len(projects))

        user_names = {
            "quanxu23@gmail.com": "Nguyễn Văn Quân",
            "vanphuctrinh2211@gmail.com": "Trịnh Văn Phúc",
            "ha91steel@gmail.com": "Vũ Thanh Hà",
            "trinh58xd2@gmail.com": "Nguyễn Văn Trịnh",
        }

        for r, p in enumerate(projects):
            item_id = QTableWidgetItem(p["project_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_name = QTableWidgetItem(p["project_name"])
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

            sales_email = p.get("sales_email") or ""
            sales_name = user_names.get(
                sales_email, sales_email if sales_email else "Chưa phân công"
            )
            item_sales = QTableWidgetItem(sales_name)
            item_sales.setFlags(item_sales.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if not sales_email:
                item_sales.setForeground(Qt.GlobalColor.gray)

            designer_email = p.get("designer_email") or ""
            designer_name = user_names.get(
                designer_email,
                designer_email if designer_email else "Chưa phân công",
            )
            item_designer = QTableWidgetItem(designer_name)
            item_designer.setFlags(item_designer.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if not designer_email:
                item_designer.setForeground(Qt.GlobalColor.gray)

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
            self.tbl_projects.setItem(r, 2, item_sales)
            self.tbl_projects.setItem(r, 3, item_designer)
            self.tbl_projects.setItem(r, 4, item_status)

        self.tbl_projects.blockSignals(False)

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

    def _on_create_project(self) -> None:
        """Xử lý sự kiện click nút [Tạo Dự án] hoặc [Lưu Thay Đổi]."""
        project_id = self.txt_project_id.text().strip()
        project_name = self.txt_project_name.text().strip()
        sales_email = self.cb_sales.currentData()
        designer_email = self.cb_designer.currentData()

        if not project_id or not project_name:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập đầy đủ Mã dự án và Tên dự án!"
            )
            return

        success = False
        db = SessionLocal()
        try:
            if self.edit_mode:
                # Chế độ cập nhật dự án hiện có
                proj = project_service.update_project(
                    db,
                    project_id,
                    project_name,
                    roles={"sales": sales_email, "designer": designer_email},
                )
                if proj:
                    success = True
            else:
                # Chế độ tạo mới dự án
                proj = project_service.create_project(
                    db,
                    project_id,
                    project_name,
                    roles={"sales": sales_email, "designer": designer_email},
                )
                if proj:
                    success = True
        except Exception as e:
            logger.error("Lỗi khi xử lý dữ liệu dự án: %s", str(e), exc_info=True)
        finally:
            db.close()

        if success:
            action_str = "Cập nhật" if self.edit_mode else "Tạo"
            QMessageBox.information(
                self,
                "Thông báo",
                f"Đã {action_str.lower()} thành công dự án: {project_id}",
            )
            self.load_projects()
            self.clear_form()
            self.project_created.emit()
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                "Xử lý dự án thất bại. Vui lòng kiểm tra lại log hệ thống.",
            )

    def _on_item_selection_changed(self) -> None:
        """Xử lý khi thay đổi dòng được chọn trên bảng."""
        selected_items = self.tbl_projects.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            item_id = self.tbl_projects.item(row, 0)
            if item_id:
                project_id = item_id.text()
                self.set_edit_project(project_id)
        else:
            self.clear_form()

    def set_edit_project(self, project_id: str) -> None:
        """Kích hoạt chế độ chỉnh sửa thông tin dự án.

        Args:
            project_id: Mã dự án cần chỉnh sửa.
        """
        # Tìm thông tin dự án trong dữ liệu cache
        proj_data = None
        for p in self.current_projects_data:
            if p["project_id"] == project_id:
                proj_data = p
                break

        if not proj_data:
            return

        self.txt_project_id.setText(proj_data["project_id"])
        self.txt_project_id.setReadOnly(True)
        self.txt_project_id.setStyleSheet("background-color: #E2E8F0; color: #64748B;")

        self.txt_project_name.setText(proj_data["project_name"])

        # Set dropdown values
        sales_email = proj_data.get("sales_email") or ""
        idx_sales = self.cb_sales.findData(sales_email)
        if idx_sales >= 0:
            self.cb_sales.setCurrentIndex(idx_sales)

        designer_email = proj_data.get("designer_email") or ""
        idx_designer = self.cb_designer.findData(designer_email)
        if idx_designer >= 0:
            self.cb_designer.setCurrentIndex(idx_designer)

        self.btn_create_proj.setText("💾 Lưu Thay Đổi")
        self.btn_cancel_edit.show()
        self.edit_mode = True

    def clear_form(self) -> None:
        """Reset form về chế độ Tạo mới mặc định."""
        self.txt_project_id.clear()
        self.txt_project_id.setReadOnly(False)
        self.txt_project_id.setStyleSheet("background-color: #F8FAFC; color: #0F172A;")

        self.txt_project_name.clear()
        self.cb_sales.setCurrentIndex(0)
        self.cb_designer.setCurrentIndex(0)

        self.btn_create_proj.setText("➕ Tạo Dự án")
        self.btn_cancel_edit.hide()
        self.edit_mode = False

        # Bỏ chọn dòng trên bảng
        self.tbl_projects.blockSignals(True)
        self.tbl_projects.clearSelection()
        self.tbl_projects.blockSignals(False)

    def select_project_by_id(self, project_id: str) -> None:
        """Đồng bộ chọn dòng trên bảng dự án theo ID.

        Args:
            project_id: Mã dự án cần chọn.
        """
        self.tbl_projects.blockSignals(True)
        found = False
        for row in range(self.tbl_projects.rowCount()):
            item = self.tbl_projects.item(row, 0)
            if item and item.text() == project_id:
                self.tbl_projects.setCurrentCell(row, 0)
                # Kích hoạt Edit Mode cho dự án này luôn
                self.set_edit_project(project_id)
                found = True
                break

        if not found:
            self.clear_form()

        self.tbl_projects.blockSignals(False)
