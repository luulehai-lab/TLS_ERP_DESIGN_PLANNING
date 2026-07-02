---
description: Xử lý đối chiếu nhiều hợp đồng (Miễn phí 0 đ)
---
<!--
File: .agents/workflows/compare.md
Description: Workflow đối chiếu văn bản (Compare) 0đ tích hợp Fast-Track.
Changelog:
- 15:37:00 31/03/2026: [REFACTOR] Nâng cấp lên trình xử lý Fast-Track Automation. (Antigravity)
- 08:28:00 04/04/2026: [FIX] Chuyển ghi analysis.json qua IDE write_to_file + PYTHONUTF8. (Antigravity)
-->
# Workflow Đối chiếu Hợp đồng (Compare) - V2026 SSL Supreme

Workflow này dùng để đối chiếu các phiên bản hợp đồng/phụ lục và phát hiện sai khác theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_CONTRACT_COMPARISON",
    "workflow_name": "Multi-Document Comparison",
    "workflow_goal": "Identify discrepancies and highlights changes across multiple contract versions.",
    "expected_inputs": [
      {"name": "file_list", "type": "list", "description": "Danh sách file cần so sánh"}
    ],
    "constraints": [
      "Detail Level: Focus on Price, Timeline, and Warranty",
      "Format: Must use Comparison Matrix (Markdown Table)",
      "Sync: Must output to tmp/analysis.json"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Xác định danh sách tệp tin mục tiêu từ Bridge request.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Đọc nội dung Verbatim của tất cả các phiên bản tệp tin.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Phân tích so sánh: Lập bảng Matrix và chỉ ra các điểm mâu thuẫn/thay đổi.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi file tmp/analysis.json và thực thi Bridge Processor.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo hoàn tất và ghi nhật ký nghiệp vụ.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Nhận diện)
- [ ] Kiểm tra `.gemini/bridge/request.json`. Lấy danh sách file cần so sánh.

### 🛰️ Scene 2: ACQUIRE (Thu thập)
- [ ] Đọc nội dung từng file. Nếu là PDF/Ảnh, tự động gọi workflow con `/pdf-scan`.

### 🧠 Scene 3: REASON (Comparative Matrix Logic)
- **Comparison Engine**: `DIFF_DETECTOR_V2026`.
- **Target Dimensions**:
    - `dimensions = ["Price", "Timeline", "Warranty", "Scope", "Liability"]`
- **Logic**:
    - `table = Matrix(cols=file_list, rows=dimensions)`
    - `diffs = [compare(v1, v2) for v1, v2 in version_pairs]`
- **Alert Logic**:
    - `if v1 != v2: cell_format = "BOLD_RED_WARNING"`
    - `else: cell_format = "NORMAL"`
- **Template**: `use_template(".agents/templates/tpl_contract_comparison.md")`

### 💾 Scene 4: ACT (Ghi & Đồng bộ)
- [ ] Ghi `tmp/analysis.json` theo đúng Schema đối chiếu sau:
```json
{
  "project_key": "{project_key}",
  "is_contract": true,
  "type": "COMPARE_CONTRACTS",
  "filename": "Báo cáo đối chiếu.md",
  "data": "Nội dung bảng Matrix so sánh bằng Markdown Table (BẮT BUỘC)"
}
```
// turbo
```powershell
$env:PYTHONUTF8="1"; set PYTHONPATH=.; python tools/bridge/bridge_processor.py --analysis_file tmp/analysis.json --auto
```

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [COMPARE] Đối chiếu hồ sơ: {Project}`.
