---
description: Số hóa DOCX sang Markdown (Verbatim Supreme TLS - SSL v2026)
---

<!-- 
FILE: .agents/workflows/docx-to-md-verbatim.md
CHANGELOG:
- 16:55:00 04/05/2026: [REFACTOR] Nâng cấp Workflow sang chuẩn SSL v2026. (Antigravity)
- 11:08:00 22/04/2026: [UPDATE] Bổ dung quy tắc ghi ngày số hóa và link file gốc ở cuối file. (Antigravity)
-->

# 🚀 WORKFLOW: Digitalize DOCX to Markdown (SSL v2026)

Mục đích: Chuyển đổi file Word (.docx) sang Markdown với độ chính xác **100% Verbatim**, giữ nguyên cấu trúc TLS.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_DOCX_TO_MD",
    "workflow_name": "Digitalize DOCX to MD",
    "workflow_goal": "100% Verbatim digitalization of Word documents to Markdown.",
    "expected_inputs": [
      {"name": "path_to_docx", "type": "str", "description": "Đường dẫn file Word gốc"},
      {"name": "path_to_md", "type": "str", "description": "Đường dẫn file Markdown đích"}
    ],
    "dependencies": [
      {"type": "software", "value": "Microsoft Word (COM Automation)"},
      {"type": "library", "value": "pywin32"}
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Kiểm tra file đầu vào và môi trường Word.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực hiện số hóa thô qua script COM Automation.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON_ACT"}]
    },
    {
      "scene_id": "S_REASON_ACT",
      "scene_type": "REASON",
      "scene_goal": "Hậu xử lý chuyên sâu (Heading, Tables, Steel Symbols).",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Đối soát Verbatim 100/100 và cấu trúc Sidebar.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Ghi dấu vết số hóa và nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🔍 Scene 1: PREPARE (Kiểm tra)
- [ ] Xác nhận file `[PATH_TO_DOCX]` tồn tại.
- [ ] Kiểm tra môi trường Windows + Microsoft Word.

### ⚙️ Scene 2: ACT (Số hóa thô - V9.0 Image Support)
// turbo
```powershell
python "tools/data/docx_digitizer.py" "[PATH_TO_DOCX]" -o "[PATH_TO_OUTPUT_MD]"
```
> [!NOTE]
> V9.0 tự động trích xuất ảnh vào thư mục `[filename]_images` và gắn link vào MD.

### 🖋️ Scene 3: REASON & ACT (Technical Post-Processing)
- **Heading Resolution**:
    - `logic = "Auto-detect structure based on font size and uppercase"`
    - `mapping = { "Level 1": "#", "Level 2": "##" }`
- **Table Transformation**: 
    - `if table.is_simple: target = "MARKDOWN"`
    - `else: target = "HTML_PREMIUM_TLS"`
- **Technical Normalization**:
    - `normalization = [ (r'([HIUVL])(\d+)\*(\d+)', r'\1\2x\3') ]`
- **Encoding**: `charset = "UTF-8-NFC"`

### ✅ Scene 4: VERIFY (Kiểm soát chất lượng)
- [ ] **Sidebar**: Sidebar hiện đủ Điều/Phụ lục chưa?
- [ ] **Nội dung**: Có bị mất chữ hay sai chính tả không? (Verbatim 100/100).
- [ ] **Bảng**: Bảng hiển thị ngay ngắn, không vỡ khung.

### 💾 Scene 5: FINALIZE (Dấu vết)
- **Path Resolution**: `output_path = os.path.join(os.path.dirname(path_to_docx), f"{os.path.splitext(os.path.basename(path_to_docx))[0]}.md")`
- [ ] **ACT**: Ghi file `.md` vào `output_path`.
- [ ] Chèn link file gốc ở cuối file MD.
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.

---
*Ghi chú: Workflow này sử dụng COM Automation, không đóng Word đột ngột khi đang chạy.*
