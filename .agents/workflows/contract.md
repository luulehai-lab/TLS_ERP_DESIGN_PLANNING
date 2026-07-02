---
description: Xử lý phân tích Hợp đồng/Phần mềm/Hồ sơ dự án (Verbatim 100% - Phí 0đ)
---
<!--
File: .agents/workflows/contract.md
Description: Quy trình phân tích Hợp đồng/Phụ lục chuyên sâu - Fast-Track (High-Fidelity Markdown).
Changelog:
- 16:45:00 09/06/2026: [UPDATE] Tích hợp công cụ dùng chung tools/data/contract_appendix_analyzer.py vào workflow phân tích JSONL. (Antigravity)
- 16:17:00 09/06/2026: [UPDATE] Đồng bộ schema JSON của analysis.json khớp hoàn toàn với cấu trúc mong đợi của PyQt6 UI (general_info và appendix_summary). (Antigravity)
- 16:45:00 28/03/2026: [UPDATE] Tích hợp Pipeline High-Fidelity Markdown & Verbatim Indexing. (Antigravity)
- 10:55:00 21/03/2026: [UPDATE] Chuyển đổi sang quy trình xử lý 0đ qua Agent Bridge. (Antigravity)
- 15:32:00 31/03/2026: [REFACTOR] Nâng cấp lên hệ thống Fast-Track Automation. (Antigravity)
- 08:28:00 04/04/2026: [FIX] Chuyển ghi analysis.json qua IDE write_to_file + PYTHONUTF8. (Antigravity)
- 08:35:00 08/04/2026: [UPDATE] Chuyển đổi sang High-Fidelity Markdown. (Antigravity)
-->
# Workflow Phân tích Hợp đồng (Contract) - V2026 SSL Supreme

Workflow này dùng để bóc tách dữ liệu hợp đồng chuyên sâu và đồng bộ vào hệ thống quản lý TLS theo chuẩn SSL.

---

## 🤖 SSL REPRESENTATION (Machine-Facing)

```json
{
  "workflow": {
    "workflow_id": "WORKFLOW_CONTRACT_ANALYSIS",
    "workflow_name": "Contract High-Fidelity Digitization",
    "workflow_goal": "Extract 100/100 verbatim data from contracts and sync with App UI/DB.",
    "expected_inputs": [
      {"name": "content", "type": "string", "description": "Raw text or OCR from contract"},
      {"name": "project_key", "type": "string", "description": "Project ID"}
    ],
    "constraints": [
      "Verbatim Extraction: Do NOT summarize numbers or technical specs",
      "Format: Standard 7-item matrix in JSON",
      "Aesthetics: Premium center-aligned header for reports"
    ],
    "entry_scene_id": "S_PREPARE"
  },
  "scenes": [
    {
      "scene_id": "S_PREPARE",
      "scene_type": "PREPARE",
      "scene_goal": "Nhận diện tệp tin và xác định bối cảnh dự án từ Bridge.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACQUIRE"}]
    },
    {
      "scene_id": "S_ACQUIRE",
      "scene_type": "ACQUIRE",
      "scene_goal": "Thu thập nội dung hợp đồng (Bridge-First) và đảm bảo mã hóa UTF-8.",
      "next_scene_rules": [{"condition": "success", "target": "S_REASON"}]
    },
    {
      "scene_id": "S_REASON",
      "scene_type": "REASON",
      "scene_goal": "Bóc tách 7 mục matrix: General, Scope, Value, Payment, Timeline, Technical, Legal.",
      "next_scene_rules": [{"condition": "success", "target": "S_ACT"}]
    },
    {
      "scene_id": "S_ACT",
      "scene_type": "ACT",
      "scene_goal": "Ghi tmp/analysis.json với cấu trúc Diamond Precision (Flat JSON).",
      "next_scene_rules": [{"condition": "success", "target": "S_VERIFY"}]
    },
    {
      "scene_id": "S_VERIFY",
      "scene_type": "VERIFY",
      "scene_goal": "Chạy Bridge Processor để cập nhật DB và giao diện App.",
      "next_scene_rules": [{"condition": "success", "target": "S_FINALIZE"}]
    },
    {
      "scene_id": "S_FINALIZE",
      "scene_type": "FINALIZE",
      "scene_goal": "Báo cáo hoàn tất và ghi nhận vào nhật ký công việc.",
      "next_scene_rules": [{"condition": "success", "target": "END_SUCCESS"}]
    }
  ]
}
```

---

## 🎬 SCENE-LEVEL GUIDELINES

### 🛠️ Scene 1: PREPARE (Nhận diện)
- [ ] Kiểm tra `.gemini/bridge/request.json` để lấy `project_key` và tên file.

### 🛰️ Scene 2: ACQUIRE (Thu thập)
- [ ] Ưu tiên dùng trường `content` trong request. Nếu không có, đọc file vật lý bằng `read_file_content`.
- [ ] **[NEW] Hỗ trợ JSONL**: Nếu tệp đầu vào có đuôi `.jsonl` hoặc dữ liệu trong request là JSONL, Agent phải chạy trực tiếp công cụ `python tools/data/contract_appendix_analyzer.py` để tự động hóa việc đọc dữ liệu, bóc tách thông tin metadata, xây dựng bảng Markdown và tạo file `tmp/analysis.json` theo đúng Schema Diamond chuẩn UI. Tránh tự viết script scratch.

### 🧠 Scene 3: REASON (Technical Matrix Logic)
- **Extraction Protocol**: `DIAMOND_PRECISION_V2026` (Verbatim 100/100).
- **Matrix Mapping**:
    - `target_schema = load(".agents/templates/tpl_contract_analysis.md")`
    - `logic = "Extract 7 mandatory segments from raw content"`
    - `audit = ["Monetary_Values", "Payment_Percentages", "Deadlines"]`
- **Data Integrity**: `assert all(val.is_numeric() for val in currency_fields)`
- **Appendix Rendering**: `appendix_summary = table_transform(raw_tables, format="MARKDOWN")`
- **[NEW] Ánh xạ Phụ lục**: Đối với phụ lục dạng bảng giá trị (như JSONL), các phần điều khoản không có sẵn (như Tiến độ, Thanh toán, Pháp lý) phải được tự động ánh xạ tham chiếu về Hợp đồng gốc (Ví dụ: "Áp dụng theo quy định tại HĐKT gốc số...").

### 💾 Scene 4: ACT (Ghi JSON)
- [ ] Dùng `write_to_file` để ghi `tmp/analysis.json` theo đúng Schema Diamond sau:
```json
{
  "project_key": "{project_key}",
  "is_contract": true,
  "filename": "{filename}",
  "data": {
    "general_info": {
      "so_hop_dong_phu_luc": "Phần text hiển thị Số HĐ hoặc PL",
      "ngay_ky_ket": "DD/MM/YYYY",
      "ben_a": "Tên Bên A",
      "ben_b": "Tên Bên B"
    },
    "scope_content": ["Dòng 1", "Dòng 2"],
    "contract_value": ["Dòng 1", "Dòng 2"],
    "payment_method": ["Dòng 1", "Dòng 2"],
    "timeline": ["Dòng 1", "Dòng 2"],
    "technical_specs": ["Dòng 1", "Dòng 2"],
    "legal_terms": ["Dòng 1", "Dòng 2"],
    "appendix_summary": {
      "summary": "Tóm tắt phụ lục",
      "table_markdown": "Nội dung bảng biểu Markdown (nếu có)"
    }
  }
}
```

### 🔄 Scene 5: VERIFY (Thực thi Bridge)
// turbo
```powershell
$env:PYTHONUTF8="1"; set PYTHONPATH=.; python tools/bridge/bridge_processor.py --analysis_file tmp/analysis.json --auto
```

### 🏁 Scene 6: FINALIZE (Hoàn tất)
- [ ] Kiểm tra phản hồi đã hiện lên Tab Hồ Sơ.
- [ ] Ghi nhật ký vào `docs/work_log_code_YYYY_MM_DD.md` (tag: `[CONTRACT]`).
