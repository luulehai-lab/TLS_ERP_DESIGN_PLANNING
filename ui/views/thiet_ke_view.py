# Tên file: ui/views/thiet_ke_view.py
# CHỨC NĂNG: Giao diện ban hành bản vẽ dành cho phòng Thiết kế (kế thừa BaseDrawingView)
# CHANGELOG:
# - 15:17:43 11/07/2026: [UPDATE] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 14:57:00 11/07/2026: [UPDATE] Filter combobox hạng mục theo designer email đăng nhập (Antigravity)
# - 14:34:36 11/07/2026: [REFACTOR] refactor(ui-modularity): complete modular refactoring of codebase graph tools and adopt UI-Backend Separation rules (Antigravity)
# - 14:30:00 11/07/2026: [UPDATE] Thêm ô nhập Ghi chú vào form ban hành bản vẽ (Antigravity)
# - 17:29:28 10/07/2026: [FIX] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 17:45:00 10/07/2026: [REFACTOR] Kế thừa BaseDrawingView để tối ưu hóa code và sử dụng theme dùng chung (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QComboBox,
)

from ui.styles.theme import TLSTheme
from ui.common.base_drawing_view import BaseDrawingView
from core.services.section_service import list_project_sections_safe
from core.services.drawing_service import create_drawing_safe

logger = logging.getLogger(__name__)


class ThietKeView(BaseDrawingView):
    """Màn hình nghiệp vụ của phòng Thiết kế.

    Cho phép ban hành các bản vẽ kỹ thuật kết cấu thép lên hệ thống dựa theo Dự án đang chọn.
    """

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo ThietKeView.

        Args:
            parent: MainWindow chứa view này.
        """
        super().__init__(parent, settings_width_key="thiet_ke_table_widths")
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập các thành phần giao diện của view Thiết kế."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ THIẾT KẾ & BAN HÀNH BẢN VẼ", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Khung ban hành bản vẽ (tràn hết chiều ngang)
        drawing_group = self._create_drawing_group()
        layout.addWidget(drawing_group)

        # Khung bảng danh sách bản vẽ đã ban hành (Kế thừa từ BaseDrawingView)
        table_group = self._create_table_group("Danh sách bản vẽ đã ban hành")
        layout.addWidget(table_group)

        # Áp dụng stylesheet dùng chung
        self.setStyleSheet(TLSTheme.content_view_stylesheet())

    def _create_drawing_group(self) -> QGroupBox:
        """Tạo panel điều khiển cho nghiệp vụ Bản vẽ.

        Returns:
            QGroupBox: Nhóm các ô nhập liệu liên quan tới Bản vẽ.
        """
        group = QGroupBox("Ban hành Bản vẽ Mới", self)
        grid = QGridLayout(group)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Dự án hiện hành:", group), 0, 0)
        self.lbl_current_project = QLabel("Chưa chọn", group)
        self.lbl_current_project.setStyleSheet(
            "font-weight: bold; color: #0284C7; font-size: 13px;"
        )
        grid.addWidget(self.lbl_current_project, 0, 1)

        grid.addWidget(QLabel("Chọn Hạng mục (nếu có):", group), 1, 0)
        self.cb_sections = QComboBox(group)
        grid.addWidget(self.cb_sections, 1, 1)

        grid.addWidget(QLabel("Mã Bản vẽ:", group), 2, 0)
        self.txt_drawing_id = QLineEdit(group)
        self.txt_drawing_id.setPlaceholderText("Ví dụ: TLS-D01")
        grid.addWidget(self.txt_drawing_id, 2, 1)

        grid.addWidget(QLabel("Tên Bản vẽ:", group), 3, 0)
        self.txt_drawing_name = QLineEdit(group)
        self.txt_drawing_name.setPlaceholderText("Tên bản vẽ dầm, cột, kèo...")
        grid.addWidget(self.txt_drawing_name, 3, 1)

        grid.addWidget(QLabel("Ghi chú:", group), 4, 0)
        self.txt_notes = QLineEdit(group)
        self.txt_notes.setPlaceholderText("Ghi chú kỹ thuật (nếu có)...")
        grid.addWidget(self.txt_notes, 4, 1)

        grid.addWidget(QLabel("Google Drive Link:", group), 5, 0)
        self.txt_drive_link = QLineEdit(group)
        self.txt_drive_link.setPlaceholderText(
            "Dán URL File hoặc Thư mục Google Drive..."
        )
        grid.addWidget(self.txt_drive_link, 5, 1)

        self.btn_create_draw = QPushButton("🚀 Ban hành Bản vẽ", group)
        self.btn_create_draw.clicked.connect(self._on_create_drawing)
        grid.addWidget(self.btn_create_draw, 6, 0, 1, 2)

        return group

    def on_project_changed(self) -> None:
        """Ghi đè hook của BaseDrawingView khi dự án thay đổi."""
        self.lbl_current_project.setText(
            self.current_project_id if self.current_project_id else "Chưa chọn"
        )
        self.load_sections()

    def load_sections(self) -> None:
        """Nạp danh sách hạng mục của dự án hiện tại vào Combobox.

        Designer chỉ thấy hạng mục được gán cho mình. Admin/Sale thấy tất cả.
        """
        self.cb_sections.clear()
        self.cb_sections.addItem("--- Không chọn hạng mục ---", None)
        if not self.current_project_id:
            return
        try:
            sections = list_project_sections_safe(self.current_project_id)

            # Lấy email đăng nhập từ MainWindow
            user_email = ""
            if self.main_window and hasattr(self.main_window, "user_email"):
                user_email = (self.main_window.user_email or "").lower()

            is_admin = user_email == "luu.lehai@gmail.com"

            for s in sections:
                # Designer chỉ thấy hạng mục được gán cho mình
                if not is_admin and user_email:
                    s_designer = (s.designer_email or "").lower()
                    if s_designer and s_designer != user_email:
                        continue
                self.cb_sections.addItem(
                    f"{s.section_code} - {s.section_name}", s.section_id
                )
        except Exception as e:
            logger.error(
                "ThietKeView: Lỗi khi nạp hạng mục vào Combobox: %s",
                str(e),
                exc_info=True,
            )

    def _on_create_drawing(self) -> None:
        """Xử lý sự kiện click nút [Ban hành Bản vẽ]."""
        project_id = self.current_project_id
        drawing_id = self.txt_drawing_id.text().strip()
        drawing_name = self.txt_drawing_name.text().strip()
        notes = self.txt_notes.text().strip()
        drive_link = self.txt_drive_link.text().strip()
        section_id = self.cb_sections.currentData()

        if not project_id:
            QMessageBox.warning(
                self,
                "Cảnh báo",
                "Vui lòng chọn hoặc tạo một Dự án ở thanh bên trái trước!",
            )
            return

        if not drawing_id or not drawing_name:
            QMessageBox.warning(
                self, "Cảnh báo", "Mã bản vẽ và Tên bản vẽ là bắt buộc!"
            )
            return

        drawing_data = {
            "drawing_id": drawing_id,
            "drawing_name": drawing_name,
            "notes": notes,
            "drive_link": drive_link,
            "section_id": section_id,
        }

        created_success = False
        try:
            draw = create_drawing_safe(project_id, drawing_data)
            if draw:
                created_success = True
        except Exception as e:
            logger.error(
                "ThietKeView: Lỗi khi ban hành bản vẽ: %s", str(e), exc_info=True
            )

        if created_success:
            QMessageBox.information(
                self, "Thông báo", f"Ban hành thành công bản vẽ: {drawing_id}"
            )
            self.txt_drawing_id.clear()
            self.txt_drawing_name.clear()
            self.txt_notes.clear()
            self.txt_drive_link.clear()
            self.load_drawings()
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                "Ban hành bản vẽ thất bại. Vui lòng xem lại log hệ thống hoặc kết nối.",
            )
