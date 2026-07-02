---
description: Khởi động Bridge Worker để xử lý AI 0đ (Nhúng, OCR ngầm, Phân tích gộp)
---
<!--
File: .agents/workflows/start-bridge.md
Description: Workflow khởi động hệ thống trực chiến 0đ (Bot Telegram + Bridge Listener + Stimulator).
Changelog:
- 09:15:00 14/05/2026: [UPDATE] Tích hợp khởi động luôn Bot Telegram vào workflow này để đồng bộ hóa hệ thống trực chiến. (Antigravity)
- 15:57:00 22/04/2026: [FIX] Cập nhật đường dẫn chính xác tới tools/bridge/bridge_listener.py và thêm PYTHONPATH. (Antigravity)
- 10:55:00 21/03/2026: [UPDATE] Chuyển sang chỉ bật Listener (chuông báo) và tắt Worker tự động để bảo vệ ví tiền. (Antigravity)
-->

# Workflow Khởi động Bridge Listener - V2026 SSL Supreme

Workflow này dùng để khởi động hệ thống chuông báo (Listener) phục vụ xử lý 0đ theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_BRIDGE_LISTENER_START",
    "workflow_name": "Zero-Cost Bridge Activation",
    "workflow_goal": "Start the background listener to alert when the App requests technical processing.",
    "expected_inputs": [],
    "constraints": [
      "No Auto-Worker: Must alert (BEEP) instead of processing with paid API",
      "Environment: Must set PYTHONPATH and PYTHONIOENCODING",
      "Persistence: Listener must stay active in the background"
    ],
    "entry_scene_id": "S_ACT"
  },
  "scenes": [
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script bridge_listener.py để theo dõi thư mục yêu cầu.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Xác nhận chuông báo hoạt động và thông báo cho Anh Lưu.",
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
# Khởi động Bot Telegram (TLS Station)
start /b cmd /c "set PYTHONIOENCODING=utf-8 && set PYTHONPATH=. && python tools/telegram/run_bot.py"
# Khởi động Listener (Chuông báo)
start /b cmd /c "set PYTHONIOENCODING=utf-8 && set PYTHONPATH=. && python tools/bridge/bridge_listener.py"
# Khởi động Stimulator (Bộ gõ hộ đánh thức AI từ xa)
start /b cmd /c "set PYTHONIOENCODING=utf-8 && set PYTHONPATH=. && python tools/bridge/remote_stimulator.py"
```

### 🏁 Scene 2: FINALIZE (Hoàn tất)
- [ ] Báo cáo: "🔔 Hệ thống trực chiến 0đ (Bot Telegram + Listener + Remote Stimulator) đã sẵn sàng!".
- [ ] Nhắc nhở: Giờ đây Anh Lưu có thể dùng lệnh /tổng hợp từ Telegram, hệ thống sẽ tự động 'gõ phím' đánh thức AI trong IDE để xử lý giúp anh!

