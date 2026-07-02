---
description: Cập nhật nhật ký công việc (work_log) hàng ngày
---
<!--
File: .agents/workflows/work-log.md
Description: Workflow hỗ trợ AI tự động ghi nhật ký công việc hàng ngày vào thư mục docs/.
CHANGELOG:
- 17:40:00 12/06/2026: [UPDATE] Tự động hóa hoàn toàn: Sử dụng update_work_log.py để cập nhật log thay vì ghi thủ công. (Antigravity)
- 09:40:00 26/03/2026: [NEW] Khởi tạo workflow ghi nhật ký công việc. (Antigravity)
-->

# Workflow Nhật ký Công việc (Work Log) - V2026 SSL Supreme

Workflow này dùng để tự động hóa việc ghi lại các thay đổi và tiến độ công việc vào file nhật ký hàng ngày trong thư mục `docs/` theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_WORK_LOG",
    "workflow_name": "Daily Activity Logging",
    "workflow_goal": "Ensure all activities (Code/Tasks) are documented chronologically and safely.",
    "expected_inputs": [
      {"name": "activity_type", "type": "string", "description": "CODE hoặc TASK"},
      {"name": "summary", "type": "string", "description": "Tóm tắt công việc đã làm"}
    ],
    "constraints": [
      "Read Before Write: Always use view_file before updating",
      "No Overwrite: Must use replace_file_content to append at top",
      "Header Integrity: Maintain the changelog header"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Xác định loại nhật ký (Code/Task) và ngày hiện tại.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Đọc nội dung hiện tại của file nhật ký để tránh ghi đè.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Soạn thảo nội dung nhật ký: Vấn đề -> Giải pháp -> Kết quả -> Tệp ảnh hưởng.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi scripts/update_work_log.py để cập nhật log tự động và chính xác 100%.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Thông báo hoàn tất cho Anh Lưu.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Xác định)
- [ ] Chọn file: `docs/work_log_code_YYYY_MM_DD.md` hoặc `docs/work_log_task_YYYY_MM_DD.md`.

### 🛰️ Scene 2: ACQUIRE (Đọc)
- [ ] **BẮT BUỘC**: Dùng `view_file` đọc nội dung file log. Nếu file chưa tồn tại, tạo mới với header chuẩn.

### 🧠 Scene 3: REASON (Soạn thảo)
- [ ] Ngôn ngữ: Tiếng Việt, xưng hô "em" - "Anh Lưu".
- [ ] **Bắt buộc viết tường tận quá trình làm việc**:
  - Agent cần biên soạn chi tiết quá trình làm việc dưới dạng Markdown (bao gồm: **Vấn đề / Yêu cầu**, **Giải pháp thực hiện**, và **Thực chứng kết quả**).
  - Khuyến khích ghi nội dung chi tiết này ra tệp tạm `scratch/work_log_temp.md` trước khi chạy script để tránh lỗi ký tự đặc biệt hoặc vượt quá giới hạn chiều dài lệnh trong Windows shell.

### 💾 Scene 4: ACT (Ghi log tự động)
- [ ] Chạy lệnh cập nhật log tự động có độ chính xác cao:
  - Nếu chỉ muốn ghi nhận các file thực sự chỉnh sửa cho tác vụ này (tránh kê thừa file rác khác), hãy chỉ định rõ bằng tùy chọn `--files` hoặc dùng `--staged` (chỉ lấy các file đã `git add`).
  - Sử dụng tùy chọn `--details` hoặc `--details-file scratch/work_log_temp.md` để đưa phần mô tả chi tiết quá trình làm việc vào nhật ký.
  - Ví dụ lệnh:
    ```bash
    python scripts/update_work_log.py --task "[Mô tả ngắn gọn tác vụ]" --type "[code|task]" --files "path/to/file1.py,path/to/file2.py" --details-file "scratch/work_log_temp.md"
    ```
- [ ] Script Python sẽ tự động chèn khối log mới định dạng chuẩn lên đầu tệp nhật ký mà không làm mất lịch sử cũ. Sau khi ghi xong, có thể xóa tệp tạm `scratch/work_log_temp.md`.

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Xác nhận file đã được cập nhật thành công.
