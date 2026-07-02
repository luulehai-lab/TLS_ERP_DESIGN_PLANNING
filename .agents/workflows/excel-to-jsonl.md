---
description: Số hóa Excel kỹ thuật sang định dạng Smart JSONL (Bimodal)
---
# Workflow Số hóa Excel sang JSONL (Excel-to-JSONL) - V2026 SSL Supreme

Workflow này dùng để chuyển đổi Excel kỹ thuật sang định dạng Smart JSONL (Bimodal) tối ưu cho tra cứu và hiển thị theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_EXCEL_TO_JSONL",
    "workflow_name": "Excel to Smart JSONL Conversion",
    "workflow_goal": "Convert technical Excel files into atomic, searchable JSONL records for high-precision RAG.",
    "expected_inputs": [
      {"name": "excel_path", "type": "string", "description": "Đường dẫn file Excel"}
    ],
    "constraints": [
      "Bimodal Format: Must include both text lines (#) and JSON lines",
      "Precision: Preserve all decimal digits for technical numbers",
      "Tool: Must use tools/data/excel_to_smart_jsonl.py"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Kiểm tra file Excel và xác định các sheet cần trích xuất.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script excel_to_smart_jsonl.py để tạo file đầu ra.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Kiểm tra cấu trúc file .jsonl (dòng # và dòng JSON).",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo hoàn tất và ghi nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Khởi động)
- [ ] Xác nhận file Excel tồn tại.

### ⚙️ Scene 2: ACT (Số hóa)
- **Path Resolution**: `output_jsonl = os.path.join(os.path.dirname(excel_path), f"{os.path.splitext(os.path.basename(excel_path))[0]}.jsonl")`
- [ ] **ACT**: Thực thi script với output tại `output_jsonl`.
// turbo
```powershell
python "tools/data/excel_to_smart_jsonl.py" "[excel_path]" --output "[output_jsonl]"
```

### 🧠 Scene 3: VERIFY (Hậu kiểm)
- **Cấu trúc**: Các dòng ghi chú phải bắt đầu bằng `#`. Các dòng dữ liệu phải là JSON hợp lệ.
- **Dữ liệu**: Đối soát ngẫu nhiên 3 dòng để đảm bảo không mất cột.

### 🏁 Scene 4: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [CONVERT] Chuyển đổi Excel sang JSONL: {Filename}`.
