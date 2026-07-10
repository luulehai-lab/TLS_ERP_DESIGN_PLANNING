# Tên file: scripts/audit_code_quality.py
# CHỨC NĂNG: Phân tích cú pháp AST tự động kiểm tra Clean Code, Type Hints, Docstrings và Ranh giới kiến trúc (Orchestrator).
# CHANGELOG:
# - 18:28:00 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:45:00 10/07/2026: [REFACTOR] Phân rã cấu trúc kiểm toán thành các module audit_rules, audit_duplication, audit_reporter để đảm bảo modularity bền vững (Lê Thanh Vân/Antigravity)
# - 17:38:00 10/07/2026: [UPDATE] Cập nhật các quy tắc kiểm toán mới cho tách biệt UI/Backend, cấm SQL trực tiếp trong UI, và cấm setStyleSheet thô dài > 5 dòng (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import Any

# Tự động chèn project root vào sys.path để hỗ trợ import từ scripts package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit_reporter import (  # noqa: E402
    generate_json_report,
    generate_markdown_report,
    save_report_to_file,
)
from scripts.audit_rules import AuditRules  # noqa: E402
from scripts.audit_duplication import DuplicationChecker  # noqa: E402

# Ngưỡng cảnh báo trùng lặp logic (%)
SIMILARITY_THRESHOLD = 0.75

# Thư mục loại trừ
EXCLUDE_DIRS = {
    ".git",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "archives",
    "backups",
    "_backups",
    "scratch",
    ".gemini",
    "chroma_db",
    "local_data",
    "user_data_zalo",
    "user_data_zalo_bot",
    "user_data_zalo_web",
    "user_data_notebooklm",
    "tmp",
    "temp_snippets",
    "temp_vision_images",
    "htmlcov",
    "chat_sessions",
    "node_modules",
}


class CodeQualityAuditor:
    """Hệ thống phân tích cú pháp tĩnh AST để kiểm tra Clean Code & Kiến trúc thông minh (Điều phối viên)."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.function_signatures: list[dict[str, Any]] = []

    def _analyze_class_node(self, node: ast.ClassDef, results: dict[str, Any]) -> None:
        """Kiểm tra tài liệu (docstring) của class."""
        doc_ok, doc_warns = AuditRules.check_docstring_style(node)
        if not doc_ok:
            results["warnings"].append(
                {
                    "line": node.lineno,
                    "type": "DOCSTRING_MISSING",
                    "msg": f"Class `{node.name}`: {doc_warns[0]}",
                }
            )

    def _analyze_function_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        results: dict[str, Any],
        relative_path: Path,
    ) -> None:
        """Kiểm tra chi tiết một hàm: độ dài, đối số, type hints, docstring và lưu thông tin AST."""
        results["total_funcs"] += 1

        # Kiểm tra độ dài của hàm
        func_lines = getattr(node, "end_lineno", node.lineno) - node.lineno + 1
        if func_lines > 100:
            results["errors"].append(
                {
                    "line": node.lineno,
                    "type": "FUNCTION_LIMIT_EXCEEDED",
                    "msg": f"Hàm `{node.name}` dài {func_lines} dòng, vượt quá giới hạn cứng 100 dòng.",
                }
            )
        elif func_lines > 50:
            results["warnings"].append(
                {
                    "line": node.lineno,
                    "type": "FUNCTION_TOO_LONG",
                    "msg": f"Hàm `{node.name}` dài {func_lines} dòng, vượt quá giới hạn mềm 50 dòng.",
                }
            )

        # Kiểm tra số lượng đối số
        raw_args = node.args.args
        num_args = len(raw_args)
        if num_args > 0 and raw_args[0].arg in {"self", "cls"}:
            num_args -= 1
        if num_args > 4:
            results["errors"].append(
                {
                    "line": node.lineno,
                    "type": "TOO_MANY_ARGUMENTS",
                    "msg": f"Hàm `{node.name}` nhận {num_args} đối số, vượt quá giới hạn chuẩn 4 đối số.",
                }
            )

        # Check Type Hints
        th_ok, th_missing = AuditRules.check_type_hints(node)
        if th_ok:
            results["type_hint_pass"] += 1
        else:
            rel_path_str = str(relative_path).replace("\\", "/")
            is_strict_zone = rel_path_str.startswith(
                "core/"
            ) or rel_path_str.startswith("agents/")
            if is_strict_zone:
                results["errors"].append(
                    {
                        "line": node.lineno,
                        "type": "TYPE_HINT_MISSING",
                        "msg": f"Hàm `{node.name}` thiếu Type Hints: {', '.join(th_missing)}.",
                    }
                )
            else:
                results["warnings"].append(
                    {
                        "line": node.lineno,
                        "type": "TYPE_HINT_MISSING",
                        "msg": f"Hàm `{node.name}` thiếu Type Hints: {', '.join(th_missing)} (Vùng UI/Tools - Warning).",
                    }
                )

        # Check Docstrings
        doc_ok, doc_warns = AuditRules.check_docstring_style(node)
        if doc_ok:
            results["docstring_pass"] += 1
        else:
            results["warnings"].append(
                {
                    "line": node.lineno,
                    "type": "DOCSTRING_MISSING",
                    "msg": f"Hàm `{node.name}`: {', '.join(doc_warns)}.",
                }
            )

        # Lưu thông tin AST của hàm phục vụ so sánh lặp logic nâng cao
        try:
            norm_ast = DuplicationChecker.normalize_ast_structure(node)
            if len(node.body) >= 2:
                self.function_signatures.append(
                    {
                        "file": results["file"],
                        "func_name": node.name,
                        "line": node.lineno,
                        "ast_str": norm_ast,
                    }
                )
        except Exception:
            pass

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """Phân tích một file Python đơn lẻ và thu thập tất cả lỗi/cảnh báo chất lượng."""
        relative_path = file_path.relative_to(self.project_root)
        results = {
            "file": str(relative_path).replace("\\", "/"),
            "errors": [],
            "warnings": [],
            "total_funcs": 0,
            "type_hint_pass": 0,
            "docstring_pass": 0,
        }

        # 1. Kiểm tra Header Changelog
        header_ok, header_msg = AuditRules.load_changelog_header(file_path)
        if not header_ok:
            results["warnings"].append(
                {
                    "line": 1,
                    "type": "HEADER_MISSING",
                    "msg": f"Thiếu Header Changelog chuẩn dự án ({header_msg}).",
                }
            )

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError as se:
            results["errors"].append(
                {
                    "line": se.lineno or 0,
                    "type": "SYNTAX_ERROR",
                    "msg": f"Lỗi cú pháp không thể parse: {se.msg}",
                }
            )
            return results
        except Exception as e:
            results["errors"].append(
                {
                    "line": 0,
                    "type": "READ_ERROR",
                    "msg": f"Không thể đọc file: {str(e)}",
                }
            )
            return results

        # 1.5 Kiểm tra số lượng Class ở cấp module
        module_classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        if len(module_classes) > 1:
            results["warnings"].append(
                {
                    "line": module_classes[1].lineno,
                    "type": "MULTIPLE_CLASSES_IN_FILE",
                    "msg": f"Tệp tin chứa {len(module_classes)} Class ở cấp module. Khuyến nghị tách mỗi file chỉ chứa 1 Class chính.",
                }
            )

        # 2. Phân tích cây AST để quét các rule
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._analyze_class_node(node, results)

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._analyze_function_node(node, results, relative_path)

            elif isinstance(node, ast.Try):
                silent_fails = AuditRules.check_silent_exception(node)
                for line, msg in silent_fails:
                    results["errors"].append(
                        {"line": line, "type": "SILENT_EXCEPTION", "msg": msg}
                    )

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                boundary_violations = AuditRules.check_import_boundary(
                    node, relative_path
                )
                for violation in boundary_violations:
                    results["errors"].append(
                        {
                            "line": node.lineno,
                            "type": "IMPORT_BOUNDARY_VIOLATION",
                            "msg": violation,
                        }
                    )

            elif isinstance(node, ast.Assign):
                naming_violations = AuditRules.check_ui_widget_naming(
                    node, relative_path
                )
                for msg in naming_violations:
                    results["warnings"].append(
                        {
                            "line": node.lineno,
                            "type": "UI_WIDGET_NAMING_VIOLATION",
                            "msg": msg,
                        }
                    )

            elif isinstance(node, ast.Call):
                if AuditRules.check_print_calls(node):
                    results["warnings"].append(
                        {
                            "line": node.lineno,
                            "type": "RAW_PRINT_CALL",
                            "msg": "Sử dụng lệnh `print()` trực tiếp. Hãy chuyển đổi sang `logger`.",
                        }
                    )

                # Check setStyleSheet thô dài quá 5 dòng
                qss_violations = AuditRules.check_raw_stylesheet_limits(
                    node, relative_path
                )
                for msg in qss_violations:
                    results["errors"].append(
                        {
                            "line": node.lineno,
                            "type": "RAW_STYLESHEET_LIMIT_EXCEEDED",
                            "msg": msg,
                        }
                    )

                # Check layout hardcoding (setGeometry, move, resize thô trên widget con)
                layout_violations = AuditRules.check_ui_layout_hardcoding(
                    node, relative_path
                )
                for msg in layout_violations:
                    results["errors"].append(
                        {
                            "line": node.lineno,
                            "type": "UI_LAYOUT_HARDCODED",
                            "msg": msg,
                        }
                    )

                # Check blocking calls (time.sleep, requests.get)
                blocking_violations = AuditRules.check_ui_blocking_calls(
                    node, relative_path
                )
                for msg in blocking_violations:
                    results["errors"].append(
                        {
                            "line": node.lineno,
                            "type": "UI_BLOCKING_CALL",
                            "msg": msg,
                        }
                    )

            # Phân tích SQL thô và truy vấn trực tiếp DB trong UI
            db_violations = AuditRules.check_database_queries_in_ui(node, relative_path)
            for msg in db_violations:
                results["errors"].append(
                    {
                        "line": node.lineno if hasattr(node, "lineno") else 0,
                        "type": "UI_DATABASE_DIRECT_ACCESS",
                        "msg": msg,
                    }
                )

        return results

    def is_app_file(self, file_path: Path) -> bool:
        """Kiểm tra xem một file Python có thuộc codebase chính của app hay không."""
        try:
            abs_path = file_path.resolve()
            abs_root = self.project_root.resolve()
            rel_path = abs_path.relative_to(abs_root)
            parts = rel_path.parts

            if not parts:
                return False

            if len(parts) == 1:
                name = parts[0]
                app_root_files = {
                    "orchestrator.py",
                    "main_qt.py",
                    "config.py",
                    "database_client.py",
                    "app_secrets.py",
                    "lightrag_bridge_real.py",
                }
                return name in app_root_files

            first_dir = parts[0]
            app_dirs = {"core", "ui", "ui_qt", "agents", "utils"}
            return first_dir in app_dirs
        except Exception:
            return False

    def scan_project(
        self, target_files: list[Path] | None = None, check_dups: bool = False
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Quét các file chỉ định hoặc toàn project và trả về báo cáo."""
        reports = []
        files_to_scan = []

        if target_files:
            files_to_scan = [
                f for f in target_files if f.suffix == ".py" and self.is_app_file(f)
            ]
        else:
            for root, dirs, files in os.walk(self.project_root):
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for file in files:
                    if file.endswith(".py"):
                        full_path = Path(root) / file
                        if self.is_app_file(full_path):
                            files_to_scan.append(full_path)

        for file_path in files_to_scan:
            reports.append(self.analyze_file(file_path))

        duplicates = []
        if check_dups:
            duplicates = DuplicationChecker.check_logic_duplication(
                self.function_signatures, SIMILARITY_THRESHOLD
            )
        return reports, duplicates


def main() -> None:
    """Hàm chạy chính của công cụ kiểm toán."""
    parser = argparse.ArgumentParser(
        description="Clean Code & Code Quality Auditor cho dự án."
    )
    parser.add_argument("--scan", action="store_true", help="Quét toàn bộ dự án.")
    parser.add_argument(
        "--files",
        nargs="+",
        help="Quét danh sách các file cụ thể (phù hợp Git staged check).",
    )
    parser.add_argument(
        "--check-dups",
        action="store_true",
        help="Kích hoạt quét trùng lặp logic thuật toán (chạy chậm trên codebase lớn).",
    )
    parser.add_argument("--output", "-o", type=str, help="Đường dẫn lưu tệp báo cáo.")
    parser.add_argument(
        "--format",
        "-f",
        choices=["md", "json", "both"],
        default="md",
        help="Định dạng kết xuất báo cáo (md, json, both).",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    auditor = CodeQualityAuditor(project_root)

    target_files = None
    if args.files:
        target_files = [Path(f).resolve() for f in args.files]

    reports, duplicates = auditor.scan_project(target_files, check_dups=args.check_dups)

    total_errors = sum(len(r["errors"]) for r in reports)
    total_warnings = sum(len(r["warnings"]) for r in reports) + len(duplicates)
    total_funcs = sum(r["total_funcs"] for r in reports)
    total_th_pass = sum(r["type_hint_pass"] for r in reports)
    th_coverage = (total_th_pass / total_funcs * 100) if total_funcs > 0 else 100

    score = 10.0 - (total_errors * 0.01) - (total_warnings * 0.0002)
    score = max(0.0, min(10.0, score))

    md_report = generate_markdown_report(
        reports,
        duplicates,
        score,
        th_coverage=th_coverage,
        total_errors=total_errors,
        total_warnings=total_warnings,
        total_funcs=total_funcs,
        total_th_pass=total_th_pass,
    )
    json_report = generate_json_report(
        reports,
        duplicates,
        score,
        th_coverage=th_coverage,
        total_errors=total_errors,
        total_warnings=total_warnings,
        total_funcs=total_funcs,
        total_th_pass=total_th_pass,
    )

    status_emoji = "🟢" if score >= 8.0 else ("⚠️" if score >= 5.0 else "🚨")
    print(f"\n* Điểm chất lượng mã nguồn: {status_emoji} **{score:.1f}/10.0**")
    print(
        f"* Độ bao phủ Type Hints: **{th_coverage:.1f}%** ({total_th_pass}/{total_funcs} hàm)"
    )
    print(f"* Tổng số Lỗi nặng (High Error): **{total_errors}**")
    print(f"* Tổng số Cảnh báo (Warning): **{total_warnings}**")

    if args.output:
        save_report_to_file(args.output, args.format, md_report, json_report)
    else:
        print(md_report)

    if total_errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
