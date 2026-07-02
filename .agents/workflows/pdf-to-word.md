---
description: Quy trình chuyển đổi PDF sang Word chuyên sâu (Antigravity Pipeline - Bản V2026 Supreme)
---

Sử dụng workflow này khi cần tái tạo một file PDF scan thành Word (.docx) với độ chính xác tuyệt đối (Perfect Twin, Verbatim 100%).

# Workflow Chuyển đổi PDF sang Word (PDF-to-Word) - V2026 SSL Supreme

Workflow này dùng để tái tạo PDF (đặc biệt là bản scan) thành file Word (.docx) với độ chính xác "Perfect Twin" (100/100) theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PDF_TO_WORD_PERFECT_TWIN",
    "workflow_name": "High-Fidelity PDF to Word Reconstruction",
    "workflow_goal": "Reconstruct PDF documents into DOCX with pixel-perfect alignment and verbatim content.",
    "expected_inputs": [
      {"name": "pdf_path", "type": "string", "description": "Đường dẫn file PDF"},
      {"name": "page_number", "type": "int", "description": "Trang cần tái tạo"}
    ],
    "constraints": [
      "Fixed Form: Must use A4 Absolute dimensions",
      "Zero Normalization: No text simplification allowed",
      "Table Precision: Use fixed width tables for layouts"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Thực hiện CoT Visual Survey: Phân tích Typography, Margins, Bold/Italic Mapping.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Chạy visual_audit_grid.py để lấy tọa độ 1000-scale của các khối nội dung.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Lập kế hoạch Page Budgeting: Thiết lập giãn dòng, font size để ép nội dung về 1 trang.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script tái tạo Word (python-docx + oxml) với Ultimate Precision.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Visual Self-Audit: Đối chiếu ảnh gốc và bản docx pixel-by-pixel.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Thông báo hoàn tất và ghi nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Khảo sát thị giác)
- [ ] Xác định Font chữ (Thường 13pt), Margins (Ước lượng theo cm).
- [ ] Map Bold/Italic: Liệt kê đích danh các từ cần định dạng.

### 🛰️ Scene 2: ACQUIRE (Tọa độ)
// turbo
```powershell
python "tools/ocr/visual_audit_grid.py" "[pdf_path]" --page [page_number]
```

### 🧠 Scene 3: REASON (Technical Budgeting Logic)
- **Layout Logic**:
    - `page_size = "A4_ABSOLUTE"`
    - `enforce_single_page = True`
    - `line_spacing = 1.0`
- **Component Mapping**:
    - `entity_info = "FIXED_WIDTH_TABLE"`
    - `content_body = "NATIVE_DOCX_ELEMENTS"`
- **Visual Audit**:
    - `grid_resolution = "1000-scale"`
    - `pixel_perfect_match = True`

### 💾 Scene 4: ACT (Tái tạo Word)
- [ ] Ép cứng khổ A4: `8.27 x 11.69 inches`.
- [ ] Sử dụng `docx.oxml` để can thiệp sâu vào XML nếu cần Fixed Width.

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- **Path Resolution**: `output_docx = os.path.join(os.path.dirname(pdf_path), f"{os.path.splitext(os.path.basename(pdf_path))[0]}.docx")`
- [ ] **ACT**: Ghi file `.docx` vào `output_docx`.
