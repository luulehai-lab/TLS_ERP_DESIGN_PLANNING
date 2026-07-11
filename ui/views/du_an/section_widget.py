# Tên file: ui/views/du_an/section_widget.py
# CHỨC NĂNG: Giao diện quản lý Hạng mục Dự án cho phòng Thiết kế
# CHANGELOG:
# - 17:24:43 11/07/2026: [UPDATE] feat(staff-ui): create staff management view and tab navigation for admin (Antigravity)
# - 18:28:01 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:05:31 10/07/2026: [REFACTOR] refactor(ui): modularize CreateProjectDialog and restructure project management to vertical stacked layout (Antigravity)
# - 16:35:00 10/07/2026: [UPDATE] Tích hợp lưu và khôi phục chiều rộng cột cho bảng hạng mục bằng QSettings (Lê Thanh Vân/Antigravity)
# - 15:24:10 10/07/2026: [NEW] feat(auth): support auto login with SessionManager (Antigravity)
# - 15:18:00 10/07/2026: [UPDATE] Bổ sung dropdown gán Thiết kế phụ trách từng Hạng mục và cột hiển thị trên bảng (Lê Thanh Vân/Antigravity)
# - 15:00:00 10/07/2026: [NEW] Khởi tạo component SectionWidget tách từ du_an_view.py (Lê Thanh Vân/Antigravity)

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
from PyQt6.QtCore import Qt, pyqtSignal, QSettings

from core.services.section_service import (
    list_project_sections_safe,
    delete_section_safe,
    create_section_safe,
    update_section_safe,
)
from ui.styles.theme import TLSTheme

logger = logging.getLogger(__name__)


class SectionWidget(QWidget):
    """Widget quản lý nghiệp vụ Thêm và Quản lý Hạng mục trong Dự án."""

    section_changed = pyqtSignal()

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo SectionWidget.

        Args:
            parent: Widget cha của widget này.
        """
        super().__init__(parent)
        self.main_window = parent
        self.current_project_id: str = ""
        self.edit_mode: bool = False
        self.current_section_id: int = 0
        self.current_sections_data: list[Any] = []
        self.settings = QSettings("TuanLongSteel", "ERP_TK_KH")
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập giao diện của SectionWidget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # 1. Khung tạo hạng mục
        section_group = self._create_section_group()
        layout.addWidget(section_group)

        # 2. Bảng danh sách hạng mục
        table_sect_group = self._create_table_sect_group()
        layout.addWidget(table_sect_group)

    def _create_section_group(self) -> QGroupBox:
        """Tạo panel điều khiển cho nghiệp vụ tạo hạng mục.

        Returns:
            QGroupBox: Nhóm các ô nhập liệu liên quan tới Hạng mục.
        """
        group = QGroupBox("Thêm Hạng mục vào Dự án", self)
        grid = QGridLayout(group)
        grid.setSpacing(10)

        # 1. Khởi tạo các trường nhập liệu
        self._setup_form_inputs(grid, group)

        # 2. Khởi tạo các nút hành động thêm/hủy
        self._setup_form_buttons(grid, group)

        return group

    def _setup_form_inputs(self, grid: QGridLayout, group: QGroupBox) -> None:
        """Thiết lập các trường nhập liệu thông tin hạng mục.

        Args:
            grid: Bố cục lưới của GroupBox.
            group: GroupBox chứa các thành phần.
        """
        grid.addWidget(QLabel("Dự án hiện hành:", group), 0, 0)
        self.lbl_selected_project_section = QLabel("Chưa chọn dự án ở Sidebar", group)
        self.lbl_selected_project_section.setStyleSheet(
            "font-weight: bold; color: #0284C7; font-size: 13px;"
        )
        grid.addWidget(self.lbl_selected_project_section, 0, 1)

        grid.addWidget(QLabel("Mã Hạng mục:", group), 1, 0)
        self.txt_section_code = QLineEdit(group)
        self.txt_section_code.setPlaceholderText("Ví dụ: NX1, NX2, MN...")
        grid.addWidget(self.txt_section_code, 1, 1)

        grid.addWidget(QLabel("Tên Hạng mục:", group), 2, 0)
        self.txt_section_name = QLineEdit(group)
        self.txt_section_name.setPlaceholderText("Ví dụ: Nhà xưởng 1, Mái lấy sáng...")
        grid.addWidget(self.txt_section_name, 2, 1)

        grid.addWidget(QLabel("Thiết kế phụ trách:", group), 3, 0)
        self.cb_designer = QComboBox(group)
        from core.services.project_service import list_staffs_by_role

        try:
            designers = list_staffs_by_role("Thiết kế")
            for d in designers:
                self.cb_designer.addItem(f"{d['name']} - {d['email']}", d["email"])
        except Exception as e:
            logger.error(
                "Lỗi khi load danh sách Thiết kế từ DB: %s", str(e), exc_info=True
            )
            self.cb_designer.addItem(
                "Vũ Thanh Hà - ha91steel@gmail.com", "ha91steel@gmail.com"
            )
            self.cb_designer.addItem(
                "Nguyễn Văn Trịnh - trinh58xd2@gmail.com", "trinh58xd2@gmail.com"
            )
        grid.addWidget(self.cb_designer, 3, 1)

    def _setup_form_buttons(self, grid: QGridLayout, group: QGroupBox) -> None:
        """Thiết lập layout chứa nút Lưu/Hủy của Hạng mục.

        Args:
            grid: Bố cục lưới của GroupBox.
            group: GroupBox chứa các thành phần.
        """
        btn_layout = QHBoxLayout()
        self.btn_create_sect = QPushButton("➕ Thêm Hạng mục", group)
        self.btn_create_sect.clicked.connect(self._on_create_section)
        btn_layout.addWidget(self.btn_create_sect)

        self.btn_cancel_edit = QPushButton("❌ Hủy / Tạo mới", group)
        self.btn_cancel_edit.setStyleSheet(TLSTheme.cancel_button_stylesheet())
        self.btn_cancel_edit.clicked.connect(self.clear_form)
        self.btn_cancel_edit.hide()
        btn_layout.addWidget(self.btn_cancel_edit)

        grid.addLayout(btn_layout, 4, 0, 1, 2)

    def _create_table_sect_group(self) -> QGroupBox:
        """Tạo khung hiển thị bảng danh sách các hạng mục của dự án hiện hành.

        Returns:
            QGroupBox: Nhóm bảng hiển thị dữ liệu hạng mục.
        """
        group = QGroupBox("Danh sách hạng mục dự án", self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 15, 10, 10)

        self.tbl_sections = QTableWidget(group)
        self.tbl_sections.setColumnCount(4)
        self.tbl_sections.setHorizontalHeaderLabels(
            ["Mã Hạng Mục", "Tên Hạng Mục", "Thiết kế phụ trách", "Hành Động"]
        )

        header = self.tbl_sections.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.sectionResized.connect(self._save_column_widths)

        self.tbl_sections.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tbl_sections.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tbl_sections.itemSelectionChanged.connect(self._on_item_selection_changed)

        layout.addWidget(self.tbl_sections)
        return group

    def set_project(self, project_id: str) -> None:
        """Thiết lập dự án hiện hành để tải hạng mục tương ứng.

        Args:
            project_id: Mã dự án hiện hành.
        """
        self.current_project_id = project_id if project_id else ""
        self.lbl_selected_project_section.setText(
            project_id if project_id else "Chưa chọn dự án"
        )
        self.load_sections()

    def load_sections(self) -> None:
        """Tải danh sách hạng mục của dự án hiện hành từ database (Đồng bộ)."""
        self.tbl_sections.blockSignals(True)
        self.tbl_sections.setRowCount(0)
        if not self.current_project_id:
            self.current_sections_data = []
            self.tbl_sections.blockSignals(False)
            return

        try:
            sections = list_project_sections_safe(self.current_project_id)
            self.current_sections_data = sections
            self.tbl_sections.setRowCount(len(sections))

            user_names = {
                "ha91steel@gmail.com": "Vũ Thanh Hà",
                "trinh58xd2@gmail.com": "Nguyễn Văn Trịnh",
            }

            for r, s in enumerate(sections):
                item_code = QTableWidgetItem(s.section_code)
                item_code.setData(Qt.ItemDataRole.UserRole, s.section_id)
                item_code.setFlags(item_code.flags() ^ Qt.ItemFlag.ItemIsEditable)

                item_name = QTableWidgetItem(s.section_name)
                item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)

                designer_email = s.designer_email or ""
                designer_name = user_names.get(
                    designer_email,
                    designer_email if designer_email else "Chưa phân công",
                )
                item_designer = QTableWidgetItem(designer_name)
                item_designer.setFlags(
                    item_designer.flags() ^ Qt.ItemFlag.ItemIsEditable
                )
                if not designer_email:
                    item_designer.setForeground(Qt.GlobalColor.gray)

                btn_delete = QPushButton("🗑 Xóa", self.tbl_sections)
                btn_delete.setStyleSheet(TLSTheme.delete_button_stylesheet())
                btn_delete.setProperty("section_id", s.section_id)
                btn_delete.clicked.connect(self._on_delete_section)

                self.tbl_sections.setItem(r, 0, item_code)
                self.tbl_sections.setItem(r, 1, item_name)
                self.tbl_sections.setItem(r, 2, item_designer)
                self.tbl_sections.setCellWidget(r, 3, btn_delete)
        except Exception as e:
            logger.error(
                "Lỗi cơ sở dữ liệu khi tải hạng mục: %s", str(e), exc_info=True
            )
        finally:
            self._restore_column_widths()
            self.tbl_sections.blockSignals(False)

    def _on_delete_section(self) -> None:
        """Xử lý sự kiện khi click nút [Xóa] hạng mục."""
        btn = self.sender()
        if not btn:
            return
        section_id = btn.property("section_id")
        if not section_id:
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            "Anh có chắc chắn muốn xóa hạng mục này?\n"
            "Các bản vẽ đang thuộc hạng mục này sẽ được đưa về trạng thái không thuộc hạng mục nào.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = delete_section_safe(int(section_id))
                if success:
                    QMessageBox.information(
                        self, "Thông báo", "Đã xóa hạng mục thành công!"
                    )
                    self.load_sections()
                    self.section_changed.emit()

                    # Thông báo reload tab Thiết kế để load lại combobox hạng mục
                    if (
                        self.main_window
                        and hasattr(self.main_window, "main_window")
                        and hasattr(self.main_window.main_window, "thiet_ke_view")
                        and hasattr(
                            self.main_window.main_window.thiet_ke_view, "load_sections"
                        )
                    ):
                        self.main_window.main_window.thiet_ke_view.load_sections()
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể xóa hạng mục này.")
            except Exception as e:
                logger.error(
                    "Lỗi khi xóa hạng mục ID %d: %s", section_id, str(e), exc_info=True
                )
                QMessageBox.critical(self, "Lỗi", "Lỗi kết nối cơ sở dữ liệu.")

    def _on_create_section(self) -> None:
        """Xử lý sự kiện click nút [Thêm Hạng mục] hoặc [Lưu Thay Đổi]."""
        project_id = self.current_project_id
        section_code = self.txt_section_code.text().strip()
        section_name = self.txt_section_name.text().strip()
        designer_email = self.cb_designer.currentData()

        if not project_id:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng chọn một Dự án bên trái Sidebar trước!"
            )
            return

        if not section_code or not section_name:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập đầy đủ Mã hạng mục và Tên hạng mục!"
            )
            return

        success = self._perform_save_section(
            project_id, section_code, section_name, designer_email
        )

        if success:
            self._trigger_view_reload(section_code)
        else:
            QMessageBox.critical(
                self, "Lỗi", "Không thể xử lý hạng mục này hoặc lỗi kết nối database."
            )

    def _perform_save_section(
        self, project_id: str, code: str, name: str, designer: str | None
    ) -> bool:
        """Gọi service để thực thi việc lưu hoặc cập nhật hạng mục.

        Args:
            project_id: ID dự án liên kết.
            code: Mã hạng mục.
            name: Tên hạng mục.
            designer: Email thiết kế phụ trách.

        Returns:
            True nếu lưu thành công, ngược lại False.
        """
        try:
            if self.edit_mode:
                sect = update_section_safe(
                    self.current_section_id,
                    name=name,
                    designer=designer,
                )
                return sect is not None
            else:
                sect = create_section_safe(
                    project_id,
                    code=code,
                    name=name,
                    designer=designer,
                )
                return sect is not None
        except Exception as e:
            logger.error("Lỗi khi xử lý dữ liệu hạng mục: %s", str(e), exc_info=True)
            return False

    def _trigger_view_reload(self, code: str) -> None:
        """Hiển thị thông báo lưu thành công và phát tín hiệu reload các màn hình liên quan.

        Args:
            code: Mã hạng mục vừa lưu.
        """
        action_str = "Cập nhật" if self.edit_mode else "Thêm"
        QMessageBox.information(
            self,
            "Thông báo",
            f"Đã {action_str.lower()} thành công hạng mục: {code}",
        )
        self.load_sections()
        self.clear_form()
        self.section_changed.emit()

        # Đồng thời reload combobox hạng mục của thiet_ke_view nếu có
        if (
            self.main_window
            and hasattr(self.main_window, "main_window")
            and hasattr(self.main_window.main_window, "thiet_ke_view")
            and hasattr(self.main_window.main_window.thiet_ke_view, "load_sections")
        ):
            self.main_window.main_window.thiet_ke_view.load_sections()

    def _on_item_selection_changed(self) -> None:
        """Xử lý khi chọn dòng trên bảng hạng mục."""
        selected_items = self.tbl_sections.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            item_code = self.tbl_sections.item(row, 0)
            if item_code:
                section_id = item_code.data(Qt.ItemDataRole.UserRole)
                if section_id:
                    self.set_edit_section(section_id)
        else:
            self.clear_form()

    def set_edit_section(self, section_id: int) -> None:
        """Kích hoạt chế độ chỉnh sửa thông tin hạng mục.

        Args:
            section_id: Khóa chính của hạng mục cần chỉnh sửa.
        """
        # Tìm thông tin hạng mục trong cache
        sect_data = None
        for s in self.current_sections_data:
            if s.section_id == section_id:
                sect_data = s
                break

        if not sect_data:
            return

        self.txt_section_code.setText(sect_data.section_code)
        self.txt_section_code.setReadOnly(True)
        self.txt_section_code.setStyleSheet(
            "background-color: #E2E8F0; color: #64748B;"
        )

        self.txt_section_name.setText(sect_data.section_name)

        # Set designer value
        designer_email = sect_data.designer_email or ""
        idx_designer = self.cb_designer.findData(designer_email)
        if idx_designer >= 0:
            self.cb_designer.setCurrentIndex(idx_designer)

        self.btn_create_sect.setText("💾 Lưu Thay Đổi")
        self.btn_cancel_edit.show()
        self.current_section_id = section_id
        self.edit_mode = True

    def clear_form(self) -> None:
        """Reset form về chế độ Tạo mới mặc định."""
        self.txt_section_code.clear()
        self.txt_section_code.setReadOnly(False)
        self.txt_section_code.setStyleSheet(
            "background-color: #F8FAFC; color: #0F172A;"
        )

        self.txt_section_name.clear()
        self.cb_designer.setCurrentIndex(0)

        self.btn_create_sect.setText("➕ Thêm Hạng mục")
        self.btn_cancel_edit.hide()
        self.current_section_id = 0
        self.edit_mode = False

        # Bỏ chọn trên bảng
        self.tbl_sections.blockSignals(True)
        self.tbl_sections.clearSelection()
        self.tbl_sections.blockSignals(False)

    def _save_column_widths(self) -> None:
        """Lưu lại độ rộng các cột của bảng hạng mục."""
        widths = [
            self.tbl_sections.columnWidth(i)
            for i in range(self.tbl_sections.columnCount())
        ]
        self.settings.setValue("section_table_widths", widths)

    def _restore_column_widths(self) -> None:
        """Khôi phục độ rộng các cột của bảng hạng mục."""
        widths = self.settings.value("section_table_widths")
        if widths:
            self.tbl_sections.horizontalHeader().blockSignals(True)
            try:
                for i, w in enumerate(widths):
                    if i < self.tbl_sections.columnCount():
                        self.tbl_sections.setColumnWidth(i, int(w))
            except Exception as e:
                logger.error("Lỗi khi khôi phục độ rộng cột bảng hạng mục: %s", str(e))
            self.tbl_sections.horizontalHeader().blockSignals(False)
        else:
            # Mặc định dãn cột Tên hạng mục
            self.tbl_sections.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeMode.Stretch
            )
