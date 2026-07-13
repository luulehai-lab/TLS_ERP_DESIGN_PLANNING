# Tên file: tests/test_project_local_path.py
# CHỨC NĂNG: Test đơn vị kiểm tra cấu hình local_path của dự án
# CHANGELOG:
# - 14:35:51 13/07/2026: [NEW] feat(drawing-ui): integrate auto google drive file/folder upload and auto fill link during drawing release (Antigravity)
# - 14:35:00 13/07/2026: [NEW] Khởi tạo test đơn vị local_path dự án (Antigravity)

from core.services.project_service import (
    create_project_safe,
    update_project_safe,
    get_project_safe,
    delete_project_safe,
)


def test_project_local_path_crud() -> None:
    """Kiểm tra hoạt động CRUD trường local_path trong Project."""
    project_id = "TEST-PROJ-999"
    project_name = "Dự án Test Local Path"
    roles = {"sales": "sales@test.com", "designer": "designer@test.com"}
    local_path = "D:/CloudStation/TEST-PROJ-999"

    # Dọn dẹp trước nếu có
    delete_project_safe(project_id)

    try:
        # 2. Tạo mới dự án kèm local_path
        proj = create_project_safe(project_id, project_name, roles, local_path)
        assert proj is not None
        assert proj.local_path == local_path

        # 3. Lấy lại dự án kiểm tra
        fetched = get_project_safe(project_id)
        assert fetched is not None
        assert fetched.local_path == local_path

        # 4. Cập nhật local_path mới
        new_path = "E:/Work/TEST-PROJ-999_NEW"
        updated = update_project_safe(project_id, project_name, roles, new_path)
        assert updated is not None
        assert updated.local_path == new_path

        # 5. Kiểm tra lấy lại sau khi cập nhật
        fetched_updated = get_project_safe(project_id)
        assert fetched_updated is not None
        assert fetched_updated.local_path == new_path

    finally:
        # 6. Dọn dẹp dữ liệu test
        delete_project_safe(project_id)
