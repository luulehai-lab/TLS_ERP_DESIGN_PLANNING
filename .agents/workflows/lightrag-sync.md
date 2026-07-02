---
description: Đồng bộ hóa & Xây dựng Đồ thị Tri thức LightRAG cho Dự án (LightRAG Sync)
---
<!--
File: .agents/workflows/lightrag-sync.md
Description: Workflow hỗ trợ tự động đồng bộ hóa tri thức và xây dựng đồ thị tri thức lai LightRAG cho một dự án cụ thể.
Changelog:
- 14:26:00 18/05/2026: [NEW] Khởi tạo workflow đồng bộ tri thức LightRAG cho mọi dự án của Anh Lưu. (Antigravity)
-->

# Workflow Đồng bộ Đồ thị Tri thức LightRAG (LightRAG Sync) - V2026 SSL Supreme

Workflow này dùng để đồng bộ toàn bộ dữ liệu (Tasks, Chats, Documents, Souls) của một dự án cụ thể từ SQLite vào cơ sở dữ liệu đồ thị tri thức lai **LightRAG**, tối ưu hóa truy vấn thông minh và vẽ đồ thị Pyvis trực quan.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_LIGHTRAG_SYNC",
    "workflow_name": "Project Knowledge Graph Ingestion",
    "workflow_goal": "Ingest all project logs and documents into the LightRAG hybrid database and generate a Pyvis interactive graph.",
    "expected_inputs": [
      {"name": "project_key", "type": "string", "description": "Tên mã dự án (ví dụ: Z_CÁ NHÂN, VIỆC CHUNG, DONGHUI...)"},
      {"name": "clean_build", "type": "boolean", "description": "Xóa sạch làm lại từ đầu (mặc định: false)"}
    ],
    "constraints": [
      "Zero Data Loss: Ensure SQLite transactions are committed before sync",
      "Dynamic Route: Adapt extraction based on project_key profile",
      "Interactive Update: Pyvis HTML must be refreshed on UI completion"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Nhận diện mã dự án (project_key), kiểm tra thư mục lưu trữ đích tại local_data/lightrag/.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Đọc và gom toàn bộ tasks, documents ngoài và hồ sơ linh hồn dự án từ SQLite.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Thực thi script sync_project_lightrag.py để nạp dữ liệu và xây dựng đồ thị.",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Chạy truy vấn kiểm chứng (aquery) để xác nhận hệ thống RAG phản hồi hoàn hảo.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Thông báo hoàn thành cho Anh Lưu, làm mới Pyvis Đồ thị và ghi nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Xác định)
- [ ] Chọn `project_key` cần đồng bộ (Mặc định: `Z_CÁ NHÂN`).
- [ ] Xác định thư mục lưu trữ: `local_data/lightrag/[PROJECT_KEY]/`.

### 🛰️ Scene 2: ACQUIRE (Quét tri thức)
- [ ] Kiểm tra các file hồ sơ linh hồn tại `local_data/profiles/[PROJECT_KEY].md`.
- [ ] Đối soát số lượng task thuộc dự án trong cơ sở dữ liệu SQLite.

### 💾 Scene 3: ACT (Đồng bộ đồ thị)
// turbo
```powershell
python "tools/lightrag/sync_project_lightrag.py" --project "[PROJECT_KEY]"
```
*(Nếu cần xóa làm lại sạch sẽ từ đầu, thêm tham số `--clean` vào câu lệnh)*

### 🔍 Scene 4: VERIFY (Kiểm chứng)
- [ ] Đặt một câu hỏi tra cứu tri thức ngẫu nhiên thuộc dự án để kiểm tra khả năng trả lời lai (Hybrid RAG) của LightRAG.

### 🏁 Scene 5: FINALIZE (Báo cáo)
- [ ] Ghi nhật ký công việc mã nguồn: `## [LIGHTRAG_SYNC] Đồng bộ thành công Đồ thị Tri thức dự án: {PROJECT_KEY}`.
- [ ] Cập nhật tệp Pyvis HTML để hiển thị visual đồ thị mới trên Tab dự án của UI PyQt6.
