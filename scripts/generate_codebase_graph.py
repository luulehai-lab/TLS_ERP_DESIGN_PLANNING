# Tên file: scripts/generate_codebase_graph.py
# CHỨC NĂNG: Quét codebase bằng AST, xây dựng đồ thị tri thức (JSON/Mermaid) hỗ trợ Incremental Cache siêu tốc và phân tích tác động.
# CHANGELOG:
# - 18:28:00 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:53:55 08/07/2026: [FIX] fix(ui): fix white text on white background in Windows Dark Mode for QLineEdit, QTableWidget, and QMessageBox (Antigravity)
# - 17:42:00 08/07/2026: [FIX] Sửa tiêu đề và mô tả đồ thị codebase cho đúng nghiệp vụ ERP (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 17:03:17 19/06/2026: [UPDATE] feat(audit): integrate clean code AST auditor and sync workspace updates (Antigravity)
# - 17:00:33 19/06/2026: [UPDATE] feat(audit): integrate clean code AST auditor and sync workspace updates (Antigravity)
# - 18:00:00 28/05/2026: [UPDATE] Tích hợp cơ chế Incremental Cache tối ưu tốc độ quét dưới 0.3s (Lê Thanh Vân/Antigravity)
# - 17:45:00 28/05/2026: [NEW] Tích hợp công cụ Đồ thị Codebase cho AI Assistant (Lê Thanh Vân/Antigravity)

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any

# Tự động chèn project root vào sys.path để hỗ trợ import từ scripts package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.graph_parser import CodebaseParser  # noqa: E402
from scripts.graph_core import CodebaseGraph  # noqa: E402
from scripts.graph_exporter import GraphExporter  # noqa: E402


def scan_codebase_incremental(
    project_root: Path, cache_path: Path
) -> tuple[CodebaseGraph, dict[str, Any]]:
    """
    Quét codebase hỗ trợ Incremental Cache:
    Chỉ parse AST những file đã bị chỉnh sửa mới, giữ lại dữ liệu cũ cho các file không đổi.
    """
    files_cache = {}

    # 1. Đọc cache cũ nếu tồn tại
    if cache_path.exists():
        try:
            with open(cache_path, encoding="utf-8") as f:
                old_data = json.load(f)
                files_cache = old_data.get("_files_cache", {})
                print(
                    f"📦 Đã tìm thấy cache đồ thị hiện tại ({len(files_cache)} files)."
                )
        except Exception as e:
            print(f"⚠️ Không thể load cache đồ thị cũ: {e}. Quét lại từ đầu.")

    exclude_dirs = {
        ".git",
        ".vscode",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "archives",
        "backups",
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
    }

    parsers_data = []
    scanned_count = 0
    cached_count = 0

    # 2. Duyệt codebase và cập nhật động
    for py_file in project_root.glob("**/*.py"):
        if any(ex in py_file.parts for ex in exclude_dirs):
            continue
        if py_file.name.startswith("test_"):
            continue

        relative_path = py_file.relative_to(project_root)
        module_name = ".".join(relative_path.with_suffix("").parts)

        try:
            file_mtime = py_file.stat().st_mtime

            # Kiểm tra xem có cache hợp lệ không
            if (
                module_name in files_cache
                and files_cache[module_name].get("mtime") == file_mtime
            ):
                # Đọc trực tiếp từ cache cũ!
                parsers_data.append(files_cache[module_name])
                cached_count += 1
            else:
                # Parse AST file mới
                with open(py_file, encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                parser = CodebaseParser(py_file, project_root)
                parser.visit(tree)

                # Đóng gói dữ liệu trích xuất dạng JSON dict
                pdata = {
                    "module_name": parser.module_name,
                    "file_path": str(relative_path).replace("\\", "/"),
                    "mtime": file_mtime,
                    "imports": parser.imports,
                    "classes": parser.classes,
                    "functions": parser.functions,
                    "calls": parser.calls,
                }

                # Cập nhật cache
                files_cache[module_name] = pdata
                parsers_data.append(pdata)
                scanned_count += 1
        except Exception as e:
            print(f"⚠️ Không thể parse file {py_file}: {e}")

    print(
        f"⚡ Tối ưu hóa: Phân tích AST {scanned_count} files thay đổi. Đọc nhanh từ Cache {cached_count} files."
    )

    # 3. Dựng đồ thị
    graph = CodebaseGraph()
    graph.resolve_relationships(parsers_data)
    return graph, files_cache


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Công cụ quét Codebase dạng Graph siêu tốc cho AI Assistant."
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Quét codebase cập nhật đồ thị bằng Incremental Cache.",
    )
    parser.add_argument(
        "--impact", type=str, help="Truy vết tác động sửa đổi của thực thể."
    )
    parser.add_argument("--mermaid", type=str, help="Lọc module xuất sơ đồ Mermaid.")

    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent.parent
    output_dir = project_root / "docs" / "architecture"
    json_path = output_dir / "codebase_graph.json"

    if args.scan:
        print("🔄 Đang quét codebase AI Assistant...")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Gọi quét Incremental Cache!
        graph, files_cache = scan_codebase_incremental(project_root, json_path)

        # 1. Lưu file JSON đồ thị kèm Cache
        exporter = GraphExporter(graph)
        exporter.to_json(json_path, files_cache)
        print(f"💾 Đã lưu đồ thị và cache: {json_path}")

        # 2. Tạo sơ đồ Mermaid cho các module chính của AI Assistant
        core_mermaid = exporter.to_mermaid(
            ["core.services", "core.dxf_boq", "orchestrator"]
        )
        ui_mermaid = exporter.to_mermaid(["ui_qt"])

        # 3. Ghi vào file MAP_GRAPH.md
        map_graph_path = output_dir / "MAP_GRAPH.md"
        with open(map_graph_path, "w", encoding="utf-8") as f:
            f.write(f"""<!--
File: docs/architecture/MAP_GRAPH.md
Description: 🌐 ĐỒ THỊ LIÊN KẾT CODEBASE ERP
CHANGELOG:
- 18:00:00 28/05/2026: [UPDATE] Tối ưu hóa quét Incremental Cache (Lê Thanh Vân)
-->

# 🌐 ĐỒ THỊ LIÊN KẾT CODEBASE ERP TUẤN LONG STEEL

> [!TIP]
> Tài liệu này được tự động cập nhật bằng cơ chế **Incremental Cache** siêu tốc.
> Giúp hình dung rõ ràng mối liên kết gọi hàm và kế thừa trong hệ thống ERP.

---

## 💾 1. Đồ thị liên kết Core & Services (Database, Auth, Project, Drawing, BOQ)
```mermaid
{core_mermaid}
```

---

## 🎨 2. Đồ thị liên kết Frontend PyQt6 (Giao diện người dùng)
```mermaid
{ui_mermaid}
```
""")
        print(f"📝 Đã tạo/cập nhật tài liệu đồ thị: {map_graph_path}")
        print("✅ Hoàn thành quét codebase thành công!")

    elif args.impact:
        # Load đồ thị từ cache JSON để chạy lập tức (tốc độ dưới 0.1s!)
        if not json_path.exists():
            print("⚠️ File đồ thị chưa tồn tại. Vui lòng chạy quét `--scan` trước.")
            return

        try:
            with open(json_path, encoding="utf-8") as f:
                graph_data = json.load(f)
                files_cache = graph_data.get("_files_cache", {})
                parsers_data = list(files_cache.values())
        except Exception as e:
            print(f"⚠️ Lỗi đọc cache: {e}. Đang quét trực tiếp...")
            graph, files_cache = scan_codebase_incremental(project_root, json_path)
            parsers_data = list(files_cache.values())

        graph = CodebaseGraph()
        graph.resolve_relationships(parsers_data)

        target = args.impact
        if target not in graph.nodes:
            matches = [nid for nid in graph.nodes if target in nid]
            if not matches:
                print(f"❌ Không tìm thấy thực thể nào khớp với: {target}")
                return
            elif len(matches) == 1:
                target = matches[0]
            else:
                print("❓ Tìm thấy nhiều thực thể khớp, vui lòng nhập chính xác:")
                for m in matches[:10]:
                    print(f"  - {m}")
                return

        print(
            f"🔍 Đang truy vết tác động khi thay đổi: {target} ({graph.nodes[target]['type']})"
        )
        impacts = graph.find_impact(target)
        if not impacts:
            print(
                "🟢 Tuyệt vời! Không phát hiện ảnh hưởng trực tiếp nào đến các module khác."
            )
        else:
            print(f"⚠️ Phát hiện {len(impacts)} điểm bị ảnh hưởng trực tiếp/gián tiếp:")
            print(
                f"{'Thực thể bị ảnh hưởng':<70} | {'Mối quan hệ':<12} | {'Chi tiết file'}"
            )
            print("-" * 120)
            for imp in impacts:
                node = imp["node"]
                rel = imp["relation"].upper()
                file_info = f"{node.get('file_path', 'unknown')}:{node.get('line', '')}"
                print(f"{node['id']:<70} | {rel:<12} | {file_info}")

    elif args.mermaid:
        if not json_path.exists():
            print("⚠️ File đồ thị chưa tồn tại. Vui lòng chạy quét `--scan` trước.")
            return
        with open(json_path, encoding="utf-8") as f:
            graph_data = json.load(f)
            files_cache = graph_data.get("_files_cache", {})
            parsers_data = list(files_cache.values())

        graph = CodebaseGraph()
        graph.resolve_relationships(parsers_data)

        exporter = GraphExporter(graph)
        modules = args.mermaid.split(",")
        print(exporter.to_mermaid(modules))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
