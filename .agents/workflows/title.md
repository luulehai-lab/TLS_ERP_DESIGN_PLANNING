---
description: Sử dụng Agent gợi ý tiêu đề task súc tích từ chat log
---
# Workflow Đặt tên tiêu đề (Title) - V2026 SSL Supreme

Workflow này dùng để gợi ý và tối ưu hóa tiêu đề công việc dựa trên nội dung chat log từ Dialog F12 bằng cơ chế Agent Bridge.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_TITLE_SUGGESTION",
    "workflow_name": "Task Title Suggestion",
    "workflow_goal": "Automatically suggest a concise title from the chat log using the Agent's reasoning.",
    "expected_inputs": [
      {"name": "request_file", "type": "string", "description": "Đường dẫn file .gemini/bridge/request.json"}
    ],
    "constraints": [
      "Must follow suggest_prompts.py instructions strictly",
      "Format: [Đối tượng chính/Vật tư]_[Nội dung chính/Trạng thái/Lịch giao]_[Hành động/Chủ thể tương tác]",
      "Output: Only short Vietnamese string in title field of response.json"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Đọc nội dung chat log từ file .gemini/bridge/request.json.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Áp dụng System Instruction từ utils/suggest_prompts.py để gợi ý tiêu đề.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi nhận tiêu đề được gợi ý vào file .gemini/bridge/response.json.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Hiển thị thông báo và ghi nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Bối cảnh)
- **Hành động**: Đọc file `.gemini/bridge/request.json` bằng công cụ `view_file`.
- **Ràng buộc**: Trích xuất trường `text` (nội dung chat log), `category` (hạng mục hiện tại) và `timestamp` của yêu cầu.

### 🧠 Scene 2: REASON (Gợi ý tiêu đề)
- **Hành động**: Áp dụng tri thức từ [suggest_prompts.py](file:///d:/CloudStation/CODE/AI_ASSISTANT/ZZZ.DANG%20TEST/utils/suggest_prompts.py) để gợi ý một tiêu đề súc tích.
- **Quy tắc**:
  - Dạng tiếng Việt cực kỳ súc tích (dưới 15 từ).
  - Định dạng: `[Đối tượng chính/Vật tư]_[Nội dung chính/Trạng thái/Lịch giao]_[Hành động/Chủ thể tương tác]`.
  - KHÔNG chứa ký tự tiếng Trung hoặc từ ví dụ mẫu (Alpha, Beta, v.v.).
  - **Ràng buộc lọc trùng lặp hạng mục và dự án (Deduplication constraint)**:
    - Nếu trường `category` có dữ liệu và không trống (ví dụ: 'NHÁNH_PHỤ_Y6'): AI tuyệt đối không lặp lại các thực thể hay từ ngữ đã có trong tên hạng mục (ví dụ: không dùng lại 'cầu ống nhánh Y6', 'Y6') trong tiêu đề gợi ý để tránh trùng lặp khi nối chuỗi.
    - Nếu trường `project_names` có dữ liệu: AI tuyệt đối không lặp lại các từ khóa, mã dự án hoặc tên riêng của dự án đó (ví dụ: không dùng lại từ 'Đức Giang' hoặc 'S13' nếu `project_names` chứa 'S13', 'Đức Giang') trong tiêu đề gợi ý.
    - Tập trung vào phần nội dung thực tế còn lại (ví dụ: 'bản kê tôn bao che_Lưu gửi thư mục ban hành 05-03_Linh nhắn Lưu').
    - Nếu trường `category` trống hoặc chưa phân nhóm: Đưa đối tượng chính vào đầu tiêu đề để giữ ngữ cảnh (ví dụ: 'Cầu ống nhánh Y6_bản vẽ phê duyệt_Anh Thuận nhắn Hà').

### 💾 Scene 3: ACT (Ghi kết quả)
- **Hành động**: Tạo file `.gemini/bridge/response.json` bằng công cụ `write_to_file`.
- **Nội dung JSON**:
```json
{
  "type": "SUGGEST_TITLE",
  "title": "{Tiêu đề gợi ý}",
  "timestamp": {timestamp}
}
```

### 🏁 Scene 4: FINALIZE (Hoàn tất)
- **Hành động**: Báo cáo tiêu đề gợi ý lên khung Chat IDE để Anh Lưu theo dõi.
- **Nhật ký**: Chạy lệnh ghi nhật ký công việc:
```powershell
python scripts/update_work_log.py --task "Gợi ý tiêu đề task F12 qua Agent AI: {Tiêu đề gợi ý}" --type task
```
