# Tên file: ui/common/base_drawing_view.py
# CHỨC NĂNG: Class cha dùng chung cho các View hiển thị bảng Bản vẽ (Thiết kế / Kế hoạch)
# CHANGELOG:
# - 13:12:37 13/07/2026: [UPDATE] docs: sync codebase graph and update modular graph (Antigravity)
# - 13:10:00 13/07/2026: [NEW] feat(search): add drawing search field with multi-column client-side filter (Lê Thanh Vân/Antigravity)
# - 18:09:38 11/07/2026: [UPDATE] feat(drawing-ui): add version input field to drawing release form and update backend (Antigravity)
# - 18:08:00 11/07/2026: [UPDATE] Tích hợp QRPreviewWidget hiển thị QR Code động bên cạnh bảng bản vẽ (Lê Thanh Vân/Antigravity)
# - 16:38:10 11/07/2026: [UPDATE] test(ke-hoach): add UI unit tests for performer combobox validation (Antigravity)
# - 15:17:43 11/07/2026: [UPDATE] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 14:57:00 11/07/2026: [UPDATE] Filter bảng bản vẽ theo phân quyền designer cấp hạng mục (Antigravity)
# - 14:30:00 11/07/2026: [UPDATE] Thêm cột Ghi Chú vào bảng danh sách bản vẽ (Antigravity)
# - 17:29:28 10/07/2026: [NEW] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 17:40:00 10/07/2026: [NEW] Khởi tạo BaseDrawingView gom logic bảng bản vẽ bất đồng bộ (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QHeaderView,
    QLineEdit,
)
from PyQt6.QtCore import Qt, QTimer, QSettings

from ui.common.workers import DrawingLoaderThread
from ui.styles.theme import TLSTheme

logger = logging.getLogger(__name__)


class BaseDrawingView(QWidget):
    """Lớp cơ sở cho các màn hình quản lý bản vẽ.

    Chứa logic dùng chung cho việc tải bản vẽ bất đồng bộ, hiển thị bảng,
    lưu trữ trạng thái và tự động làm mới dữ liệu.
    """

    def __init__(
        self, parent: Any = None, settings_width_key: str = "drawing_table_widths"
    ) -> None:
        """Khởi tạo BaseDrawingView.

        Args:
            parent: Widget cha.
            settings_width_key: Khóa dùng để lưu/khôi phục độ rộng cột bảng bản vẽ.
        """
        super().__init__(parent)
        self.main_window = parent
        self.current_project_id: str = ""
        self.last_selected_drawing_id: str | None = None
        self.settings = QSettings("TuanLongSteel", "ERP_TK_KH")
        self.settings_width_key: str = settings_width_key
        self.loader_thread: DrawingLoaderThread | None = None

        # Khởi chạy timer tự động làm mới ngầm mỗi 15 giây
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(15000)
        self.refresh_timer.timeout.connect(self.auto_refresh_drawings)
        self.refresh_timer.start()

    def _create_table_group(self, title: str = "Danh sách bản vẽ") -> QGroupBox:
        """Tạo group box chứa bảng danh sách bản vẽ dùng chung.

        Args:
            title: Tiêu đề của group box.

        Returns:
            QGroupBox chứa bảng bản vẽ và nút Refresh.
        """
        group = QGroupBox(title, self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 15, 10, 10)

        # Thanh tiêu đề / công cụ cho bảng
        table_actions_layout = QHBoxLayout()

        self.txt_search_drawing = QLineEdit(group)
        self.txt_search_drawing.setPlaceholderText(
            "🔍 Tìm bản vẽ (Mã, tên, ghi chú...)..."
        )
        self.txt_search_drawing.setClearButtonEnabled(True)
        self.txt_search_drawing.setFixedWidth(250)
        self.txt_search_drawing.textChanged.connect(self.filter_drawings)
        table_actions_layout.addWidget(self.txt_search_drawing)

        table_actions_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Làm mới", group)
        self.btn_refresh.setFixedWidth(100)
        self.btn_refresh.setStyleSheet(TLSTheme.refresh_button_stylesheet())
        self.btn_refresh.clicked.connect(self._on_manual_refresh)
        table_actions_layout.addWidget(self.btn_refresh)
        layout.addLayout(table_actions_layout)

        # Layout ngang chứa bảng bản vẽ bên trái và QR Widget bên phải
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        self.tbl_drawings = QTableWidget(group)
        self.tbl_drawings.setColumnCount(8)
        self.tbl_drawings.setHorizontalHeaderLabels(
            [
                "Mã Bản Vẽ",
                "Hạng Mục",
                "Tên Bản Vẽ",
                "Ghi Chú",
                "Trạng Thái",
                "Phiên Bản",
                "Link Drive",
                "Cập Nhật Lúc",
            ]
        )

        header = self.tbl_drawings.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.sectionResized.connect(self._save_column_widths)

        # Cấu hình chọn nguyên dòng
        self.tbl_drawings.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_drawings.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tbl_drawings.itemSelectionChanged.connect(self._on_table_selection_changed)

        content_layout.addWidget(self.tbl_drawings, 4)

        # Nhúng QRPreviewWidget
        from ui.common.qr_widget import QRPreviewWidget

        self.qr_widget = QRPreviewWidget(group)
        content_layout.addWidget(self.qr_widget, 1)

        layout.addLayout(content_layout)
        return group

    def set_project(self, project_id: str) -> None:
        """Thiết lập dự án hiện tại và nạp danh sách bản vẽ tương ứng.

        Args:
            project_id: Mã dự án được chọn.
        """
        project_id = project_id if project_id else ""
        if project_id == self.current_project_id:
            return

        self.current_project_id = project_id
        self.on_project_changed()
        self.load_drawings()

    def on_project_changed(self) -> None:
        """Hàm hook dành cho các class con ghi đè khi dự án thay đổi."""
        pass

    def load_drawings(self, silent: bool = False) -> None:
        """Nạp danh sách bản vẽ của dự án đang chọn (Bất đồng bộ).

        Args:
            silent: Nếu True, không xóa bảng cũ và không hiển thị loading item.
        """
        project_id = self.current_project_id

        # Nếu đã có thread cũ đang chạy, ngắt kết nối và dừng nó để tránh chồng chéo
        if self.loader_thread and self.loader_thread.isRunning():
            if silent:
                return
            try:
                self.loader_thread.finished.disconnect()
                self.loader_thread.error.disconnect()
            except TypeError:
                pass
            self.loader_thread.terminate()
            self.loader_thread.wait()

        self.last_selected_drawing_id = self._get_selected_drawing_id()

        if not project_id:
            self.tbl_drawings.setRowCount(0)
            return

        if not silent:
            self.tbl_drawings.setRowCount(0)
            self.tbl_drawings.setRowCount(1)
            loading_item = QTableWidgetItem("⏳ Đang tải bản vẽ từ database...")
            loading_item.setFlags(Qt.ItemFlag.NoItemFlags)
            loading_item.setForeground(Qt.GlobalColor.gray)
            self.tbl_drawings.setItem(0, 1, loading_item)

        self.loader_thread = DrawingLoaderThread(project_id)
        self.loader_thread.finished.connect(self._on_drawings_loaded)
        self.loader_thread.error.connect(self._on_load_error)
        self.loader_thread.start()

    def _on_drawings_loaded(self, drawings: list[dict[str, Any]]) -> None:
        """Callback nhận danh sách bản vẽ tải ngầm và vẽ lên bảng.

        Args:
            drawings: Danh sách bản vẽ dạng dict thô.
        """
        # Phân quyền: designer chỉ thấy bản vẽ thuộc hạng mục được gán
        # Sale và Admin xem được tất cả bản vẽ
        user_email = ""
        if self.main_window and hasattr(self.main_window, "user_email"):
            user_email = (self.main_window.user_email or "").lower()
        is_admin = user_email == "luu.lehai@gmail.com"
        # Lấy phòng ban của user
        user_dept = ""
        if self.main_window and hasattr(self.main_window, "user_dept"):
            user_dept = self.main_window.user_dept
        is_planning = (
            user_dept == "Kế hoạch" or user_email == "phongkehoachkythuat25@gmail.com"
        )

        # Kiểm tra user có phải là Sale của dự án này không
        is_project_sale = False
        if drawings and user_email:
            p_sales = (drawings[0].get("project_sales_email") or "").lower()
            is_project_sale = user_email == p_sales

        if not is_admin and not is_planning and not is_project_sale and user_email:
            filtered = []
            for d in drawings:
                s_designer = (d.get("section_designer_email") or "").lower()
                # Hiện bản vẽ nếu: section không gán designer, hoặc designer khớp
                if not s_designer or s_designer == user_email:
                    filtered.append(d)
            drawings = filtered

        self.tbl_drawings.setRowCount(len(drawings))
        target_row_to_select: int = -1

        for r, d in enumerate(drawings):
            item_id = QTableWidgetItem(d["drawing_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_section = QTableWidgetItem(d.get("section_name", "") or "---")
            item_section.setFlags(item_section.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_name = QTableWidgetItem(d["drawing_name"])
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_notes = QTableWidgetItem(d.get("notes", ""))
            item_notes.setFlags(item_notes.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_status = QTableWidgetItem(d["status"])
            item_status.setFlags(item_status.flags() ^ Qt.ItemFlag.ItemIsEditable)

            status_str = d["status"]
            if status_str == "Chờ triển khai":
                item_status.setForeground(Qt.GlobalColor.darkYellow)
            elif status_str == "Đang sản xuất":
                item_status.setForeground(Qt.GlobalColor.blue)
            elif status_str == "Đã hoàn thành":
                item_status.setForeground(Qt.GlobalColor.darkGreen)

            item_version = QTableWidgetItem(d["current_version"])
            item_version.setFlags(item_version.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_link = QTableWidgetItem(d["drive_link"] or "Trống")
            item_link.setFlags(item_link.flags() ^ Qt.ItemFlag.ItemIsEditable)

            from datetime import timedelta

            local_time = d["updated_at"] + timedelta(hours=7)
            item_time = QTableWidgetItem(local_time.strftime("%d/%m/%y_%H:%M:%S"))
            item_time.setFlags(item_time.flags() ^ Qt.ItemFlag.ItemIsEditable)

            self.tbl_drawings.setItem(r, 0, item_id)
            self.tbl_drawings.setItem(r, 1, item_section)
            self.tbl_drawings.setItem(r, 2, item_name)
            self.tbl_drawings.setItem(r, 3, item_notes)
            self.tbl_drawings.setItem(r, 4, item_status)
            self.tbl_drawings.setItem(r, 5, item_version)
            self.tbl_drawings.setItem(r, 6, item_link)
            self.tbl_drawings.setItem(r, 7, item_time)

            if (
                self.last_selected_drawing_id
                and d["drawing_id"] == self.last_selected_drawing_id
            ):
                target_row_to_select = r

        if target_row_to_select != -1:
            self.tbl_drawings.selectRow(target_row_to_select)
        else:
            if hasattr(self, "qr_widget"):
                self.qr_widget.clear_qr()

        self._restore_column_widths()

        # Áp dụng bộ lọc tìm kiếm hiện hành
        if hasattr(self, "txt_search_drawing"):
            self.filter_drawings(self.txt_search_drawing.text())

    def _on_load_error(self, error_msg: str) -> None:
        """Callback hiển thị thông báo lỗi khi không thể tải bản vẽ.

        Args:
            error_msg: Chi tiết thông báo lỗi.
        """
        logger.error("BaseDrawingView: Lỗi tải bản vẽ: %s", error_msg)
        self.tbl_drawings.setRowCount(1)
        err_item = QTableWidgetItem("❌ Lỗi tải dữ liệu: Mất kết nối mạng hoặc lỗi DB.")
        err_item.setFlags(Qt.ItemFlag.NoItemFlags)
        err_item.setForeground(Qt.GlobalColor.red)
        self.tbl_drawings.setItem(0, 1, err_item)

    def _on_manual_refresh(self) -> None:
        """Xử lý làm mới danh sách bản vẽ thủ công khi bấm nút."""
        logger.info("BaseDrawingView: Nhận yêu cầu làm mới dữ liệu thủ công.")
        self.load_drawings(silent=False)

    def auto_refresh_drawings(self) -> None:
        """Tự động làm mới danh sách bản vẽ ngầm định kỳ bằng QTimer."""
        if not self.current_project_id:
            return
        if self.loader_thread and self.loader_thread.isRunning():
            return
        self.load_drawings(silent=True)

    def _get_selected_drawing_id(self) -> str | None:
        """Lấy Mã bản vẽ của dòng đang được người dùng click chọn trong bảng.

        Returns:
            str | None: Mã bản vẽ, hoặc None nếu không chọn dòng nào.
        """
        selected_ranges = self.tbl_drawings.selectedRanges()
        if not selected_ranges:
            return None
        row = selected_ranges[0].topRow()
        item = self.tbl_drawings.item(row, 0)
        return item.text() if item else None

    def _save_column_widths(self) -> None:
        """Lưu lại độ rộng các cột của bảng bản vẽ."""
        widths = [
            self.tbl_drawings.columnWidth(i)
            for i in range(self.tbl_drawings.columnCount())
        ]
        self.settings.setValue(self.settings_width_key, widths)

    def _restore_column_widths(self) -> None:
        """Khôi phục độ rộng các cột của bảng bản vẽ."""
        widths = self.settings.value(self.settings_width_key)
        if widths:
            self.tbl_drawings.horizontalHeader().blockSignals(True)
            try:
                for i, w in enumerate(widths):
                    if i < self.tbl_drawings.columnCount():
                        self.tbl_drawings.setColumnWidth(i, int(w))
            except Exception as e:
                logger.error("BaseDrawingView: Lỗi khôi phục độ rộng cột: %s", str(e))
            self.tbl_drawings.horizontalHeader().blockSignals(False)
        else:
            header = self.tbl_drawings.horizontalHeader()
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

    def _on_table_selection_changed(self) -> None:
        """Xử lý khi người dùng chọn một bản vẽ khác trong bảng."""
        selected_ranges = self.tbl_drawings.selectedRanges()
        if not selected_ranges:
            if hasattr(self, "qr_widget"):
                self.qr_widget.clear_qr()
            return
        row = selected_ranges[0].topRow()
        item_id = self.tbl_drawings.item(row, 0)
        item_version = self.tbl_drawings.item(row, 5)
        item_link = self.tbl_drawings.item(row, 6)

        drawing_id = item_id.text() if item_id else ""
        version = item_version.text() if item_version else "V1"
        drive_link = item_link.text() if item_link else ""

        if drive_link == "Trống":
            drive_link = ""

        if hasattr(self, "qr_widget"):
            self.qr_widget.set_drawing(drawing_id, version, drive_link)

    def filter_drawings(self, text: str) -> None:
        """Lọc danh sách bản vẽ trên bảng dựa theo từ khóa tìm kiếm (Client-side).

        Args:
            text: Từ khóa tìm kiếm.
        """
        search_term = text.strip().lower()
        for r in range(self.tbl_drawings.rowCount()):
            # Lọc theo nhiều cột: Mã bản vẽ (0), Hạng mục (1), Tên bản vẽ (2), Ghi chú (3), Trạng thái (4)
            row_visible = False
            for col in range(5):
                item = self.tbl_drawings.item(r, col)
                if item and search_term in item.text().lower():
                    row_visible = True
                    break

            # Ẩn hoặc hiển thị hàng
            self.tbl_drawings.setRowHidden(r, not row_visible)
