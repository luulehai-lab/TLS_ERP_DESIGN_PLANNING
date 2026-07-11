# Tên file: ui/views/staff_view.py
# CHỨC NĂNG: Giao diện Quản lý Nhân sự dành riêng cho Admin (thêm, sửa, xóa, phân quyền email)
# CHANGELOG:
# - 17:30:15 11/07/2026: [UPDATE] feat(du-an): load sales and designers dropdowns dynamically from database staff table (Antigravity)
# - 17:07:38 11/07/2026: [NEW] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 16:59:00 11/07/2026: [NEW] Khởi tạo giao diện Quản lý Nhân sự StaffManagementView (Antigravity)

import logging
from typing import Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from ui.styles.theme import TLSTheme
from core.database import SessionLocal
from core.models import Staff

logger = logging.getLogger(__name__)


class StaffManagementView(QWidget):
    """Màn hình nghiệp vụ Quản lý Nhân sự dành cho Admin.

    Cho phép xem, thêm mới và xóa tài khoản nhân viên trong hệ thống ERP.
    """

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo StaffManagementView.

        Args:
            parent: MainWindow chứa view này.
        """
        super().__init__(parent)
        self.main_window = parent
        self.selected_staff_id: int | None = None

        self._init_ui()
        self.load_staffs()

    def _init_ui(self) -> None:
        """Khởi tạo giao diện lắp ghép bảng nhân viên và form chỉnh sửa."""
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(20, 20, 20, 20)
        self.layout_main.setSpacing(15)

        # 1. Tiêu đề màn hình
        title_label = QLabel("QUẢN LÝ NHÂN SỰ & PHÂN QUYỀN EMAIL", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        self.layout_main.addWidget(title_label)

        # Splitter hoặc layout chia đôi giữa Bảng và Form nhập
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # 2. Bảng danh sách nhân sự (Bên trái)
        table_group = QGroupBox("Danh sách nhân viên", self)
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(15, 15, 15, 15)

        self.tbl_staffs = QTableWidget(self)
        self.tbl_staffs.setColumnCount(4)
        self.tbl_staffs.setHorizontalHeaderLabels(["ID", "Họ Tên", "Email", "Vai Trò"])
        self.tbl_staffs.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_staffs.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tbl_staffs.itemSelectionChanged.connect(self._on_table_selection_changed)

        # Cấu hình header tự co giãn
        header = self.tbl_staffs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        table_layout.addWidget(self.tbl_staffs)
        content_layout.addWidget(table_group, stretch=2)

        # 3. Form nhập liệu (Bên phải)
        form_group = QGroupBox("Thông tin nhân viên", self)
        form_layout = QVBoxLayout(form_group)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setSpacing(15)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Họ Tên:", form_group), 0, 0)
        self.txt_name = QLineEdit(form_group)
        self.txt_name.setPlaceholderText("Ví dụ: Nguyễn Văn A")
        grid.addWidget(self.txt_name, 0, 1)

        grid.addWidget(QLabel("Email Google:", form_group), 1, 0)
        self.txt_email = QLineEdit(form_group)
        self.txt_email.setPlaceholderText("Ví dụ: nguyenvana@gmail.com")
        grid.addWidget(self.txt_email, 1, 1)

        grid.addWidget(QLabel("Vai Trò (Role):", form_group), 2, 0)
        self.cb_role = QComboBox(form_group)
        self.cb_role.addItems(["Admin", "Thiết kế", "Kế hoạch", "Kinh doanh"])
        grid.addWidget(self.cb_role, 2, 1)

        form_layout.addLayout(grid)

        # Nút bấm hành động
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Lưu / Thêm mới", form_group)
        self.btn_save.setStyleSheet("background-color: #10B981;")  # Green
        self.btn_save.clicked.connect(self._on_save_clicked)
        btn_layout.addWidget(self.btn_save)

        self.btn_delete = QPushButton("🗑 Xóa nhân sự", form_group)
        self.btn_delete.setStyleSheet("background-color: #EF4444;")  # Red
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        btn_layout.addWidget(self.btn_delete)

        self.btn_clear = QPushButton("🔄 Reset Form", form_group)
        self.btn_clear.setStyleSheet("background-color: #64748B;")  # Slate
        self.btn_clear.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.btn_clear)

        form_layout.addLayout(btn_layout)
        form_layout.addStretch()

        content_layout.addWidget(form_group, stretch=1)

        self.layout_main.addLayout(content_layout)
        self.setStyleSheet(TLSTheme.main_window_stylesheet())

    def load_staffs(self) -> None:
        """Truy vấn database để nạp danh sách nhân viên vào bảng."""
        self.tbl_staffs.setRowCount(0)
        db = SessionLocal()
        try:
            staffs = db.query(Staff).order_by(Staff.staff_id).all()
            self.tbl_staffs.setRowCount(len(staffs))

            for r, s in enumerate(staffs):
                item_id = QTableWidgetItem(str(s.staff_id))
                item_id.setFlags(item_id.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.tbl_staffs.setItem(r, 0, item_id)

                item_name = QTableWidgetItem(s.name)
                item_name.setFlags(item_name.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.tbl_staffs.setItem(r, 1, item_name)

                item_email = QTableWidgetItem(s.email)
                item_email.setFlags(item_email.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.tbl_staffs.setItem(r, 2, item_email)

                item_role = QTableWidgetItem(s.role)
                item_role.setFlags(item_role.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.tbl_staffs.setItem(r, 3, item_role)

        except Exception as e:
            logger.error("Lỗi khi load danh sách nhân viên: %s", str(e), exc_info=True)
            QMessageBox.critical(
                self, "Lỗi", f"Không thể tải danh sách nhân viên: {str(e)}"
            )
        finally:
            db.close()

    def _on_table_selection_changed(self) -> None:
        """Đồng bộ dòng được chọn lên form nhập liệu."""
        selected_ranges = self.tbl_staffs.selectedRanges()
        if not selected_ranges:
            self.clear_form()
            return

        row = selected_ranges[0].topRow()
        staff_id_str = self.tbl_staffs.item(row, 0).text()
        self.selected_staff_id = int(staff_id_str)

        name = self.tbl_staffs.item(row, 1).text()
        email = self.tbl_staffs.item(row, 2).text()
        role = self.tbl_staffs.item(row, 3).text()

        self.txt_name.setText(name)
        self.txt_email.setText(email)

        idx = self.cb_role.findText(role)
        if idx >= 0:
            self.cb_role.setCurrentIndex(idx)

        # Không cho xóa Admin tối cao luu.lehai@gmail.com
        self.btn_delete.setEnabled(email.lower() != "luu.lehai@gmail.com")

    def clear_form(self) -> None:
        """Xóa trắng form nhập liệu để chuẩn bị thêm mới."""
        self.selected_staff_id = None
        self.txt_name.clear()
        self.txt_email.clear()
        self.cb_role.setCurrentIndex(0)
        self.btn_delete.setEnabled(False)
        self.tbl_staffs.clearSelection()

    def _on_save_clicked(self) -> None:
        """Thêm mới hoặc cập nhật thông tin nhân viên."""
        name = self.txt_name.text().strip()
        email = self.txt_email.text().strip()
        role = self.cb_role.currentText()

        if not name or not email:
            QMessageBox.warning(
                self, "Cảnh báo", "Vui lòng nhập đầy đủ Họ Tên và Email!"
            )
            return

        db = SessionLocal()
        try:
            # Check trùng email nếu thêm mới
            existing = db.query(Staff).filter(Staff.email.ilike(email)).first()

            if self.selected_staff_id is None:
                # Thêm mới
                if existing:
                    QMessageBox.warning(
                        self, "Cảnh báo", f"Email '{email}' đã tồn tại trong hệ thống!"
                    )
                    return

                new_staff = Staff(name=name, email=email.lower(), role=role)
                db.add(new_staff)
                db.commit()
                QMessageBox.information(
                    self, "Thành công", f"Đã thêm nhân viên: {name}"
                )
            else:
                # Cập nhật
                staff = (
                    db.query(Staff)
                    .filter(Staff.staff_id == self.selected_staff_id)
                    .first()
                )
                if staff:
                    if existing and existing.staff_id != self.selected_staff_id:
                        QMessageBox.warning(
                            self,
                            "Cảnh báo",
                            f"Email '{email}' đã được dùng bởi nhân viên khác!",
                        )
                        return

                    staff.name = name
                    staff.email = email.lower()
                    staff.role = role
                    db.commit()
                    QMessageBox.information(
                        self, "Thành công", f"Đã cập nhật thông tin cho: {name}"
                    )

            self.load_staffs()
            self.clear_form()

            # Đồng bộ lại dropdown ở tab Kế hoạch
            if self.main_window and hasattr(self.main_window, "ke_hoach_view"):
                self.main_window.ke_hoach_view.reload_planners()

        except Exception as e:
            db.rollback()
            logger.error("Lỗi khi lưu nhân viên: %s", str(e), exc_info=True)
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu nhân viên: {str(e)}")
        finally:
            db.close()

    def _on_delete_clicked(self) -> None:
        """Xóa nhân viên khỏi hệ thống."""
        if self.selected_staff_id is None:
            return

        db = SessionLocal()
        try:
            staff = (
                db.query(Staff).filter(Staff.staff_id == self.selected_staff_id).first()
            )
            if not staff:
                return

            reply = QMessageBox.warning(
                self,
                "⚠️ Xác nhận Xóa",
                f"Bạn có chắc chắn muốn xóa nhân viên:\n\n{staff.name} ({staff.email})?\n\n"
                f"Họ sẽ không thể truy cập hệ thống ERP nữa!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            db.delete(staff)
            db.commit()
            QMessageBox.information(
                self, "Thành công", "Đã xóa nhân viên khỏi hệ thống."
            )

            self.load_staffs()
            self.clear_form()

            # Đồng bộ lại dropdown ở tab Kế hoạch
            if self.main_window and hasattr(self.main_window, "ke_hoach_view"):
                self.main_window.ke_hoach_view.reload_planners()

        except Exception as e:
            db.rollback()
            logger.error("Lỗi khi xóa nhân viên: %s", str(e), exc_info=True)
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa nhân viên: {str(e)}")
        finally:
            db.close()
