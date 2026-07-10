# Tên file: scripts/graph_parser.py
# CHỨC NĂNG: Phân tích cú pháp AST của tệp tin Python để trích xuất các imports, classes, functions và calls
# CHANGELOG:
# - 18:28:01 10/07/2026: [NEW] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:56:00 10/07/2026: [NEW] Khởi tạo module trích xuất thông tin AST tách từ generate_codebase_graph.py (Lê Thanh Vân/Antigravity)

import ast
from pathlib import Path
from typing import Any


class CodebaseParser(ast.NodeVisitor):
    """Bộ phân tích cú pháp AST của từng file Python để trích xuất các thực thể và mối quan hệ.

    Attributes:
        file_path: Đường dẫn tuyệt đối đến tệp Python.
        project_root: Thư mục gốc của project để tính relative path.
        module_name: Tên module dạng package (ví dụ: core.services.auth_service).
    """

    def __init__(self, file_path: Path, project_root: Path) -> None:
        """Khởi tạo bộ phân tích cú pháp AST.

        Args:
            file_path: Đường dẫn tuyệt đối đến tệp Python.
            project_root: Thư mục gốc của project.
        """
        self.file_path: Path = file_path
        self.project_root: Path = project_root
        relative_path = file_path.relative_to(project_root)
        self.module_name: str = ".".join(relative_path.with_suffix("").parts)

        self.current_class: str | None = None
        self.current_function: str | None = None

        # Dữ liệu trích xuất
        self.imports: list[dict[str, Any]] = []
        self.classes: list[dict[str, Any]] = []
        self.functions: list[dict[str, Any]] = []
        self.calls: list[dict[str, Any]] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Trích xuất import trực tiếp dạng 'import x'.

        Args:
            node: Node AST của lệnh import trực tiếp.
        """
        for alias in node.names:
            self.imports.append(
                {
                    "type": "direct",
                    "name": alias.name,
                    "asname": alias.asname,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Trích xuất import dạng 'from x import y'.

        Args:
            node: Node AST của lệnh from-import.
        """
        if node.module:
            module_name = node.module
            if node.level > 0:
                parts = self.file_path.parent.relative_to(self.project_root).parts
                if node.level <= len(parts):
                    base = ".".join(parts[: len(parts) - node.level + 1])
                    module_name = f"{base}.{module_name}" if base else module_name

            for alias in node.names:
                self.imports.append(
                    {
                        "type": "from",
                        "module": module_name,
                        "name": alias.name,
                        "asname": alias.asname,
                        "line": node.lineno,
                    }
                )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Ghi nhận định nghĩa Class và các Class cha kế thừa.

        Args:
            node: Node AST định nghĩa class.
        """
        class_id = f"{self.module_name}.{node.name}"
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self.visit_Attribute_name(base)}")

        self.classes.append(
            {
                "id": class_id,
                "name": node.name,
                "bases": bases,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
            }
        )

        old_class = self.current_class
        self.current_class = class_id
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Ghi nhận định nghĩa Function/Method.

        Args:
            node: Node AST định nghĩa function/method.
        """
        func_name = node.name
        if self.current_class:
            func_id = f"{self.current_class}.{func_name}"
            parent_type = "class"
            parent_id = self.current_class
        else:
            func_id = f"{self.module_name}.{func_name}"
            parent_type = "module"
            parent_id = self.module_name

        args_hints = {}
        for arg in node.args.args:
            if arg.annotation:
                args_hints[arg.arg] = self.get_annotation_str(arg.annotation)

        return_hint = None
        if node.returns:
            return_hint = self.get_annotation_str(node.returns)

        self.functions.append(
            {
                "id": func_id,
                "name": func_name,
                "parent_id": parent_id,
                "parent_type": parent_type,
                "args": list(args_hints.keys()),
                "args_hints": args_hints,
                "return_hint": return_hint,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
            }
        )

        old_func = self.current_function
        self.current_function = func_id
        self.generic_visit(node)
        self.current_function = old_func

    def visit_Call(self, node: ast.Call) -> None:
        """Ghi nhận cuộc gọi hàm.

        Args:
            node: Node AST thực hiện cuộc gọi hàm.
        """
        call_name = ""
        caller_obj = None

        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr
            caller_obj = self.visit_Attribute_name(node.func.value)

        if self.current_function:
            self.calls.append(
                {
                    "caller": self.current_function,
                    "call_name": call_name,
                    "caller_obj": caller_obj,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)

    def visit_Attribute_name(self, node: ast.AST) -> str:
        """Đệ quy lấy tên đầy đủ của Attribute (e.g. self.takeoff_repo).

        Args:
            node: Node AST thuộc tính.

        Returns:
            Tên đầy đủ của thuộc tính dạng chuỗi.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.visit_Attribute_name(node.value)}.{node.attr}"
        return ""

    def get_annotation_str(self, node: ast.AST) -> str:
        """Chuyển đổi node Type Hint thành chuỗi trực quan.

        Args:
            node: Node AST của kiểu dữ liệu type hint.

        Returns:
            Chuỗi text thể hiện kiểu dữ liệu trực quan.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.visit_Attribute_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            value = self.get_annotation_str(node.value)
            slice_val = self.get_annotation_str(node.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Tuple):
            return f"Tuple[{', '.join(self.get_annotation_str(e) for e in node.elts)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "Any"
