# Tên file: ui/views/du_an/project_widget.py
# CHỨC NĂNG: Giao diện hiển thị & chỉnh sửa thông tin Dự án hiện hành dạng hàng ngang nhỏ gọn
# CHANGELOG:
# - 16:23:44 10/07/2026: [UPDATE] feat(ui): add right click delete project from sidebar with table reload sync (Antigravity)
# - 16:10:00 10/07/2026: [REFACTOR] Thay đổi thành Form xem/sửa dự án hiện hành dạng hàng ngang nhỏ gọn, loại bỏ bảng danh sách dự án (Lê Thanh Vân/Antigravity)
# - 15:24:10 10/07/2026: [NEW] feat(auth): support auto login with SessionManager (Antigravity)
# - 14:56:00 10/07/2026: [NEW] Khởi tạo component ProjectWidget tách từ du_an_view.py (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QComboBox,
)
from PyQt6.QtCore import pyqtSignal

from core.database import SessionLocal
from core.services import project_service

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

        # Hàng 1: Sales, Designer và Nút lưu
        grid.addWidget(QLabel("Kinh doanh (Sales):", self.group_box), 1, 0)
        self.cb_sales = QComboBox(self.group_box)
        self.cb_sales.addItem(
            "Nguyễn Văn Quân - quanxu23@gmail.com", "quanxu23@gmail.com"
        )
        self.cb_sales.addItem(
            "Trịnh Văn Phúc - vanphuctrinh2211@gmail.com", "vanphuctrinh2211@gmail.com"
        )
        grid.addWidget(self.cb_sales, 1, 1)

        grid.addWidget(QLabel("Chủ trì Thiết kế:", self.group_box), 1, 2)
        self.cb_designer = QComboBox(self.group_box)
        self.cb_designer.addItem(
            "Vũ Thanh Hà - ha91steel@gmail.com", "ha91steel@gmail.com"
        )
        self.cb_designer.addItem(
            "Nguyễn Văn Trịnh - trinh58xd2@gmail.com", "trinh58xd2@gmail.com"
        )
        grid.addWidget(self.cb_designer, 1, 3)

        self.btn_save = QPushButton("💾 Lưu Thay Đổi", self.group_box)
        self.btn_save.setStyleSheet(
            """
            QPushButton {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E293B;
            }
            """
        )
        self.btn_save.clicked.connect(self._on_save_project)
        grid.addWidget(self.btn_save, 1, 4)

        layout.addWidget(self.group_box, 0, 0)

        # Mặc định ban đầu khi chưa chọn dự án
        self.set_project_id("")

    def set_project_id(self, project_id: str) -> None:
        """Nạp dữ liệu dự án tương ứng từ database lên Form.

        Args:
            project_id: Mã dự án được chọn.
        """
        self.current_project_id = project_id

        if not project_id:
            self.txt_project_id.clear()
            self.txt_project_name.clear()
            self.cb_sales.setCurrentIndex(0)
            self.cb_designer.setCurrentIndex(0)
            self.group_box.setEnabled(False)
            self.group_box.setTitle("Thông tin dự án (Vui lòng chọn dự án ở Sidebar)")
            return

        self.group_box.setEnabled(True)
        self.group_box.setTitle(f"Thông tin chi tiết dự án: {project_id}")

        db = SessionLocal()
        try:
            proj = project_service.get_project(db, project_id)
            if proj:
                self.txt_project_id.setText(proj.project_id)
                self.txt_project_name.setText(proj.project_name)

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
        finally:
            db.close()

    def _on_save_project(self) -> None:
        """Xử lý sự kiện khi bấm nút [Lưu Thay Đổi] để lưu lại cấu hình dự án."""
        project_id = self.current_project_id
        project_name = self.txt_project_name.text().strip()
        sales_email = self.cb_sales.currentData()
        designer_email = self.cb_designer.currentData()

        if not project_id or not project_name:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng không để trống Tên dự án!")
            return

        success = False
        db = SessionLocal()
        try:
            roles = {"sales": sales_email, "designer": designer_email}
            updated_proj = project_service.update_project(
                db, project_id=project_id, project_name=project_name, roles=roles
            )
            if updated_proj:
                success = True
        except Exception as e:
            logger.error(
                "Lỗi khi cập nhật dự án '%s': %s", project_id, str(e), exc_info=True
            )
        finally:
            db.close()

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
