<!--
File: docs/architecture/MAP_GRAPH.md
Description: 🌐 ĐỒ THỊ LIÊN KẾT CODEBASE AI ASSISTANT
CHANGELOG:
- 18:00:00 28/05/2026: [UPDATE] Tối ưu hóa quét Incremental Cache (Lê Thanh Vân)
-->

# 🌐 ĐỒ THỊ LIÊN KẾT CODEBASE AI ASSISTANT

> [!TIP]
> Tài liệu này được tự động cập nhật bằng cơ chế **Incremental Cache** siêu tốc.
> Giúp hình dung rõ ràng mối liên kết gọi hàm và kế thừa trong toàn bộ hệ thống AI Assistant.

---

## 💾 1. Đồ thị liên kết Core & Services (Nghiệp vụ AI, Garmin, Netflix, DXF BOQ)
```mermaid
graph TD
    classDef file fill:#f9f,stroke:#333,stroke-width:1px;
    classDef cls fill:#bbf,stroke:#333,stroke-width:1px;
    classDef func fill:#bfb,stroke:#333,stroke-width:1px;
    core_services_drawing_service["📄 drawing_service.py"]:::file
    core_services_drawing_service_create_drawing["⚙️ create_drawing()"]:::func
    core_services_drawing_service_update_drawing_status["⚙️ update_drawing_status()"]:::func
    core_services_drawing_service_get_project_drawings["⚙️ get_project_drawings()"]:::func
    core_services_project_service["📄 project_service.py"]:::file
    core_services_project_service_create_project["⚙️ create_project()"]:::func
    core_services_project_service_get_project["⚙️ get_project()"]:::func
    core_services_project_service_list_active_projects["⚙️ list_active_projects()"]:::func
    core_services_project_service_update_project_status["⚙️ update_project_status()"]:::func
    core_services___init__["📄 __init__.py"]:::file
    core_services_drawing_service -->|contains| core_services_drawing_service_create_drawing
    core_services_drawing_service -->|contains| core_services_drawing_service_update_drawing_status
    core_services_drawing_service -->|contains| core_services_drawing_service_get_project_drawings
    core_services_project_service -->|contains| core_services_project_service_create_project
    core_services_project_service -->|contains| core_services_project_service_get_project
    core_services_project_service -->|contains| core_services_project_service_list_active_projects
    core_services_project_service -->|contains| core_services_project_service_update_project_status
```

---

## 🎨 2. Đồ thị liên kết Frontend PyQt6 (Giao diện người dùng)
```mermaid
graph TD
    classDef file fill:#f9f,stroke:#333,stroke-width:1px;
    classDef cls fill:#bbf,stroke:#333,stroke-width:1px;
    classDef func fill:#bfb,stroke:#333,stroke-width:1px;
```
