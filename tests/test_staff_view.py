# Tên file: tests/test_staff_view.py
# CHỨC NĂNG: Unit test cho giao diện StaffManagementView (Xem, Thêm, Sửa, Xóa nhân sự trên UI)
# CHANGELOG:
# - 17:07:37 11/07/2026: [NEW] feat(auth): support official planning email, bypass filters and add related unit tests (Antigravity)
# - 16:59:00 11/07/2026: [NEW] Viết unit test cho giao diện quản lý nhân sự StaffManagementView (Antigravity)

import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.views.staff_view import StaffManagementView
from core.database import SessionLocal
from core.models import Staff


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Fixture khởi tạo đối tượng QApplication một lần duy nhất cho toàn bộ module test."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def staff_view(qapp) -> StaffManagementView:
    """Fixture khởi tạo widget StaffManagementView để kiểm thử."""
    view = StaffManagementView(parent=None)
    return view


def test_staff_view_initial_load(staff_view) -> None:
    """Kiểm tra xem dữ liệu nhân viên ban đầu có được load đầy đủ lên bảng UI."""
    table = staff_view.tbl_staffs

    # Số lượng seed ban đầu là 10 người (trong conftest.py)
    assert table.rowCount() == 10

    # Kiểm tra dòng đầu tiên (Lê Hải Lưu - luu.lehai@gmail.com)
    assert table.item(0, 1).text() == "Lê Hải Lưu"
    assert table.item(0, 2).text() == "luu.lehai@gmail.com"
    assert table.item(0, 3).text() == "Admin"


def test_staff_view_form_selection_sync(staff_view) -> None:
    """Kiểm tra việc click chọn dòng trên bảng đồng bộ lên form nhập liệu."""
    table = staff_view.tbl_staffs

    # Chọn dòng index 1 (Nguyễn Văn Quân - Kinh doanh)
    table.selectRow(1)

    assert staff_view.selected_staff_id is not None
    assert staff_view.txt_name.text() == "Nguyễn Văn Quân"
    assert staff_view.txt_email.text() == "quanxu23@gmail.com"
    assert staff_view.cb_role.currentText() == "Kinh doanh"
    assert staff_view.btn_delete.isEnabled() is True


def test_staff_view_clear_form(staff_view) -> None:
    """Kiểm tra chức năng reset form."""
    table = staff_view.tbl_staffs
    table.selectRow(1)

    staff_view.clear_form()

    assert staff_view.selected_staff_id is None
    assert staff_view.txt_name.text() == ""
    assert staff_view.txt_email.text() == ""
    assert staff_view.btn_delete.isEnabled() is False


def test_staff_view_add_new_staff(staff_view) -> None:
    """Kiểm tra chức năng thêm mới nhân sự thông qua giao diện UI."""
    staff_view.clear_form()

    # Nhập thông tin cho nhân viên mới
    staff_view.txt_name.setText("Test Nhân Viên Mới")
    staff_view.txt_email.setText("newemployee@tls.vn")
    staff_view.cb_role.setCurrentText("Thiết kế")

    # Mock QMessageBox để tránh treo test
    from unittest.mock import patch

    with patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info:
        # Thực thi hành động Save
        staff_view._on_save_clicked()
        assert mock_info.called

    # Bảng UI phải tăng lên 11 dòng
    table = staff_view.tbl_staffs
    assert table.rowCount() == 11

    # Kiểm tra xem dữ liệu thực tế có trong DB in-memory không
    db = SessionLocal()
    try:
        inserted = db.query(Staff).filter(Staff.email == "newemployee@tls.vn").first()
        assert inserted is not None
        assert inserted.name == "Test Nhân Viên Mới"
        assert inserted.role == "Thiết kế"
    finally:
        db.close()


def test_staff_view_delete_staff(staff_view) -> None:
    """Kiểm tra chức năng xóa nhân sự thông qua UI."""
    table = staff_view.tbl_staffs

    # Tìm dòng chứa nhân viên vừa thêm
    row_to_delete = -1
    for r in range(table.rowCount()):
        if table.item(r, 2).text() == "newemployee@tls.vn":
            row_to_delete = r
            break

    assert row_to_delete != -1

    # Chọn dòng
    table.selectRow(row_to_delete)

    # MokMessageBox để tự động xác nhận Yes khi click delete
    # Do QMessageBox.warning chặn luồng, ta sẽ mock behavior standard button
    from unittest.mock import patch

    with (
        patch("PyQt6.QtWidgets.QMessageBox.warning") as mock_warn,
        patch("PyQt6.QtWidgets.QMessageBox.information") as mock_info,
    ):
        mock_warn.return_value = QMessageBox.StandardButton.Yes
        staff_view._on_delete_clicked()
        assert mock_warn.called
        assert mock_info.called

    # Bảng UI phải giảm về 10 dòng
    assert table.rowCount() == 10

    # Kiểm tra DB xem dữ liệu đã bị xóa chưa
    db = SessionLocal()
    try:
        deleted = db.query(Staff).filter(Staff.email == "newemployee@tls.vn").first()
        assert deleted is None
    finally:
        db.close()
