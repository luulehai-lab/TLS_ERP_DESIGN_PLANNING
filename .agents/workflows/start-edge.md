---
description: Khởi động trình duyệt Edge ở chế độ Debug để AI kết nối (CDP 9222)
---

# 🚀 Workflow: Start Edge Debug Mode

Workflow này sẽ tự động đóng toàn bộ các cửa sổ Edge hiện tại và khởi động lại Edge với cổng Debug 9222 để em (Antigravity) có thể kết nối và hỗ trợ Anh Lưu.

### 🛠️ Bước 1: Đóng sạch Edge cũ (Dọn dẹp hiện trường)
// turbo
```powershell
taskkill /F /IM msedge.exe /T
```

### 🌐 Bước 2: Khởi động Edge Debug Mode
// turbo
```powershell
start msedge --remote-debugging-port=9222 --remote-allow-origins=*
```

### 🏁 Bước 3: Kiểm tra kết nối
Sau khi Edge mở lên, em sẽ chạy script kiểm tra xem cổng 9222 đã sẵn sàng chưa.
// turbo
```powershell
python tools/rnd/chrome/test_connection.py
```

---
**💡 Ghi chú cho Anh Lưu:** 
Sau khi chạy lệnh này, Anh hãy chọn Profile Anh thường dùng và mở các trang web cần nghiên cứu nhé. Em đã sẵn sàng kết nối! 🫡
