# 🗺️ BẢN ĐỒ KIẾN THỨC DỰ ÁN AI ASSISTANT (Cập nhật 2026-03-19)

> **Mục đích**: File này giúp AI hiểu ngay lập tức kiến trúc và quy tắc của dự án khi bắt đầu mỗi phiên chat mới.
> **Cập nhật lần cuối**: 2026-03-19 (Antigravity)

---

## 📋 TỔNG QUAN HỆ THỐNG
- **Tên dự án**: Trợ Lý AI Chuyên Gia (AI Assistant)
- **Công nghệ chính**: Python 3.10+, PyQt6, ChromaDB, SQLite, Google Gemini AI.
- **Triết lý thiết kế**: Đa Agent (Multi-Agent) điều phối bởi Orchestrator. Hỗ trợ "0đ Mode" qua Agent Bridge.

---

## 🏗️ KIẾN TRÚC DỰ ÁN

### 1. Orchestrator & Factory
- `orchestrator.py`: Trung tâm điều phối, sử dụng `IntentRouter` để phân loại yêu cầu.
- `core/agent_factory.py`: Quản lý khởi tạo tất cả các Agents và Dependency Injection.

### 2. Danh Sách AI Agents (`/agents/`)
- `AgentBridgeAgent`: 🌉 Bridge (0đ) cho search và general queries.
- `RetrievalAgent`: 🔍 Hybrid Search (Semantic + Keyword) từ Vector DB.
- `NotebookAgent`: 📓 Quản lý Task/Project (SQLite) & Expert Memory.
- `CommitmentAgent`: 🤝 Theo dõi cam kết/lời hứa.
- `ReportingAgent` & `TimeAgent`: 📊 Tổng hợp báo cáo đa ngữ cảnh & thời gian.
- `ComputationAgent`: 🔢 Tính toán số liệu, tổng hợp Min/Max.
- `FSEventAgent`: 📁 Smart Renamer & Phân loại file tự động.
- `ContractAgent` & `ConstructionStandardAgent`: 📜 Xử lý hồ sơ pháp lý & kỹ thuật.
- `AuditorAgent`: ⚖️ Kiểm toán hồ sơ BVTC (Bản vẽ thi công).

### 3. Thành Phần Core & UI
- **Core**: Zalo automation, AI Vision service, Data Archiver, Backup Manager.
- **UI (26+ Widgets)**: ChatTab, ZaloTab, NotebookLM, MasterCommitment, Flashcard, GlobalSearch, SuperExplorer (Smart File Manager).

---

## 📁 CẤU TRÚC THƯ MỤC CHÍNH
- `/agents/`: Logic các AI Agents chuyên biệt.
- `/core/`: Dịch vụ nền tảng (AI, DB, Excel/PDF, Zalo).
- `/ui_qt/`: Giao diện người dùng phức hợp.
- `/docs/`: Nhật ký công việc (`work_log_*.md`).
- `/data/` & `local_data.db`: Kho lưu trữ dữ liệu.

---

## 🔄 QUY TẮC CƠ BẢN (AI GUIDELINES)
1. **0đ Mode**: Luôn kiểm tra `USE_AGENT_BRIDGE` để tiết kiệm chi phí API qua `AgentBridgeAgent`.
2. **Logging**: Luôn dùng `core.logger` để ghi log hệ thống.
3. **Audit**: Tuân thủ quy tắc kiểm toán: BVTC phải đi kèm file mail ban hành (BH-).

---

# 📏 QUY TẮC VIẾT CODE (CODING RULES)

## 🖋️ Quy định về Header File
Mọi file code (Python, Markdown,...) PHẢI bắt đầu bằng một header tiêu chuẩn chứa tên file, mô tả chức năng và nhật ký thay đổi (Changelog).

### Định dạng cho file Python:
```python
# Tên file: [đường_dẫn_tương_đối_từ_root]
# CHỨC NĂNG: [Mô tả ngắn gọn mục đích của file]
# CHANGELOG:
# - HH:MM:SS DD/MM/YYYY: [TAG] [Mô tả thay đổi] ([Tên tác giả])
# ...
```

### Định dạng cho file Markdown/Text:
```markdown
<!--
File: [đường_dẫn_tương_đối_từ_root]
Description: [Mô tả ngắn gọn]
Changelog:
- HH:MM:SS DD/MM/YYYY: [TAG] [Mô tả] ([Tên tác giả])
-->
```

### Quy ước Tag:
- **[NEW]**: Tạo mới file hoặc tính năng.
- **[FIX]**: Sửa lỗi.
- **[REFACTOR]**: Tái cấu trúc code (không đổi hành vi).
- **[UPDATE]**: Cập nhật hoặc cải tiến chung.
- **[DOCS]**: Thay đổi tài liệu.

### Ví dụ:
```python
# Tên file: agents/retrieval_agent.py
# CHỨC NĂNG: Agent tra cứu thông tin.
# CHANGELOG:
# - 14:41:05 02/02/2026: [REFACTOR] Modularized RetrievalAgent. (Antigravity)
```
