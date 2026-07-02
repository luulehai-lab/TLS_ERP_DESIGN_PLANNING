---
description: Khởi động Bot Telegram trực chiến ngầm phục vụ Anh Lưu từ xa.
---

# Workflow Khởi động Bot Telegram - V2026 SSL Supreme

Workflow này dùng để kích hoạt Bot Telegram trực chiến (TLS Station) phục vụ Anh Lưu từ xa theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_TELEGRAM_BOT_START",
    "workflow_name": "TLS Station Activation",
    "workflow_goal": "Start the Telegram bot worker to handle remote technical inquiries and catalog lookups.",
    "expected_inputs": [],
    "constraints": [
      "Continuity: Must run as a persistent background process",
      "Availability: Requires stable internet connection and active session",
      "Logging: Must log interactions for auditing"
    ],
    "entry_scene_id": "S_ACT"
  },
  "scenes": [
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script run_bot.py để bắt đầu lắng nghe lệnh từ Telegram.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Xác nhận trạng thái kết nối và thông báo cho Anh Lưu.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 💾 Scene 1: ACT (Khởi động)
// turbo
```powershell
set PYTHONPATH=.
python tools/telegram/run_bot.py
```

### 🏁 Scene 2: FINALIZE (Hoàn tất)
- [ ] Báo cáo: "🚀 Bot Telegram (TLS Station) đã sẵn sàng trực chiến!".
- [ ] Nhắc nhở: Anh Lưu có thể tra cứu barem, giá thép, hoặc gửi ảnh báo giá trực tiếp qua Telegram.
