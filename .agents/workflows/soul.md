---
description: Lập/Cập nhật Hồ sơ Linh hồn dự án (Project Soul) - Lưu trữ tri thức bền vững
---
# Workflow Hồ sơ Linh hồn (Project Soul) - V2026 SSL Supreme

Workflow này dùng để khởi tạo hoặc cập nhật định kỳ "Linh hồn" của dự án theo chuẩn SSL (Scheduling-Structural-Logical).

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PROJECT_SOUL",
    "workflow_name": "Project Soul Management",
    "workflow_goal": "Maintain a high-fidelity persistent project profile in Markdown and sync with UI.",
    "expected_inputs": [
      {"name": "project_key", "type": "string", "description": "Mã định danh dự án (e.g. 028_DONGHUI)"}
    ],
    "constraints": [
      "Persistence First: Must write to .md in /profiles folder",
      "Format: 7-part matrix (Identity to Risks)",
      "Verbatim Integrity: Data must match project logs and contracts"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Xác định mã dự án và kiểm tra sự tồn tại của file Soul cũ.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Thu thập dữ liệu từ db_context (Nhật ký, Hợp đồng) và nội dung Soul cũ.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Tổng hợp tri thức mới vào khung 7 phần Premium.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi file .md bền vững và chuẩn bị JSON đồng bộ UI.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Chạy Bridge Processor để cập nhật App và kiểm tra LAST_TASK_ID.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo hoàn tất cho Anh Lưu và ghi nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Chuẩn bị)
- [ ] Trích xuất `project_key` từ `request.json`.
- [ ] Kiểm tra `local_data/profiles/{project_key}.md`.

### 🛰️ Scene 2: ACQUIRE (Thu thập)
- [ ] Đọc toàn bộ nhật ký liên quan trong `db_context`.
- [ ] Nếu là Cập nhật (Update): Đọc nội dung Soul cũ để giữ lại các phần không thay đổi.

### 🧠 Scene 3: REASON (Strategic Profiling Logic)
- **Data Enrichment Logic**:
    - `template = load(".agents/templates/tpl_project_soul.md")`
    - `audit_fields = ["Tonnage", "Deadline", "Scope", "Stakeholders"]`
    - `logic = "Correlate Extract with Soul History"`
- **Critical Analysis**:
    - `calc_remaining_tonnage = contract_total - delivered_total`
    - `calc_progress_percentage = (delivered / contract) * 100`
    - `alert_level = "HIGH" if deadline < current_date + 30 days else "NORMAL"`
- **Formatting**: `wrap_report(marker="AI_REPORT")`

### 💾 Scene 4: ACT (Ghi tri thức)
- [ ] **BẮT BUỘC**: Dùng `write_to_file` ghi vào `local_data/profiles/{project_key}.md`.
- [ ] Tạo `tmp/analysis.json` (Flat structure, `is_contract: true`).

### 🔄 Scene 5: VERIFY (Đồng bộ)
// turbo
```powershell
$env:PYTHONUTF8="1"; set PYTHONPATH=.; python tools/bridge/bridge_processor.py --analysis_file tmp/analysis.json --auto
```

### 🏁 Scene 6: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_code_YYYY_MM_DD.md` với tag `[SOUL]`.
- [ ] Thông báo cho Anh Lưu: "Linh hồn dự án đã được cập nhật bền vững tại hồ sơ .md".
