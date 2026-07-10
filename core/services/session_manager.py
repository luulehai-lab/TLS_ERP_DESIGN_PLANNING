# Tên file: core/services/session_manager.py
# CHỨC NĂNG: Quản lý phiên đăng nhập (Session) của người dùng qua file JSON cục bộ
# CHANGELOG:
# - 12:35:53 10/07/2026: [NEW] fix(ui): convert database UTC time representation to GMT+7 local time for display (Antigravity)
# - 12:35:00 10/07/2026: [NEW] Khởi tạo SessionManager quản lý tự động đăng nhập (Lê Thanh Vân/Antigravity)

import json
import logging
from typing import Any
from config import BASE_DIR

logger = logging.getLogger(__name__)
SESSION_FILE = BASE_DIR / ".session.json"


class SessionManager:
    """Bộ quản lý phiên đăng nhập của người dùng.

    Lưu trữ thông tin email và phòng ban vào file JSON cục bộ để hỗ trợ
    tính năng tự động đăng nhập khi khởi chạy ứng dụng.
    """

    @staticmethod
    def save_session(email: str, department: str) -> bool:
        """Lưu thông tin phiên đăng nhập vào tệp tin cục bộ.

        Args:
            email: Địa chỉ email người dùng đã đăng nhập thành công.
            department: Phòng ban tương ứng của người dùng.

        Returns:
            bool: True nếu lưu thành công, ngược lại False.
        """
        try:
            data = {
                "email": email,
                "department": department,
            }
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info("Đã lưu phiên đăng nhập cho email: %s", email)
            return True
        except Exception as e:
            logger.error("Lỗi khi lưu tệp phiên đăng nhập: %s", str(e), exc_info=True)
            return False

    @staticmethod
    def load_session() -> dict[str, str] | None:
        """Tải thông tin phiên đăng nhập đã lưu từ tệp tin cục bộ.

        Returns:
            dict[str, str] | None: Dictionary chứa 'email' và 'department'
            nếu tồn tại phiên hợp lệ, ngược lại trả về None.
        """
        try:
            if not SESSION_FILE.exists():
                return None

            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            email = data.get("email", "")
            department = data.get("department", "")

            if email and department:
                return {"email": email, "department": department}
            return None
        except Exception as e:
            logger.error("Lỗi khi tải tệp phiên đăng nhập: %s", str(e), exc_info=True)
            return None

    @staticmethod
    def clear_session() -> bool:
        """Xóa thông tin phiên đăng nhập (khi người dùng đăng xuất).

        Returns:
            bool: True nếu xóa thành công (hoặc file không tồn tại), ngược lại False.
        """
        try:
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
                logger.info("Đã xóa tệp phiên đăng nhập (Đăng xuất thành công).")
            return True
        except Exception as e:
            logger.error("Lỗi khi xóa tệp phiên đăng nhập: %s", str(e), exc_info=True)
            return False
