# Tên file: ui/views/thiet_ke_view.py
# CHỨC NĂNG: Màn hình ban hành bản vẽ và quản lý dự án dành cho phòng Thiết kế
# CHANGELOG:
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
)
from PyQt6.QtCore import Qt

from core.database import SessionLocal
from core.services import project_service, drawing_service
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
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập các thành phần giao diện của view Thiết kế."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Phần tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ THIẾT KẾ & BAN HÀNH BẢN VẼ", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Layout ngang chứa 2 panel nhập liệu: Tạo dự án & Ban hành bản vẽ
        forms_layout = QHBoxLayout()
        forms_layout.setSpacing(15)

        # 1. Khung tạo dự án mới
        project_group = self._create_project_group()
        forms_layout.addWidget(project_group)

        # 2. Khung ban hành bản vẽ
        drawing_group = self._create_drawing_group()
        forms_layout.addWidget(drawing_group)

        layout.addLayout(forms_layout)

        # 3. Khung bảng danh sách bản vẽ đã ban hành
        table_group = self._create_table_group()
        layout.addWidget(table_group)

        # Áp dụng CSS QSS cho các controls trong view
        self._apply_view_styles()

    def _create_project_group(self) -> QGroupBox:
        """Tạo panel điều khiển cho nghiệp vụ Dự án.

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

        grid.addWidget(QLabel("Mã Bản vẽ:", group), 1, 0)
        self.txt_drawing_id = QLineEdit(group)
        self.txt_drawing_id.setPlaceholderText("Ví dụ: TLS-D01")
        grid.addWidget(self.txt_drawing_id, 1, 1)

        grid.addWidget(QLabel("Tên Bản vẽ:", group), 2, 0)
        self.txt_drawing_name = QLineEdit(group)
        self.txt_drawing_name.setPlaceholderText("Tên bản vẽ dầm, cột, kèo...")
        grid.addWidget(self.txt_drawing_name, 2, 1)

        grid.addWidget(QLabel("Google Drive Link:", group), 3, 0)
        self.txt_drive_link = QLineEdit(group)
        self.txt_drive_link.setPlaceholderText("Dán URL file PDF trên Drive...")
        grid.addWidget(self.txt_drive_link, 3, 1)

        self.btn_create_draw = QPushButton("🚀 Ban hành Bản vẽ", group)
        self.btn_create_draw.clicked.connect(self._on_create_drawing)
        grid.addWidget(self.btn_create_draw, 4, 0, 1, 2)

        return group

    def _create_table_group(self) -> QGroupBox:
        """Tạo khung hiển thị bảng danh sách các bản vẽ.

        Returns:
            QGroupBox: Nhóm bảng hiển thị dữ liệu bản vẽ.
        """
        group = QGroupBox("Danh sách bản vẽ đã ban hành", self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 15, 10, 10)

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
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )  # Tên bản vẽ tự giãn
        header.setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )  # Link Drive tự giãn

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
        self.load_drawings()

    def load_drawings(self) -> None:
        """Nạp danh sách bản vẽ của dự án đang được chọn vào QTableWidget (Bất đồng bộ)."""
        project_id = self.current_project_id

        # Nếu đã có thread cũ đang chạy, ngắt kết nối và dừng nó để tránh chồng chéo
        if hasattr(self, "loader_thread") and self.loader_thread.isRunning():
            try:
                self.loader_thread.finished.disconnect()
                self.loader_thread.error.disconnect()
            except TypeError:
                pass  # Đã ngắt kết nối trước đó
            self.loader_thread.terminate()
            self.loader_thread.wait()

        self.tbl_drawings.setRowCount(0)
        if not project_id:
            return

        logger.info("Yêu cầu tải danh sách bản vẽ ngầm cho dự án: %s", project_id)

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
        for r, d in enumerate(drawings):
            item_id = QTableWidgetItem(d["drawing_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)

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

            item_time = QTableWidgetItem(d["updated_at"].strftime("%H:%M:%S %d/%m/%Y"))
            item_time.setFlags(item_time.flags() ^ Qt.ItemFlag.ItemIsEditable)

            self.tbl_drawings.setItem(r, 0, item_id)
            self.tbl_drawings.setItem(r, 1, item_name)
            self.tbl_drawings.setItem(r, 2, item_status)
            self.tbl_drawings.setItem(r, 3, item_version)
            self.tbl_drawings.setItem(r, 4, item_link)
            self.tbl_drawings.setItem(r, 5, item_time)

    def _on_load_error(self, error_msg: str) -> None:
        """Callback nhận thông báo lỗi từ luồng phụ.

        Args:
            error_msg: Nội dung thông báo lỗi.
        """
        logger.error("Lỗi tải bản vẽ: %s", error_msg)
        self.tbl_drawings.setRowCount(1)
        err_item = QTableWidgetItem(
            "❌ Lỗi tải dữ liệu: Mất kết nối mạng hoặc lỗi DB."
        )
        err_item.setFlags(Qt.ItemFlag.NoItemFlags)
        err_item.setForeground(Qt.GlobalColor.red)
        self.tbl_drawings.setItem(0, 1, err_item)

    def _on_create_project(self) -> None:
        """Xử lý sự kiện click nút [Tạo Dự án]."""
        project_id = self.txt_project_id.text().strip()
        project_name = self.txt_project_name.text().strip()

        if not project_id or not project_name:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập đầy đủ Mã dự án và Tên dự án!"
            )
            return

        db = SessionLocal()
        try:
            proj = project_service.create_project(db, project_id, project_name)
            if proj:
                QMessageBox.information(
                    self, "Thông báo", f"Đã tạo thành công dự án: {project_id}"
                )
                self.txt_project_id.clear()
                self.txt_project_name.clear()

                # Gọi ngược lên MainWindow để nạp lại danh sách dự án ở Sidebar
                if self.main_window and hasattr(self.main_window, "load_projects"):
                    self.main_window.load_projects()
            else:
                QMessageBox.critical(
                    self,
                    "Lỗi",
                    "Tạo dự án thất bại. Vui lòng kiểm tra lại log hệ thống.",
                )
        except Exception as e:
            logger.error("Lỗi khi tạo dự án: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu để tạo dự án."
            )
        finally:
            db.close()

    def _on_create_drawing(self) -> None:
        """Xử lý sự kiện click nút [Ban hành Bản vẽ]."""
        project_id = self.current_project_id
        drawing_id = self.txt_drawing_id.text().strip()
        drawing_name = self.txt_drawing_name.text().strip()
        drive_link = self.txt_drive_link.text().strip()

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
        }

        db = SessionLocal()
        try:
            draw = drawing_service.create_drawing(db, project_id, drawing_data)
            if draw:
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
                    "Ban hành bản vẽ thất bại. Vui lòng xem lại log hệ thống.",
                )
        except Exception as e:
            logger.error("Lỗi khi ban hành bản vẽ: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Lỗi", "Không thể kết nối database để ban hành bản vẽ."
            )
        finally:
            db.close()

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
            }
            QLineEdit:focus {
                border: 1px solid #38BDF8;
                background-color: #FFFFFF;
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
                gridline-color: #F1F5F9;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #475569;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """
        )
