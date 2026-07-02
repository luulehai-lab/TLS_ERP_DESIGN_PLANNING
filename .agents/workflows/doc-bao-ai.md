---
description: Đọc báo tin tức AI từ các nguồn RSS quốc tế và tóm tắt chuyên sâu (Supreme V3)
---

<!-- 
FILE: .agents/workflows/doc-bao-ai.md
CHANGELOG:
- 09:05:00 05/05/2026: [REFACTOR] Nâng cấp sang chuẩn SSL v2026. Tích hợp kịch bản Scenes và quy tắc Anti-Lag. (Antigravity)
- 16:45:00 09/05/2026: [UPDATE] Cập nhật toàn diện sang chuẩn Supreme V3 (Tự động hóa 100% bằng automate).
- 15:15:00 11/05/2026: [UPDATE] V7.9: Tự động hóa hoàn toàn 100% quy trình nạp và biên tập (Senior Polish). (Antigravity)
-->

# 📰 WORKFLOW: Đọc Báo AI Chuyên Sâu (Supreme V3)

Mục đích: Quét, dịch thô toàn văn bằng sức mạnh máy, và AI chỉ đóng vai trò Tổng Biên Tập (Senior Polish) để rút ra các insight đắt giá nhất.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_DOC_BAO_AI_V3",
    "workflow_name": "AI News Digest Supreme",
    "workflow_goal": "Execute the fully automated A-Z news pipeline and apply Senior Polish to top articles.",
    "expected_inputs": [],
    "constraints": [
      "NO Manual steps for Fetching/Translating.",
      "Must rely on news_workflow_manager.py automate"
    ],
    "entry_scene_id": "S_AUTOMATE_AZ"
  },
  "scenes": [
    {
      "scene_id": "S_AUTOMATE_AZ",
      "scene_type": "ACT",
      "scene_goal": "Chạy toàn bộ quy trình săn tin, hút toàn văn, dịch tự động và đẩy lên App.",
      "next_scene_rules": [{"condition": "success", "target": "S_SENIOR_POLISH"}]
    },
    {
      "scene_id": "S_SENIOR_POLISH",
      "scene_type": "REASON",
      "scene_goal": "Đóng vai Tổng Biên Tập: Đọc news_discovery.json, chọn ra 3-5 bài đắt giá nhất để viết Highlights và Senior Editorial.",
      "next_scene_rules": [{"condition": "success", "target": "S_SYNC_FINAL"}]
    },
    {
      "scene_id": "S_SYNC_FINAL",
      "scene_type": "ACT",
      "scene_goal": "Đồng bộ lại database với các bài đã được Polish.",
      "next_scene_rules": [{"condition": "success", "target": "S_BACKUP"}]
    },
    {
      "scene_id": "S_BACKUP",
      "scene_type": "ACT",
      "scene_goal": "Thực thi backup an toàn.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🚀 Scene 1: AUTOMATE A-Z (Sức mạnh của Máy)
// turbo
```powershell
python "tools/reporting/news_workflow_manager.py" automate
```
*Lưu ý: Lệnh này sẽ tự động chạy toàn bộ quy trình: `Fetch` -> `Split` -> `Enrich (Browser Translate)` -> `Senior Polish` -> `Merge` -> `Sync`. Mọi thứ sẽ xong 100% không cần can thiệp.*

### 🛡️ Scene 2: BACKUP (Bảo vệ dữ liệu)
// turbo
```powershell
python "tools/database/backup_manager.py"
```

### 🏁 Hoàn tất:
- Thông báo cho Anh Lưu: "Quá trình săn tin và Biên tập tin AI (Senior Polish) đã hoàn tất 100%. Mời Anh mở App thưởng thức!"

