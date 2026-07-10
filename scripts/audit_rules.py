# Tên file: scripts/audit_rules.py
# CHỨC NĂNG: Khai báo các quy tắc kiểm toán AST đơn lẻ (Clean Code, ranh giới kiến trúc, UI/Backend và CSS/QSS).
# CHANGELOG:
# - 18:28:00 10/07/2026: [NEW] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:45:00 10/07/2026: [NEW] Tách các quy tắc kiểm toán từ scripts/audit_code_quality.py thành module riêng để dễ mở rộng (Lê Thanh Vân/Antigravity)

import ast
import re
from pathlib import Path


class AuditRules:
    """Tập hợp các quy tắc kiểm toán cú pháp tĩnh AST cho dự án."""

    @staticmethod
    def load_changelog_header(file_path: Path) -> tuple[bool, str]:
        """Kiểm tra sự hiện diện của Header Changelog ở 15 dòng đầu file."""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                lines = [f.readline() for _ in range(15)]

            has_file = False
            has_func = False
            has_changelog = False

            for line in lines:
                stripped = line.strip().lower()
                if "tên file:" in stripped or "file:" in stripped:
                    has_file = True
                if "chức năng:" in stripped or "description:" in stripped:
                    has_func = True
                if "changelog:" in stripped:
                    has_changelog = True

            if has_file and has_func and has_changelog:
                return True, "Valid"

            missing = []
            if not has_file:
                missing.append("Tên file")
            if not has_func:
                missing.append("Chức năng")
            if not has_changelog:
                missing.append("Changelog")
            return False, f"Thiếu: {', '.join(missing)}"
        except Exception as e:
            return False, f"Lỗi đọc file: {str(e)}"

    @staticmethod
    def check_type_hints(
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> tuple[bool, list[str]]:
        """Kiểm tra Type Hints của hàm."""
        missing = []
        is_init = node.name == "__init__"

        # 1. Kiểm tra đối số
        args = node.args
        for idx, arg in enumerate(args.args):
            if idx == 0 and arg.arg in {"self", "cls"}:
                continue
            if not arg.annotation:
                missing.append(f"Đối số `{arg.arg}`")

        # 2. Kiểm tra kiểu trả về (trừ __init__)
        if not is_init and not node.returns:
            missing.append("Kiểu trả về (Returns)")

        return len(missing) == 0, missing

    @staticmethod
    def check_docstring_style(
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    ) -> tuple[bool, list[str]]:
        """Kiểm tra Docstring chuẩn Google."""
        doc = ast.get_docstring(node)
        if not doc:
            return False, ["Thiếu Docstring"]

        warnings = []
        stripped_doc = doc.strip()

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_real_args = False
            for idx, arg in enumerate(node.args.args):
                if idx == 0 and arg.arg in {"self", "cls"}:
                    continue
                has_real_args = True
                break

            if has_real_args and "Args:" not in stripped_doc:
                warnings.append("Thiếu phần mô tả đối số 'Args:' trong Docstring")

            is_init = node.name == "__init__"
            if not is_init and "Returns:" not in stripped_doc:
                if node.returns and not (
                    isinstance(node.returns, ast.Constant)
                    and node.returns.value is None
                ):
                    warnings.append(
                        "Thiếu phần mô tả kiểu trả về 'Returns:' trong Docstring"
                    )

        return len(warnings) == 0, warnings

    @staticmethod
    def check_silent_exception(node: ast.Try) -> list[tuple[int, str]]:
        """Kiểm tra xem khối try-except có nuốt lỗi im lặng (silent fail) không."""
        violations = []
        for handler in node.handlers:
            is_generic = False
            if not handler.type:
                is_generic = True
            elif isinstance(handler.type, ast.Name) and handler.type.id in {
                "Exception",
                "BaseException",
            }:
                is_generic = True

            if is_generic:
                body = handler.body
                is_silent = False

                if len(body) == 1:
                    child = body[0]
                    if isinstance(child, ast.Pass) or isinstance(child, ast.Continue):
                        is_silent = True
                    elif (
                        isinstance(child, ast.Expr)
                        and isinstance(child.value, ast.Constant)
                        and child.value.value is None
                    ):
                        is_silent = True

                if is_silent:
                    violations.append(
                        (
                            handler.lineno,
                            "Nuốt lỗi im lặng bằng `pass` hoặc `continue` trong except Exception.",
                        )
                    )
        return violations

    @staticmethod
    def check_import_boundary(
        node: ast.Import | ast.ImportFrom, file_relative_path: Path
    ) -> list[str]:
        """Kiểm tra ranh giới nhập khẩu (Import Boundary) của tầng UI và Core."""
        violations = []
        parts = file_relative_path.parts
        # 1. Kiểm tra ranh giới của tầng UI
        if "ui" in parts:
            forbidden_modules = {
                "docx",
                "openpyxl",
                "sqlite3",
                "google",
                "database_client",
                "app_secrets",
            }

            if isinstance(node, ast.Import):
                for name in node.names:
                    root_module = name.name.split(".")[0]
                    if root_module in forbidden_modules:
                        violations.append(
                            f"UI import trực tiếp thư viện ngoài/backend `{root_module}`. Hãy sử dụng qua core/."
                        )
                    elif name.name.startswith(
                        "core.database_client"
                    ) or name.name.startswith("core.app_secrets"):
                        violations.append(
                            f"UI import trực tiếp module backend `{name.name}`. Hãy sử dụng qua core services/managers."
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_module = node.module.split(".")[0]
                    if root_module in forbidden_modules:
                        violations.append(
                            f"UI import trực tiếp thư viện ngoài/backend `{root_module}`. Hãy sử dụng qua core/."
                        )

                    if node.module == "core":
                        for name in node.names:
                            if name.name in {"database_client", "app_secrets"}:
                                violations.append(
                                    f"UI import trực tiếp module backend `core.{name.name}`. Hãy sử dụng qua core services/managers."
                                )

                    parts_module = node.module.split(".")
                    if (
                        len(parts_module) > 1
                        and parts_module[0] == "core"
                        and parts_module[1] in {"database_client", "app_secrets"}
                    ):
                        violations.append(
                            f"UI import trực tiếp module backend `core.{parts_module[1]}`. Hãy sử dụng qua core services/managers."
                        )

        # 2. Kiểm tra ranh giới của tầng Core (Backend)
        elif "core" in parts:
            forbidden_ui_modules = {"PyQt6", "PyQt5", "PySide6"}
            if isinstance(node, ast.Import):
                for name in node.names:
                    root_module = name.name.split(".")[0]
                    if root_module in forbidden_ui_modules:
                        violations.append(
                            f"Backend Core import trực tiếp thư viện UI `{root_module}`. Vi phạm nguyên tắc UI/Backend Separation."
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_module = node.module.split(".")[0]
                    if root_module in forbidden_ui_modules:
                        violations.append(
                            f"Backend Core import trực tiếp thư viện UI `{root_module}`. Vi phạm nguyên tắc UI/Backend Separation."
                        )
        return violations

    @staticmethod
    def check_print_calls(node: ast.Call) -> bool:
        """Phát hiện các hàm gọi print debug trực tiếp."""
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            return True
        return False

    @staticmethod
    def check_database_queries_in_ui(
        node: ast.AST, file_relative_path: Path
    ) -> list[str]:
        """Phát hiện các truy vấn database trực tiếp hoặc SQL thô trong các file UI."""
        violations = []
        parts = file_relative_path.parts
        if "ui" in parts:
            # 1. Phát hiện chuỗi SQL thô trong các chuỗi hằng số
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value.strip()
                sql_pattern = r"(?i)\b(select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from)\b"
                if re.search(sql_pattern, val):
                    violations.append(
                        f"UI chứa câu lệnh SQL thô trực tiếp: `{val[:50]}...`. Hãy chuyển logic này về core/."
                    )

            # 2. Phát hiện gọi DatabaseClient trực tiếp
            elif isinstance(node, ast.Attribute):
                if node.attr in {
                    "DatabaseClient",
                    "execute_query",
                    "execute_non_query",
                }:
                    violations.append(
                        f"UI gọi trực tiếp phương thức database `{node.attr}`. Hãy sử dụng qua core services/managers."
                    )
        return violations

    @staticmethod
    def check_raw_stylesheet_limits(
        node: ast.Call, file_relative_path: Path
    ) -> list[str]:
        """Kiểm tra độ dài của QSS stylesheet thô trong lệnh setStyleSheet (Tối đa 5 dòng)."""
        violations = []
        parts = file_relative_path.parts
        if "ui" in parts:
            is_set_stylesheet = False
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "setStyleSheet"
            ):
                is_set_stylesheet = True
            elif isinstance(node.func, ast.Name) and node.func.id == "setStyleSheet":
                is_set_stylesheet = True

            if is_set_stylesheet and node.args:
                arg = node.args[0]
                lines_count = 0
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    lines_count = len(arg.value.splitlines())
                elif isinstance(arg, ast.JoinedStr):
                    full_str = ""
                    for val in arg.values:
                        if isinstance(val, ast.Constant) and isinstance(val.value, str):
                            full_str += val.value
                        else:
                            full_str += "\n"
                    lines_count = len(full_str.splitlines())

                if lines_count > 5:
                    violations.append(
                        f"setStyleSheet() thô dài {lines_count} dòng, vượt quá giới hạn 5 dòng. "
                        f"Hãy khai báo tập trung trong `ui/styles/theme.py` (TLSTheme) để chống duplicate CSS."
                    )
        return violations

    @staticmethod
    def check_ui_layout_hardcoding(
        node: ast.Call, file_relative_path: Path
    ) -> list[str]:
        """Phát hiện việc gọi setGeometry, move, resize thô trên các widget con ở UI.

        Args:
            node: Node AST thực hiện cuộc gọi hàm.
            file_relative_path: Đường dẫn tương đối của file đang quét.

        Returns:
            Danh sách các chuỗi mô tả vi phạm.
        """
        violations = []
        parts = file_relative_path.parts
        if "ui" in parts:
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "setGeometry",
                "move",
                "resize",
            }:
                # Kiểm tra đối tượng gọi hàm
                obj = node.func.value
                is_self = False
                if isinstance(obj, ast.Name) and obj.id == "self":
                    is_self = True

                # Nếu không phải self gọi (tức là gọi trên widget con, e.g. self.button.setGeometry)
                if not is_self:
                    violations.append(
                        f"Giao diện gọi .{node.func.attr}() thô trên widget con. "
                        f"Hãy sử dụng các lớp QLayout (QHBoxLayout, QVBoxLayout, QGridLayout) để co giãn tự động."
                    )
        return violations

    @staticmethod
    def check_ui_widget_naming(node: ast.Assign, file_relative_path: Path) -> list[str]:
        """Kiểm tra quy chuẩn đặt tên biến thành viên giao diện (self.xxx) trong UI.

        Args:
            node: Node AST của lệnh gán.
            file_relative_path: Đường dẫn tương đối của file đang quét.

        Returns:
            Danh sách các chuỗi mô tả vi phạm quy chuẩn đặt tên.
        """
        violations = []
        parts = file_relative_path.parts
        if "ui" not in parts:
            return violations

        # Kiểm tra xem vế phải có phải là cuộc gọi khởi tạo Widget không
        if not isinstance(node.value, ast.Call):
            return violations

        # Lấy tên Class của Widget khởi tạo
        widget_class = ""
        func_node = node.value.func
        if isinstance(func_node, ast.Name):
            widget_class = func_node.id
        elif isinstance(func_node, ast.Attribute):
            widget_class = func_node.attr

        # Danh sách ánh xạ Widget class -> tiền tố bắt buộc
        naming_rules = {
            "QPushButton": "btn_",
            "QToolButton": "btn_",
            "QLabel": "lbl_",
            "QLineEdit": "txt_",
            "QTextEdit": "txt_",
            "QPlainTextEdit": "txt_",
            "QComboBox": "cb_",
            "QCheckBox": "cb_",
            "QTableWidget": "tbl_",
            "QListWidget": "lst_",
            "QRadioButton": "rad_",
            "QHBoxLayout": "layout_",
            "QVBoxLayout": "layout_",
            "QGridLayout": "layout_",
            "QGroupBox": "group_",
            "QSplitter": "splitter_",
        }

        if widget_class not in naming_rules:
            return violations

        required_prefix = naming_rules[widget_class]

        # Kiểm tra các mục tiêu gán ở vế trái (thường chỉ có 1 target trong self.xxx = ...)
        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                var_name = target.attr
                if not var_name.startswith(required_prefix):
                    violations.append(
                        f"Widget `{widget_class}` đặt tên biến là `self.{var_name}`. "
                        f"Bắt buộc phải bắt đầu bằng tiền tố `{required_prefix}` để đúng quy chuẩn UI."
                    )
        return violations

    @staticmethod
    def check_ui_blocking_calls(node: ast.Call, file_relative_path: Path) -> list[str]:
        """Phát hiện các cuộc gọi gây chặn luồng chính (blocking calls) trong các file UI.

        Args:
            node: Node AST thực hiện cuộc gọi hàm.
            file_relative_path: Đường dẫn tương đối của file đang quét.

        Returns:
            Danh sách các chuỗi mô tả vi phạm chặn luồng.
        """
        violations = []
        parts = file_relative_path.parts
        if "ui" in parts:
            is_blocking = False
            details = ""

            # 1. Check time.sleep
            if isinstance(node.func, ast.Attribute) and node.func.attr == "sleep":
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "time"
                ):
                    is_blocking = True
                    details = "time.sleep()"
            elif isinstance(node.func, ast.Name) and node.func.id == "sleep":
                is_blocking = True
                details = "sleep()"

            # 2. Check requests.get / post / request
            elif isinstance(node.func, ast.Attribute) and isinstance(
                node.func.value, ast.Name
            ):
                if node.func.value.id == "requests" and node.func.attr in {
                    "get",
                    "post",
                    "delete",
                    "put",
                    "patch",
                    "request",
                }:
                    is_blocking = True
                    details = f"requests.{node.func.attr}()"

            if is_blocking:
                violations.append(
                    f"UI gọi lệnh blocking `{details}` chặn luồng chính. "
                    f"Hãy chuyển các tác vụ tốn thời gian hoặc kết nối mạng ra luồng riêng (QThread / Worker)."
                )
        return violations
