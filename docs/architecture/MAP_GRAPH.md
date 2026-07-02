<!--
File: docs/architecture/MAP_GRAPH.md
CHỨC NĂNG: Sơ đồ liên kết codebase và đồ thị phụ thuộc của dự án (ERP TK-KH)
CHANGELOG:
- 10:42:00 02/07/2026: [NEW] Khởi tạo sơ đồ liên kết codebase (Lê Thanh Vân/Antigravity)
-->

# 🌐 ĐỒ THỊ LIÊN KẾT CODEBASE & PHÂN TÍCH TÁC ĐỘNG

> **Dự án**: 55_ERP_TK_KH_01726
> **Nguyên tắc**: Đảm bảo Loose Coupling (Liên kết lỏng). UI không import DB, DB không phụ thuộc UI.

---

## 🗺️ 1. SƠ ĐỒ PHỤ THUỘC TỔNG THỂ (Dependency Graph)

Dưới đây là sơ đồ mối quan hệ nhập khẩu (Import Hierarchy) giữa các module trong hệ thống. Chiều mũi tên `A --> B` nghĩa là **A import B** để sử dụng.

```mermaid
graph TD
    %% Tầng UI (Khách)
    main.py["main.py (Khởi chạy)"] --> UI_Main["ui/main_window.py (Khung giao diện)"]
    UI_Main --> UI_TK["ui/views/thiet_ke_view.py"]
    UI_Main --> UI_KH["ui/views/ke_hoach_view.py"]
    UI_TK --> UI_Common["ui/common/ (Widgets dùng chung)"]
    UI_KH --> UI_Common

    %% Tầng Services (Đệm định tuyến logic)
    UI_TK --> Core_DrawServ["core/services/drawing_service.py"]
    UI_KH --> Core_DrawServ
    UI_Main --> Core_ProjServ["core/services/project_service.py"]

    %% Tầng DB/Models (Cốt lõi)
    Core_DrawServ --> Core_Models["core/models.py (Models DB)"]
    Core_ProjServ --> Core_Models
    Core_Models --> Core_DB["core/database.py (Kết nối SQLAlchemy)"]
    Core_DB --> Config["config.py (Thông số cấu hình)"]

    %% Phân tầng màu sắc
    style main.py fill:#f9f,stroke:#333,stroke-width:2px
    style UI_Main fill:#bbf,stroke:#333,stroke-width:1px
    style UI_TK fill:#bbf,stroke:#333,stroke-width:1px
    style UI_KH fill:#bbf,stroke:#333,stroke-width:1px
    style Core_DrawServ fill:#f96,stroke:#333,stroke-width:1px
    style Core_ProjServ fill:#f96,stroke:#333,stroke-width:1px
    style Core_Models fill:#ff9,stroke:#333,stroke-width:1px
    style Core_DB fill:#ff9,stroke:#333,stroke-width:1px
    style Config fill:#ccc,stroke:#333,stroke-width:1px
```

---

## 🔍 2. BẢN ĐỒ PHÂN TÍCH TÁC ĐỘNG (Impact Analysis Guide)

Khi sửa đổi một thành phần trong hệ thống, hãy đối soát bảng sau để kiểm tra các vùng có khả năng bị ảnh hưởng (Side Effects):

| Thành phần bị thay đổi | Vùng bị ảnh hưởng trực tiếp | Hành động bắt buộc |
| --- | --- | --- |
| **`config.py`** | Toàn bộ ứng dụng (Kết nối DB, API) | Chạy kiểm tra kết nối ngay lập tức |
| **`core/database.py`** | `core/models.py`, các Services | Chạy test suite của DB |
| **`core/models.py`** | Các Services, Database Schema | Thực hiện di chuyển DB (Migration) |
| **`core/services/*`** | Các PyQt Views tương ứng | Chạy unit test logic nghiệp vụ |
| **`ui/common/*`** | Toàn bộ giao diện PyQt6 | Mở app trực quan để test UI render |

---

*Đồ thị này sẽ được cập nhật tự động bằng lệnh `python scripts/generate_codebase_graph.py --scan` sau mỗi phiên làm việc.*
