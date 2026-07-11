# Tên file: ui/views/ke_hoach_view.py
# CHỨC NĂNG: Giao diện phòng Kế hoạch (tiếp nhận bản vẽ, mở Drive in ấn, cập nhật chuyển xưởng - kế thừa BaseDrawingView)
# CHANGELOG:
# - 17:07:38 11/07/2026: [UPDATE] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 14:45:04 11/07/2026: [UPDATE] feat(drawing): add notes field to drawing issuance form and table (Antigravity)
# - 14:38:00 11/07/2026: [UPDATE] Đổi Người Thực Hiện thành dropdown QComboBox, disable nút khi chưa chọn (Antigravity)
# - 17:29:28 10/07/2026: [FIX] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 17:48:00 10/07/2026: [REFACTOR] Kế thừa BaseDrawingView để tối ưu hóa code và sử dụng theme dùng chung (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QGroupBox,
    QMessageBox,
)
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from ui.styles.theme import TLSTheme
from ui.common.base_drawing_view import BaseDrawingView
from core.database import SessionLocal
from core.services import drawing_service

logger = logging.getLogger(__name__)


class KeHoachView(BaseDrawingView):
    """Màn hình nghiệp vụ của phòng Kế hoạch.

    Cho phép theo dõi bản vẽ chờ triển khai, mở link Google Drive để in ấn,
    và xác nhận chuyển xưởng sản xuất.
    """

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo KeHoachView.

        Args:
            parent: MainWindow chứa view này.
        """
        super().__init__(parent, settings_width_key="ke_hoach_table_widths")
        self._init_ui()

    def _init_ui(self) -> None:
        """Khởi tạo và sắp xếp các thành phần giao diện của view Kế hoạch."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ KẾ HOẠCH & TIẾP NHẬN BẢN VẼ SẢN XUẤT", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Panel điều khiển xử lý bản vẽ đang chọn
        action_group = self._create_action_group()
        layout.addWidget(action_group)

        # Bảng danh sách bản vẽ (Kế thừa từ BaseDrawingView)
        table_group = self._create_table_group("Danh sách bản vẽ kỹ thuật")
        layout.addWidget(table_group)

        # Áp dụng stylesheet dùng chung
        self.setStyleSheet(TLSTheme.content_view_stylesheet())

    def _create_action_group(self) -> QGroupBox:
        """Tạo panel điền thông tin người tiếp nhận và các nút hành động.

        Returns:
            QGroupBox: Nhóm hành động cập nhật bản vẽ.
        """
        group = QGroupBox("Xử lý Bản vẽ được chọn", self)
        grid = QGridLayout(group)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Người Thực Hiện:", group), 0, 0)
        self.cb_performed_by = QComboBox(group)
        self.cb_performed_by.addItem("--- Chọn người thực hiện ---", "")
        from core.services.project_service import list_staffs_by_role

        try:
            planners = list_staffs_by_role("Kế hoạch")
            for p in planners:
                if p["name"] == "Phòng Kế Hoạch":
                    continue
                self.cb_performed_by.addItem(p["name"], p["name"])
        except Exception as e:
            logger.error(
                "Lỗi khi load danh sách Kế hoạch từ DB: %s", str(e), exc_info=True
            )
            for name in [
                "Trần Mạnh Linh",
                "Nguyễn Hồng Thái",
                "Nguyễn Mạnh Tuấn",
                "Lê Viết Hiệu",
            ]:
                self.cb_performed_by.addItem(name, name)
        self.cb_performed_by.currentIndexChanged.connect(self._on_performer_changed)
        grid.addWidget(self.cb_performed_by, 0, 1)

        grid.addWidget(QLabel("Ghi Chú Triển Khai:", group), 1, 0)
        self.txt_note = QLineEdit(group)
        self.txt_note.setPlaceholderText("Ví dụ: In giao Tổ cơ khí 1, đổi mác thép...")
        grid.addWidget(self.txt_note, 1, 1)

        # Layout chứa 2 nút hành động chính nằm ngang
        btn_layout = QHBoxLayout()
        self.btn_open_link = QPushButton("🌐 Mở File/Thư mục (Drive)", group)
        self.btn_open_link.setStyleSheet("background-color: #0284C7;")  # Sky 600
        self.btn_open_link.setEnabled(False)
        self.btn_open_link.clicked.connect(self._on_open_link)
        btn_layout.addWidget(self.btn_open_link)

        self.btn_confirm_prod = QPushButton("✔ Xác Nhận Chuyển Xưởng", group)
        self.btn_confirm_prod.setStyleSheet("background-color: #16A34A;")  # Green 600
        self.btn_confirm_prod.setEnabled(False)
        self.btn_confirm_prod.clicked.connect(self._on_confirm_production)
        btn_layout.addWidget(self.btn_confirm_prod)

        grid.addLayout(btn_layout, 2, 0, 1, 2)

        return group

    def _on_performer_changed(self) -> None:
        """Bật/tắt nút hành động tùy theo việc đã chọn người thực hiện hay chưa."""
        has_performer = bool(self.cb_performed_by.currentData())
        self.btn_open_link.setEnabled(has_performer)
        self.btn_confirm_prod.setEnabled(has_performer)

    def _on_open_link(self) -> None:
        """Xử lý sự kiện click nút [Mở Bản Vẽ (Drive)].

        Sử dụng QDesktopServices để mở URL an toàn trên trình duyệt mặc định.
        """
        drawing_id = self._get_selected_drawing_id()
        if not drawing_id:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn một Bản vẽ từ bảng trước!"
            )
            return

        db = SessionLocal()
        try:
            drawing = (
                db.query(drawing_service.Drawing)
                .filter(drawing_service.Drawing.drawing_id == drawing_id)
                .first()
            )
            if drawing and drawing.drive_link:
                url = QUrl(drawing.drive_link)
                opened = QDesktopServices.openUrl(url)
                if opened:
                    logger.info(
                        "KeHoachView: Đã mở link Drive bản vẽ: ID=%s, Link=%s",
                        drawing_id,
                        drawing.drive_link,
                    )
                else:
                    QMessageBox.warning(
                        self, "Cảnh báo", "Không thể mở đường dẫn URL này!"
                    )
            else:
                QMessageBox.warning(
                    self, "Cảnh báo", "Bản vẽ được chọn không có liên kết Google Drive!"
                )
        except Exception as e:
            logger.error(
                "KeHoachView: Lỗi khi truy xuất link bản vẽ: %s", str(e), exc_info=True
            )
            QMessageBox.critical(
                self, "Lỗi", "Không thể truy vấn liên kết bản vẽ từ database."
            )
        finally:
            db.close()

    def _on_confirm_production(self) -> None:
        """Xử lý sự kiện click nút [Xác Nhận Chuyển Xưởng]."""
        drawing_id = self._get_selected_drawing_id()
        performed_by = self.cb_performed_by.currentData() or ""
        note = self.txt_note.text().strip()

        if not drawing_id:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn một Bản vẽ từ bảng trước!"
            )
            return

        if not performed_by:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn người thực hiện!")
            return

        update_data = {
            "status": "Đang sản xuất",
            "performed_by": performed_by,
            "note": note,
        }

        db = SessionLocal()
        try:
            updated = drawing_service.update_drawing_status(db, drawing_id, update_data)
            if updated:
                QMessageBox.information(
                    self,
                    "Thông báo",
                    f"Đã chuyển bản vẽ {drawing_id} sang trạng thái 'Đang sản xuất'!",
                )
                self.txt_note.clear()
                self.load_drawings()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể chuyển trạng thái bản vẽ.")
        except Exception as e:
            logger.error(
                "KeHoachView: Lỗi khi chuyển trạng thái bản vẽ: %s",
                str(e),
                exc_info=True,
            )
            QMessageBox.critical(
                self, "Lỗi", "Lỗi kết nối database khi chuyển trạng thái bản vẽ."
            )
        finally:
            db.close()
