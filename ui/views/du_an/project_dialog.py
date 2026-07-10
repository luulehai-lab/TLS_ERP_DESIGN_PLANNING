# Tên file: ui/views/du_an/project_dialog.py
# CHỨC NĂNG: Hộp thoại popup nhập liệu để tạo mới một Dự án kết cấu thép
# CHANGELOG:
# - 18:28:01 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 16:23:44 10/07/2026: [NEW] feat(ui): add right click delete project from sidebar with table reload sync (Antigravity)
# - 16:22:00 10/07/2026: [NEW] Khởi tạo CreateProjectDialog tách từ main_window.py để tuân thủ giới hạn 800 dòng (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QComboBox,
    QLineEdit,
    QMessageBox,
)

from core.services.project_service import create_project_safe
from ui.styles.theme import TLSTheme

logger = logging.getLogger(__name__)


class CreateProjectDialog(QDialog):
    """Hộp thoại popup nhập liệu để tạo mới một Dự án kết cấu thép."""

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo hộp thoại CreateProjectDialog.

        Args:
            parent: Widget cha chứa hộp thoại.
        """
        super().__init__(parent)
        self.setWindowTitle("➕ Tạo Dự án Mới")
        self.resize(450, 250)
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập các thành phần giao diện của hộp thoại."""
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.txt_project_id = QLineEdit(self)
        self.txt_project_id.setPlaceholderText("Ví dụ: TLS-01726")
        layout.addRow("Mã Dự án:", self.txt_project_id)

        self.txt_project_name = QLineEdit(self)
        self.txt_project_name.setPlaceholderText("Ví dụ: Nhà máy tôn thép Mỹ Đình...")
        layout.addRow("Tên Dự án:", self.txt_project_name)

        self.cb_sales = QComboBox(self)
        self.cb_sales.addItem(
            "Nguyễn Văn Quân - quanxu23@gmail.com", "quanxu23@gmail.com"
        )
        self.cb_sales.addItem(
            "Trịnh Văn Phúc - vanphuctrinh2211@gmail.com", "vanphuctrinh2211@gmail.com"
        )
        layout.addRow("Kinh doanh (Sales):", self.cb_sales)

        self.cb_designer = QComboBox(self)
        self.cb_designer.addItem(
            "Vũ Thanh Hà - ha91steel@gmail.com", "ha91steel@gmail.com"
        )
        self.cb_designer.addItem(
            "Nguyễn Văn Trịnh - trinh58xd2@gmail.com", "trinh58xd2@gmail.com"
        )
        layout.addRow("Chủ trì Thiết kế:", self.cb_designer)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

        self.setStyleSheet(TLSTheme.project_dialog_stylesheet())

    def _on_save(self) -> None:
        """Xử lý sự kiện lưu dự án khi người dùng đồng ý."""
        project_id = self.txt_project_id.text().strip()
        project_name = self.txt_project_name.text().strip()
        sales_email = self.cb_sales.currentData()
        designer_email = self.cb_designer.currentData()

        if not project_id or not project_name:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập đầy đủ Mã dự án và Tên dự án!"
            )
            return

        try:
            roles = {"sales": sales_email, "designer": designer_email}
            new_proj = create_project_safe(
                project_id=project_id, project_name=project_name, roles=roles
            )
            if new_proj:
                QMessageBox.information(
                    self, "Thành công", f"Đã tạo mới thành công dự án: {project_id}"
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Thất bại",
                    f"Mã dự án '{project_id}' đã tồn tại hoặc lỗi tạo dự án.",
                )
        except Exception as e:
            logger.error("Lỗi khi tạo dự án mới: %s", str(e), exc_info=True)
            QMessageBox.critical(self, "Lỗi", f"Lỗi kết nối cơ sở dữ liệu: {str(e)}")
