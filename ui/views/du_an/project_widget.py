# Tên file: ui/views/du_an/project_widget.py
# CHỨC NĂNG: Giao diện hiển thị & chỉnh sửa thông tin Dự án hiện hành dạng hàng ngang nhỏ gọn
# CHANGELOG:
# - 14:35:51 13/07/2026: [UPDATE] feat(drawing-ui): integrate auto google drive file/folder upload and auto fill link during drawing release (Antigravity)
# - 17:24:43 11/07/2026: [UPDATE] feat(staff-ui): create staff management view and tab navigation for admin (Antigravity)
# - 18:28:01 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 16:23:44 10/07/2026: [UPDATE] feat(ui): add right click delete project from sidebar with table reload sync (Antigravity)
# - 16:10:00 10/07/2026: [REFACTOR] Thay đổi thành Form xem/sửa dự án hiện hành dạng hàng ngang nhỏ gọn, loại bỏ bảng danh sách dự án (Lê Thanh Vân/Antigravity)
# - 15:24:10 10/07/2026: [NEW] feat(auth): support auto login with SessionManager (Antigravity)
# - 14:56:00 10/07/2026: [NEW] Khởi tạo component ProjectWidget tách từ du_an_view.py (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QComboBox,
    QFileDialog,
)
from PyQt6.QtCore import pyqtSignal

from core.services.project_service import get_project_safe, update_project_safe
from ui.styles.theme import TLSTheme

logger = logging.getLogger(__name__)


class ProjectWidget(QWidget):
    """Widget hiển thị thông tin chi tiết và cho phép chỉnh sửa Dự án hiện hành."""

    project_updated = pyqtSignal(str)

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo ProjectWidget.

        Args:
            parent: Widget cha của widget này (DuAnView).
        """
        super().__init__(parent)
        self.main_window = parent
        self.current_project_id: str = ""
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập giao diện của ProjectWidget dạng hàng ngang nhỏ gọn."""
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.group_box = QGroupBox("Thông tin chi tiết dự án đang chọn", self)
        grid = QGridLayout(self.group_box)
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 15)

        # 1. Các trường thông tin nhập liệu
        self._setup_info_fields(grid)

        # 2. Nút hành động Lưu thay đổi
        self._setup_action_buttons(grid)

        layout.addWidget(self.group_box, 0, 0)

        # Mặc định ban đầu khi chưa chọn dự án
        self.set_project_id("")

    def _setup_info_fields(self, grid: QGridLayout) -> None:
        """Khởi tạo các trường nhập liệu thông tin dự án.

        Args:
            grid: Bố cục lưới của GroupBox.
        """
        # Hàng 0: Mã dự án và Tên dự án
        grid.addWidget(QLabel("Mã Dự án:", self.group_box), 0, 0)
        self.txt_project_id = QLineEdit(self.group_box)
        self.txt_project_id.setReadOnly(True)
        self.txt_project_id.setStyleSheet("background-color: #E2E8F0; color: #64748B;")
        grid.addWidget(self.txt_project_id, 0, 1)

        grid.addWidget(QLabel("Tên Dự án:", self.group_box), 0, 2)
        self.txt_project_name = QLineEdit(self.group_box)
        self.txt_project_name.setPlaceholderText("Tên dự án kết cấu thép...")
        grid.addWidget(self.txt_project_name, 0, 3)

        # Hàng 1: Sales, Designer
        grid.addWidget(QLabel("Kinh doanh (Sales):", self.group_box), 1, 0)
        self.cb_sales = QComboBox(self.group_box)
        from core.services.project_service import list_staffs_by_role

        try:
            sales = list_staffs_by_role("Kinh doanh")
            for s in sales:
                self.cb_sales.addItem(f"{s['name']} - {s['email']}", s["email"])
        except Exception as e:
            logger.error(
                "Lỗi khi load danh sách Kinh doanh từ DB: %s", str(e), exc_info=True
            )
            self.cb_sales.addItem(
                "Nguyễn Văn Quân - quanxu23@gmail.com", "quanxu23@gmail.com"
            )
            self.cb_sales.addItem(
                "Trịnh Văn Phúc - vanphuctrinh2211@gmail.com",
                "vanphuctrinh2211@gmail.com",
            )
        grid.addWidget(self.cb_sales, 1, 1)

        grid.addWidget(QLabel("Chủ trì Thiết kế:", self.group_box), 1, 2)
        self.cb_designer = QComboBox(self.group_box)
        try:
            designers = list_staffs_by_role("Thiết kế")
            for d in designers:
                self.cb_designer.addItem(f"{d['name']} - {d['email']}", d["email"])
        except Exception as e:
            logger.error(
                "Lỗi khi load danh sách Thiết kế từ DB: %s", str(e), exc_info=True
            )
            self.cb_designer.addItem(
                "Vũ Thanh Hà - ha91steel@gmail.com", "ha91steel@gmail.com"
            )
            self.cb_designer.addItem(
                "Nguyễn Văn Trịnh - trinh58xd2@gmail.com", "trinh58xd2@gmail.com"
            )
        grid.addWidget(self.cb_designer, 1, 3)

        # Hàng 2: Thư mục bản vẽ cục bộ
        grid.addWidget(QLabel("Thư mục cục bộ:", self.group_box), 2, 0)

        path_layout = QHBoxLayout()
        self.txt_local_path = QLineEdit(self.group_box)
        self.txt_local_path.setReadOnly(True)
        self.txt_local_path.setPlaceholderText("Chưa cấu hình thư mục cục bộ chứa bản vẽ...")
        self.txt_local_path.setStyleSheet("background-color: #F1F5F9; color: #1E293B;")

        self.btn_select_local_path = QPushButton("📁 Chọn...", self.group_box)
        self.btn_select_local_path.setStyleSheet(TLSTheme.secondary_button_stylesheet())
        self.btn_select_local_path.clicked.connect(self._on_select_local_path)

        path_layout.addWidget(self.txt_local_path)
        path_layout.addWidget(self.btn_select_local_path)

        grid.addLayout(path_layout, 2, 1, 1, 3)

    def _setup_action_buttons(self, grid: QGridLayout) -> None:
        """Thiết lập các nút điều khiển của Form.

        Args:
            grid: Bố cục lưới của GroupBox.
        """
        self.btn_save = QPushButton("💾 Lưu\nThay Đổi", self.group_box)
        self.btn_save.setStyleSheet(TLSTheme.save_button_stylesheet())
        # Nút Lưu có kích thước lớn hơn chiếm cả hàng 1 và hàng 2 ở cột 4
        self.btn_save.clicked.connect(self._on_save_project)
        grid.addWidget(self.btn_save, 1, 4, 2, 1)

    def _on_select_local_path(self) -> None:
        """Mở hộp thoại chọn thư mục cục bộ của dự án."""
        dir_path = QFileDialog.getExistingDirectory(self, "Chọn Thư mục cục bộ của dự án")
        if dir_path:
            self.txt_local_path.setText(dir_path)

    def set_project_id(self, project_id: str) -> None:
        """Nạp dữ liệu dự án tương ứng từ database lên Form.

        Args:
            project_id: Mã dự án được chọn.
        """
        self.current_project_id = project_id

        if not project_id:
            self.txt_project_id.clear()
            self.txt_project_name.clear()
            self.txt_local_path.clear()
            self.cb_sales.setCurrentIndex(0)
            self.cb_designer.setCurrentIndex(0)
            self.group_box.setEnabled(False)
            self.group_box.setTitle("Thông tin dự án (Vui lòng chọn dự án ở Sidebar)")
            return

        self.group_box.setEnabled(True)
        self.group_box.setTitle(f"Thông tin chi tiết dự án: {project_id}")

        try:
            proj = get_project_safe(project_id)
            if proj:
                self.txt_project_id.setText(proj.project_id)
                self.txt_project_name.setText(proj.project_name)
                self.txt_local_path.setText(proj.local_path or "")

                # Chọn email Kinh doanh
                idx_sales = self.cb_sales.findData(proj.sales_email or "")
                if idx_sales >= 0:
                    self.cb_sales.setCurrentIndex(idx_sales)

                # Chọn email Thiết kế
                idx_designer = self.cb_designer.findData(proj.designer_email or "")
                if idx_designer >= 0:
                    self.cb_designer.setCurrentIndex(idx_designer)
        except Exception as e:
            logger.error(
                "Lỗi khi nạp dữ liệu dự án '%s' lên Form: %s",
                project_id,
                str(e),
                exc_info=True,
            )

    def _on_save_project(self) -> None:
        """Xử lý sự kiện khi bấm nút [Lưu Thay Đổi] để lưu lại cấu hình dự án."""
        project_id = self.current_project_id
        project_name = self.txt_project_name.text().strip()
        sales_email = self.cb_sales.currentData()
        designer_email = self.cb_designer.currentData()
        local_path = self.txt_local_path.text().strip() or None

        if not project_id or not project_name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng không để trống Tên dự án!")
            return

        success = False
        try:
            roles = {"sales": sales_email, "designer": designer_email}
            updated_proj = update_project_safe(
                project_id=project_id,
                project_name=project_name,
                roles=roles,
                local_path=local_path,
            )
            if updated_proj:
                success = True
        except Exception as e:
            logger.error(
                "Lỗi khi cập nhật dự án '%s': %s", project_id, str(e), exc_info=True
            )

        if success:
            QMessageBox.information(
                self,
                "Thông báo",
                f"Đã cập nhật thông tin dự án '{project_id}' thành công.",
            )
            self.project_updated.emit(project_id)
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                "Không thể cập nhật thông tin dự án này. Vui lòng kiểm tra lại DB.",
            )
