---
description: [HỆ THỐNG] Quy chuẩn truy vấn 100% Verbatim Tasks của Project
---
# Workflow Truy vấn Task Dự án (Fetch-Project-Tasks) - V2026 SSL Supreme

Workflow này hướng dẫn cách lấy chính xác 100% Task của một dự án thông qua bảng mapping `task_project_links` theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_FETCH_PROJECT_TASKS",
    "workflow_name": "Standard Verbatim Task Extraction",
    "workflow_goal": "Retrieve all tasks associated with a specific project key using database JOINs.",
    "expected_inputs": [
      {"name": "project_key", "type": "string", "description": "Mã dự án cần truy vấn"}
    ],
    "constraints": [
      "No Direct Query: DO NOT use 'WHERE project_key=...' on tasks table directly",
      "Mapping: Must INNER JOIN with task_project_links",
      "Output: Must export to tmp/deep_history.json in valid JSON format"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Xác định project_key và khởi tạo script truy vấn tạm thời.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script Python để JOIN bảng và trích xuất dữ liệu verbatim.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Kiểm tra file tmp/deep_history.json: Đảm bảo số lượng task khớp với thực tế.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo hoàn tất và bàn giao dữ liệu cho bước xử lý tiếp theo (Báo cáo/Audit).",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: ACT (Truy vấn Verbatim)
// turbo
```powershell
# Tạo script truy vấn chuẩn (JOIN logic)
python -c "import sqlite3, json; conn=sqlite3.connect('local_data.db'); conn.row_factory=sqlite3.Row; tasks=conn.execute('SELECT t.* FROM tasks t INNER JOIN task_project_links l ON t.id = l.task_id WHERE l.project_key = ?', ('[project_key]',)).fetchall(); history=[dict(t) for t in tasks]; json.dump(history, open('tmp/deep_history.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2); print(f'Xác nhận: Tìm thấy {len(tasks)} tasks.')"
```

### 🧠 Scene 2: VERIFY (Đối soát)
- [ ] Dùng `view_file` đọc `tmp/deep_history.json`.
- [ ] Kiểm tra các task quan trọng (ví dụ: task ban hành, báo giá) có xuất hiện không.

### 🏁 Scene 3: FINALIZE (Hoàn tất)
- [ ] Thông báo: "Hệ thống đã trích xuất {Count} task cho dự án {Project}.".