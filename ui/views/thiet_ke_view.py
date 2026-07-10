# Tên file: ui/views/thiet_ke_view.py
# CHỨC NĂNG: Màn hình ban hành bản vẽ dành cho phòng Thiết kế
# CHANGELOG:
# - 17:05:31 10/07/2026: [REFACTOR] refactor(ui): modularize CreateProjectDialog and restructure project management to vertical stacked layout (Antigravity)
# - 18:28:04 08/07/2026: [UPDATE] feat(ui): format drawing update time to dd/mm/yy_hh:mm:ss and auto stretch column width (Antigravity)
# - 18:23:41 08/07/2026: [UPDATE] feat(ui): support project sections and drawings nesting, optimize layout rendering (Antigravity)
# - 18:19:45 08/07/2026: [UPDATE] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [UPDATE] Cập nhật thiet_ke_view để hỗ trợ lựa chọn Hạng mục khi ban hành bản vẽ và hiển thị cột Hạng mục (Antigravity)
# - 18:03:19 08/07/2026: [UPDATE] feat(ui): support Google Drive folder URLs for drawing packages (Antigravity)
# - 18:00:00 08/07/2026: [UPDATE] Cải tiến form ban hành bản vẽ dãn tràn hết chiều ngang trang theo yêu cầu (Antigravity)
# - 17:58:00 08/07/2026: [REFACTOR] Tách logic Tạo dự án mới sang view độc lập ui/views/du_an_view.py và tinh gọn giao diện Thiết kế (Antigravity)
# - 17:53:55 08/07/2026: [FIX] fix(ui): fix white text on white background in Windows Dark Mode for QLineEdit, QTableWidget, and QMessageBox (Antigravity)
# - 17:48:00 08/07/2026: [UPDATE] Cập nhật placeholder Drive link để hỗ trợ cả URL thư mục Google Drive (Lê Thanh Vân/Antigravity)
# - 17:37:32 08/07/2026: [FIX] fix(ui): synchronize drawing status between Design and Planning views with manual and auto refresh (Antigravity)
# - 17:30:00 08/07/2026: [FIX] Khắc phục lỗi chữ trắng trên nền trắng trong các ô nhập liệu, bảng dữ liệu và nút bấm hộp thoại cảnh báo trên các máy chạy Windows Dark Mode (Antigravity)
# - 17:15:26 08/07/2026: [FIX] fix(auth): fix socket deadlock, redirect issues and optimize DB connection performance (Antigravity)
# - 17:15:00 08/07/2026: [UPDATE] Thêm nút làm mới thủ công và cơ chế auto-refresh 15 giây (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:30:00 02/07/2026: [NEW] Khởi tạo giao diện Thiết kế view và tích hợp core services (Lê Thanh Vân/Antigravity)
# - 11:19:00 02/07/2026: [UPDATE] Di chuyển bộ chọn Dự án lên Sidebar dùng chung, đồng bộ reload khi tạo dự án (Lê Thanh Vân/Antigravity)

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
from PyQt6.QtCore import Qt, QTimer, QSettings

from core.database import SessionLocal
from core.services import drawing_service, section_service
from ui.common.workers import DrawingLoaderThread

logger = logging.getLogger(__name__)


class ThietKeView(QWidget):
    """Màn hình nghiệp vụ của phòng Thiết kế.

    Cho phép khởi tạo dự án mới, ban hành các bản vẽ kỹ thuật kết cấu thép
    lên hệ thống dựa theo Dự án đang chọn ở Sidebar.
    """

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.main_window = parent
        self.current_project_id: str = ""
        self.last_selected_drawing_id: str | None = None
        self.settings = QSettings("TuanLongSteel", "ERP_TK_KH")
        self._init_ui()

        # Khởi chạy timer tự động làm mới ngầm mỗi 15 giây
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(15000)
        self.refresh_timer.timeout.connect(self.auto_refresh_drawings)
        self.refresh_timer.start()

    def _init_ui(self) -> None:
        """Thiết lập các thành phần giao diện của view Thiết kế."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Phần tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ THIẾT KẾ & BAN HÀNH BẢN VẼ", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Khung ban hành bản vẽ (tràn hết chiều ngang)
        drawing_group = self._create_drawing_group()
        layout.addWidget(drawing_group)

        # 3. Khung bảng danh sách bản vẽ đã ban hành
        table_group = self._create_table_group()
        layout.addWidget(table_group)

        # Áp dụng CSS QSS cho các controls trong view
        self._apply_view_styles()

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

        grid.addWidget(QLabel("Google Drive Link:", group), 4, 0)
        self.txt_drive_link = QLineEdit(group)
        self.txt_drive_link.setPlaceholderText(
            "Dán URL File hoặc Thư mục Google Drive..."
        )
        grid.addWidget(self.txt_drive_link, 4, 1)

        self.btn_create_draw = QPushButton("🚀 Ban hành Bản vẽ", group)
        self.btn_create_draw.clicked.connect(self._on_create_drawing)
        grid.addWidget(self.btn_create_draw, 5, 0, 1, 2)

        return group

    def _create_table_group(self) -> QGroupBox:
        """Tạo khung hiển thị bảng danh sách các bản vẽ.

        Returns:
            QGroupBox: Nhóm bảng hiển thị dữ liệu bản vẽ.
        """
        group = QGroupBox("Danh sách bản vẽ đã ban hành", self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 15, 10, 10)

        # Thanh tiêu đề / công cụ cho bảng
        table_actions_layout = QHBoxLayout()
        table_actions_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 Làm mới", group)
        self.btn_refresh.setFixedWidth(100)
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

        self.tbl_drawings = QTableWidget(group)
        self.tbl_drawings.setColumnCount(7)
        self.tbl_drawings.setHorizontalHeaderLabels(
            [
                "Mã Bản Vẽ",
                "Hạng Mục",
                "Tên Bản Vẽ",
                "Trạng Thái",
                "Phiên Bản",
                "Link Drive",
                "Cập Nhật Lúc",
            ]
        )

        header = self.tbl_drawings.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.sectionResized.connect(self._save_column_widths)

        # Cấu hình chọn nguyên dòng để phục vụ lưu dòng chọn
        self.tbl_drawings.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_drawings.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.tbl_drawings)
        return group

    def set_project(self, project_id: str) -> None:
        """Thiết lập dự án hiện tại từ Sidebar truyền xuống.

        Args:
            project_id: Mã dự án được chọn.
        """
        project_id = project_id if project_id else ""
        if project_id == self.current_project_id:
            logger.debug("Dự án không thay đổi, bỏ qua load DB Thiết kế.")
            return

        logger.info("Thiết lập dự án hiện hành: %s", project_id)
        self.current_project_id = project_id
        self.lbl_current_project.setText(project_id if project_id else "Chưa chọn")
        self.load_sections()
        self.load_drawings()

    def load_sections(self) -> None:
        """Nạp danh sách hạng mục của dự án hiện tại vào Combobox chọn hạng mục."""
        self.cb_sections.clear()
        self.cb_sections.addItem("--- Không chọn hạng mục ---", None)
        if not self.current_project_id:
            return
        db = SessionLocal()
        try:
            sections = section_service.list_project_sections(
                db, self.current_project_id
            )
            for s in sections:
                self.cb_sections.addItem(
                    f"{s.section_code} - {s.section_name}", s.section_id
                )
        except Exception as e:
            logger.error("Lỗi khi nạp hạng mục vào Combobox: %s", str(e), exc_info=True)
        finally:
            db.close()

    def load_drawings(self, silent: bool = False) -> None:
        """Nạp danh sách bản vẽ của dự án đang được chọn vào QTableWidget (Bất đồng bộ).

        Args:
            silent: Nếu True, không xóa bảng cũ và không hiển thị loading item.
        """
        project_id = self.current_project_id

        # Nếu đã có thread cũ đang chạy, ngắt kết nối và dừng nó để tránh chồng chéo
        if hasattr(self, "loader_thread") and self.loader_thread.isRunning():
            if silent:
                # Nếu chạy ngầm, bỏ qua đợt load mới để chờ thread cũ hoàn tất
                return
            try:
                self.loader_thread.finished.disconnect()
                self.loader_thread.error.disconnect()
            except TypeError:
                pass  # Đã ngắt kết nối trước đó
            self.loader_thread.terminate()
            self.loader_thread.wait()

        # Lưu lại dòng bản vẽ đang được chọn trước khi reload
        self.last_selected_drawing_id = self._get_selected_drawing_id()

        if not project_id:
            self.tbl_drawings.setRowCount(0)
            return

        logger.info(
            "Yêu cầu tải danh sách bản vẽ cho dự án: %s (silent=%s)",
            project_id,
            silent,
        )

        if not silent:
            self.tbl_drawings.setRowCount(0)
            # Hiển thị trạng thái loading chuyên nghiệp trên bảng
            self.tbl_drawings.setRowCount(1)
            loading_item = QTableWidgetItem("⏳ Đang tải bản vẽ từ database...")
            loading_item.setFlags(Qt.ItemFlag.NoItemFlags)
            loading_item.setForeground(Qt.GlobalColor.gray)
            self.tbl_drawings.setItem(0, 1, loading_item)

        # Khởi tạo và chạy luồng phụ
        self.loader_thread = DrawingLoaderThread(project_id)
        self.loader_thread.finished.connect(self._on_drawings_loaded)
        self.loader_thread.error.connect(self._on_load_error)
        self.loader_thread.start()

    def _on_drawings_loaded(self, drawings: list[dict[str, Any]]) -> None:
        """Callback nhận kết quả danh sách bản vẽ từ luồng phụ và vẽ lên bảng.

        Args:
            drawings: Danh sách các bản vẽ dưới dạng dict thô đã bóc tách.
        """
        self.tbl_drawings.setRowCount(len(drawings))
        target_row_to_select: int = -1

        for r, d in enumerate(drawings):
            item_id = QTableWidgetItem(d["drawing_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_section = QTableWidgetItem(d.get("section_name", "") or "---")
            item_section.setFlags(item_section.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_name = QTableWidgetItem(d["drawing_name"])
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_status = QTableWidgetItem(d["status"])
            item_status.setFlags(item_status.flags() ^ Qt.ItemFlag.ItemIsEditable)

            # Đổi màu nền theo trạng thái
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
            self.tbl_drawings.setItem(r, 3, item_status)
            self.tbl_drawings.setItem(r, 4, item_version)
            self.tbl_drawings.setItem(r, 5, item_link)
            self.tbl_drawings.setItem(r, 6, item_time)

            # Kiểm tra xem dòng này có khớp với ID đã lưu trước đó không
            if (
                self.last_selected_drawing_id
                and d["drawing_id"] == self.last_selected_drawing_id
            ):
                target_row_to_select = r

        # Khôi phục dòng chọn
        if target_row_to_select != -1:
            self.tbl_drawings.selectRow(target_row_to_select)

        # Khôi phục độ rộng cột đã lưu
        self._restore_column_widths()

    def _on_load_error(self, error_msg: str) -> None:
        """Callback nhận thông báo lỗi từ luồng phụ.

        Args:
            error_msg: Nội dung thông báo lỗi.
        """
        logger.error("Lỗi tải bản vẽ: %s", error_msg)
        self.tbl_drawings.setRowCount(1)
        err_item = QTableWidgetItem("❌ Lỗi tải dữ liệu: Mất kết nối mạng hoặc lỗi DB.")
        err_item.setFlags(Qt.ItemFlag.NoItemFlags)
        err_item.setForeground(Qt.GlobalColor.red)
        self.tbl_drawings.setItem(0, 1, err_item)

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

    def _on_manual_refresh(self) -> None:
        """Xử lý làm mới danh sách bản vẽ thủ công khi bấm nút."""
        logger.info("Nhận yêu cầu làm mới dữ liệu thủ công từ người dùng.")
        self.load_drawings(silent=False)

    def auto_refresh_drawings(self) -> None:
        """Tự động làm mới danh sách bản vẽ ngầm định kỳ bằng QTimer."""
        if not self.current_project_id:
            return
        if hasattr(self, "loader_thread") and self.loader_thread.isRunning():
            return
        self.load_drawings(silent=True)

    def _on_create_drawing(self) -> None:
        """Xử lý sự kiện click nút [Ban hành Bản vẽ]."""
        project_id = self.current_project_id
        drawing_id = self.txt_drawing_id.text().strip()
        drawing_name = self.txt_drawing_name.text().strip()
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
            "drive_link": drive_link,
            "section_id": section_id,
        }

        created_success = False
        db = SessionLocal()
        try:
            draw = drawing_service.create_drawing(db, project_id, drawing_data)
            if draw:
                created_success = True
        except Exception as e:
            logger.error("Lỗi khi ban hành bản vẽ: %s", str(e), exc_info=True)
        finally:
            db.close()

        if created_success:
            QMessageBox.information(
                self, "Thông báo", f"Ban hành thành công bản vẽ: {drawing_id}"
            )
            self.txt_drawing_id.clear()
            self.txt_drawing_name.clear()
            self.txt_drive_link.clear()
            self.load_drawings()
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                "Ban hành bản vẽ thất bại. Vui lòng xem lại log hệ thống hoặc kết nối.",
            )

    def _save_column_widths(self) -> None:
        """Lưu lại độ rộng các cột của bảng bản vẽ thiết kế."""
        widths = [
            self.tbl_drawings.columnWidth(i)
            for i in range(self.tbl_drawings.columnCount())
        ]
        self.settings.setValue("thiet_ke_table_widths", widths)

    def _restore_column_widths(self) -> None:
        """Khôi phục độ rộng các cột của bảng bản vẽ thiết kế."""
        widths = self.settings.value("thiet_ke_table_widths")
        if widths:
            self.tbl_drawings.horizontalHeader().blockSignals(True)
            try:
                for i, w in enumerate(widths):
                    if i < self.tbl_drawings.columnCount():
                        self.tbl_drawings.setColumnWidth(i, int(w))
            except Exception as e:
                logger.error("Lỗi khi khôi phục độ rộng cột bảng thiết kế: %s", str(e))
            self.tbl_drawings.horizontalHeader().blockSignals(False)
        else:
            # Mặc định dãn cột Tên bản vẽ, Link drive và resize nội dung
            header = self.tbl_drawings.horizontalHeader()
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

    def _apply_view_styles(self) -> None:
        """Áp dụng các định dạng giao diện cục bộ (QSS)."""
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
            QComboBox {
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: #F8FAFC;
                color: #0F172A;
            }
            QComboBox:focus {
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
