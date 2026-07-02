---
description: Đánh chỉ mục Excel kỹ thuật (High-Precision Smart Indexing)
---

# Workflow Đánh chỉ mục Excel (Excel-Index) - V2026 SSL Supreme

Workflow này dùng để đánh chỉ mục các tệp Excel vật tư (Thép, Sơn, Biện pháp) với độ chính xác Tuyệt đối (100/100) theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_EXCEL_INDEXING",
    "workflow_name": "High-Precision Excel Indexing",
    "workflow_goal": "Digitize Excel workbooks into structured, searchable blocks with verbatim header integrity.",
    "expected_inputs": [
      {"name": "file_path", "type": "string", "description": "Đường dẫn file Excel"}
    ],
    "constraints": [
      "Verbatim: Keep 100% of column headers and numeric precision",
      "Block-based: Separate Project info from Data tables",
      "Persistence: Must sync with project_docs and Soul"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Nhận diện số lượng Sheet và cấu trúc cột yêu cầu.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Đọc dữ liệu Excel bằng pandas/openpyxl và lưu vào cấu trúc trung gian.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Phân đoạn thông minh: Tách Khối Căn cước (Văn bản) và Khối Quy cách (MD Table).",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi nhận vào SQLite (project_docs) và đồng bộ Soul Profile.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo số lượng bản ghi đã nạp và nhắc Anh Lưu Refresh UI.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Phân tích)
- [ ] Xác định danh sách Sheet cần xử lý.
- [ ] Quy tắc: Giữ nguyên TOÀN BỘ tiêu đề cột bản gốc.

### 🛰️ Scene 2: ACQUIRE (Trích xuất)
- [ ] Đọc trọn vẹn 100% nội dung, không tự ý xóa dòng/cột.
- [ ] Bảo lưu độ chính xác của số thập phân.

### 🧠 Scene 3: REASON (Định dạng Premium)
- **Khối Căn cước**: Dùng Bold + Bullets (DỰ ÁN, HẠNG MỤC...).
- **Khối Dữ liệu**: Dùng Markdown Table chuẩn.
- **Tiêu đề Section**: `[Tên_File] [Tên_Sheet] - [Mô tả khối]`.

### 💾 Scene 4: ACT (Đồng bộ)
- **Path Resolution (Preview)**: `md_output = os.path.join(os.path.dirname(file_path), f"{os.path.splitext(os.path.basename(file_path))[0]}_INDEX.md")`
- [ ] **ACT**: Nếu có phát sinh file Markdown preview, ghi vào `md_output`.
// turbo
```powershell
python "tools/indexing/excel_to_smart_jsonl.py" --file "[file_path]"
```

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký: `## [INDEX] Đã đánh chỉ mục Excel: {Filename}`.
