---
description: Số hóa Ảnh (Quotation, Minutes, Drawing) sang Markdown Supreme (Verbatim 100/100 - Phí 0đ)
---

# Workflow Số hóa Hình ảnh (Image-MD) - V2026 SSL Supreme

Workflow này dùng để chuyển đổi ảnh chụp/scan (Báo giá, Biên bản, Bản vẽ) sang định dạng Markdown Verbatim 100/100 theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_IMAGE_TO_MD",
    "workflow_name": "Supreme Image Digitization",
    "workflow_goal": "Convert visual data (JPG/PNG) to high-fidelity verbatim Markdown.",
    "expected_inputs": [
      {"name": "image_path", "type": "string", "description": "Đường dẫn file ảnh"}
    ],
    "constraints": [
      "Verbatim Only: Do NOT summarize text",
      "Table Reconstruction: Must use Markdown Tables",
      "Steel Symbols: Replace '*' with 'x' (e.g. H200x100)"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Nhận diện định dạng ảnh và kiểm tra bối cảnh dự án.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Sử dụng Vision Tool để đọc nội dung ảnh (Văn bản, Bảng biểu).",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Tái tạo dữ liệu: Chuyển bảng sang MD Table, chuẩn hóa ký hiệu thép.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi file .md (hậu tố _DIGITIZED.md) và thông báo kết quả.",
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

### 🛠️ Scene 1: PREPARE (Nhận diện)
- [ ] Xác định file ảnh có tồn tại. 
- [ ] Ghi nhận mã dự án liên quan (nếu có).

### 🛰️ Scene 2: ACQUIRE (Quét ảnh)
- [ ] Sử dụng `view_file` (Vision) để "soi" ảnh.
- [ ] **Lưu ý**: Đọc kỹ các ghi chú tay, con dấu và số hiệu tài liệu.

### 🧠 Scene 3: REASON (Technical Processing Logic)
- **Execution Mode**: `VERBATIM_SUPREME_V2026` (No summarization, 100/100 copy).
- **Technical Normalization**:
    - `pattern = r'([HIUVL])(\d+)\*(\d+)'`
    - `replacement = r'\1\2x\3'`
    - `action = content.regex_replace(pattern, replacement)`
- **Structural Mapping**:
    - `input_type = "IMAGE_PIXELS"`
    - `output_format = "MARKDOWN_GITHUB_FLAVORED"`
    - `table_engine = "GfmTableGenerator"`
- **Quality Assurance**:
    - `assert content.verbatim_score == 1.0`
    - `check_handwriting_extraction(ocr_confidence_threshold=0.85)`

### 💾 Scene 4: ACT (Ghi file)
- **Path Resolution**: `output_path = os.path.join(os.path.dirname(image_path), f"{os.path.splitext(os.path.basename(image_path))[0]}_DIGITIZED.md")`
- [ ] **ACT**: Ghi file `.md` vào `output_path`.
- [ ] Thêm Footer dẫn chiếu ảnh gốc.

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [DIGITIZE] Số hóa ảnh: {Filename}`.
