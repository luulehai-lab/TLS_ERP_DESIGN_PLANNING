# Tên file: ui/main_window.py
# CHỨC NĂNG: Cửa sổ chính điều hướng ứng dụng ERP PyQt6 (Sidebar list dự án, Header tab bar)
# CHANGELOG:
# - 18:19:45 08/07/2026: [UPDATE] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [UPDATE] Kết nối bộ chọn dự án Sidebar với DuAnView để quản lý Hạng mục (Antigravity)
# - 18:03:18 08/07/2026: [UPDATE] feat(ui): support Google Drive folder URLs for drawing packages (Antigravity)
# - 18:00:00 08/07/2026: [UPDATE] Làm sáng nhãn phiên bản ở chân sidebar (Antigravity)
# - 17:58:00 08/07/2026: [UPDATE] Tích hợp DuAnView, thêm tab "QUẢN LÝ DỰ ÁN" trên Header và phân quyền điều hướng (Antigravity)
# - 17:37:32 08/07/2026: [FIX] fix(ui): synchronize drawing status between Design and Planning views with manual and auto refresh (Antigravity)
# - 17:30:00 08/07/2026: [FIX] Khắc phục lỗi chữ trắng trên nền trắng trong các ô nhập liệu, bảng dữ liệu và nút bấm hộp thoại cảnh báo trên các máy chạy Windows Dark Mode (Antigravity)
# - 14:13:50 08/07/2026: [UPDATE] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 13:38:54 08/07/2026: [UPDATE] feat(db): add script to enable Row-Level Security and update code graph (Antigravity)
# - 13:28:00 08/07/2026: [REFACTOR] Chuyển đổi load_projects sang tải bất đồng bộ sử dụng ProjectLoaderThread để tránh treo ứng dụng (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:25:00 02/07/2026: [NEW] Thiết kế cửa sổ chính với giao diện Premium Slate và QStackedWidget (Lê Thanh Vân/Antigravity)
# - 11:19:00 02/07/2026: [UPDATE] Di chuyển bộ chọn Dự án từ các View cục bộ sang Sidebar dùng chung (Lê Thanh Vân/Antigravity)
# - 11:23:00 02/07/2026: [REFACTOR] Trải rộng danh sách dự án (QListWidget) ở Sidebar và đưa nút chuyển View lên Header nằm ngang (Lê Thanh Vân/Antigravity)
# - 11:27:00 02/07/2026: [PERF] Áp dụng cơ chế Lazy Loading giảm thiểu tối đa các truy vấn database đồng thời trên UI Thread (Lê Thanh Vân/Antigravity)

import logging
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QFrame,
    QButtonGroup,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui.views.thiet_ke_view import ThietKeView
from ui.views.ke_hoach_view import KeHoachView
from ui.common.workers import ProjectLoaderThread

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng ERP TK-KH TLS.

    Quản lý danh sách dự án trải rộng bên Sidebar trái và thanh công cụ điều hướng
    (Thiết kế / Kế hoạch) dạng tab ngang trên cùng bên phải.
    """

    logout_clicked: pyqtSignal = pyqtSignal()

    def __init__(self, user_email: str = "", user_dept: str = "") -> None:
        super().__init__()
        self.setWindowTitle("ERP TK-KH - TUAN LONG STEEL (TLS)")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        self.user_email: str = user_email
        self.user_dept: str = user_dept
        self.current_project_id: str = ""
        self.project_loader_thread: ProjectLoaderThread | None = None
        self._init_ui()
        self.load_projects()

    def _init_ui(self) -> None:
        """Khởi tạo cấu trúc layout Sidebar Dự án bên trái và Content Area + Header bên phải."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout chính dạng ngang chia đôi
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar bên trái (Chuyên hiển thị logo và danh sách dự án trải rộng)
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # 2. Vùng bên phải (Bao gồm Header nằm ngang và Content Stack bên dưới)
        right_container = QWidget(self)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 2a. Header nằm ngang phía trên
        header = self._create_header()
        right_layout.addWidget(header)

        # 2b. QStackedWidget chứa các view chính
        self.content_stack = QStackedWidget(right_container)
        right_layout.addWidget(self.content_stack)

        main_layout.addWidget(right_container)

        # Khởi tạo các Views phòng ban
        from ui.views.du_an_view import DuAnView

        self.du_an_view = DuAnView(self)
        self.thiet_ke_view = ThietKeView(self)
        self.ke_hoach_view = KeHoachView(self)

        # Thêm Views vào Stacked Widget
        self.content_stack.addWidget(self.du_an_view)
        self.content_stack.addWidget(self.thiet_ke_view)
        self.content_stack.addWidget(self.ke_hoach_view)

        # Áp dụng stylesheet tổng thể cho ứng dụng
        self._apply_styles()

        # Hiển thị View mặc định dựa vào phân quyền phòng ban
        if self.user_dept == "Kế hoạch":
            self.content_stack.setCurrentIndex(2)
            self.btn_ke_hoach.setChecked(True)
        else:
            # Mặc định mở tab Ban hành Bản vẽ (Index 1) cho phòng Thiết kế để thuận tiện làm việc ngay
            self.content_stack.setCurrentIndex(1)
            self.btn_thiet_ke.setChecked(True)

    def _create_sidebar(self) -> QFrame:
        """Tạo thanh Sidebar bên trái chứa danh sách dự án.

        Returns:
            QFrame: Khung giao diện Sidebar đã hoàn thiện.
        """
        sidebar = QFrame(self)
        sidebar.setObjectName("sidebar")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 20)
        sidebar_layout.setSpacing(10)

        # Phần tiêu đề thương hiệu TLS
        brand_label = QLabel("TUAN LONG STEEL", sidebar)
        brand_label.setObjectName("brandLabel")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand_label)

        sub_brand_label = QLabel("ERP TK-KH SYSTEM", sidebar)
        sub_brand_label.setObjectName("subBrandLabel")
        sub_brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(sub_brand_label)

        # Đường gạch trang trí
        divider = QFrame(sidebar)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("background-color: #1E293B; margin: 10px 0px;")
        sidebar_layout.addWidget(divider)

        # Danh sách dự án trải rộng
        lbl_select = QLabel("DANH SÁCH DỰ ÁN:", sidebar)
        lbl_select.setStyleSheet(
            "color: #38BDF8; font-size: 11px; font-weight: bold; margin-left: 2px;"
        )
        sidebar_layout.addWidget(lbl_select)

        self.lst_projects = QListWidget(sidebar)
        self.lst_projects.setObjectName("projectList")
        self.lst_projects.itemSelectionChanged.connect(self._on_project_selected)
        sidebar_layout.addWidget(self.lst_projects)

        # Thông tin bản quyền / Version ở chân sidebar
        version_label = QLabel("Phiên bản v1.0.0", sidebar)
        version_label.setStyleSheet(
            "color: #94A3B8; font-size: 11px; margin-top: 10px;"
        )
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)

        return sidebar

    def _create_header(self) -> QFrame:
        """Tạo thanh Header nằm ngang bên trên Content Area.

        Header này chứa tên dự án đang chọn ở bên trái và 2 nút tab chuyển đổi view ở bên phải.

        Returns:
            QFrame: Khung Header đã hoàn thiện.
        """
        header = QFrame(self)
        header.setObjectName("headerBar")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Tên dự án hiện hành bên trái
        self.lbl_header_project = QLabel("DỰ ÁN HIỆN HÀNH: Chưa chọn", header)
        self.lbl_header_project.setObjectName("headerProjectLabel")
        self.lbl_header_project.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1E293B;"
        )
        header_layout.addWidget(self.lbl_header_project)

        # Spacer đẩy các tab điều hướng sang phải
        header_layout.addStretch()

        # Group button quản lý trạng thái checked độc quyền cho tab ngang
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Nút chuyển màn hình Dự án
        self.btn_du_an = QPushButton("🏢 QUẢN LÝ DỰ ÁN", header)
        self.btn_du_an.setObjectName("navButton")
        self.btn_du_an.setCheckable(True)
        self.btn_du_an.clicked.connect(lambda: self._switch_view(0))
        self.button_group.addButton(self.btn_du_an)
        header_layout.addWidget(self.btn_du_an)

        # Nút chuyển màn hình Thiết kế
        self.btn_thiet_ke = QPushButton("📂 BAN HÀNH BẢN VẼ", header)
        self.btn_thiet_ke.setObjectName("navButton")
        self.btn_thiet_ke.setCheckable(True)
        self.btn_thiet_ke.clicked.connect(lambda: self._switch_view(1))
        self.button_group.addButton(self.btn_thiet_ke)
        header_layout.addWidget(self.btn_thiet_ke)

        # Nút chuyển màn hình Kế hoạch
        self.btn_ke_hoach = QPushButton("⚙️ TIẾP NHẬN SẢN XUẤT", header)
        self.btn_ke_hoach.setObjectName("navButton")
        self.btn_ke_hoach.setCheckable(True)
        self.btn_ke_hoach.clicked.connect(lambda: self._switch_view(2))
        self.button_group.addButton(self.btn_ke_hoach)
        header_layout.addWidget(self.btn_ke_hoach)

        # Ẩn nút Thiết kế & Dự án nếu người dùng là phòng Kế hoạch
        if self.user_dept == "Kế hoạch":
            self.btn_du_an.hide()
            self.btn_thiet_ke.hide()

        # Thêm đường phân tách nhỏ
        sep = QFrame(header)
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: #E2E8F0; margin: 0px 15px;")
        header_layout.addWidget(sep)

        # Khung thông tin User đăng nhập
        user_info_widget = QWidget(header)
        user_info_layout = QHBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(10)

        # Avatar tròn giả lập bằng chữ cái đầu của email
        first_char = self.user_email[0].upper() if self.user_email else "U"
        self.lbl_avatar = QLabel(first_char, user_info_widget)
        self.lbl_avatar.setStyleSheet(
            """
            background-color: #38BDF8;
            color: #0F172A;
            font-weight: bold;
            font-size: 13px;
            border-radius: 14px;
            min-width: 28px;
            max-width: 28px;
            min-height: 28px;
            max-height: 28px;
            qproperty-alignment: 'AlignCenter';
            """
        )
        user_info_layout.addWidget(self.lbl_avatar)

        # Label email và vai trò
        dept_display = "Thiết Kế" if self.user_dept == "Thiết kế" else "Kế Hoạch"
        self.lbl_user = QLabel(f"{self.user_email}\n({dept_display})", user_info_widget)
        self.lbl_user.setStyleSheet(
            "font-size: 11px; color: #475569; font-weight: 600;"
        )
        user_info_layout.addWidget(self.lbl_user)

        # Nút đăng xuất
        self.btn_logout = QPushButton("🚪 Đăng xuất", user_info_widget)
        self.btn_logout.setStyleSheet(
            """
            background-color: #F1F5F9;
            color: #EF4444;
            border: 1px solid #E2E8F0;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 11px;
            font-weight: bold;
            """
        )
        self.btn_logout.clicked.connect(self._on_logout_clicked)
        user_info_layout.addWidget(self.btn_logout)

        header_layout.addWidget(user_info_widget)

        return header

    def _on_logout_clicked(self) -> None:
        """Xử lý sự kiện click nút đăng xuất."""
        logger.info("Người dùng click đăng xuất: %s", self.user_email)
        self.logout_clicked.emit()

    def load_projects(self) -> None:
        """Truy vấn database bất đồng bộ để nạp danh sách dự án vào QListWidget ở Sidebar."""
        logger.info("Khởi động tiến trình tải danh sách dự án bất đồng bộ...")
        self.lst_projects.blockSignals(True)
        self.lst_projects.clear()

        # Hiển thị thông báo đang kết nối database
        loading_item = QListWidgetItem("🔄 Đang kết nối database Cloud...")
        loading_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Vô hiệu hóa click
        self.lst_projects.addItem(loading_item)
        self.lst_projects.blockSignals(False)

        # Khởi chạy luồng phụ tải dự án
        self.project_loader_thread = ProjectLoaderThread()
        self.project_loader_thread.finished.connect(self._on_projects_loaded)
        self.project_loader_thread.error.connect(self._on_projects_load_error)
        self.project_loader_thread.start()

    def _on_projects_loaded(self, projects: list[dict]) -> None:
        """Xử lý nạp danh sách dự án khi luồng phụ hoàn thành.

        Args:
            projects: Danh sách dự án thô (dạng dict) nhận từ database.
        """
        logger.info("Nạp danh sách dự án nhận được từ luồng phụ vào Sidebar...")
        self.lst_projects.blockSignals(True)
        self.lst_projects.clear()

        # Lưu lại ID dự án đang chọn trước đó (nếu có)
        prev_selected_id = self.current_project_id

        for p in projects:
            p_id = p["project_id"]
            p_name = p["project_name"]
            item = QListWidgetItem(f"🏢 {p_id} - {p_name}")
            item.setData(Qt.ItemDataRole.UserRole, p_id)
            self.lst_projects.addItem(item)

        self.lst_projects.blockSignals(False)

        # Thực hiện chọn lại dự án
        if self.lst_projects.count() > 0:
            found_idx = 0
            if prev_selected_id:
                for i in range(self.lst_projects.count()):
                    item = self.lst_projects.item(i)
                    if item and item.data(Qt.ItemDataRole.UserRole) == prev_selected_id:
                        found_idx = i
                        break
            self.lst_projects.setCurrentRow(found_idx)
        else:
            self._on_project_selected()

    def _on_projects_load_error(self, err_msg: str) -> None:
        """Xử lý lỗi nạp dự án, thông báo cho người dùng và cho phép thử lại.

        Args:
            err_msg: Chi tiết thông điệp lỗi.
        """
        logger.error("Lỗi khi tải danh sách dự án từ Cloud database: %s", err_msg)
        self.lst_projects.blockSignals(True)
        self.lst_projects.clear()

        # Hiển thị thông báo lỗi trên Sidebar để người dùng click tải lại
        error_item = QListWidgetItem("❌ Lỗi kết nối. Click để tải lại...")
        error_item.setData(Qt.ItemDataRole.UserRole, "RETRY")
        self.lst_projects.addItem(error_item)
        self.lst_projects.blockSignals(False)

        # Hiển thị MessageBox cảnh báo thân thiện
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.warning(
            self,
            "Lỗi Kết Nối Cơ Sở Dữ Liệu",
            f"Không thể kết nối đến Database Supabase Cloud.\n\n"
            f"Lưu ý: Vui lòng kiểm tra lại đường truyền mạng hoặc VPN (nếu có).\n\n"
            f"Chi tiết lỗi: {err_msg}",
        )

    def _on_project_selected(self) -> None:
        """Xử lý sự kiện khi click chọn dự án trong QListWidget (Lazy Loading)."""
        selected_items = self.lst_projects.selectedItems()
        if selected_items:
            item = selected_items[0]
            project_id = item.data(Qt.ItemDataRole.UserRole)

            if project_id == "RETRY":
                logger.info("Người dùng click nút tải lại danh sách dự án...")
                self.load_projects()
                return

            logger.info("Dự án được chọn ở Sidebar thay đổi thành: %s", project_id)

            self.current_project_id = project_id
            self.lbl_header_project.setText(f"DỰ ÁN: {item.text()}")

            # Lazy Loading: Chỉ truyền và tải dữ liệu cho View đang hiển thị
            active_idx = self.content_stack.currentIndex()
            if active_idx == 0 and hasattr(self, "du_an_view"):
                self.du_an_view.set_project(project_id)
            elif active_idx == 1 and hasattr(self, "thiet_ke_view"):
                self.thiet_ke_view.set_project(project_id)
            elif active_idx == 2 and hasattr(self, "ke_hoach_view"):
                self.ke_hoach_view.set_project(project_id)
        else:
            logger.info("Không có dự án nào được chọn")
            self.current_project_id = ""
            self.lbl_header_project.setText("DỰ ÁN HIỆN HÀNH: Chưa chọn")

            active_idx = self.content_stack.currentIndex()
            if active_idx == 0 and hasattr(self, "du_an_view"):
                self.du_an_view.set_project("")
            elif active_idx == 1 and hasattr(self, "thiet_ke_view"):
                self.thiet_ke_view.set_project("")
            elif active_idx == 2 and hasattr(self, "ke_hoach_view"):
                self.ke_hoach_view.set_project("")

    def _switch_view(self, index: int) -> None:
        """Định tuyến chuyển đổi view hiển thị trên Content Area.

        Args:
            index: Chỉ mục của view trong QStackedWidget (0: Thiết kế, 1: Kế hoạch).
        """
        logger.info("Chuyển màn hình sang index: %d", index)
        self.content_stack.setCurrentIndex(index)

        # Lazy Loading: Nạp bản vẽ của dự án đang chọn cho view vừa được mở ra
        if index == 0 and hasattr(self, "du_an_view"):
            self.du_an_view.set_project(self.current_project_id)
        elif index == 1 and hasattr(self, "thiet_ke_view"):
            self.thiet_ke_view.set_project(self.current_project_id)
        elif index == 2 and hasattr(self, "ke_hoach_view"):
            self.ke_hoach_view.set_project(self.current_project_id)

    def _apply_styles(self) -> None:
        """Thiết lập các stylesheet CSS (QSS) cho toàn bộ ứng dụng."""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #F8FAFC;
            }
            #sidebar {
                background-color: #0F172A; /* Slate 900 */
                border-right: 1px solid #1E293B;
                min-width: 260px;
                max-width: 260px;
            }
            #brandLabel {
                color: #F1F5F9;
                font-size: 18px;
                font-weight: 800;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1px;
                margin-top: 5px;
            }
            #subBrandLabel {
                color: #38BDF8; /* Sky 400 */
                font-size: 12px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-top: 2px;
            }
            #projectList {
                background-color: transparent;
                border: none;
                outline: none;
                margin-top: 5px;
            }
            #projectList::item {
                color: #94A3B8;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 4px;
            }
            #projectList::item:hover {
                background-color: #1E293B; /* Slate 800 */
                color: #F8FAFC;
            }
            #projectList::item:selected {
                background-color: #38BDF8; /* Sky 400 */
                color: #0F172A; /* Chữ tối */
            }
            #headerBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
                min-height: 60px;
                max-height: 60px;
            }
            #headerProjectLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 700;
                color: #0F172A;
            }
            #navButton {
                color: #475569; /* Slate 600 */
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                margin-left: 8px;
            }
            #navButton:hover {
                color: #0284C7; /* Sky 600 */
                background-color: #F0F9FF; /* Sky 50 */
            }
            #navButton:checked {
                background-color: #E0F2FE; /* Sky 100 */
                color: #0369A1; /* Sky 700 */
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
