# Tên file: tests/test_permission_filter.py
# CHỨC NĂNG: Test phân quyền xem dự án và bản vẽ theo email đăng nhập
# CHANGELOG:
# - 15:17:43 11/07/2026: [NEW] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 15:05:00 11/07/2026: [NEW] Viết test phân quyền 2 tầng (dự án + hạng mục) (Antigravity)

"""Test logic phân quyền xem dự án và bản vẽ theo email đăng nhập.

Mô phỏng dữ liệu thực tế:
- Dự án VAN_LOC: sale=phuc@tls.vn, designer chung=None
  + Hạng mục NX1: designer=trinhA@tls.vn
  + Hạng mục NX2: designer=haB@tls.vn
- Dự án SONG_HONG: sale=phuc@tls.vn, designer=trinhA@tls.vn (dự án nhỏ không có hạng mục)
- Dự án DAI_PHONG: sale=nam@tls.vn, designer=haB@tls.vn
"""



# ============================================================================
# MOCK DATA: Giả lập dữ liệu dự án giống cấu trúc dict thô từ ProjectLoaderThread
# ============================================================================

MOCK_PROJECTS = [
    {
        "project_id": "VAN_LOC",
        "project_name": "Nhà máy Vạn Lộc",
        "status": "Đang chạy",
        "sales_email": "phuc@tls.vn",
        "designer_email": None,  # Dự án nhiều hạng mục → để trống
        "section_designer_emails": ["trinha@tls.vn", "hab@tls.vn"],
    },
    {
        "project_id": "SONG_HONG",
        "project_name": "Cầu Sông Hồng",
        "status": "Đang chạy",
        "sales_email": "phuc@tls.vn",
        "designer_email": "trinha@tls.vn",  # Dự án nhỏ → gán designer chung
        "section_designer_emails": [],
    },
    {
        "project_id": "DAI_PHONG",
        "project_name": "KCN Đại Phong",
        "status": "Đang chạy",
        "sales_email": "nam@tls.vn",
        "designer_email": "hab@tls.vn",
        "section_designer_emails": [],
    },
]

# Mock bản vẽ cho dự án VAN_LOC (có 2 hạng mục)
MOCK_DRAWINGS_VAN_LOC = [
    {
        "drawing_id": "VL-NX1-01",
        "drawing_name": "Mặt bằng NX1",
        "section_name": "Nhà xưởng 1",
        "section_designer_email": "trinha@tls.vn",
        "project_sales_email": "phuc@tls.vn",
        "status": "Chờ triển khai",
    },
    {
        "drawing_id": "VL-NX1-02",
        "drawing_name": "Mặt cắt NX1",
        "section_name": "Nhà xưởng 1",
        "section_designer_email": "trinha@tls.vn",
        "project_sales_email": "phuc@tls.vn",
        "status": "Chờ triển khai",
    },
    {
        "drawing_id": "VL-NX2-01",
        "drawing_name": "Mặt bằng NX2",
        "section_name": "Nhà xưởng 2",
        "section_designer_email": "hab@tls.vn",
        "project_sales_email": "phuc@tls.vn",
        "status": "Chờ triển khai",
    },
    {
        "drawing_id": "VL-CHUNG-01",
        "drawing_name": "Bản vẽ chung",
        "section_name": "",
        "section_designer_email": "",
        "project_sales_email": "phuc@tls.vn",
        "status": "Chờ triển khai",
    },
]


# ============================================================================
# HÀM FILTER THUẦN TÚY (Trích xuất logic từ sidebar.py và base_drawing_view.py)
# ============================================================================

ADMIN_EMAIL = "luu.lehai@gmail.com"


def filter_projects_by_permission(projects: list[dict], user_email: str) -> list[dict]:
    """Logic filter dự án theo phân quyền (trích xuất từ sidebar._on_projects_loaded).

    Args:
        projects: Danh sách dự án dạng dict thô.
        user_email: Email người đăng nhập.

    Returns:
        Danh sách dự án mà user có quyền xem.
    """
    if user_email == ADMIN_EMAIL:
        return projects

    result = []
    current_email = user_email.lower()
    for p in projects:
        p_sales = (p.get("sales_email") or "").lower()
        p_designer = (p.get("designer_email") or "").lower()
        section_emails = p.get("section_designer_emails", [])
        if (
            current_email == p_sales
            or current_email == p_designer
            or current_email in section_emails
        ):
            result.append(p)
    return result


def filter_drawings_by_permission(drawings: list[dict], user_email: str) -> list[dict]:
    """Logic filter bản vẽ theo phân quyền designer cấp hạng mục.

    Admin và Sale xem được tất cả bản vẽ. Designer chỉ thấy bản vẽ hạng mục mình.

    Args:
        drawings: Danh sách bản vẽ dạng dict thô.
        user_email: Email người đăng nhập.

    Returns:
        Danh sách bản vẽ mà user có quyền xem.
    """
    if user_email == ADMIN_EMAIL:
        return drawings

    current_email = user_email.lower()

    # Sale của dự án xem được tất cả bản vẽ
    if drawings:
        p_sales = (drawings[0].get("project_sales_email") or "").lower()
        if current_email == p_sales:
            return drawings

    # Designer chỉ thấy bản vẽ hạng mục mình hoặc bản vẽ không gán designer
    result = []
    for d in drawings:
        s_designer = (d.get("section_designer_email") or "").lower()
        if not s_designer or s_designer == current_email:
            result.append(d)
    return result


# ============================================================================
# TEST CASES
# ============================================================================


class TestProjectPermissionFilter:
    """Test phân quyền xem dự án trên Sidebar."""

    def test_admin_sees_all_projects(self) -> None:
        """Admin (Anh Lưu) phải xem được tất cả dự án."""
        result = filter_projects_by_permission(MOCK_PROJECTS, ADMIN_EMAIL)
        assert len(result) == 3

    def test_sale_sees_own_projects(self) -> None:
        """Sale Phúc chỉ xem được dự án mình phụ trách (VAN_LOC, SONG_HONG)."""
        result = filter_projects_by_permission(MOCK_PROJECTS, "phuc@tls.vn")
        ids = [p["project_id"] for p in result]
        assert "VAN_LOC" in ids
        assert "SONG_HONG" in ids
        assert "DAI_PHONG" not in ids

    def test_sale_nam_sees_only_dai_phong(self) -> None:
        """Sale Nam chỉ xem được dự án DAI_PHONG."""
        result = filter_projects_by_permission(MOCK_PROJECTS, "nam@tls.vn")
        assert len(result) == 1
        assert result[0]["project_id"] == "DAI_PHONG"

    def test_designer_with_project_level_email(self) -> None:
        """Designer TrinhA xem được SONG_HONG (project-level) VÀ VAN_LOC (section-level)."""
        result = filter_projects_by_permission(MOCK_PROJECTS, "trinhA@tls.vn")
        ids = [p["project_id"] for p in result]
        assert "SONG_HONG" in ids
        assert "VAN_LOC" in ids
        assert "DAI_PHONG" not in ids

    def test_designer_with_section_level_only(self) -> None:
        """Designer HaB xem được VAN_LOC (section) VÀ DAI_PHONG (project-level)."""
        result = filter_projects_by_permission(MOCK_PROJECTS, "hab@tls.vn")
        ids = [p["project_id"] for p in result]
        assert "VAN_LOC" in ids
        assert "DAI_PHONG" in ids
        assert "SONG_HONG" not in ids

    def test_unknown_email_sees_nothing(self) -> None:
        """Email không liên quan đến bất kỳ dự án nào → không thấy gì."""
        result = filter_projects_by_permission(MOCK_PROJECTS, "stranger@tls.vn")
        assert len(result) == 0

    def test_case_insensitive_matching(self) -> None:
        """Kiểm tra so sánh email không phân biệt hoa thường."""
        result = filter_projects_by_permission(MOCK_PROJECTS, "PHUC@TLS.VN")
        assert len(result) == 2


class TestDrawingPermissionFilter:
    """Test phân quyền xem bản vẽ theo hạng mục."""

    def test_admin_sees_all_drawings(self) -> None:
        """Admin xem được tất cả bản vẽ."""
        result = filter_drawings_by_permission(MOCK_DRAWINGS_VAN_LOC, ADMIN_EMAIL)
        assert len(result) == 4

    def test_designer_trinha_sees_nx1_and_unassigned(self) -> None:
        """Designer TrinhA chỉ thấy bản vẽ NX1 (mình phụ trách) + bản vẽ chung (không gán section)."""
        result = filter_drawings_by_permission(MOCK_DRAWINGS_VAN_LOC, "trinha@tls.vn")
        ids = [d["drawing_id"] for d in result]
        assert "VL-NX1-01" in ids
        assert "VL-NX1-02" in ids
        assert "VL-CHUNG-01" in ids  # Không gán section → ai cũng thấy
        assert "VL-NX2-01" not in ids  # Bản vẽ NX2 của HaB → không thấy

    def test_designer_hab_sees_nx2_and_unassigned(self) -> None:
        """Designer HaB chỉ thấy bản vẽ NX2 (mình phụ trách) + bản vẽ chung."""
        result = filter_drawings_by_permission(MOCK_DRAWINGS_VAN_LOC, "hab@tls.vn")
        ids = [d["drawing_id"] for d in result]
        assert "VL-NX2-01" in ids
        assert "VL-CHUNG-01" in ids
        assert "VL-NX1-01" not in ids
        assert "VL-NX1-02" not in ids

    def test_sale_sees_all_drawings(self) -> None:
        """Sale Phúc xem được TẤT CẢ bản vẽ của dự án."""
        result = filter_drawings_by_permission(MOCK_DRAWINGS_VAN_LOC, "phuc@tls.vn")
        assert len(result) == 4  # Sale xem được toàn bộ

    def test_unknown_email_sees_only_unassigned(self) -> None:
        """Email lạ chỉ thấy bản vẽ không gán section designer."""
        result = filter_drawings_by_permission(MOCK_DRAWINGS_VAN_LOC, "stranger@tls.vn")
        assert len(result) == 1
        assert result[0]["drawing_id"] == "VL-CHUNG-01"
