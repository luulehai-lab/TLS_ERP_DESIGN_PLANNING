---
description: Cập nhật giá thép hàng ngày và dự báo xu hướng (SSL v2026)
---

<!-- 
FILE: .agents/workflows/update-steel-price.md
CHANGELOG:
- 09:07:00 05/05/2026: [REFACTOR] Nâng cấp sang chuẩn SSL v2026. Chuẩn hóa bộ chỉ số thép Trung Quốc & VN. (Antigravity)
- 09:10:00 05/05/2026: [FIX] Chuẩn hóa SOP: Ép dùng dữ liệu thô để script hệ thống tự sinh báo cáo mẫu chuẩn (Thanh xanh), tránh lỗi hiển thị. (Antigravity)
-->

# 📈 WORKFLOW: Cập Nhật Giá Thép (SSL v2026)

Mục đích: Tự động cập nhật dữ liệu vĩ mô, giá thép Futures/Spot và tin tức thị trường cho Tab Chuyên Môn.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_UPDATE_STEEL_PRICE",
    "workflow_name": "Steel Price Update",
    "workflow_goal": "Collect and analyze global/local steel market data accurately.",
    "expected_inputs": [
      {"name": "market_indicators", "type": "list", "description": "SHFE HRC, Iron Ore, USD/VND, CNY/VND"}
    ],
    "constraints": [
      "China Steel Stocks: ONLY Baosteel, Angang, Masteel",
      "Steel Groups: Tôn lợp, Sàn Deck, Xà gồ (Fixed specs)",
      "Mandatory Section 9: Expert Dialogue integration"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Kiểm tra kết nối và môi trường thực thi UTF-8.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Quét dữ liệu thị trường thực tế qua Robot Scraper V2.4.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Phân tích biến động, đối soát giá Thép Mạ và HRC nền.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi báo cáo Mẫu Lai (Hybrid Template) vào market_discovery.json.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Đồng bộ dữ liệu vào SQLite và ChromaDB (RAG).",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo hoàn tất và chuẩn bị chạy backup.",
      "next_scene_rules": [{"condition": "success", "target": "S_BACKUP"}]
    },
    {
      "scene_id": "S_BACKUP",
      "scene_type": "ACT",
      "scene_goal": "Thực thi backup đa lớp (Snapshot + JSON).",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Kiểm tra)
- [ ] Ép `$env:PYTHONUTF8=1`.
- [ ] Xác nhận đường dẫn `local_data/technical/` sẵn dụng.

### 📊 Scene 2: ACQUIRE (Quét dữ liệu)
// turbo
```powershell
python "tools/reporting/technical_market_scraper.py"
```
*Dữ liệu thu thập: Tỷ giá (Vietcombank), SHFE HRC, Thép Mạ Thượng Hải (镀锌现货), Quặng sắt, Dầu Brent.*

### 🧠 Scene 3: REASON (Analytical Market Logic)
- **Variance Calculation**:
    - `variance = (current_price - prev_price) / prev_price`
    - `trend = "UP" if variance > 0 else "DOWN"`
- **Asset Filtering**:
    - `target_stocks = ["600019.SS", "000898.SZ", "600808.SS"]`
    - `target_specs = {"roofing": [0.3, 0.92], "decking": [1.15, 1.5], "purlin": [1.5, 3.0]}`
- **Expert Insight Logic**:
    - `logic = "Analyze impact of HRC Futures on VN Spot Price"`
    - `tone = "Senior Consultant"`

### 📝 Scene 4: ACT (Data Integrity & Template Injection)
- **Schema Validation**:
    - `mandatory_keys = ["date", "shfe_hrc", "iron_ore", "expert_dialogue", ...]`
    - `assert all(k in output for k in mandatory_keys)`
- **Presentation Protocol**:
    - `use_template = ".agents/templates/tpl_steel_price.md"`
    - `inject_css = True` (wrapped in template)
- **Storage**: `write_json("local_data/technical/market_discovery.json")`

### 🔄 Scene 5: VERIFY (Kích hoạt Seed Script)
- **Mục tiêu**: Chạy script để tự động sinh báo cáo Premium từ template và nạp DB.
// turbo
```powershell
$env:PYTHONUTF8=1; python "tools/database/seed_technical_data.py" --latest
```

### 🏁 Scene 6: FINALIZE (Hoàn tất)
- Nhắc Anh Lưu: "Quay lại Tab **CHUYÊN MÔN** và bấm **Refresh**".
- Ghi nhật ký vào `work_log_task_YYYY_MM_DD.md`.

### 🛡️ Scene 7: BACKUP (Bảo vệ dữ liệu)
// turbo
```powershell
python "tools/database/backup_manager.py"
```
