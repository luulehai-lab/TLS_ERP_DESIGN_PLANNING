# Tên file: scripts/setup_drive_oauth.py
# CHỨC NĂNG: Xác thực tài khoản Google cá nhân và lưu refresh token để tải lên Drive
# CHANGELOG:
# - 17:09:30 14/07/2026: [NEW] feat(drawing-evidence): add project_id, section_name, and notes to release evidence image (Antigravity)
# - 17:05:00 14/07/2026: [NEW] Khởi tạo script cấu hình OAuth2 Drive cá nhân (Antigravity)

import os
import sys
import json
import logging
import webbrowser
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

# Chèn thư mục gốc vào đầu python path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SetupDriveOAuth")

PORT = 8080
REDIRECT_URI = f"http://localhost:{PORT}"
SCOPES = ["https://www.googleapis.com/auth/drive"]

HTML_SUCCESS = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Liên kết Google Drive thành công</title>
    <style>
        body { font-family: sans-serif; background-color: #0F172A; color: #F8FAFC; text-align: center; padding-top: 100px; }
        .card { background-color: #1E293B; border: 1px solid #334155; padding: 40px; border-radius: 8px; display: inline-block; max-width: 500px; }
        h1 { color: #10B981; }
        p { color: #94A3B8; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="card">
        <h1>✔ Liên kết thành công!</h1>
        <p>Ứng dụng đã nhận được quyền truy cập Google Drive của anh.</p>
        <p>Tệp tin cấu hình <strong>drive_token.json</strong> đã được lưu thành công.</p>
        <p>Bây giờ anh có thể đóng tab này và quay lại sử dụng ứng dụng ERP.</p>
    </div>
</body>
</html>
"""


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP Handler xử lý callback từ Google OAuth2."""

    def log_message(self, format_str: str, *args: Any) -> None:
        """Tắt log mặc định của server để tránh rác terminal."""
        pass

    def do_GET(self) -> None:
        """Xử lý request GET từ Google redirect về."""
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if "code" in query_params:
            auth_code = query_params["code"][0]
            logger.info("Da nhan duoc authorization code. Dang trao doi lay token...")

            token_data = exchange_code_for_token(auth_code, REDIRECT_URI)
            if token_data and "refresh_token" in token_data:
                save_token(token_data)
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_SUCCESS.encode("utf-8"))

                # Ra lệnh dừng server sau khi phản hồi xong
                self.server.oauth_success = True
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(
                    "<h1>Lỗi xác thực</h1><p>Không thể đổi mã code lấy token hoặc không có refresh_token.</p>".encode(
                        "utf-8"
                    )
                )
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("<h1>Yêu cầu không hợp lệ</h1>".encode("utf-8"))


def exchange_code_for_token(code: str, redirect_uri: str) -> dict[str, Any] | None:
    """Đổi authorization code lấy access_token và refresh_token.

    Args:
        code: Mã authorization code nhận được từ Google.
        redirect_uri: URI redirect đã khai báo.

    Returns:
        Dictionary chứa token từ Google hoặc None nếu lỗi.
    """
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": code,
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        # Bỏ qua xác thực SSL nếu cần (đồng bộ với auth_service)
        import ssl

        context = ssl._create_unverified_context()

        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(token_url, data=data)
        with urllib.request.urlopen(req, context=context) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except Exception as e:
        logger.error("Loi khi trao doi authorization code: %s", str(e), exc_info=True)
        return None


def save_token(token_data: dict[str, Any]) -> None:
    """Lưu trữ token vào file json cục bộ.

    Args:
        token_data: Dictionary dữ liệu token trả về từ Google.
    """
    token_path = os.path.join(str(config.BASE_DIR), "drive_token.json")
    try:
        with open(token_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=4)
        logger.info("Da luu token tai: %s", token_path)
    except Exception as e:
        logger.error("Loi khi ghi file token: %s", str(e), exc_info=True)


def run_oauth_flow() -> None:
    """Bắt đầu luồng OAuth2 để xin quyền Google Drive."""
    client_id = config.GOOGLE_CLIENT_ID
    if not client_id:
        logger.error("Chua cau hinh GOOGLE_CLIENT_ID trong config/env!")
        return

    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
        params
    )

    logger.info("Khoi dong local server de nhan callback tai port %d...", PORT)
    server = HTTPServer(("localhost", PORT), OAuthCallbackHandler)
    server.oauth_success = False

    logger.info("Dang mo trinh duyet de anh dang nhap Google...")
    webbrowser.open(auth_url)

    # Lắng nghe request cho đến khi thành công hoặc người dùng tắt
    while not server.oauth_success:
        server.handle_request()

    logger.info("Hoan thanh qua trinh lien ket tai khoan!")


if __name__ == "__main__":
    run_oauth_flow()
