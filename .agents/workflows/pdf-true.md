---
description: Số hóa PDF văn bản (True PDF) sang Markdown - Verbatim 100/100 (Không Enrich, Không Sync).
---

# Workflow Số hóa True PDF (PDF-True) - V2026 SSL Supreme

Workflow này dùng để số hóa các file PDF có lớp văn bản (True PDF) sang Markdown nguyên văn 100/100 một cách nhanh chóng và chính xác.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PDF_TRUE_TO_MD",
    "workflow_name": "High-Precision True PDF Digitization",
    "workflow_goal": "Convert text-based PDFs to verbatim Markdown without enrichment or DB sync.",
    "expected_inputs": [
      {"name": "pdf_path", "type": "string", "description": "Đường dẫn file PDF văn bản"}
    ],
    "constraints": [
      "Diamond Precision: 100/100 Verbatim extraction",
      "No Truncation: Preserve all headers, footers, and legal notes",
      "Speed: Direct text extraction (No OCR unless forced)",
      "Source Linking: Must include a clickable link to the original PDF at the end of the file."
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Kiểm tra file và xác nhận lớp văn bản (Selectable Text).",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Trích xuất văn bản thô bằng công cụ chuyên dụng.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Tái cấu trúc Markdown: Bảo toàn bảng biểu, định dạng in đậm, và cấu trúc trang.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi file .md (hậu tố _DIGITIZED.md) cạnh file gốc.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Ghi nhật ký nghiệp vụ và báo cáo hoàn tất.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Khởi động)
- [ ] Dùng `view_file` hoặc `extract_pdf_text.py` để kiểm tra lớp văn bản.
- [ ] Nếu là PDF Scan -> Hướng dẫn người dùng dùng lệnh `/pdf-scan`.

### ⚙️ Scene 2: ACQUIRE (Trích xuất)
// turbo
```powershell
python "tools/pdf/extract_pdf_text.py" "[pdf_path]"
```

### 🧠 Scene 3: REASON (Technical Processing Logic)
- **Execution Mode**: `VERBATIM_SUPREME_V2026`.
- **Formatting Rules**:
    - Chuyển đổi bảng thô sang **Gfm Table**.
    - Sử dụng `#`, `##` để phân cấp tiêu đề theo văn bản gốc.
    - Đảm bảo các công thức toán học hoặc ký hiệu thép (`*` -> `x`) được chuẩn hóa.
- **Source Link Generation**:
    - `link_text = "[File gốc: {basename}]({absolute_uri})"`
    - `action = append_to_eof(link_text)`

### 💾 Scene 4: ACT (Ghi file)
- **Path Resolution**: `output_path = os.path.join(os.path.dirname(pdf_path), f"{os.path.splitext(os.path.basename(pdf_path))[0]}_DIGITIZED.md")`
- [ ] **ACT**: Ghi nội dung số hóa kèm link file gốc vào `output_path`.

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [DIGITIZE] Số hóa True PDF: {Filename}`.
