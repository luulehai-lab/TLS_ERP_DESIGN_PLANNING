# Tên file: ui/sidebar.py
# CHỨC NĂNG: Thanh Sidebar bên trái chứa danh sách dự án và các nút tạo mới/xóa dự án
# CHANGELOG:
# - 17:29:28 10/07/2026: [NEW] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 17:28:00 10/07/2026: [NEW] Tách SidebarWidget từ MainWindow để tối ưu cấu trúc module (Lê Thanh Vân/Antigravity)

import logging
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint

from ui.common.workers import ProjectLoaderThread
from core.database import SessionLocal
from ui.views.du_an.project_dialog import CreateProjectDialog

logger = logging.getLogger(__name__)


class SidebarWidget(QFrame):
    """Thanh điều hướng Sidebar bên trái.

    Quản lý danh sách dự án và các tác vụ liên quan như tạo mới, xóa dự án.
    """

    project_selected: pyqtSignal = pyqtSignal(
        str, str
    )  # Phát đi: (project_id, display_text)
    project_deleted: pyqtSignal = pyqtSignal(str)  # Phát đi: (project_id)
    project_list_reloaded: pyqtSignal = (
        pyqtSignal()
    )  # Phát đi khi nạp xong danh sách dự án

    def __init__(
        self, parent: QFrame | None = None, user_email: str = "", user_dept: str = ""
    ) -> None:
        """Khởi tạo SidebarWidget.

        Args:
            parent: Widget cha.
            user_email: Email của người dùng đăng nhập.
            user_dept: Phòng ban của người dùng đăng nhập.
        """
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.user_email: str = user_email
        self.user_dept: str = user_dept
        self.current_project_id: str = ""
        self.project_loader_thread: ProjectLoaderThread | None = None

        self._init_ui()
        self.load_projects()

    def _init_ui(self) -> None:
        """Khởi tạo giao diện Sidebar."""
        sidebar_layout = QVBoxLayout(self)
        sidebar_layout.setContentsMargins(15, 25, 15, 20)
        sidebar_layout.setSpacing(10)

        # Phần tiêu đề thương hiệu TLS
        brand_label = QLabel("TUAN LONG STEEL", self)
        brand_label.setObjectName("brandLabel")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand_label)

        sub_brand_label = QLabel("ERP TK-KH SYSTEM", self)
        sub_brand_label.setObjectName("subBrandLabel")
        sub_brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(sub_brand_label)

        # Đường gạch trang trí
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("background-color: #1E293B; margin: 10px 0px;")
        sidebar_layout.addWidget(divider)

        # Tiêu đề danh sách
        lbl_select = QLabel("DANH SÁCH DỰ ÁN:", self)
        lbl_select.setStyleSheet(
            "color: #38BDF8; font-size: 11px; font-weight: bold; margin-left: 2px;"
        )
        sidebar_layout.addWidget(lbl_select)

        # Nút tạo dự án mới (chỉ hiển thị với luu.lehai@gmail.com)
        self.btn_new_project = QPushButton("➕ Tạo dự án mới", self)
        self.btn_new_project.setStyleSheet(
            """
            QPushButton {
                background-color: #0284C7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
            """
        )
        self.btn_new_project.clicked.connect(self._show_create_project_dialog)

        if self.user_email == "luu.lehai@gmail.com":
            self.btn_new_project.show()
        else:
            self.btn_new_project.hide()

        sidebar_layout.addWidget(self.btn_new_project)

        # Danh sách dự án
        self.lst_projects = QListWidget(self)
        self.lst_projects.setObjectName("projectList")
        self.lst_projects.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lst_projects.customContextMenuRequested.connect(
            self._show_project_context_menu
        )
        self.lst_projects.itemSelectionChanged.connect(self._on_project_selected)
        sidebar_layout.addWidget(self.lst_projects)

        # Thông tin bản quyền / Version ở chân sidebar
        version_label = QLabel("Phiên bản v1.0.0", self)
        version_label.setStyleSheet(
            "color: #94A3B8; font-size: 11px; margin-top: 10px;"
        )
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)

    def load_projects(self) -> None:
        """Truy vấn database bất đồng bộ để nạp danh sách dự án vào QListWidget."""
        logger.info("Sidebar: Khởi động tiến trình tải danh sách dự án bất đồng bộ...")
        self.lst_projects.blockSignals(True)
        self.lst_projects.clear()

        loading_item = QListWidgetItem("🔄 Đang kết nối database Cloud...")
        loading_item.setFlags(Qt.ItemFlag.NoItemFlags)
        self.lst_projects.addItem(loading_item)
        self.lst_projects.blockSignals(False)

        self.project_loader_thread = ProjectLoaderThread()
        self.project_loader_thread.finished.connect(self._on_projects_loaded)
        self.project_loader_thread.error.connect(self._on_projects_load_error)
        self.project_loader_thread.start()

    def _on_projects_loaded(self, projects: list[dict]) -> None:
        """Xử lý nạp danh sách dự án khi luồng phụ hoàn thành.

        Args:
            projects: Danh sách dự án dạng dict thô.
        """
        logger.info("Sidebar: Nạp danh sách dự án nhận từ database...")
        self.lst_projects.blockSignals(True)
        self.lst_projects.clear()

        prev_selected_id = self.current_project_id

        for p in projects:
            p_id = p["project_id"]
            p_name = p["project_name"]
            item = QListWidgetItem(f"🏢 {p_id} - {p_name}")
            item.setData(Qt.ItemDataRole.UserRole, p_id)
            self.lst_projects.addItem(item)

        self.lst_projects.blockSignals(False)

        # Chọn lại dự án trước đó nếu có
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

        self.project_list_reloaded.emit()

    def _on_projects_load_error(self, err_msg: str) -> None:
        """Xử lý lỗi nạp dự án.

        Args:
            err_msg: Chi tiết thông điệp lỗi.
        """
        logger.error("Sidebar: Lỗi kết nối Supabase Cloud: %s", err_msg)
        self.lst_projects.blockSignals(True)
        self.lst_projects.clear()

        error_item = QListWidgetItem("❌ Lỗi kết nối. Click để tải lại...")
        error_item.setData(Qt.ItemDataRole.UserRole, "RETRY")
        self.lst_projects.addItem(error_item)
        self.lst_projects.blockSignals(False)

        QMessageBox.warning(
            self,
            "Lỗi Kết Nối Cơ Sở Dữ Liệu",
            f"Không thể kết nối đến Database Supabase Cloud.\n\n"
            f"Lưu ý: Vui lòng kiểm tra lại đường truyền mạng hoặc VPN.\n\n"
            f"Chi tiết lỗi: {err_msg}",
        )

    def _on_project_selected(self) -> None:
        """Xử lý sự kiện chọn dòng dự án trong QListWidget."""
        selected_items = self.lst_projects.selectedItems()
        if selected_items:
            item = selected_items[0]
            project_id = item.data(Qt.ItemDataRole.UserRole)

            if project_id == "RETRY":
                self.load_projects()
                return

            self.current_project_id = project_id
            self.project_selected.emit(project_id, item.text())
        else:
            self.current_project_id = ""
            self.project_selected.emit("", "Chưa chọn")

    def _show_create_project_dialog(self) -> None:
        """Hiển thị hộp thoại tạo dự án mới."""
        dialog = CreateProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_projects()

    def _show_project_context_menu(self, pos: QPoint) -> None:
        """Hiển thị menu chuột phải trên danh sách dự án.

        Args:
            pos: Vị trí chuột.
        """
        item = self.lst_projects.itemAt(pos)
        if not item:
            return

        project_id = item.data(Qt.ItemDataRole.UserRole)
        if not project_id or project_id in [
            "RETRY",
            "🔄 Đang kết nối database Cloud...",
        ]:
            return

        menu = QMenu(self)
        delete_action = menu.addAction("🗑 Xóa dự án")

        action = menu.exec(self.lst_projects.mapToGlobal(pos))
        if action == delete_action:
            self._confirm_and_delete_project(project_id, item.text())

    def _confirm_and_delete_project(self, project_id: str, display_text: str) -> None:
        """Thực hiện đối soát và xác nhận xóa dự án an toàn 2 bước.

        Args:
            project_id: ID dự án cần xóa.
            display_text: Tên hiển thị dự án.
        """
        reply = QMessageBox.warning(
            self,
            "⚠️ Xác nhận Xóa Dự án",
            f"Bạn có chắc chắn muốn xóa dự án:\n\n{display_text}?\n\n"
            f"LƯU Ý: Hành động này sẽ xóa vĩnh viễn dự án này khỏi hệ thống!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        reply2 = QMessageBox.critical(
            self,
            "🛑 CẢNH BÁO NGUY HIỂM",
            f"Dự án '{project_id}' chứa các Hạng mục và Bản vẽ đi kèm.\n\n"
            f"Khi xóa dự án, TOÀN BỘ HẠNG MỤC VÀ BẢN VẼ liên quan cũng sẽ bị xóa vĩnh viễn và KHÔNG THỂ KHÔI PHỤC!\n\n"
            f"Bạn vẫn chắc chắn muốn thực hiện hành động này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply2 != QMessageBox.StandardButton.Yes:
            return

        success = False
        db = SessionLocal()
        try:
            from core.services import project_service

            success = project_service.delete_project(db, project_id)
        except Exception as e:
            logger.error(
                "Lỗi khi xóa dự án '%s': %s", project_id, str(e), exc_info=True
            )
        finally:
            db.close()

        if success:
            QMessageBox.information(
                self, "Thành công", f"Đã xóa thành công dự án: {project_id}"
            )
            if self.current_project_id == project_id:
                self.current_project_id = ""
            self.project_deleted.emit(project_id)
            self.load_projects()
        else:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể xóa dự án '{project_id}'. Vui lòng kiểm tra lại kết nối database.",
            )
