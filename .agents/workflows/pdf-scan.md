---
description: Số hóa PDF Scan sang Markdown (Verbatim Supreme - Phí 0đ)
---
<!--
File: .agents/workflows/pdf-scan.md
Description: Số hóa PDF Scan (Công văn, thông báo) sang Markdown/HTML - Direct Mode (Siêu tốc).
Changelog:
- 15:15:00 21/04/2026: [UPDATE] Cập nhật Frontmatter để hệ thống nhận diện lệnh gọi /pdf-scan. (Antigravity)
- 15:05:00 21/04/2026: [UPGRADE] Chuyển đổi sang quy trình Direct OCR Bimodal (MD + HTML). (Antigravity)
- 14:40:00 21/04/2026: [NEW] Khởi tạo workflow số hóa PDF Scan. (Antigravity)
-->
# Workflow Số hóa PDF Scan (PDF-Scan) - V2026 SSL Supreme

Workflow này dùng để số hóa các file PDF scan (dạng ảnh) sang Markdown Verbatim 100/100 theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PDF_SCAN_TO_MD",
    "workflow_name": "High-Speed PDF Scan Digitization",
    "workflow_goal": "Convert image-based PDFs to verbatim Markdown with 100/100 precision.",
    "expected_inputs": [
      {"name": "pdf_path", "type": "string", "description": "Đường dẫn file PDF"}
    ],
    "constraints": [
      "Zero Hallucination: Verbatim OCR only",
      "Anti-Truncation: Must read full file before updating knowledge",
      "Cleanup: Delete temp images after processing",
      "Source Linking: Must include a clickable link to the original PDF at the end of the file."
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Kiểm tra file PDF và khởi tạo thư mục tạm để rã ảnh.",
      "next_scene_rules": [{"condition": "success", "target": "S_EXTRACT"}]
    },
    {
      "scene_id": "S_EXTRACT",
      "scene_type": "ACT",
      "scene_goal": "Rã PDF thành ảnh JPEG chất lượng cao (200 DPI).",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Sử dụng Vision Tool để đọc từng trang ảnh một cách tuần tự.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Tái cấu trúc Markdown: Văn bản nguyên văn + Bảng biểu MD Table.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi file .md (hậu tố _SCAN.md) và dọn dẹp ảnh tạm.",
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
- [ ] Xác nhận file PDF tồn tại.

### ⚙️ Scene 2: EXTRACT (Rã ảnh)
// turbo
```powershell
python "tools/ocr/pdf_scan_to_md.py" "[PATH_TO_PDF]"
```

### 🛰️ Scene 3: ACQUIRE (Quét ảnh)
- [ ] Duyệt qua thư mục `.tmp_ocr_[FILE_NAME]`.
- [ ] Dùng `view_file` cho từng trang. **KHÔNG** bỏ sót trang nào.

### 🧠 Scene 4: REASON (Technical Processing Logic)
- **Execution Mode**: `VERBATIM_SUPREME_V2026` (100/100, no summarization).
- **Technical Normalization**:
    - `pattern = r'([HIUVL])(\d+)\*(\d+)'`
    - `replacement = r'\1\2x\3'`
    - `action = content.regex_replace(pattern, replacement)`
- **Structural Mapping**:
    - `output_format = "MARKDOWN_GITHUB_FLAVORED"`
    - `table_engine = "GfmTableGenerator"`
- **Source Link Generation**:
    - `link_text = "[File gốc: {basename}]({absolute_uri})"`
    - `action = append_to_eof(link_text)`
- **Quality Assurance**:
    - `assert content.verbatim_score == 1.0`
    - `check_missing_pages() == False`

### 💾 Scene 5: ACT (Ghi file & Dọn dẹp)
- **Path Resolution**: `output_path = os.path.join(os.path.dirname(pdf_path), f"{os.path.splitext(os.path.basename(pdf_path))[0]}_SCAN.md")`
- [ ] **ACT**: Ghi nội dung số hóa kèm link file gốc vào `output_path`.
- [ ] **BẮT BUỘC**: Xóa thư mục ảnh tạm `.tmp_ocr_*` để tránh rác ổ đĩa.

### 🏁 Scene 6: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [DIGITIZE] Số hóa PDF Scan: {Filename}`.
