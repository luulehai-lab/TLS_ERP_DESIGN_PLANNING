---
description: Xử lý Yêu cầu Index Dữ liệu Kỹ thuật (Smart Index) sang SQLite & ChromaDB
---
<!--
File: .agents/workflows/smart-index.md
Description: Workflow hỗ trợ AI tự động Index dữ liệu kỹ thuật từ PDF/Word/Excel theo chuẩn SSL.
Changelog:
- 11:15:00 05/05/2026: [REFACTOR] Nâng cấp sang chuẩn SSL v2026. Chuẩn hóa quy trình đánh chỉ mục High-Fidelity. (Antigravity)
-->

# Workflow Đánh chỉ mục Thông minh (Smart-Index) - V2026 SSL Supreme

Workflow này dùng để số hóa và đánh chỉ mục dữ liệu kỹ thuật (PDF/Word/Excel) vào SQLite & ChromaDB theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_SMART_INDEXING",
    "workflow_name": "High-Precision Technical Indexing",
    "workflow_goal": "Transform raw technical documents into structured, searchable database records with 100/100 fidelity.",
    "expected_inputs": [
      {"name": "file_path", "type": "string", "description": "Đường dẫn file cần index"},
      {"name": "index_target", "type": "string", "description": "Bảng đích (technical_data, contracts...)"}
    ],
    "constraints": [
      "Zero Truncation: No summarizing allowed",
      "Format: Must use Markdown Tables for structured data",
      "Validation: Mandatory search check after indexing"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Nhận diện định dạng tệp (PDF/DOCX/XLSX) và kiểm tra bảng đích.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Trích xuất dữ liệu thô (OCR/Text/Table) và lưu vào file trung gian.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "So soát Verbatim: Sửa lỗi chính tả, chuẩn hóa Header bảng, phân mục (Granularity).",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script nạp dữ liệu (seed_*.py) vào SQLite & ChromaDB.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Thực hiện truy vấn mẫu để xác nhận dữ liệu đã được index thành công.",
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
- [ ] Xác định định dạng file để chọn Processor phù hợp (Word/PDF/Excel).

### 🛰️ Scene 2: ACQUIRE (Trích xuất)
- [ ] Sử dụng các script tại `tools/indexing/` (ví dụ: `excel_to_smart_jsonl.py`).
- [ ] Dùng Vision để đọc bảng biểu nếu là PDF/Ảnh.

### 🧠 Scene 3: REASON (So soát)
- **BẮT BUỘC**: Sửa lỗi tiếng Việt, tái tạo cấu trúc bảng chính xác 100/100.
- **Phân mục**: Mỗi chương/mục lớn phải được tách thành bản ghi riêng để tra cứu nhanh.

### 💾 Scene 4: ACT (Nạp dữ liệu)
// turbo
```powershell
python "tools/database/seed_technical_data.py" --file "[JSONL_PATH]"
```

### 🔍 Scene 5: VERIFY (Kiểm tra)
- [ ] Thực hiện lệnh `grep_search` hoặc `inspect_db.py` để tìm thử từ khóa vừa index.

### 🏁 Scene 6: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký: `## [INDEX] Đã đánh chỉ mục tài liệu: {Filename}`.
