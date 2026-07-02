---
description: Xử lý làm giàu tri thức Kỹ thuật (Enrichment) cho tệp tin dựa trên con số thực chứng (0đ Mode)
---
<!--
File: .agents/workflows/file-enrichment.md
Description: Workflow làm giàu dữ liệu kỹ thuật và phản xạ 0đ (Supreme Enrichment) theo chuẩn SSL v2026.
Changelog:
- 11:20:00 05/05/2026: [REFACTOR] Nâng cấp sang chuẩn SSL v2026. Chuẩn hóa quy trình bóc tách dải năng lực. (Antigravity)
-->

# Workflow Làm giàu Tri thức (File-Enrichment) - V2026 SSL Supreme

Workflow này dùng để biến dữ liệu thô (Excel/PDF/MD) thành "Linh hồn Kỹ thuật" cho RAG và AI tư vấn theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_FILE_ENRICHMENT",
    "workflow_name": "Supreme Technical Enrichment",
    "workflow_goal": "Synthesize raw data into high-value engineering insights (Summary, Warnings, Range) for the knowledge base.",
    "expected_inputs": [
      {"name": "source_file", "type": "string", "description": "Tệp tin nguồn đã số hóa"},
      {"name": "db_records", "type": "list", "description": "Dữ liệu thực tế từ SQLite"}
    ],
    "constraints": [
      "No Hallucination: Insights must be backed by DB numbers",
      "Negative Reflex: Explicitly state what the data does NOT cover",
      "0đ Mode: No external API calls during synthesis"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Xác định tệp tin và trích xuất thống kê mật độ (Density) từ DB.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Thu thập quy luật dữ liệu: Dải biên quy cách, tỷ lệ phổ biến, các điểm đột biến.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Soạn thảo Chú giải Kỹ thuật (Technical Synthesis) và Phản xạ Phủ định.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Cập nhật file_semantic_registry, ChromaDB và KNOWLEDGE_SYNTHESIS.md.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo hoàn tất và ghi nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Soi dữ liệu)
- [ ] Dùng Python script để quét DB lấy dải Min/Max của quy cách (D, t, W).

### 🛰️ Scene 2: ACQUIRE (Tìm quy luật)
- [ ] Xác định dải năng lực thực tế (vd: Thép tấm Q355 từ 6mm đến 40mm).
- [ ] Tìm các thông số bất thường (Anomalies).

### 🧠 Scene 3: REASON (Viết Chú giải)
- **Summary**: Phải chứa "Dải năng lực chốt".
- **Phản xạ Phủ định**: Ghi rõ những gì **KHÔNG** làm (vd: Không có hàng nhập khẩu, không có mác Q355D).
- **Warning**: Ghi chú các mục `[TECHNICAL WARNING]`.

### 💾 Scene 4: ACT (Đồng bộ tri thức)
// turbo
```powershell
# Cập nhật registry và ChromaDB
python "tools/maintenance/sync_supreme_metadata.py"
# Cập nhật KNOWLEDGE_SYNTHESIS.md (Tuân thủ CHỐNG TRUNCATION)
python "tools/maintenance/sync_supreme_knowledge.py"
```

### 🏁 Scene 5: FINALIZE (Hoàn tất)
- [ ] Ghi nhật ký vào `docs/work_log_task_YYYY_MM_DD.md`.
- [ ] Tag: `## [ENRICH] Làm giàu tri thức: {Filename}`.
