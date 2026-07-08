# Tên file: ui/views/ke_hoach_view.py
# CHỨC NĂNG: Giao diện phòng Kế hoạch (tiếp nhận bản vẽ, mở Drive in ấn, cập nhật chuyển xưởng)
# CHANGELOG:
# - 17:53:55 08/07/2026: [FIX] fix(ui): fix white text on white background in Windows Dark Mode for QLineEdit, QTableWidget, and QMessageBox (Antigravity)
# - 17:48:00 08/07/2026: [UPDATE] Cập nhật nhãn nút mở link Drive để làm rõ hỗ trợ cả file và thư mục Google Drive (Lê Thanh Vân/Antigravity)
# - 17:37:32 08/07/2026: [FIX] fix(ui): synchronize drawing status between Design and Planning views with manual and auto refresh (Antigravity)
# - 17:30:00 08/07/2026: [FIX] Khắc phục lỗi chữ trắng trên nền trắng trong các ô nhập liệu, bảng dữ liệu và nút bấm hộp thoại cảnh báo trên các máy chạy Windows Dark Mode (Antigravity)
# - 17:15:26 08/07/2026: [FIX] fix(auth): fix socket deadlock, redirect issues and optimize DB connection performance (Antigravity)
# - 17:18:00 08/07/2026: [UPDATE] Thêm nút làm mới thủ công và cơ chế auto-refresh 15 giây (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:35:00 02/07/2026: [NEW] Khởi tạo giao diện Kế hoạch view và liên kết QDesktopServices mở link (Lê Thanh Vân/Antigravity)
# - 11:19:00 02/07/2026: [UPDATE] Di chuyển bộ chọn Dự án lên Sidebar dùng chung, làm gọn giao diện cục bộ (Lê Thanh Vân/Antigravity)

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
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QDesktopServices

from core.database import SessionLocal
from core.services import drawing_service
from ui.common.workers import DrawingLoaderThread

logger = logging.getLogger(__name__)


class KeHoachView(QWidget):
    """Màn hình nghiệp vụ của phòng Kế hoạch.

    Cho phép theo dõi bản vẽ chờ triển khai của Dự án chọn tại Sidebar,
    mở link Google Drive để in bản vẽ và cập nhật trạng thái "Đang sản xuất".
    """

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.main_window = parent
        self.current_project_id: str = ""
        self.last_selected_drawing_id: str | None = None
        self._init_ui()

        # Khởi chạy timer tự động làm mới ngầm mỗi 15 giây
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(15000)
        self.refresh_timer.timeout.connect(self.auto_refresh_drawings)
        self.refresh_timer.start()

    def _init_ui(self) -> None:
        """Khởi tạo và sắp xếp các thành phần giao diện của view Kế hoạch."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ KẾ HOẠCH & TIẾP NHẬN BẢN VẼ SẢN XUẤT", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Panel điều khiển xử lý bản vẽ đang chọn (Trải ngang toàn chiều rộng)
        action_group = self._create_action_group()
        layout.addWidget(action_group)

        # Bảng danh sách bản vẽ
        table_group = self._create_table_group()
        layout.addWidget(table_group)

        self._apply_view_styles()

    def _create_action_group(self) -> QGroupBox:
        """Tạo panel điền thông tin người tiếp nhận và các nút hành động.

        Returns:
            QGroupBox: Nhóm hành động cập nhật bản vẽ.
        """
        group = QGroupBox("Xử lý Bản vẽ được chọn", self)
        grid = QGridLayout(group)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Người Thực Hiện:", group), 0, 0)
        self.txt_performed_by = QLineEdit(group)
        self.txt_performed_by.setPlaceholderText("Tên nhân viên Kế hoạch...")
        grid.addWidget(self.txt_performed_by, 0, 1)

        grid.addWidget(QLabel("Ghi Chú Triển Khai:", group), 1, 0)
        self.txt_note = QLineEdit(group)
        self.txt_note.setPlaceholderText("Ví dụ: In giao Tổ cơ khí 1, đổi mác thép...")
        grid.addWidget(self.txt_note, 1, 1)

        # Layout chứa 2 nút hành động chính nằm ngang
        btn_layout = QHBoxLayout()
        self.btn_open_link = QPushButton("🌐 Mở File/Thư mục (Drive)", group)
        self.btn_open_link.setStyleSheet("background-color: #0284C7;")  # Sky 600
        self.btn_open_link.clicked.connect(self._on_open_link)
        btn_layout.addWidget(self.btn_open_link)

        self.btn_confirm_prod = QPushButton("✔ Xác Nhận Chuyển Xưởng", group)
        self.btn_confirm_prod.setStyleSheet("background-color: #16A34A;")  # Green 600
        self.btn_confirm_prod.clicked.connect(self._on_confirm_production)
        btn_layout.addWidget(self.btn_confirm_prod)

        grid.addLayout(btn_layout, 2, 0, 1, 2)

        return group

    def _create_table_group(self) -> QGroupBox:
        """Tạo bảng danh sách bản vẽ.

        Returns:
            QGroupBox: Khung chứa bảng hiển thị dữ liệu bản vẽ.
        """
        group = QGroupBox("Danh sách bản vẽ kỹ thuật", self)
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
        self.tbl_drawings.setColumnCount(6)
        self.tbl_drawings.setHorizontalHeaderLabels(
            [
                "Mã Bản Vẽ",
                "Tên Bản Vẽ",
                "Trạng Thái",
                "Phiên Bản",
                "Link Drive",
                "Cập Nhật Lúc",
            ]
        )

        header = self.tbl_drawings.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        # Cấu hình chọn nguyên dòng để dễ xử lý thao tác
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
            logger.debug("Dự án không thay đổi, bỏ qua load DB Kế hoạch.")
            return

        logger.info("Thiết lập dự án hiện hành tại view Kế hoạch: %s", project_id)
        self.current_project_id = project_id
        self.load_drawings()

    def load_drawings(self, silent: bool = False) -> None:
        """Nạp danh sách bản vẽ của dự án đang chọn (Bất đồng bộ).

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
            "Yêu cầu tải danh sách bản vẽ ngầm (Kế hoạch) cho dự án: %s (silent=%s)",
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
        """Callback nhận danh sách bản vẽ tải ngầm và vẽ lên bảng.

        Args:
            drawings: Danh sách bản vẽ dạng dict thô.
        """
        self.tbl_drawings.setRowCount(len(drawings))
        target_row_to_select: int = -1

        for r, d in enumerate(drawings):
            item_id = QTableWidgetItem(d["drawing_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_name = QTableWidgetItem(d["drawing_name"])
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_status = QTableWidgetItem(d["status"])
            item_status.setFlags(item_status.flags() ^ Qt.ItemFlag.ItemIsEditable)

            # Định nghĩa màu sắc trực quan theo trạng thái
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

            item_time = QTableWidgetItem(d["updated_at"].strftime("%H:%M:%S %d/%m/%Y"))
            item_time.setFlags(item_time.flags() ^ Qt.ItemFlag.ItemIsEditable)

            self.tbl_drawings.setItem(r, 0, item_id)
            self.tbl_drawings.setItem(r, 1, item_name)
            self.tbl_drawings.setItem(r, 2, item_status)
            self.tbl_drawings.setItem(r, 3, item_version)
            self.tbl_drawings.setItem(r, 4, item_link)
            self.tbl_drawings.setItem(r, 5, item_time)

            # Kiểm tra xem dòng này có khớp với ID đã lưu trước đó không
            if (
                self.last_selected_drawing_id
                and d["drawing_id"] == self.last_selected_drawing_id
            ):
                target_row_to_select = r

        # Khôi phục dòng chọn
        if target_row_to_select != -1:
            self.tbl_drawings.selectRow(target_row_to_select)

    def _on_load_error(self, error_msg: str) -> None:
        """Callback hiển thị thông báo lỗi khi không thể tải bản vẽ từ luồng phụ.

        Args:
            error_msg: Chi tiết thông báo lỗi.
        """
        logger.error("Lỗi tải bản vẽ Kế hoạch: %s", error_msg)
        self.tbl_drawings.setRowCount(1)
        err_item = QTableWidgetItem("❌ Lỗi tải dữ liệu: Mất kết nối mạng hoặc lỗi DB.")
        err_item.setFlags(Qt.ItemFlag.NoItemFlags)
        err_item.setForeground(Qt.GlobalColor.red)
        self.tbl_drawings.setItem(0, 1, err_item)

    def _on_manual_refresh(self) -> None:
        """Xử lý làm mới danh sách bản vẽ thủ công khi bấm nút."""
        logger.info("Nhận yêu cầu làm mới dữ liệu thủ công từ người dùng Kế hoạch.")
        self.load_drawings(silent=False)

    def auto_refresh_drawings(self) -> None:
        """Tự động làm mới danh sách bản vẽ ngầm định kỳ bằng QTimer."""
        if not self.current_project_id:
            return
        if hasattr(self, "loader_thread") and self.loader_thread.isRunning():
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

    def _on_open_link(self) -> None:
        """Xử lý sự kiện click nút [Mở Bản Vẽ (Drive)].

        Truy xuất URL Google Drive của bản vẽ đang chọn và dùng QDesktopServices
        để mở URL này trên trình duyệt mặc định của hệ thống.
        """
        drawing_id = self._get_selected_drawing_id()
        if not drawing_id:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn một Bản vẽ từ bảng trước!"
            )
            return

        db = SessionLocal()
        try:
            # Truy vấn lấy link của bản vẽ
            drawing = (
                db.query(drawing_service.Drawing)
                .filter(drawing_service.Drawing.drawing_id == drawing_id)
                .first()
            )
            if drawing and drawing.drive_link:
                # Sử dụng QDesktopServices để mở URL an toàn trên trình duyệt mặc định
                url = QUrl(drawing.drive_link)
                opened = QDesktopServices.openUrl(url)
                if opened:
                    logger.info(
                        "Đã mở link Drive bản vẽ: ID=%s, Link=%s",
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
            logger.error("Lỗi khi truy xuất link bản vẽ: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Lỗi", "Không thể truy vấn liên kết bản vẽ từ database."
            )
        finally:
            db.close()

    def _on_confirm_production(self) -> None:
        """Xử lý sự kiện click nút [Xác Nhận Chuyển Xưởng]."""
        drawing_id = self._get_selected_drawing_id()
        performed_by = self.txt_performed_by.text().strip()
        note = self.txt_note.text().strip()

        if not drawing_id:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn một Bản vẽ từ bảng trước!"
            )
            return

        if not performed_by:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập tên người tiếp nhận vận hành!"
            )
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
            logger.error("Lỗi khi chuyển trạng thái bản vẽ: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Lỗi", "Lỗi kết nối database khi chuyển trạng thái bản vẽ."
            )
        finally:
            db.close()

    def _apply_view_styles(self) -> None:
        """Áp dụng stylesheet QSS cho các thành phần giao diện của view Kế hoạch."""
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
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
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
