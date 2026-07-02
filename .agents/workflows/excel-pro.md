---
description: Siêu công cụ Excel Pro (Pivot, Chart, Format Premium - Phí 0đ)
---
<!-- 
File: .agents/workflows/excel-pro.md
Description: Quy trình sử dụng siêu công cụ Excel (Excel MCP CLI) cho các tác vụ nâng cao.
Changelog:
- 19:15:00 21/04/2026: [NEW] Khởi tạo workflow xử lý Excel chuyên nghiệp (Antigravity)
-->

---
description: Siêu công cụ Excel Pro (Pivot, Chart, Format Premium - Phí 0đ)
---

# Workflow Siêu công cụ Excel (Excel-Pro) - V2026 SSL Supreme

Workflow này dùng để thực hiện các tác vụ Excel nâng cao (Pivot, Chart, Formatting) thông qua Excel MCP CLI theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_EXCEL_PRO_ADVANCED",
    "workflow_name": "Premium Excel Automation",
    "workflow_goal": "Perform complex Excel manipulations (formatting, charting, pivoting) with pixel-perfect accuracy.",
    "expected_inputs": [
      {"name": "file_path", "type": "string", "description": "Đường dẫn file Excel"}
    ],
    "constraints": [
      "Aesthetics: Use Premium Color Palettes (Hex)",
      "Safety: Always close session with --save",
      "Verbatim: Do not overwrite existing data unless requested"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Khởi tạo Session Excel và kiểm tra danh sách Worksheet.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Đọc dữ liệu hiện có (Range values) để xác định vùng làm việc.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Lập kế hoạch thao tác: Chọn Range, định nghĩa Chart, hoặc cấu trúc Pivot.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi lệnh excelcli.exe (Batch Mode nếu > 10 lệnh) và áp dụng định dạng Premium.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Kiểm tra trực quan kết quả và đóng Session an toàn.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo tóm tắt các thay đổi định dạng và biểu đồ.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Khởi tạo)
// turbo
```powershell
# Mở file và lấy sessionId
./tools/excel_pro/excelcli.exe -q session open "[file_path]"
```

### 🧠 Scene 2: REASON (Thiết kế Premium)
- **Formatting**: Ưu tiên `TableStyleMedium2`, Font `Inter` hoặc `Segoe UI`.
- **Colors**: Sử dụng mã Hex (vd: `#4F81BD` cho Header).

### 💾 Scene 3: ACT (Thực thi)
// turbo
```powershell
# Ghi dữ liệu và định dạng
./tools/excel_pro/excelcli.exe -q range set-values --session [ID] --sheet-name "Sheet1" --range-address "A1:B2" --values '[["Mặt hàng", "Khối lượng"], ["Thép H", 150]]'
```

### 🏁 Scene 4: VERIFY & FINALIZE (Hoàn tất)
// turbo
```powershell
# Đóng session BẮT BUỘC
./tools/excel_pro/excelcli.exe -q session close --session [ID] --save
```
- [ ] Ghi nhật ký: `## [EXCEL-PRO] Xử lý Excel nâng cao: {Filename}`.
