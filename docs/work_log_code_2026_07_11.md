# 📝 NHẬT KÝ CODE - 11/07/2026

---

## [ERP_TK_KH] feat(report): Triển khai Module Báo cáo & Thống kê trực quan (18:15)

### Mô tả

- Thiết kế và triển khai tab Báo cáo Thống kê tiến độ bản vẽ (BaoCaoView) với 4 biểu đồ vector PyQt6-Charts.
- Tích hợp cơ chế fallback tự động: chuyển sang bảng thống kê + QProgressBar khi thiếu QtCharts.
- Backend report_service.py cung cấp 4 API thống kê: trạng thái, hạng mục, năng suất kỹ sư, timeline.
- Phân quyền động qua get_staff_role() thay vì hardcoded email.

### Files đã thay đổi

- `core/services/report_service.py` — [NEW] Backend thống kê tiến độ bản vẽ
- `ui/views/bao_cao_view.py` — [NEW] Giao diện Tab Báo cáo với Charts/Fallback
- `tests/test_report_service.py` — [NEW] Unit test phân quyền báo cáo (5 tests)
- `ui/header.py` — [UPDATE] Thêm nút tab Báo cáo
- `ui/main_window.py` — [UPDATE] Nhúng BaoCaoView vào content stack
- `core/services/project_service.py` — [UPDATE] Thêm hàm list_active_projects_safe()

---

## [ERP_TK_KH] fix(report): Sửa lỗi combobox trống và thông báo sai ngữ cảnh (18:36)

### Mô tả

- Sửa lỗi combobox chọn dự án trống (thiếu self.reload_projects() trong _init_ui).
- Sửa typo `self.grid_layout` → `self.layout_grid` gây crash AttributeError.
- Thay phân quyền hardcoded email bằng get_staff_role() check vai trò động từ DB.
- Đổi thông báo empty state từ "Không tìm thấy dữ liệu phù hợp với quyền hạn" → "Chưa có dữ liệu bản vẽ để thống kê".

### Files đã thay đổi

- `ui/views/bao_cao_view.py` — [FIX] Sửa 4 lỗi combobox/typo/phân quyền/thông báo

---

## [ERP_TK_KH] fix(logging): Thêm sys.excepthook toàn cục (18:40)

### Mô tả

- Thêm `sys.excepthook` vào main.py để bắt mọi unhandled exception trong PyQt6 event loop.
- Trước đó, lỗi runtime trong slot/callback PyQt6 chỉ in ra stderr mà không ghi vào app_run.log.
- Bọc thêm try/except cho _on_data_loaded trong BaoCaoView.

### Files đã thay đổi

- `main.py` — [FIX] Thêm _global_exception_hook ghi mọi lỗi vào log file
- `ui/views/bao_cao_view.py` — [FIX] Bọc try/except cho callback render biểu đồ

### Kết quả kiểm thử

- ✅ 32/32 tests PASSED
- ✅ Ruff format & lint: All checks passed
