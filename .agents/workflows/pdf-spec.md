---
description: Số hóa PDF Spec (True & Scan) sang Markdown (Verbatim Supreme - Phí 0đ)
---
# Workflow Số hóa Spec Vật tư (PDF-Spec) - V2026 SSL Supreme

Workflow này dùng để số hóa các tài liệu Specification (Sơn, Keo, Thép) với độ chính xác Tuyệt đối (100/100) theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PDF_SPEC_DIGITIZATION",
    "workflow_name": "Technical Spec Supreme Digitization",
    "workflow_goal": "Extract 100/100 verbatim data from Specs (Hybrid PDF/Scan) and sync with technical DB.",
    "expected_inputs": [
      {"name": "pdf_path", "type": "string", "description": "Đường dẫn file PDF Spec"}
    ],
    "constraints": [
      "Zero Truncation: Do NOT summarize Disclaimer or Legal notes",
      "Hybrid Mode: Auto-detect True PDF vs Scan",
      "Format: Markdown Table for Technical Data",
      "Source Linking: Must include a clickable link to the original PDF at the end of the file."
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Nhận diện loại PDF (True vs Scan) và kiểm tra bối cảnh vật tư.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Trích xuất văn bản thô theo từng trang (Page-by-Page) để chống sót tin.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Bóc tách Diamond Precision: Sửa lỗi OCR, vẽ bảng MD Table, đối soát Disclaimer.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi file .md và thực thi script đồng bộ tri thức (Sync Knowledge).",
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

### 🛠️ Scene 1: PREPARE (Nhận diện)
- [ ] Dùng `view_file` để soi PDF.
- [ ] Nếu có text chọn được -> **True PDF**. Nếu chỉ có ảnh -> **PDF Scan**.

### 🛰️ Scene 2: ACQUIRE (Trích xuất)
// turbo
```powershell
# Cho True PDF
python "tools/pdf/extract_pdf_text.py" "[pdf_path]"
# Cho PDF Scan
python "tools/ocr/pdf_scan_to_md.py" "[pdf_path]"
```

### 🧠 Scene 3: REASON (Technical Processing Logic)
- **Verification Mode**: `DIAMOND_PRECISION` (No truncation allowed).
- **Checklist Logic**:
    - `fields = ["Solis", "DFT", "Density", "Surface_Prep", "Limitations", "Disclaimer"]`
    - `status = [verify(f) for f in fields]`
- **Quality Assurance**:
    - `assert content.verbatim_score == 1.0`
    - `assert content.has_placeholders == False`
- **Source Link Generation**:
    - `link_text = "[File gốc: {basename}]({absolute_uri})"`
    - `action = append_to_eof(link_text)`

### 💾 Scene 4: ACT (Ghi file & Sync)
- **Path Resolution**: `output_path = os.path.join(os.path.dirname(pdf_path), f"{os.path.splitext(os.path.basename(pdf_path))[0]}_DIGITIZED.md")`
- [ ] **ACT**: Ghi file số hóa kèm link file gốc vào `output_path`.
// turbo
```powershell
python "tools/maintenance/sync_supreme_knowledge.py"
```

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký: `## [DIGITIZE] Số hóa Spec: {Filename}`.
