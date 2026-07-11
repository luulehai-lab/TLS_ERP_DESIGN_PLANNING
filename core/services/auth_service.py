# Tên file: core/services/auth_service.py
# CHỨC NĂNG: Xử lý xác thực Google OAuth2 và chạy local HTTP server nhận callback
# CHANGELOG:
# - 16:38:10 11/07/2026: [UPDATE] test(ke-hoach): add UI unit tests for performer combobox validation (Antigravity)
# - 16:40:16 08/07/2026: [UPDATE] feat(auth): add Google OAuth2 login with department-based access control (Antigravity)
# - 16:35:00 08/07/2026: [FIX] Sửa do_GET hỗ trợ code ở root path và chuyển đóng server sang luồng phụ tránh deadlock socket (Lê Thanh Vân/Antigravity)
# - 14:13:50 08/07/2026: [NEW] chore(db): update database port connection and sync codebase graph (Antigravity)
# - 14:30:00 08/07/2026: [UPDATE] Tối ưu cấu trúc file, trích xuất HTML constants để giảm độ dài hàm đạt chất lượng Clean Code (Lê Thanh Vân/Antigravity)
# - 14:10:00 08/07/2026: [NEW] Khởi tạo service xác thực Google OAuth2 kèm cơ chế Mock Login (Lê Thanh Vân/Antigravity)

import logging
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
import urllib.request
from typing import Any
import config

logger = logging.getLogger(__name__)

# Hằng số giao diện HTML Mock Google Login (Premium Dark Slate Style)
MOCK_LOGIN_HTML: str = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đăng nhập Google - TUAN LONG STEEL</title>
    <style>
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            color: #F8FAFC;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background-color: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 40px;
            width: 400px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
        .logo {
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 1.5px;
            color: #F1F5F9;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 13px;
            color: #38BDF8;
            font-weight: 600;
            margin-bottom: 30px;
        }
        .title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 25px;
            color: #E2E8F0;
        }
        .btn {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #FFFFFF;
            color: #1E293B;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
            margin-bottom: 12px;
            transition: all 0.2s ease-in-out;
            box-sizing: border-box;
            text-decoration: none;
        }
        .btn:hover {
            background-color: #F1F5F9;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .btn-kehoach {
            background-color: #0284C7;
            color: #FFFFFF;
        }
        .btn-kehoach:hover {
            background-color: #0369A1;
        }
        .footer {
            margin-top: 30px;
            font-size: 11px;
            color: #64748B;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">TUAN LONG STEEL</div>
        <div class="subtitle">ERP MOCK GOOGLE AUTHENTICATION</div>
        <div class="title">Chọn tài khoản Google để đăng nhập:</div>
        
        <a href="/callback?code=mock_code_1&email=luu.lehai@gmail.com" class="btn">
            🔑 luu.lehai@gmail.com (Phòng Thiết Kế)
        </a>
        <a href="/callback?code=mock_code_2&email=phongkehoachkythuat25@gmail.com" class="btn btn-kehoach">
            💼 phongkehoachkythuat25@gmail.com (Phòng Kế Hoạch)
        </a>
        <a href="/callback?code=mock_code_3&email=guest@gmail.com" class="btn" style="background-color: #475569; color: white;">
            👤 guest@gmail.com (Khách vãng lai)
        </a>
        
        <div class="footer">
            Chế độ Mock Login tự động kích hoạt do chưa cấu hình Google Client ID trong tệp tin .env
        </div>
    </div>
</body>
</html>
"""

# Hằng số giao diện HTML thông báo đăng nhập thành công
SUCCESS_LOGIN_HTML_TEMPLATE: str = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Đăng nhập thành công</title>
    <style>
        body {{
            font-family: sans-serif;
            background-color: #0F172A;
            color: #F8FAFC;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }}
        .container {{
            background-color: #1E293B;
            border: 1px solid #334155;
            padding: 30px;
            border-radius: 8px;
            max-width: 400px;
        }}
        h1 {{ color: #10B981; font-size: 22px; }}
        p {{ color: #94A3B8; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>✔ Đăng nhập thành công!</h1>
        <p>Chào mừng <strong>{email}</strong>.</p>
        <p>Bạn có thể đóng trình duyệt này và quay lại ứng dụng ERP.</p>
    </div>
</body>
</html>
"""


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handler xử lý các yêu cầu HTTP gửi tới máy chủ callback cục bộ."""

    def log_message(self, format_str: str, *args: Any) -> None:
        """Ghi đè để chuyển log của http.server sang logger hệ thống.

        Args:
            format_str: Chuỗi định dạng log từ BaseHTTPRequestHandler.
            args: Các đối số bổ trợ đi kèm log.
        """
        logger.debug(format_str % args)

    def do_GET(self) -> None:
        """Xử lý yêu cầu HTTP GET."""
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Xử lý đăng nhập nếu nhận được authorization code (hỗ trợ cả / và /callback)
        if "code" in query_params:
            self._handle_callback(query_params)
        elif parsed_url.path == "/":
            if not config.GOOGLE_CLIENT_ID:
                self._serve_mock_login_page()
            else:
                self._send_html_response(
                    "<h1>Giao thức đăng nhập Google OAuth2</h1><p>Vui lòng đăng nhập qua Google.</p>"
                )
        elif parsed_url.path == "/callback":
            self._handle_callback(query_params)
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_mock_login_page(self) -> None:
        """Phục vụ trang HTML Mock Google Login với giao diện Premium Slate."""
        self._send_html_response(MOCK_LOGIN_HTML)

    def _handle_callback(self, query_params: dict[str, list[str]]) -> None:
        """Xử lý endpoint callback khi nhận code từ Google hoặc Mock login.

        Args:
            query_params: Các tham số truy vấn nhận được từ URL.
        """
        code_list = query_params.get("code")
        if not code_list:
            self._send_html_response(
                "<h1>Lỗi xác thực</h1><p>Không nhận được mã code.</p>"
            )
            return

        code = code_list[0]
        email = ""

        if not config.GOOGLE_CLIENT_ID:
            email_list = query_params.get("email")
            if email_list:
                email = email_list[0]
        else:
            email = self._exchange_code_for_email(code)

        if email:
            self.server.authenticated_email = email  # type: ignore
            success_html = SUCCESS_LOGIN_HTML_TEMPLATE.format(email=email)
            self._send_html_response(success_html)
        else:
            self._send_html_response(
                "<h1>Lỗi xác thực</h1><p>Không thể lấy thông tin email từ Google.</p>"
            )

    def _exchange_code_for_email(self, code: str) -> str:
        """Đổi authorization code lấy email người dùng qua Google API.

        Args:
            code: Mã authorization code nhận được từ Google.

        Returns:
            str: Email của người dùng, hoặc chuỗi rỗng nếu lỗi.
        """
        try:
            token_url = "https://oauth2.googleapis.com/token"
            redirect_uri = f"http://localhost:{self.server.server_port}"  # type: ignore

            data = urllib.parse.urlencode(
                {
                    "code": code,
                    "client_id": config.GOOGLE_CLIENT_ID,
                    "client_secret": config.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            ).encode("utf-8")

            req = urllib.request.Request(token_url, data=data)
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                access_token = res_data.get("access_token")

            if not access_token:
                return ""

            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            req_info = urllib.request.Request(userinfo_url)
            req_info.add_header("Authorization", f"Bearer {access_token}")

            with urllib.request.urlopen(req_info) as response_info:
                user_info = json.loads(response_info.read().decode("utf-8"))
                return user_info.get("email", "")

        except Exception as e:
            logger.error(
                "Lỗi khi trao đổi mã lấy token Google: %s", str(e), exc_info=True
            )
            return ""

    def _send_html_response(self, content: str) -> None:
        """Gửi phản hồi HTML chuẩn về trình duyệt.

        Args:
            content: Nội dung HTML.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))


class GoogleAuthServer(HTTPServer):
    """Máy chủ HTTP tùy chỉnh lưu trữ trạng thái email xác thực."""

    def __init__(self, server_address: tuple[str, int], handler_class: Any) -> None:
        """Khởi tạo đối tượng máy chủ GoogleAuthServer.

        Args:
            server_address: Bộ hai tham số IP và Port.
            handler_class: Class RequestHandler kế thừa từ BaseHTTPRequestHandler.
        """
        super().__init__(server_address, handler_class)
        self.authenticated_email: str = ""


class GoogleAuthManager:
    """Manager quản lý toàn bộ vòng đời của server xác thực và OAuth flow."""

    def __init__(self, port: int = 8080) -> None:
        """Khởi tạo đối tượng quản lý xác thực GoogleAuthManager.

        Args:
            port: Port mạng cục bộ lắng nghe callback.
        """
        self.port: int = port
        self.server: GoogleAuthServer | None = None
        self.thread: threading.Thread | None = None
        self._is_running: bool = False

    def start_server(self) -> None:
        """Khởi động local HTTP Server trên một luồng riêng biệt."""
        if self._is_running:
            return

        try:
            self.server = GoogleAuthServer(
                ("localhost", self.port), OAuthCallbackHandler
            )
            self._is_running = True
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            logger.info("Local HTTP Server lắng nghe tại port %d...", self.port)
        except Exception as e:
            logger.error(
                "Không thể khởi động Local HTTP Server tại port %d: %s",
                self.port,
                str(e),
            )
            self._is_running = False

    def _run_server(self) -> None:
        """Vòng lặp chính chạy server."""
        if self.server:
            try:
                self.server.serve_forever()
            except Exception as e:
                logger.debug("Local Server dừng: %s", str(e))

    def get_auth_url(self) -> str:
        """Tạo Google Authorization URL hoặc trả về link local nếu là Mock Mode.

        Returns:
            str: URL dẫn tới trang đăng nhập.
        """
        if not config.GOOGLE_CLIENT_ID:
            return f"http://localhost:{self.port}"

        redirect_uri = f"http://localhost:{self.port}"
        params = {
            "client_id": config.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/userinfo.email",
            "access_type": "online",
            "prompt": "select_account",
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(
            params
        )

    def get_authenticated_email(self) -> str:
        """Lấy email đã đăng nhập thành công từ server.

        Returns:
            str: Email người dùng, hoặc chuỗi rỗng nếu chưa đăng nhập.
        """
        if self.server:
            return self.server.authenticated_email
        return ""

    def shutdown(self) -> None:
        """Dừng local HTTP server một cách an toàn ở background để tránh block UI."""
        if self.server and self._is_running:
            logger.info("Đang dừng Local HTTP Server...")
            self._is_running = False

            server_to_close = self.server
            self.server = None

            def _async_close() -> None:
                """Đóng server và socket ở luồng phụ."""
                try:
                    server_to_close.shutdown()
                    server_to_close.server_close()
                    logger.info("Đã đóng Local HTTP Server thành công ở background.")
                except Exception as ex:
                    logger.error("Lỗi khi đóng server ở background: %s", str(ex))

            threading.Thread(target=_async_close, daemon=True).start()
            self.thread = None
