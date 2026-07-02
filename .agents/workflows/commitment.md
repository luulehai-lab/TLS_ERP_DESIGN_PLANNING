---
description: Tự tạo lời nhắc/cam kết công việc (Sổ Lời Nhắc) - Mặc định người hứa là Lê Hải Lưu
---
# Workflow Tự tạo Lời nhắc (Commitment) - V2026 SSL Supreme

Workflow này giúp tự động ghi lại các lời hứa hoặc cam kết công việc của Anh Lưu hoặc đội ngũ vào Sổ Lời Nhắc theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_COMMITMENT",
    "workflow_name": "Task Commitment Generation",
    "workflow_goal": "Automatically capture and register project commitments to prevent task slippage.",
    "expected_inputs": [
      {"name": "promise_text", "type": "string", "description": "Nội dung lời hứa"},
      {"name": "deadline", "type": "string", "description": "Hạn chót (YYYY-MM-DD)"}
    ],
    "constraints": [
      "Default Promiser: Always 'Lê Hải Lưu' unless specified",
      "Tool: Must use tools/tasks/add_commitment.py",
      "Precision: Title must be concise (max 50 chars)"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Nhận diện ý định (Intent) và trích xuất thực thể: Việc gì? Khi nào? Ai hứa?",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script add_commitment.py để ghi vào cơ sở dữ liệu.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Kiểm tra file commitments.json và chuẩn bị phản hồi UI.",
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
- [ ] Quét từ khóa: "hứa", "sẽ làm", "gửi cho", "ban hành"...
- [ ] Ép tên người hứa: **Lê Hải Lưu** (Viết đầy đủ họ tên).

### 💾 Scene 2: ACT (Ghi sổ)
// turbo
```powershell
python tools/tasks/add_commitment.py --project "MÃ_DỰ_ÁN" --title "Tên lời nhắc" --content "Chi tiết công việc" --deadline "YYYY-MM-DD" --who "Lê Hải Lưu"
```

### 🔄 Scene 3: VERIFY (Kiểm chứng)
- [ ] Xác nhận script trả về kết quả thành công.
- [ ] Thông báo Anh Lưu: "Em đã ghi vào **Sổ Lời Nhắc** tại giao diện App".

### 🏁 Scene 4: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Định dạng: `## [COMMITMENT] Ghi sổ tay nhắc việc: {Title} (Who: Lê Hải Lưu)`.
