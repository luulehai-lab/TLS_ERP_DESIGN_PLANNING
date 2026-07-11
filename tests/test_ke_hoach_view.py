# Tên file: tests/test_ke_hoach_view.py
# CHỨC NĂNG: Unit test cho giao diện KeHoachView (Dropdown Người Thực Hiện và trạng thái 2 nút bấm)
# CHANGELOG:
# - 16:33:04 11/07/2026: [NEW] feat(auth): add 2-tier permission filter, whitelist unauthorized emails and add unit tests (Antigravity)
# - 16:32:00 11/07/2026: [NEW] Viết unit test giao diện dropdown người thực hiện và kiểm soát nút bấm (Antigravity)

import pytest
from PyQt6.QtWidgets import QApplication
from ui.views.ke_hoach_view import KeHoachView


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Fixture khởi tạo đối tượng QApplication một lần duy nhất cho toàn bộ module test."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def ke_hoach_view(qapp) -> KeHoachView:
    """Fixture khởi tạo widget KeHoachView để kiểm thử."""
    view = KeHoachView(parent=None)
    return view


def test_performer_combobox_items(ke_hoach_view) -> None:
    """Kiểm tra danh sách người thực hiện trong Combobox có khớp yêu cầu."""
    combobox = ke_hoach_view.cb_performed_by
    expected_names = [
        "Trần Mạnh Linh",
        "Nguyễn Hồng Thái",
        "Nguyễn Mạnh Tuấn",
        "Lê Viết Hiệu",
    ]

    # Vị trí 0 là placeholder
    assert combobox.itemText(0) == "--- Chọn người thực hiện ---"
    assert combobox.itemData(0) == ""

    # Kiểm tra các phần tử tiếp theo
    for i, name in enumerate(expected_names, start=1):
        assert combobox.itemText(i) == name
        assert combobox.itemData(i) == name

    assert combobox.count() == 5  # 1 placeholder + 4 tên


def test_initial_buttons_state(ke_hoach_view) -> None:
    """Kiểm tra trạng thái mặc định của 2 nút bấm phải là bị disabled."""
    assert ke_hoach_view.btn_open_link.isEnabled() is False
    assert ke_hoach_view.btn_confirm_prod.isEnabled() is False


def test_buttons_enabled_when_performer_selected(ke_hoach_view) -> None:
    """Kiểm tra 2 nút bấm phải được enabled khi chọn một người thực hiện hợp lệ."""
    combobox = ke_hoach_view.cb_performed_by

    # Chọn index 1 ("Trần Mạnh Linh")
    combobox.setCurrentIndex(1)
    assert combobox.currentData() == "Trần Mạnh Linh"
    assert ke_hoach_view.btn_open_link.isEnabled() is True
    assert ke_hoach_view.btn_confirm_prod.isEnabled() is True


def test_buttons_disabled_when_selection_cleared(ke_hoach_view) -> None:
    """Kiểm tra 2 nút bấm bị disabled trở lại nếu chọn lại placeholder."""
    combobox = ke_hoach_view.cb_performed_by

    # Chọn người thực hiện hợp lệ → Enabled
    combobox.setCurrentIndex(2)  # Nguyễn Hồng Thái
    assert ke_hoach_view.btn_open_link.isEnabled() is True
    assert ke_hoach_view.btn_confirm_prod.isEnabled() is True

    # Chọn lại placeholder → Disabled
    combobox.setCurrentIndex(0)
    assert ke_hoach_view.btn_open_link.isEnabled() is False
    assert ke_hoach_view.btn_confirm_prod.isEnabled() is False
