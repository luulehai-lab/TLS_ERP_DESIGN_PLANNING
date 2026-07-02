---
description: Tự động phân tích PDF tính toán xà gồ CFS và xuất báo cáo Markdown Premium.
---

# Workflow Phân tích Xà gồ (Purlin-Report) - V2026 SSL Supreme

Workflow này dùng để phân tích file PDF tính toán xà gồ xuất ra từ phần mềm CFS (Cold-Formed Steel), trích xuất các thông số kỹ thuật cốt lõi và xuất báo cáo Markdown chuyên nghiệp.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PURLIN_REPORT",
    "workflow_name": "Purlin Calculation PDF Report Generator",
    "workflow_goal": "Parse CFS purlin calculation PDF and generate a professional Markdown report.",
    "expected_inputs": [
      {"name": "pdf_path", "type": "string", "description": "Đường dẫn file PDF tính toán xà gồ CFS"}
    ],
    "constraints": [
      "Offline execution (no AI required)",
      "High precision data extraction",
      "Premium Markdown layout with HSL colors & tables",
      "Auto-calculate steel weight in kilograms"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Xác nhận file PDF tồn tại và sẵn sàng xử lý.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Chạy CLI tool phân tích và ghi file báo cáo Markdown.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Cập nhật nhật ký công việc và hiển thị kết quả cho Anh Lưu.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Khởi động)
- [ ] Xác nhận đường dẫn file PDF truyền vào hợp lệ.

### ⚙️ Scene 2: ACT (Ghi file báo cáo)
// turbo
```powershell
python "tools/engineering/purlin_report_tool.py" "[pdf_path]"
```

### 🏁 Scene 3: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_code_YYYY_MM_DD.md` và `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Trình bày kết quả trực quan và cung cấp link tải báo cáo Markdown cho Anh Lưu.
