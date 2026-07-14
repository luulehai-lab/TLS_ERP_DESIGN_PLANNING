# Tên file: ui/views/bao_cao/drawing_timeline_widget.py
# CHỨC NĂNG: Widget quản lý và hiển thị tiến độ dòng đời bản vẽ trực quan (Ban hành -> Chuyển xưởng -> Hoàn thành)
# CHANGELOG:
# - 20:05:49 14/07/2026: [NEW] fix(drive): resolve personal Google Drive upload storage quota limit by adopting user OAuth2 credentials (Antigravity)
# - 18:03:00 14/07/2026: [REFACTOR] Tối ưu hóa số lượng dòng của hàm _init_ui và thêm docstrings cho các hàm phụ để vượt qua Code Quality Audit (Lê Thanh Vân/Antigravity)
# - 17:57:00 14/07/2026: [NEW] Khởi tạo widget vẽ dòng đời bản vẽ trực quan bằng TimelineCellWidget và QTableWidget (Lê Thanh Vân/Antigravity)

import logging
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

logger = logging.getLogger(__name__)


class TimelineCellWidget(QWidget):
    """Widget phụ hiển thị sơ đồ dòng đời bản vẽ (Ban hành -> Chuyển xưởng -> Hoàn thành)."""

    def __init__(self, data: dict[str, Any], parent: Any = None) -> None:
        """Khởi tạo TimelineCellWidget.

        Args:
            data: Từ điển chứa thông tin các mốc thời gian và người thực hiện.
            parent: Widget cha.
        """
        super().__init__(parent)
        self._init_ui(data)

    def _init_ui(self, data: dict[str, Any]) -> None:
        """Thiết lập layout và các bước tiến độ dòng đời.

        Args:
            data: Dữ liệu mốc thời gian và người dùng thực hiện.
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 2, 15, 2)
        layout.setSpacing(8)

        # 1. Mốc 1: Ban hành (Luôn kích hoạt nếu bản vẽ tồn tại)
        layout.addWidget(
            self._create_node(
                "Ban hành",
                data.get("issued_at", ""),
                data.get("issued_by", ""),
                (True, "#F59E0B"),
            )
        )

        # Đường nối 1 -> 2
        is_factory_active = bool(data.get("factory_at"))
        layout.addWidget(self._create_connector(is_factory_active, "#0284C7"), 1)

        # 2. Mốc 2: Chuyển xưởng
        layout.addWidget(
            self._create_node(
                "Chuyển xưởng",
                data.get("factory_at", ""),
                data.get("factory_by", ""),
                (is_factory_active, "#0284C7"),
            )
        )

        # Đường nối 2 -> 3
        is_completed_active = bool(data.get("completed_at"))
        layout.addWidget(self._create_connector(is_completed_active, "#047857"), 1)

        # 3. Mốc 3: Hoàn thành
        layout.addWidget(
            self._create_node(
                "Hoàn thành",
                data.get("completed_at", ""),
                data.get("completed_by", ""),
                (is_completed_active, "#047857"),
            )
        )

    def _create_node(
        self,
        title: str,
        time_str: str,
        user_str: str,
        active_info: tuple[bool, str],
    ) -> QWidget:
        """Tạo một Node biểu diễn mốc thời gian trên sơ đồ dòng đời.

        Args:
            title: Tiêu đề mốc thời gian (ví dụ: Ban hành, Chuyển xưởng).
            time_str: Thời gian thực hiện hành động.
            user_str: Người thực hiện hành động.
            active_info: Bộ thông tin kích hoạt gồm trạng thái (bool) và màu sắc (str).

        Returns:
            QWidget đại diện cho Node mốc.
        """
        active, active_color = active_info
        node_widget = QWidget(self)
        node_layout = QVBoxLayout(node_widget)
        node_layout.setContentsMargins(0, 0, 0, 0)
        node_layout.setSpacing(2)

        circle_lbl = QLabel(node_widget)
        circle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if active:
            circle_lbl.setText("●")
            circle_lbl.setStyleSheet(
                f"color: {active_color}; font-size: 18px; font-weight: bold;"
            )
        else:
            circle_lbl.setText("○")
            circle_lbl.setStyleSheet("color: #94A3B8; font-size: 18px;")

        text_lbl = QLabel(node_widget)
        text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_lbl.setWordWrap(False)

        if active:
            display_user = user_str.split("@")[0] if "@" in user_str else user_str
            text_lbl.setText(
                f"<b>{title}</b><br/>"
                f"<span style='font-size: 9px; color: #475569;'>{time_str}<br/>({display_user})</span>"
            )
        else:
            text_lbl.setText(
                f"<span style='color: #94A3B8; font-size: 11px;'><b>{title}</b></span>"
            )

        node_layout.addWidget(circle_lbl)
        node_layout.addWidget(text_lbl)
        return node_widget

    def _create_connector(self, active: bool, active_color: str) -> QWidget:
        """Tạo đường kết nối giữa các mốc tiến độ.

        Args:
            active: Trạng thái kích hoạt của đường nối.
            active_color: Màu sắc của đường nối khi được kích hoạt.

        Returns:
            QWidget đại diện cho đường nối.
        """
        connector = QWidget(self)
        connector_layout = QVBoxLayout(connector)
        connector_layout.setContentsMargins(0, 0, 0, 0)
        connector_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line = QLabel(connector)
        line.setFixedHeight(3)
        if active:
            line.setStyleSheet(f"background-color: {active_color}; border-radius: 1px;")
        else:
            line.setStyleSheet("background-color: #E2E8F0; border-radius: 1px;")
        connector_layout.addWidget(line)
        return connector


class DrawingTimelineWidget(QWidget):
    """Widget chứa bảng Tiến độ Dòng đời Bản vẽ."""

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo DrawingTimelineWidget.

        Args:
            parent: Widget cha hoặc view chính.
        """
        super().__init__(parent)
        self.main_window = parent
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập cấu trúc layout bảng."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        lbl_title = QLabel("🕒 Quy trình & Tiến độ Dòng đời Bản vẽ (Trực quan)", self)
        lbl_title.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 14px;")
        layout.addWidget(lbl_title)

        self.tbl_timeline = QTableWidget(self)
        self.tbl_timeline.setColumnCount(5)
        self.tbl_timeline.setHorizontalHeaderLabels(
            [
                "Mã Bản Vẽ",
                "Tên Bản Vẽ",
                "Phiên Bản",
                "Trạng Thái",
                "Sơ Đồ Tiến Độ Dòng Đời",
            ]
        )
        self.tbl_timeline.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_timeline.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Đặt chiều cao dòng phù hợp để hiển thị trực quan timeline
        self.tbl_timeline.verticalHeader().setDefaultSectionSize(75)

        # Cấu hình co giãn các cột
        header = self.tbl_timeline.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.tbl_timeline)

    def load_data(self, lifecycle_data: list[dict[str, Any]]) -> None:
        """Đổ dữ liệu tiến độ dòng đời bản vẽ vào bảng.

        Args:
            lifecycle_data: Danh sách dòng đời các bản vẽ.
        """
        self.tbl_timeline.setRowCount(len(lifecycle_data))
        for r, item in enumerate(lifecycle_data):
            # Cột 0: Mã bản vẽ
            item_id = QTableWidgetItem(item["drawing_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.tbl_timeline.setItem(r, 0, item_id)

            # Cột 1: Tên bản vẽ
            item_name = QTableWidgetItem(item["drawing_name"])
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.tbl_timeline.setItem(r, 1, item_name)

            # Cột 2: Phiên bản
            item_version = QTableWidgetItem(item["version"])
            item_version.setFlags(item_version.flags() ^ Qt.ItemFlag.ItemIsEditable)
            item_version.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_timeline.setItem(r, 2, item_version)

            # Cột 3: Trạng thái
            item_status = QTableWidgetItem(item["status"])
            item_status.setFlags(item_status.flags() ^ Qt.ItemFlag.ItemIsEditable)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Tô màu trạng thái
            status = item["status"]
            if status == "Chờ triển khai":
                item_status.setForeground(QColor("#F59E0B"))  # Amber
            elif status == "Đang sản xuất":
                item_status.setForeground(QColor("#0284C7"))  # Sky Blue
            elif status == "Đã hoàn thành":
                item_status.setForeground(QColor("#047857"))  # Emerald Green

            self.tbl_timeline.setItem(r, 3, item_status)

            # Cột 4: Visual Timeline Cell Widget
            cell_widget = TimelineCellWidget(data=item)
            self.tbl_timeline.setCellWidget(r, 4, cell_widget)

    def clear(self) -> None:
        """Xóa trắng bảng."""
        self.tbl_timeline.setRowCount(0)
