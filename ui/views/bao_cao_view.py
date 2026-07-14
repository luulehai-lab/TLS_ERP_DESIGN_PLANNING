# Tên file: ui/views/bao_cao_view.py
# CHỨC NĂNG: Giao diện Tab Báo cáo & Thống kê trực quan dành cho tất cả phòng ban
# CHANGELOG:
# - 20:05:49 14/07/2026: [FIX] fix(drive): resolve personal Google Drive upload storage quota limit by adopting user OAuth2 credentials (Antigravity)
# - 17:57:00 14/07/2026: [UPDATE] Cân chỉnh Grid layout biểu đồ, chuyển combobox sang Mã dự án, và tích hợp Tab Tiến độ chuyển xưởng trực quan (Lê Thanh Vân/Antigravity)
# - 11:39:58 14/07/2026: [FIX] fix(drawing-ui): click on drive link column to open in browser for download (Antigravity)
# - 11:34:00 14/07/2026: [REFACTOR] Tách logic Tab Lịch sử tải sang DownloadHistoryWidget và di chuyển ReportLoaderThread để rút gọn file xuống dưới 550 dòng (Lê Thanh Vân/Antigravity)
# - 11:28:00 14/07/2026: [UPDATE] Tích hợp Tab thống kê lượt tải bản vẽ dạng Master-Detail bất đồng bộ vào BaoCaoView (Lê Thanh Vân/Antigravity)
# - 18:49:30 11/07/2026: [NEW] feat(drawing-version-qr): implement drawing revision logic and dynamic QR code panel (Antigravity)
# - 18:36:00 11/07/2026: [FIX] Sửa lỗi combobox trống, typo grid_layout, phân quyền hardcoded email, thông báo sai ngữ cảnh (Lê Thanh Vân/Antigravity)
# - 18:15:00 11/07/2026: [NEW] Khởi tạo màn hình BaoCaoView tích hợp PyQt6-Charts và cơ chế fallback (Lê Thanh Vân/Antigravity)

import logging
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

from ui.styles.theme import TLSTheme
from core.services.project_service import list_active_projects_safe, get_staff_role
from ui.common.workers import ReportLoaderThread
from ui.views.bao_cao.download_history_widget import DownloadHistoryWidget

logger = logging.getLogger(__name__)

# Thử import thư viện Charts để hỗ trợ fallback
try:
    from PyQt6.QtCharts import (
        QBarCategoryAxis,
        QBarSeries,
        QBarSet,
        QChart,
        QChartView,
        QLineSeries,
        QPieSeries,
        QValueAxis,
    )

    HAS_CHARTS = True
except ImportError:
    HAS_CHARTS = False
    logger.warning(
        "BaoCaoView: PyQt6.QtCharts không khả dụng. Sử dụng giao diện fallback."
    )


# Loader thread được quản lý tập trung tại ui.common.workers


class BaoCaoView(QWidget):
    """Màn hình Báo cáo & Thống kê trực quan."""

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo BaoCaoView.

        Args:
            parent: MainWindow chứa view này.
        """
        super().__init__(parent)
        self.main_window = parent
        self.loader_thread: ReportLoaderThread | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập cấu trúc layout giao diện tab Báo cáo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. Thanh tiêu đề & chọn Dự án
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 BÁO CÁO & THỐNG KÊ TIẾN ĐỘ", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        header_layout.addWidget(QLabel("Dự án:", self))
        self.cb_projects = QComboBox(self)
        self.cb_projects.setFixedWidth(300)
        self.cb_projects.currentIndexChanged.connect(self._on_project_changed)
        header_layout.addWidget(self.cb_projects)

        self.btn_refresh = QPushButton("🔄 Làm mới", self)
        self.btn_refresh.setFixedWidth(100)
        self.btn_refresh.setStyleSheet(TLSTheme.refresh_button_stylesheet())
        self.btn_refresh.clicked.connect(self._on_refresh_clicked)
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)

        # 2. Tạo QTabWidget
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Tab 1: Biểu đồ tiến độ
        self.tab_charts = QWidget(self)
        self.layout_grid = QGridLayout(self.tab_charts)
        self.layout_grid.setSpacing(20)
        self.tabs.addTab(self.tab_charts, "📈 Biểu đồ tiến độ")

        # Tab 2: Lịch sử tải bản vẽ
        self._init_download_tab()

        # Tab 3: Tiến độ chuyển xưởng
        self._init_timeline_tab()

        # Áp dụng stylesheet dùng chung
        self.setStyleSheet(TLSTheme.content_view_stylesheet())

        # Load danh sách dự án lần đầu
        self.reload_projects()

    def _init_download_tab(self) -> None:
        """Thiết lập cấu trúc layout giao diện tab Lịch sử tải bản vẽ."""
        self.download_widget = DownloadHistoryWidget(self)
        self.tabs.addTab(self.download_widget, "📥 Lịch sử tải bản vẽ")

    def _init_timeline_tab(self) -> None:
        """Thiết lập cấu trúc layout giao diện tab Tiến độ chuyển xưởng."""
        from ui.views.bao_cao.drawing_timeline_widget import DrawingTimelineWidget

        self.timeline_widget = DrawingTimelineWidget(self)
        self.tabs.addTab(self.timeline_widget, "🕒 Tiến độ chuyển xưởng")

    def set_project(self, project_id: str) -> None:
        """Đồng bộ dự án hiện hành từ MainWindow sang.

        Args:
            project_id: Mã dự án được chọn.
        """
        # Nạp lại danh sách dự án nếu combobox đang trống
        if self.cb_projects.count() == 0:
            self.reload_projects()

        self.cb_projects.blockSignals(True)
        idx = self.cb_projects.findData(project_id)
        if idx != -1:
            self.cb_projects.setCurrentIndex(idx)
        self.cb_projects.blockSignals(False)
        self._on_project_changed()

    def reload_projects(self) -> None:
        """Nạp danh sách dự án mà user được phép xem vào Combobox."""
        self.cb_projects.blockSignals(True)
        self.cb_projects.clear()
        try:
            projects = list_active_projects_safe()

            # Phân quyền lọc danh sách dự án - check vai trò động từ DB
            user_email = ""
            if self.main_window and hasattr(self.main_window, "user_email"):
                user_email = (self.main_window.user_email or "").lower()

            role = get_staff_role(user_email) if user_email else None
            is_admin = role in ["Admin", "Kế hoạch"]

            filtered_projects = []
            for p in projects:
                p_sales = (p.sales_email or "").lower()
                p_designer = (p.designer_email or "").lower()
                section_designers = [
                    (s.designer_email or "").lower() for s in p.sections
                ]

                if (
                    is_admin
                    or not user_email
                    or user_email == p_sales
                    or user_email == p_designer
                    or user_email in section_designers
                ):
                    filtered_projects.append(p)

            for p in filtered_projects:
                self.cb_projects.addItem(p.project_id, p.project_id)
        except Exception as e:
            logger.error(
                "BaoCaoView: Lỗi nạp danh sách dự án: %s", str(e), exc_info=True
            )

        self.cb_projects.blockSignals(False)

        # Nếu có dự án, tự động kích hoạt nạp dữ liệu dự án đầu tiên
        if self.cb_projects.count() > 0:
            self._on_project_changed()
        else:
            self._show_empty_state()

    def _on_project_changed(self) -> None:
        """Xử lý khi thay đổi Dự án hiện hành trên Combobox."""
        project_id = self.cb_projects.currentData()
        if not project_id:
            self._show_empty_state()
            return

        user_email = ""
        if self.main_window and hasattr(self.main_window, "user_email"):
            user_email = self.main_window.user_email or ""

        self._show_loading_state()

        # Khởi chạy luồng nạp dữ liệu bất đồng bộ
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.terminate()
            self.loader_thread.wait()

        self.loader_thread = ReportLoaderThread(project_id, user_email)
        self.loader_thread.finished.connect(self._on_data_loaded)
        self.loader_thread.error.connect(self._on_load_error)
        self.loader_thread.start()

    def _on_refresh_clicked(self) -> None:
        """Xử lý sự kiện bấm nút làm mới báo cáo."""
        self._on_project_changed()

    def _show_loading_state(self) -> None:
        """Hiển thị nhãn Loading trong khi nạp dữ liệu."""
        self._clear_grid()
        lbl = QLabel("⏳ Đang tính toán dữ liệu và dựng biểu đồ từ database...", self)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #64748B; font-weight: bold;")
        self.layout_grid.addWidget(lbl, 0, 0, 1, 1)

    def _show_empty_state(self) -> None:
        """Hiển thị trạng thái không có dữ liệu."""
        self._clear_grid()
        lbl = QLabel(
            "📊 Chưa có dữ liệu bản vẽ để thống kê.\n"
            "Hãy chọn dự án và ban hành bản vẽ để xem báo cáo trực quan tại đây.",
            self,
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 15px; color: #94A3B8; font-weight: bold;")
        self.layout_grid.addWidget(lbl, 0, 0, 1, 1)

    def _clear_grid(self) -> None:
        """Xóa sạch các widget trong khung Grid biểu đồ và reset các bảng tải."""
        # Khôi phục stretches về trạng thái mặc định (0) để thông báo Loading hiển thị cân đối
        self.layout_grid.setColumnStretch(0, 0)
        self.layout_grid.setColumnStretch(1, 0)
        self.layout_grid.setRowStretch(0, 0)
        self.layout_grid.setRowStretch(1, 0)

        while self.layout_grid.count():
            child = self.layout_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if hasattr(self, "download_widget"):
            self.download_widget.clear()
        if hasattr(self, "timeline_widget"):
            self.timeline_widget.clear()

    def _on_load_error(self, err_msg: str) -> None:
        """Callback khi luồng nạp dữ liệu gặp lỗi.

        Args:
            err_msg: Chi tiết thông báo lỗi.
        """
        self._clear_grid()
        QMessageBox.critical(
            self,
            "Lỗi",
            f"Không thể tải dữ liệu báo cáo thống kê:\n{err_msg}",
        )

    def _on_data_loaded(self, stats: dict) -> None:
        """Callback xử lý sau khi dữ liệu thống kê được nạp xong từ DB.

        Args:
            stats: Bộ dữ liệu thống kê đã nạp.
        """
        self._clear_grid()

        try:
            if HAS_CHARTS:
                self._render_charts(stats)
            else:
                self._render_fallback_tables(stats)

            # Đổ dữ liệu lịch sử tải bản vẽ
            if "downloads" in stats:
                self.download_widget.load_data(stats["downloads"])

            # Đổ dữ liệu tiến độ dòng đời bản vẽ
            if "lifecycle" in stats:
                self.timeline_widget.load_data(stats["lifecycle"])
        except Exception:
            logger.error(
                "BaoCaoView: Lỗi khi dựng biểu đồ/bảng thống kê", exc_info=True
            )

    def _render_charts(self, stats: dict) -> None:
        """Vẽ biểu đồ vector cao cấp sử dụng PyQt6.QtCharts.

        Args:
            stats: Bộ dữ liệu thống kê đã nạp.
        """
        # 1. BIỂU ĐỒ 1: Donut Chart - Trạng thái bản vẽ (Dưới/Bên trái)
        chart_status = self._create_donut_chart(stats["status"])
        view_status = QChartView(chart_status)
        view_status.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 8px;")
        self.layout_grid.addWidget(view_status, 0, 0)

        # 2. BIỂU ĐỒ 2: Grouped Bar Chart - Tiến độ theo hạng mục
        chart_sections = self._create_sections_bar_chart(stats["sections"])
        view_sections = QChartView(chart_sections)
        view_sections.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 8px;")
        self.layout_grid.addWidget(view_sections, 0, 1)

        # 3. BIỂU ĐỒ 3: Bar Chart - Năng suất Kỹ sư Thiết kế
        chart_designers = self._create_designers_bar_chart(stats["designers"])
        view_designers = QChartView(chart_designers)
        view_designers.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 8px;")
        self.layout_grid.addWidget(view_designers, 1, 0)

        # 4. BIỂU ĐỒ 4: Line Chart - Biến động theo thời gian
        chart_timeline = self._create_timeline_chart(stats["timeline"])
        view_timeline = QChartView(chart_timeline)
        view_timeline.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 8px;")
        self.layout_grid.addWidget(view_timeline, 1, 1)

        # Thiết lập stretches để chia đều không gian Grid 2x2
        self.layout_grid.setColumnStretch(0, 1)
        self.layout_grid.setColumnStretch(1, 1)
        self.layout_grid.setRowStretch(0, 1)
        self.layout_grid.setRowStretch(1, 1)

    def _create_donut_chart(self, status_stats: dict) -> Any:
        """Khởi tạo Biểu đồ Donut thống kê trạng thái.

        Args:
            status_stats: Thống kê số lượng theo status.

        Returns:
            QChart biểu đồ tròn Donut.
        """
        series = QPieSeries()
        series.setHoleSize(0.35)  # Kích thước donut

        # Định nghĩa màu theo TLSTheme
        colors = {
            "Chờ triển khai": QColor("#F59E0B"),  # Amber
            "Đang sản xuất": QColor("#0284C7"),  # Sky Blue
            "Đã hoàn thành": QColor("#047857"),  # Emerald Green
        }

        total_draws = sum(status_stats.values())

        for name, val in status_stats.items():
            if val > 0:
                percent = (val / total_draws * 100) if total_draws > 0 else 0
                slice_item = series.append(f"{name} ({val} - {percent:.1f}%)", val)
                slice_item.setBrush(colors[name])
                slice_item.setLabelVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("🍩 TỶ LỆ TRẠNG THÁI BẢN VẼ DỰ ÁN")
        font = chart.titleFont()
        font.setPointSize(12)
        font.setBold(True)
        chart.setTitleFont(font)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        return chart

    def _create_sections_bar_chart(self, sec_stats: list) -> Any:
        """Khởi tạo Biểu đồ Cột thống kê theo từng Hạng mục.

        Args:
            sec_stats: Thống kê hạng mục bản vẽ.

        Returns:
            QChart biểu đồ cột.
        """
        chart = QChart()
        series = QBarSeries()

        set_cho_tk = QBarSet("Chờ triển khai")
        set_cho_tk.setBrush(QColor("#F59E0B"))
        set_dang_sx = QBarSet("Đang sản xuất")
        set_dang_sx.setBrush(QColor("#0284C7"))
        set_hoan_thanh = QBarSet("Đã hoàn thành")
        set_hoan_thanh.setBrush(QColor("#047857"))

        categories = []
        for item in sec_stats:
            categories.append(item["section_code"])
            set_cho_tk.append(item["stats"]["Chờ triển khai"])
            set_dang_sx.append(item["stats"]["Đang sản xuất"])
            set_hoan_thanh.append(item["stats"]["Đã hoàn thành"])

        series.append(set_cho_tk)
        series.append(set_dang_sx)
        series.append(set_hoan_thanh)
        chart.addSeries(series)

        chart.setTitle("📊 TIẾN ĐỘ THI CÔNG THEO HẠNG MỤC")
        font = chart.titleFont()
        font.setPointSize(12)
        font.setBold(True)
        chart.setTitleFont(font)

        # Cấu hình trục X danh mục
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # Cấu hình trục Y giá trị
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        return chart

    def _create_designers_bar_chart(self, des_stats: list) -> Any:
        """Khởi tạo Biểu đồ Cột năng suất ban hành Kỹ sư Thiết kế.

        Args:
            des_stats: Danh sách stats của designer.

        Returns:
            QChart biểu đồ cột năng suất.
        """
        chart = QChart()
        series = QBarSeries()

        set_total = QBarSet("Tổng bản vẽ")
        set_total.setBrush(QColor("#334155"))  # Slate Gray
        set_prod = QBarSet("Đang sản xuất")
        set_prod.setBrush(QColor("#0284C7"))  # Sky Blue
        set_comp = QBarSet("Đã hoàn thành")
        set_comp.setBrush(QColor("#047857"))  # Emerald Green

        categories = []
        for item in des_stats:
            categories.append(item["designer_name"])
            set_total.append(item["total"])
            set_prod.append(item["production"])
            set_comp.append(item["completed"])

        series.append(set_total)
        series.append(set_prod)
        series.append(set_comp)
        chart.addSeries(series)

        chart.setTitle("👨‍💻 NĂNG SUẤT THIẾT KẾ CỦA KỸ SƯ")
        font = chart.titleFont()
        font.setPointSize(12)
        font.setBold(True)
        chart.setTitleFont(font)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        return chart

    def _create_timeline_chart(self, timeline_stats: list) -> Any:
        """Khởi tạo Biểu đồ Đường theo thời gian ban hành.

        Args:
            timeline_stats: List thống kê theo ngày.

        Returns:
            QChart biểu đồ đường.
        """
        chart = QChart()
        series = QLineSeries()
        series.setName("Bản vẽ ban hành")

        categories = []
        for i, item in enumerate(timeline_stats):
            # QLineSeries sử dụng giá trị số nguyên (i) làm trục X category
            series.append(i, item["count"])
            # Format ngày ngắn gọn DD/MM
            parts = item["date"].split("-")
            date_formatted = f"{parts[2]}/{parts[1]}"
            categories.append(date_formatted)

        chart.addSeries(series)

        chart.setTitle("📈 TẦN SUẤT BAN HÀNH BẢN VẼ")
        font = chart.titleFont()
        font.setPointSize(12)
        font.setBold(True)
        chart.setTitleFont(font)

        # Nếu không có dữ liệu, thêm dummy category
        if not categories:
            categories = ["Không có"]

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)
        return chart

    def _render_fallback_tables(self, stats: dict) -> None:
        """Giao diện dự phòng (Fallback) khi PyQt6.QtCharts không có sẵn.

        Sử dụng QTableWidget và QProgressBar để biểu diễn số liệu trực quan.

        Args:
            stats: Bộ dữ liệu thống kê.
        """
        # Tạo bảng Thống kê trạng thái (Pie fallback)
        widget_left = QWidget(self)
        layout_left = QVBoxLayout(widget_left)
        lbl_left = QLabel("📊 BẢNG TỔNG HỢP TIẾN ĐỘ BẢN VẼ DỰ ÁN", widget_left)
        lbl_left.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 14px;")
        layout_left.addWidget(lbl_left)

        table_status = QTableWidget(widget_left)
        table_status.setColumnCount(3)
        table_status.setHorizontalHeaderLabels(["Trạng Thái", "Số Lượng", "Tỷ Lệ"])
        table_status.setRowCount(3)

        status_data = stats["status"]
        total = sum(status_data.values())

        rows = [
            ("Chờ triển khai", status_data["Chờ triển khai"], "#F59E0B"),
            ("Đang sản xuất", status_data["Đang sản xuất"], "#0284C7"),
            ("Đã hoàn thành", status_data["Đã hoàn thành"], "#047857"),
        ]

        for r, (name, val, color) in enumerate(rows):
            percent = int((val / total * 100) if total > 0 else 0)

            item_name = QTableWidgetItem(name)
            item_name.setForeground(QColor(color))
            table_status.setItem(r, 0, item_name)
            table_status.setItem(r, 1, QTableWidgetItem(str(val)))

            # Thanh progress bar tỷ lệ
            pbar = QProgressBar(table_status)
            pbar.setValue(percent)
            pbar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
            table_status.setCellWidget(r, 2, pbar)

        layout_left.addWidget(table_status)
        self.layout_grid.addWidget(widget_left, 0, 0)

        # Tạo bảng Thống kê theo hạng mục (Bar fallback)
        widget_right = QWidget(self)
        layout_right = QVBoxLayout(widget_right)
        lbl_right = QLabel("🏢 TIẾN ĐỘ GIA CÔNG THEO HẠNG MỤC", widget_right)
        lbl_right.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 14px;")
        layout_right.addWidget(lbl_right)

        table_sec = QTableWidget(widget_right)
        table_sec.setColumnCount(4)
        table_sec.setHorizontalHeaderLabels(
            ["Mã Hạng Mục", "Chờ TK", "Đang SX", "Đã Xong"]
        )
        sec_data = stats["sections"]
        table_sec.setRowCount(len(sec_data))

        for r, item in enumerate(sec_data):
            table_sec.setItem(r, 0, QTableWidgetItem(item["section_code"]))
            table_sec.setItem(
                r, 1, QTableWidgetItem(str(item["stats"]["Chờ triển khai"]))
            )
            table_sec.setItem(
                r, 2, QTableWidgetItem(str(item["stats"]["Đang sản xuất"]))
            )
            table_sec.setItem(
                r, 3, QTableWidgetItem(str(item["stats"]["Đã hoàn thành"]))
            )

        layout_right.addWidget(table_sec)
        self.layout_grid.addWidget(widget_right, 0, 1)

        # Thiết lập stretches cho giao diện fallback (1 hàng, 2 cột)
        self.layout_grid.setColumnStretch(0, 1)
        self.layout_grid.setColumnStretch(1, 1)
        self.layout_grid.setRowStretch(0, 1)
        self.layout_grid.setRowStretch(1, 0)
