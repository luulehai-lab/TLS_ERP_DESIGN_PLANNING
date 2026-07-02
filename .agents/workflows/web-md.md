---
description: Số hóa trang web kỹ thuật sang Markdown Supreme (Kết nối Edge MCP - Verbatim 100/100)
---

# Workflow Số hóa Trang web (Web-MD) - V2026 Edge Supreme

Workflow này dùng để chuyển đổi dữ liệu từ các trang web kỹ thuật sang Markdown Verbatim thông qua kết nối trực tiếp với trình duyệt Edge (Edge MCP) hoặc xử lý Offline.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_WEB_TO_MD_EDGE",
    "workflow_name": "Edge Live Web Digitization",
    "workflow_goal": "Directly capture and transform web content into structured Markdown using Edge Debug Mode.",
    "expected_inputs": [
      {"name": "url", "type": "string", "description": "URL cần số hóa (nếu chưa mở tab)"},
      {"name": "mode", "type": "string", "description": "live (mặc định) hoặc offline"}
    ],
    "constraints": [
      "Verbatim: 100/100 accuracy from source",
      "Format: Supreme Markdown with standard headers",
      "Sync: Automatic enrichment to AI Second Brain"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Đồng bộ kết nối Edge MCP (Port 9222).",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Trích xuất nội dung từ tab Edge đang active hoặc URL chỉ định.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Kiểm tra tính Verbatim và làm sạch định dạng Markdown.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Lưu file MASTER.md, làm giàu tri thức và đồng bộ bộ não AI.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo kết quả và ghi nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Edge Sync)
- [ ] Chạy `/start-edge` nếu Edge chưa ở chế độ Debug.
- [ ] Kiểm tra kết nối: `python tools/rnd/chrome/test_connection.py`

### 🛰️ Scene 2: ACQUIRE (Trích xuất Live)
Sử dụng công cụ Edge MCP để bóc tách tab hiện tại:
// turbo
```powershell
python "tools/ocr/web_to_md_edge.py"
```
*Ghi chú: Nếu dùng chế độ Offline, hãy chạy `python "tools/ocr/web_to_md_offline.py" "[folder_path]"`.*

### 🧠 Scene 3: REASON (Kiểm soát chất lượng)
- **Verbatim Audit**: Đối soát nội dung Markdown với trang web gốc. Không thêm bớt thông tin kỹ thuật.
- **Header Check**: Đảm bảo có header `# 🛡️ HỒ SƠ KỸ THUẬT` và thông tin nguồn.

### 💾 Scene 4: ACT (Lưu & Sync)
- **Path**: Lưu vào `docs/technical_specs/web_digitized/{product_name}/`.
- **Sync**: Tự động gọi `sync_supreme_knowledge.py` (đã tích hợp trong script `web_to_md_edge.py`).

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Thông báo cho Anh Lưu vị trí file MASTER.md.
- [ ] Ghi nhật ký: `## [WEB-MD] Số hóa trang web: {Product_Name} (Edge MCP Mode)`.

---
**💡 Mẹo cho Anh Lưu:** 
Anh chỉ cần mở tab cần lấy dữ liệu trên Edge, sau đó gõ `/web-md`. Em sẽ tự động "hút" toàn bộ kiến thức về máy cho Anh! 🫡
