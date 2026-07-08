---
description: Đóng gói ứng dụng PyQt6 thành file .exe độc lập phục vụ mục đích phân phối (ERP_TuanLong.exe).
---

<!--
File: .agents/workflows/build-exe.md
Description: Workflow tự động đóng gói ứng dụng PyQt6 bằng PyInstaller thông qua build_exe.py.
CHANGELOG:
- 17:21:00 08/07/2026: [NEW] Khởi tạo workflow build-exe giúp tự động hóa quá trình đóng gói và giải phóng release zip (Lê Thanh Vân/Antigravity)
-->

# 📦 WORKFLOW: ĐÓNG GÓI ỨNG DỤNG THÀNH TỆP EXE ĐỘC LẬP

> [!NOTE]
> Workflow này hỗ trợ Anh Lưu đóng gói ứng dụng PyQt6 (ERP TK-KH TLS) thành một tệp chạy độc lập duy nhất `ERP_TuanLong.exe` (sử dụng PyInstaller) kèm theo tệp cấu hình `.env` động bên cạnh để phân phối đến phòng Thiết kế và Kế hoạch.

---

## 🛠️ 1. Điều Kiện Cần Thiết (Prerequisites)

- Đảm bảo bạn đã cài đặt PyInstaller trong môi trường hiện tại (đã được tự động xác minh: phiên bản 6.17.0+).
- Cấu hình database và OAuth trong file `.env` ở thư mục gốc (nếu muốn nén kèm tệp `.env` hiện tại).

---

## 🚀 2. Thực Thi Đóng Gói Ứng Dụng (Package Application)

Chạy lệnh dưới đây để bắt đầu tiến trình đóng gói tự động. Tiến trình sẽ thực hiện:
1. Dọn dẹp các tệp tin build cũ.
2. Đóng gói ứng dụng PyQt6 sang `dist/ERP_TuanLong.exe` (ẩn cửa sổ console đen).
3. Sao chép tệp cấu hình `.env` vào thư mục `dist/`.
4. Nén toàn bộ gói phát hành thành `dist/ERP_TuanLong_Release.zip`.

// turbo
```powershell
python scripts/build_exe.py
```

---

## 📁 3. Kết Quả Bàn Giao (Outputs)

Sau khi chạy xong, hãy kiểm tra thư mục [dist](file:///d:/CloudStation/CODE/PYTHON_APP/55_ERP_TK_KH_01726/dist) để nhận kết quả:
- **`ERP_TuanLong.exe`**: Tệp chạy ứng dụng chính.
- **`.env`**: Tệp cấu hình biến môi trường kết nối database và Google OAuth.
- **`ERP_TuanLong_Release.zip`**: Gói nén chứa cả hai tệp trên để gửi đi nhanh chóng.
