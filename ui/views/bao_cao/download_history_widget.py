# Tên file: ui/views/bao_cao/download_history_widget.py
# CHỨC NĂNG: Widget quản lý và hiển thị lịch sử tải bản vẽ (Master-Detail)
# CHANGELOG:
# - 20:05:49 14/07/2026: [FIX] fix(drive): resolve personal Google Drive upload storage quota limit by adopting user OAuth2 credentials (Antigravity)
# - 11:39:58 14/07/2026: [NEW] fix(drawing-ui): click on drive link column to open in browser for download (Antigravity)
# - 11:30:00 14/07/2026: [NEW] Khởi tạo widget lịch sử tải bản vẽ để modular hóa BaoCaoView (Lê Thanh Vân/Antigravity)

import logging
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

logger = logging.getLogger(__name__)


class DownloadHistoryWidget(QWidget):
    """Widget hiển thị lịch sử tải bản vẽ dưới dạng Master-Detail."""

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo DownloadHistoryWidget.

        Args:
            parent: Widget cha hoặc main window.
        """
        super().__init__(parent)
        self.main_window = parent
        self._init_ui()

    def _init_ui(self) -> None:
        """Khởi tạo giao diện Master-Detail với QSplitter."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Splitter chia Trái (Master) - Phải (Detail)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Bên trái: Bảng tổng hợp lượt tải
        widget_master = QWidget(self)
        layout_master = QVBoxLayout(widget_master)
        layout_master.setContentsMargins(0, 0, 0, 0)
        lbl_master = QLabel("📂 Tổng hợp lượt tải của từng bản vẽ", widget_master)
        lbl_master.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 14px;")
        layout_master.addWidget(lbl_master)

        self.tbl_download_summary = QTableWidget(widget_master)
        self.tbl_download_summary.setColumnCount(4)
        self.tbl_download_summary.setHorizontalHeaderLabels(
            ["Mã Bản Vẽ", "Tên Bản Vẽ", "Phiên Bản", "Tổng Lượt Tải"]
        )
        self.tbl_download_summary.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_download_summary.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.tbl_download_summary.itemSelectionChanged.connect(
            self._on_summary_selection_changed
        )

        # Co giãn header
        header_m = self.tbl_download_summary.horizontalHeader()
        header_m.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_m.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header_m.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header_m.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout_master.addWidget(self.tbl_download_summary)
        splitter.addWidget(widget_master)

        # Bên phải: Lịch sử chi tiết lượt tải
        widget_detail = QWidget(self)
        layout_detail = QVBoxLayout(widget_detail)
        layout_detail.setContentsMargins(0, 0, 0, 0)
        lbl_detail = QLabel("🕒 Lịch sử tải chi tiết của bản vẽ", widget_detail)
        lbl_detail.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 14px;")
        layout_detail.addWidget(lbl_detail)

        self.tbl_download_details = QTableWidget(widget_detail)
        self.tbl_download_details.setColumnCount(3)
        self.tbl_download_details.setHorizontalHeaderLabels(
            ["Người Tải (Email)", "Thời Gian Tải", "Phiên Bản Tải"]
        )
        self.tbl_download_details.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_download_details.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        # Co giãn header
        header_d = self.tbl_download_details.horizontalHeader()
        header_d.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_d.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_d.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        layout_detail.addWidget(self.tbl_download_details)
        splitter.addWidget(widget_detail)

        # Đặt tỷ lệ Splitter Trái 3/5, Phải 2/5
        splitter.setSizes([360, 240])
        layout.addWidget(splitter)

    def load_data(self, downloads: list[dict[str, Any]]) -> None:
        """Đổ dữ liệu thống kê lượt tải bản vẽ vào bảng Master bên trái.

        Args:
            downloads: Danh sách thống kê lượt tải.
        """
        self.tbl_download_summary.setRowCount(len(downloads))
        for r, item in enumerate(downloads):
            item_id = QTableWidgetItem(item["drawing_id"])
            item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_name = QTableWidgetItem(item["drawing_name"])
            item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_version = QTableWidgetItem(item["version"])
            item_version.setFlags(item_version.flags() ^ Qt.ItemFlag.ItemIsEditable)

            count = item["download_count"]
            item_count = QTableWidgetItem(str(count))
            item_count.setFlags(item_count.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if count > 0:
                item_count.setForeground(QColor("#1B76FF"))
                font = item_count.font()
                font.setBold(True)
                item_count.setFont(font)

            self.tbl_download_summary.setItem(r, 0, item_id)
            self.tbl_download_summary.setItem(r, 1, item_name)
            self.tbl_download_summary.setItem(r, 2, item_version)
            self.tbl_download_summary.setItem(r, 3, item_count)

        self.tbl_download_details.setRowCount(0)  # Reset bảng chi tiết

    def clear(self) -> None:
        """Xóa trắng dữ liệu của các bảng."""
        self.tbl_download_summary.setRowCount(0)
        self.tbl_download_details.setRowCount(0)

    def _on_summary_selection_changed(self) -> None:
        """Xử lý khi người dùng chọn một bản vẽ khác ở bảng Master bên trái."""
        selected_ranges = self.tbl_download_summary.selectedRanges()
        if not selected_ranges:
            self.tbl_download_details.setRowCount(0)
            return
        row = selected_ranges[0].topRow()
        item_id = self.tbl_download_summary.item(row, 0)
        if not item_id:
            self.tbl_download_details.setRowCount(0)
            return

        drawing_id = item_id.text()

        # Truy vấn lịch sử tải chi tiết của bản vẽ này
        from core.services.report_history_service import (
            get_drawing_download_details_safe,
        )

        details = get_drawing_download_details_safe(drawing_id)

        self.tbl_download_details.setRowCount(len(details))
        for r, log in enumerate(details):
            item_user = QTableWidgetItem(log["performed_by"])
            item_user.setFlags(item_user.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_time = QTableWidgetItem(log["timestamp"])
            item_time.setFlags(item_time.flags() ^ Qt.ItemFlag.ItemIsEditable)

            item_version = QTableWidgetItem(log["version"])
            item_version.setFlags(item_version.flags() ^ Qt.ItemFlag.ItemIsEditable)

            self.tbl_download_details.setItem(r, 0, item_user)
            self.tbl_download_details.setItem(r, 1, item_time)
            self.tbl_download_details.setItem(r, 2, item_version)
