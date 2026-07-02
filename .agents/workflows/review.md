---
description: Xử lý yêu cầu Lưu Soát (Review) từ App qua Agent Bridge (Miễn phí 0 đ)
---
<!--
File: .agents/workflows/review.md
Description: Workflow lưu soát (Review) qua Agent Bridge (0đ) tích hợp Fast-Track.
Changelog:
- 10:55:00 21/03/2026: [UPDATE] Chuyển đổi sang quy trình xử lý thủ công qua IDE để đảm bảo 0VND. (Antigravity)
- 12:28:00 24/03/2026: [UPDATE] Bổ sung Step 5 để đảm bảo kết quả REVIEW luôn được chèn vào Task SQLite. (Antigravity)
- 17:50:00 21/03/2026: [STRICT] Agent tự xử lý OCR + Cấm dùng API Key. (Antigravity)
- 15:30:00 31/03/2026: [REFACTOR] Nâng cấp lên hệ thống Fast-Track Automation. (Antigravity)
- 08:28:00 04/04/2026: [FIX] Chuyển ghi analysis.json qua IDE write_to_file + PYTHONUTF8. (Antigravity)
- 08:35:00 08/04/2026: [UPDATE] Chuyển đổi báo cáo Lưu soát sang Markdown. (Antigravity)
-->
# Workflow Lưu Soát (Review) - V2026 SSL Supreme

Workflow này dùng để thực hiện lưu soát (Review) các báo cáo, bản vẽ và cam kết dự án theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PROJECT_REVIEW",
    "workflow_name": "High-Precision Project Audit & Review",
    "workflow_goal": "Perform a technical review of project artifacts (Drawings, Reports) to verify commitments and data accuracy.",
    "expected_inputs": [
      {"name": "request_data", "type": "json", "description": "Dữ liệu yêu cầu từ Bridge"}
    ],
    "constraints": [
      "Vision First: Mandatory OCR of drawings and images using Vision",
      "Commitment Audit: Cross-check against pending_commitments",
      "Precision: Must include Tonnage Analysis and Scope Verification"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Đọc yêu cầu từ .gemini/bridge/request.json và nạp danh sách cam kết tồn đọng.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Thực thi OCR/Vision để bóc tách dữ liệu từ bản vẽ hoặc ảnh báo cáo.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Phân tích Trí tuệ: Đối soát cam kết, phân tích khối lượng (Tonnage) và kiểm tra ranh giới trách nhiệm (Scope).",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi file tmp/analysis.json và thực thi Bridge Processor để cập nhật kết quả lên App.",
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

### 🛠️ Scene 1: PREPARE (Bối cảnh)
- [ ] Soi `pending_commitments` để biết Anh Lưu đang hứa gì hoặc team đang hứa gì.

### 🛰️ Scene 2: ACQUIRE (Bóc tách Vision)
- **BẮT BUỘC**: OCR bản vẽ bằng Vision. Không được dùng text "đoán".
- **Dữ liệu**: Bóc tách khối lượng, mác thép, quy cách tiết diện.

### 🧠 Scene 3: REASON (Strategic Audit Logic)
- **Tonnage Analysis Logic**:
    - `issued = extract_tonnage(current_doc)`
    - `total_contract = soul.get("total_tonnage")`
    - `remaining = total_contract - issued`
    - `status = "DELAY" if current_date > deadline else "ON_TRACK"`
- **Commitment Audit**:
    - `pending = load_commitments(project_key)`
    - `logic = "Cross-reference OCR evidence with pending list"`
    - `new_promises = detect_promises(content)`
- **Template**: `use_template(".agents/templates/tpl_project_review.md")`

### 💾 Scene 4: ACT (Đồng bộ)
// turbo
```powershell
$env:PYTHONUTF8="1"; set PYTHONPATH=.; python tools/bridge/bridge_processor.py --analysis_file tmp/analysis.json --auto
```

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [REVIEW] Lưu soát dự án: {Project}`.
