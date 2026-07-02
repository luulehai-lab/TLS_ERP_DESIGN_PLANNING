---
description: Xử lý điểm tin (Pulse) Dự án từ App qua IDE Agent (Miễn phí 100%)
---
<!--
File: .agents/workflows/pulse.md
Description: Workflow điểm tin dự án (Pulse) 0đ tích hợp Fast-Track.
Changelog:
- 15:35:00 31/03/2026: [REFACTOR] Nâng cấp lên trình xử lý Fast-Track Automation. (Antigravity)
- 08:28:00 04/04/2026: [FIX] Chuyển ghi analysis.json qua IDE write_to_file + PYTHONUTF8. (Antigravity)
-->
# Workflow Nhịp đập dự án (Pulse) - V2026 SSL Supreme

Workflow này dùng để tổng hợp nhanh tình hình dự án (Nhân sự, Tiến độ, Cam kết) theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_PROJECT_PULSE",
    "workflow_name": "Rapid Project Status Synthesis",
    "workflow_goal": "Provide a high-level overview of project health, personnel updates, and pending commitments.",
    "expected_inputs": [
      {"name": "project_key", "type": "string", "description": "Mã dự án"}
    ],
    "constraints": [
      "Privacy: No task_id tagging in pulse reports",
      "Focus: Highlights Personnel, Milestones, and Commitments",
      "Sync: Must output to tmp/analysis.json"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Đọc yêu cầu từ .gemini/bridge/request.json và xác định mã dự án.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Đọc hồ sơ dự án (local_data/profiles/) và nhật ký công việc gần nhất.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Điểm tin: Tổng hợp 3 mục chính (Nhân sự, Tiến độ, Cam kết) súc tích.",
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

### 🛠️ Scene 1: PREPARE (Bối cảnh)
- [ ] Lấy `project_key`. Nếu không có, mặc định là dự án hiện tại.

### 🧠 Scene 2: REASON (Điểm tin)
- **Template**: BẮT BUỘC sử dụng mẫu tại `.agents/templates/tpl_project_pulse.md`.
- **Nhân sự**: Cập nhật thay đổi vị trí, nhiệm vụ.
- **Tiến độ**: Các mốc chuẩn (Milestones) sắp tới.
- **Cam kết**: Các đầu việc "Hứa" chưa hoàn thành.

### 💾 Scene 3: ACT (Đồng bộ)
// turbo
```powershell
$env:PYTHONUTF8="1"; set PYTHONPATH=.; python tools/bridge/bridge_processor.py --analysis_file tmp/analysis.json --auto
```

### 🏁 Scene 4: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [PULSE] Điểm tin dự án: {Project}`.
