---
description: Tư vấn & Xử lý yêu cầu kỹ thuật tức thời (Bridge-First - Phí 0đ)
---
<!--
File: .agents/workflows/answer.md
Description: Workflow xử lý yêu cầu từ App qua Agent Bridge (0đ).
Changelog:
- 10:55:00 21/03/2026: [UPDATE] Chuyển đổi sang quy trình xử lý thủ công qua IDE để đảm bảo 0VND. (Antigravity)
- 17:45:00 21/03/2026: [STRICT] BẮT BUỘC OCR trực tiếp + CẤM API Key. (Antigravity)
- 17:48:00 21/03/2026: [CLEANUP] Bỏ bước tự động cập nhật Soul Profile (Lưu sẽ tự làm qua App). (Antigravity)
- 12:28:00 23/03/2026: [STRICT] BẮT BUỘC chỉ APPEND (chèn thêm) kết quả vào cuối Task. (Antigravity)
- 10:45:00 28/03/2026: [STRICT] BẮT BUỘC ESCAPE HTML ENTITIES để tránh lỗi hiển thị. (Antigravity)
- 10:45:00 28/03/2026: [STRICT] BẢO TOÀN DỮ LIỆU TUYỆT ĐỐI: Report phải CHI TIẾT HƠN hoặc BẰNG chat. (Antigravity)
- 10:20:00 02/04/2026: [STRICT] QUY TRÌNH 2 BƯỚC: OCR verbatim trước rồi mới phân tích. (Antigravity)
- 15:30:00 04/04/2026: [FIX] Chuyển sang ghi analysis.json qua IDE write_to_file (UTF-8 chuẩn). (Antigravity)
- 11:30:00 06/04/2026: [FIX] Cập nhật quy tắc CHỐNG LẶP DỮ LIỆU. (Antigravity)
- 14:10:00 07/04/2026: [UPDATE] BẮT BUỘC TÁI TẠO BẢNG BIỂU 100/100 (BOQ, Báo giá) và cập nhật dẫn chiếu rules.md. (Antigravity)
- 08:35:00 08/04/2026: [UPDATE] Chuyển đổi sang Markdown Table & Thử nghiệm list Markdown chuẩn. (Antigravity)
- 10:52:00 10/04/2026: [UPDATE] Bổ sung bước 2.2 Đối soát Kỹ thuật (Technical Audit) & Cảnh báo [TECHNICAL WARNING]. (Antigravity)
- 15:26:00 10/04/2026: [UPDATE] Quy tắc định dạng ký hiệu thép (Chuyển '*' sang 'x'). (Antigravity)
-->

# Workflow Xử lý Bridge (Answer) - V2026 SSL Supreme

Workflow này dùng để xử lý các yêu cầu từ App thông qua Agent Bridge theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_BRIDGE_ANSWER",
    "workflow_name": "General Bridge Request Processing",
    "workflow_goal": "Respond to user requests from the App UI with 100/100 accuracy using 0đ Mode.",
    "expected_inputs": [
      {"name": "request_data", "type": "json", "description": "Dữ liệu từ .gemini/bridge/request.json"}
    ],
    "constraints": [
      "Bridge-First: Use request content as Source of Truth",
      "Vision: Sequential OCR of all attached images",
      "Format: Flat JSON output for analysis.json",
      "Aesthetics: Premium Markdown UI"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Đọc bối cảnh từ request.json và rules.md (User Soul).",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Thu thập dữ liệu: OCR Vision cho ảnh, hoặc đọc content từ request.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Xử lý trí tuệ: Đối soát kỹ thuật, phân tích khối lượng và nhận định chuyên gia.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi tmp/analysis.json (Flat JSON) và thực thi Bridge Processor.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Kiểm tra hiển thị trên App và xử lý dọn dẹp lặp (nếu có).",
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
- [ ] Soi `rules.md` để xác định vai trò Anh Lưu (Nhà thầu TLS).
- [ ] Lấy `project_key` và `task_id`.

### 🛰️ Scene 2: ACQUIRE (Bóc tách Vision)
- **BẮT BUỘC**: OCR bản vẽ bằng Vision. Không tóm tắt.
- **Tái tạo bảng**: Vẽ lại 100/100 các bảng BOQ, Báo giá bằng MD Table.

### 🧠 Scene 3: REASON (Phân tích Kỹ sư Trưởng)
- **Technical Audit**: Đối soát mác thép, bu lông với `docs/technical_standards.md`.
- **Warning**: Đưa ra `[TECHNICAL WARNING]` nếu có sai lệch.
- **Tonnage**: Phân tích khối lượng so với Soul dự án.

### 💾 Scene 4: ACT (Đồng bộ)
- [ ] Ghi `tmp/analysis.json` theo đúng Schema bắt buộc sau:
```json
{
  "project_key": "{project_key}",
  "task_id": {task_id},
  "data": "Nội dung Markdown Premium (BẮT BUỘC)",
  "is_contract": false, // BẮT BUỘC: Set false nếu có task_id để đẩy vào Task. Chỉ set true khi CHỈ muốn lưu vào Tab Hồ Sơ.
  "consultation_note": "Ghi chú tư vấn chuyên gia (nếu có)"
}
```

> [!IMPORTANT]
> **LUÔN thực thi lệnh dưới đây TRƯỚC KHI phản hồi Anh Lưu trên IDE** để đảm bảo dữ liệu được ghi vào SQLite/App UI.

// turbo
```powershell
$env:PYTHONUTF8="1"; set PYTHONPATH=.; python tools/bridge/bridge_processor.py --analysis_file tmp/analysis.json --auto
```

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [ANSWER] Trả lời yêu cầu App: {Subject}`.
- [ ] Xác nhận tính nhất quán tri thức.