---
description: Tự động phân tích logs/app_run.log để tìm lỗi/crash gần nhất và đề xuất kế hoạch sửa lỗi nhanh chóng.
---

# 🛠️ Workflow `/fix` - Tự động Phân tích Log & Đề xuất Sửa lỗi (Fix Bug SSL v2026)

Workflow này giúp tự động hóa việc truy vết lỗi từ tệp log hệ thống `logs/app_run.log`, xác định nguyên nhân gốc rễ và đề xuất phương án xử lý tức thời khi Anh Lưu gõ lệnh `/fix`.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_AUTO_FIX",
    "workflow_name": "Auto Log Fixer",
    "workflow_goal": "Automatically read latest crash logs, analyze traceback, and output implementation plan for the fix.",
    "expected_inputs": [
      {"name": "log_path", "type": "string", "default": "logs/app_run.log", "description": "Đường dẫn file log cần phân tích"}
    ],
    "entry_scene_id": "S_READ_LOG"
  },
  "scenes": [
    {
      "scene_id": "S_READ_LOG",
      "scene_type": "PREPARE",
      "scene_goal": "Đọc 100-200 dòng cuối cùng của file log để tìm các dấu vết ERROR, CRITICAL hoặc Traceback.",
      "next_scene_rules": [
        {"condition": "found_error", "target": "S_ANALYZE_TRACEBACK"},
        {"condition": "no_error", "target": "S_ASK_USER_SYMPTOM"}
      ]
    },
    {
      "scene_id": "S_ANALYZE_TRACEBACK",
      "scene_type": "REASON",
      "scene_goal": "Phân tích stack trace, xác định file nguồn, dòng bị lỗi và nguyên nhân NameError, AttributeError, ImportError, v.v...",
      "next_scene_rules": [{"condition": "success", "target": "S_PROPOSE_FIX_PLAN"}]
    },
    {
      "scene_id": "S_ASK_USER_SYMPTOM",
      "scene_type": "ACQUIRE",
      "scene_goal": "Hỏi Anh Lưu thêm thông tin chi tiết hoặc lỗi cụ thể do log chưa ghi nhận.",
      "next_scene_rules": [{"condition": "provided", "target": "S_PROPOSE_FIX_PLAN"}]
    },
    {
      "scene_id": "S_PROPOSE_FIX_PLAN",
      "scene_type": "ACT",
      "scene_goal": "Lập kế hoạch sửa lỗi chi tiết (implementation_plan.md) theo mô hình SSL và yêu cầu duyệt trước khi code.",
      "next_scene_rules": [{"condition": "approved", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES & INSTRUCTIONS FOR AGENT

### 🔍 Scene 1: PREPARE - Đọc & Lọc Log
- [ ] **Hành động đầu tiên**: Chạy lệnh xem 150 dòng cuối của file log:
  ```bash
  powershell -Command "Get-Content 'logs\app_run.log' -Tail 150 -Encoding UTF8"
  ```
- [ ] Tìm các từ khóa: `Traceback`, `ERROR`, `CRITICAL`, `Exception`, `AttributeError`, `NameError`, `TypeError`.
- [ ] Nếu tìm thấy khối traceback lỗi, đánh dấu trạng thái là `found_error` và lưu trữ nội dung traceback đó.
- [ ] Nếu log sạch sẽ không có lỗi, chuyển sang `S_ASK_USER_SYMPTOM`.

### 🧠 Scene 2: REASON - Phân tích Nguyên nhân
- [ ] Trích xuất các tệp tin liên quan trực tiếp đến lỗi. Ví dụ:
  - File gây lỗi: `core/services/personal/spotify_service.py` dòng 176.
  - Loại lỗi: `NameError: name 'datetime' is not defined`.
- [ ] Sử dụng tool `view_file` để đọc nội dung code quanh dòng bị lỗi để hiểu ngữ cảnh.
- [ ] Xác định phương án sửa lỗi nhanh nhất và ít ảnh hưởng phụ nhất (Surgical Change).

### 💬 Scene 3: ACQUIRE - Hỏi bối cảnh (Nếu log không có lỗi)
- [ ] Giao tiếp lịch sự với Anh Lưu: *"Em kiểm tra 150 dòng log cuối cùng nhưng chưa thấy lỗi hiển thị. Anh cho em biết app bị lỗi ở tính năng nào hoặc có thông báo gì hiện trên màn hình không ạ?"*

### 📋 Scene 4: ACT - Lập kế hoạch sửa lỗi SSL
- [ ] Tạo file [implementation_plan.md](file:///C:/Users/luule/.gemini/antigravity-ide/brain/current-session/implementation_plan.md) chứa:
  - **Mô tả lỗi**: Traceback trích xuất và nguyên nhân.
  - **Giải pháp**: Các file sẽ được sửa đổi (modify/new).
  - **Kế hoạch kiểm chứng**: Viết/Chạy test case để đảm bảo lỗi được sửa và không bị regression.
- [ ] Đặt `RequestFeedback: true` trong ArtifactMetadata của plan để Anh Lưu bấm duyệt trước khi thực thi code.
