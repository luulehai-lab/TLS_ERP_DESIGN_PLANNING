# Tên file: scripts/generate_boilerplate_test.py
# CHỨC NĂNG: Tự động sinh khung unit test (pytest boilerplate) từ tệp logic nguồn Python.
# CHANGELOG:
# - 09:42:18 13/07/2026: [FIX] feat(report): add visual report dashboard with charts, fix combobox/permission bugs and install global exception hook (Antigravity)
# - 15:17:43 11/07/2026: [NEW] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 14:18:00 11/07/2026: [NEW] Sao chép công cụ sinh khung test tự động từ dự án ZZZ.DANG TEST. (Antigravity)

import argparse
import ast
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Thêm thư mục gốc vào path để import các module nội bộ nếu cần
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

logger = logging.getLogger("TestGenerator")


def analyze_source_file(file_path: Path) -> dict[str, Any]:
    """Phân tích cú pháp AST của tệp Python nguồn để trích xuất class và function.

    Args:
        file_path: Đường dẫn tệp tin nguồn Python.

    Returns:
        Dictionary chứa danh sách các class và function được tìm thấy.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=str(file_path))

    classes = []
    functions = []

    for child in node.body:
        if isinstance(child, ast.ClassDef):
            class_name = child.name
            methods = []
            for sub_child in child.body:
                if isinstance(sub_child, ast.FunctionDef):
                    # Lấy các public methods và __init__
                    name = sub_child.name
                    if not name.startswith("_") or name == "__init__":
                        methods.append(name)
            classes.append({"name": class_name, "methods": methods})
        elif isinstance(child, ast.FunctionDef):
            if not child.name.startswith("_"):
                functions.append(child.name)

    return {"classes": classes, "functions": functions}


def get_import_path(file_path: Path, project_root: Path) -> str:
    """Tính toán chuỗi import path của module Python từ đường dẫn tệp.

    Args:
        file_path: Đường dẫn tuyệt đối đến tệp Python.
        project_root: Thư mục gốc của dự án.

    Returns:
        Chuỗi import path (ví dụ: 'core.utils.steel_parser').
    """
    try:
        relative_path = file_path.relative_to(project_root)
        parts = list(relative_path.parts)
        parts[-1] = (
            relative_path.prefix
            if hasattr(relative_path, "prefix")
            else relative_path.stem
        )  # Bỏ đuôi .py
        return ".".join(parts)
    except ValueError:
        # Nếu tệp nằm ngoài project_root, lấy trực tiếp stem
        return file_path.stem


def generate_test_content(
    import_path: str,
    analysis: dict[str, Any],
    test_file_rel: str,
) -> str:
    """Tạo mã nguồn Python cho tệp kiểm thử tự động.

    Args:
        import_path: Đường dẫn import của module nguồn.
        analysis: Kết quả phân tích AST của module.
        test_file_rel: Đường dẫn tương đối của tệp test để hiển thị trong header.

    Returns:
        Mã nguồn tệp test hoàn chỉnh.
    """
    time_str = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    # Header chuẩn của dự án
    content = f"""# Tên file: {test_file_rel}
# CHỨC NĂNG: Tự động kiểm thử cho module {import_path}
# CHANGELOG:
# - {time_str}: [NEW] Tự động sinh khung test case (Antigravity)

import pytest
from unittest.mock import Mock
"""

    # Thu thập tất cả các class và function để import
    imports = []
    for cls in analysis["classes"]:
        imports.append(cls["name"])
    for fn in analysis["functions"]:
        imports.append(fn)

    if imports:
        import_items = ", ".join(imports)
        content += f"from {import_path} import {import_items}\n\n"
    else:
        content += f"# Không tìm thấy class hay function public nào để import từ {import_path}\n\n"

    # Sinh test case cho các function độc lập
    for fn in analysis["functions"]:
        content += f"""
def test_{fn}() -> None:
    \"\"\"Kiểm thử hàm `{fn}`.\"\"\"
    # Arrange: Chuẩn bị dữ liệu mẫu
    # TODO: Khai báo tham số đầu vào và kết quả kỳ vọng
    expected = None

    # Act: Thực thi hàm
    # result = {fn}()

    # Assert: Đối chiếu kết quả
    # assert result == expected
    pass
"""

    # Sinh test case cho các class và method
    for cls in analysis["classes"]:
        class_name = cls["name"]
        instance_var = class_name.lower()
        if instance_var.endswith("class"):
            instance_var = instance_var[:-5]
        elif len(instance_var) > 15:
            instance_var = "obj"

        content += f"\n\nclass Test{class_name}:\n"
        content += f'    """Bộ kiểm thử cho class `{class_name}`."""\n\n'

        # Fixture khởi tạo mặc định
        content += "    @pytest.fixture\n"
        content += f"    def {instance_var}_fixture(self) -> {class_name}:\n"
        content += (
            f'        """Khởi tạo đối tượng `{class_name}` cho từng test case."""\n'
        )
        content += "        # Arrange: Cấu hình tham số khởi tạo nếu cần\n"
        content += "        # TODO: Cập nhật đối số khởi tạo\n"
        content += f"        return {class_name}()\n"

        for method in cls["methods"]:
            if method == "__init__":
                continue
            content += "\n"
            content += f"    def test_{method}(self, {instance_var}_fixture: {class_name}) -> None:\n"
            content += f'        """Kiểm thử phương thức `{method}`."""\n'
            content += "        # Arrange: Thiết lập trạng thái và tham số\n"
            content += "        # TODO: Setup data\n"
            content += "        expected = None\n\n"
            content += "        # Act: Gọi phương thức cần test\n"
            content += f"        # result = {instance_var}_fixture.{method}()\n\n"
            content += "        # Assert: Kiểm tra đầu ra\n"
            content += "        # assert result == expected\n"
            content += "        pass\n"

    return content


def determine_test_path(source_path: Path, project_root: Path) -> Path:
    """Xác định đường dẫn lưu file test tương ứng dựa trên cấu trúc file nguồn.

    Args:
        source_path: Đường dẫn tệp tin nguồn.
        project_root: Thư mục gốc dự án.

    Returns:
        Đường dẫn tuyệt đối đến tệp test sẽ tạo.
    """
    try:
        rel_path = source_path.relative_to(project_root)
        parts = list(rel_path.parts)
    except ValueError:
        parts = [source_path.name]

    # Nếu file nguồn nằm trong thư mục con của dự án (ví dụ: core/utils/file.py)
    # Ta sẽ map sang tests/core/utils/test_file.py
    if parts and parts[0] == "tests":
        # Nếu truyền nhầm file test vào, lưu đè hoặc báo lỗi
        test_filename = f"test_{source_path.stem}.py"
        return project_root / "tests" / test_filename

    if parts:
        parts[-1] = f"test_{source_path.stem}.py"
        return project_root / "tests" / "/".join(parts)

    return project_root / "tests" / f"test_{source_path.stem}.py"


def main() -> None:
    """Hàm chạy chính điều phối luồng sinh test boilerplate."""
    parser = argparse.ArgumentParser(
        description="Tự động sinh khung tệp unit test cho module Python."
    )
    parser.add_argument(
        "source_file",
        type=str,
        help="Đường dẫn đến file logic nguồn Python cần viết test.",
    )
    parser.add_argument(
        "--force", action="store_true", help="Ghi đè file test nếu đã tồn tại."
    )
    args = parser.parse_args()

    source_path = Path(args.source_file).resolve()
    if not source_path.exists() or not source_path.is_file():
        logger.error(f"❌ Tệp tin nguồn không tồn tại: {args.source_file}")
        sys.exit(1)

    if source_path.suffix != ".py":
        logger.error("❌ Chỉ hỗ trợ sinh test cho các tệp tin Python (.py)")
        sys.exit(1)

    # 1. Phân tích AST
    logger.info(f"🔍 Đang phân tích cú pháp AST: {source_path.name}...")
    analysis = analyze_source_file(source_path)

    # 2. Tính toán đường dẫn xuất
    test_path = determine_test_path(source_path, PROJECT_ROOT)
    test_path.parent.mkdir(parents=True, exist_ok=True)

    if test_path.exists() and not args.force:
        logger.warning(
            f"⚠️ Tệp test đã tồn tại tại: {test_path.relative_to(PROJECT_ROOT).as_posix()}\n"
            "Chạy lại lệnh kèm tham số `--force` nếu muốn ghi đè."
        )
        sys.exit(0)

    # 3. Tạo nội dung test
    import_path = get_import_path(source_path, PROJECT_ROOT)
    test_file_rel = test_path.relative_to(PROJECT_ROOT).as_posix()
    test_content = generate_test_content(import_path, analysis, test_file_rel)

    # 4. Ghi file
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(test_content)

    logger.info(f"✅ Sinh thành công tệp kiểm thử tại: {test_file_rel}")


if __name__ == "__main__":
    main()
