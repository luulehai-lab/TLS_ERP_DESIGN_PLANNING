# Tên file: scripts/audit_imports.py
# CHỨC NĂNG: Quét toàn bộ codebase và thử nạp (import) từng file Python qua subprocess để phát hiện lỗi Syntax và NameError.
# CHANGELOG:
# - 09:42:18 13/07/2026: [NEW] feat(report): add visual report dashboard with charts, fix combobox/permission bugs and install global exception hook (Antigravity)
# - 09:39:00 13/07/2026: [NEW] Tạo mới công cụ kiểm tra nạp module toàn diện (Import Validator) cho dự án ERP. (Antigravity)

import concurrent.futures
import os
import subprocess
import sys
from pathlib import Path

# Thư mục gốc dự án
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Các thư mục cần quét tìm file .py
TARGET_DIRS = ["core", "ui", "scripts"]

# Các thư mục hoặc tệp tin bị bỏ qua (file test, file nháp, automation phụ trợ)
IGNORE_PATTERNS = [
    "__pycache__",
    ".git",
    ".gemini",
    "/scratch/",
    "/tmp/",
    "htmlcov",
    "tests",
    "vulture_whitelist.py",
    "app_secrets.py",
    "build",
    "dist",
    "dxf_to_excel_boq.py",
]


def convert_path_to_module(file_path: Path) -> str:
    """Chuyển đổi đường dẫn file tuyệt đối thành tên module Python (dạng x.y.z).

    Args:
        file_path: Đường dẫn tuyệt đối của file .py.

    Returns:
        Tên module Python dạng dấu chấm phân cách.
    """
    rel_path = file_path.relative_to(PROJECT_ROOT)
    parts = list(rel_path.with_suffix("").parts)

    # Nếu file nằm ở thư mục gốc (như main.py)
    if len(parts) == 1:
        return parts[0]

    return ".".join(parts)


def should_ignore(file_path: Path) -> bool:
    """Kiểm tra xem đường dẫn file có nằm trong danh sách loại trừ hay không.

    Args:
        file_path: Đường dẫn tuyệt đối của file cần kiểm tra.

    Returns:
        True nếu file nên bị bỏ qua, ngược lại là False.
    """
    path_str = file_path.as_posix()
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
    # Bỏ qua các file backup
    if file_path.name.endswith(".bak") or "_bak" in file_path.name:
        return True
    return False


def test_import_module(module_name: str) -> tuple[bool, str]:
    """Chạy một tiến trình con (subprocess) để thử nạp (import) module chỉ định.

    Args:
        module_name: Tên module cần import thử.

    Returns:
        Tuple chứa trạng thái (True nếu nạp thành công) và thông điệp lỗi nếu có.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    try:
        cmd = [sys.executable, "-c", f"import {module_name}"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return (
            False,
            "Import bị treo (Timeout > 5 giây) - có thể có vòng lặp vô hạn ở module level.",
        )
    except Exception as e:
        return False, f"Lỗi hệ thống khi thực thi subprocess: {e}"


def run_audit() -> int:
    """Quét toàn bộ dự án và chạy kiểm tra nạp tất cả module Python tìm thấy.

    Returns:
        Mã thoát (0 nếu tất cả module import thành công, 1 nếu có lỗi).
    """
    print("====================================================")
    print("🔍 KHỞI ĐỘNG CÔNG CỤ KIỂM TRA IMPORT TOÀN CỤC (IMPORT VALIDATOR) 🔍")
    print("====================================================")

    python_files: list[Path] = []

    # 1. Tìm các file Python ở thư mục gốc
    for file in PROJECT_ROOT.glob("*.py"):
        if file.is_file() and not should_ignore(file):
            python_files.append(file)

    # 2. Tìm các file Python ở các thư mục con chỉ định
    for target_dir in TARGET_DIRS:
        dir_path = PROJECT_ROOT / target_dir
        if not dir_path.exists():
            continue
        for file in dir_path.rglob("*.py"):
            if file.is_file() and not should_ignore(file):
                python_files.append(file)

    print(f"-> Tìm thấy {len(python_files)} tệp tin Python cần kiểm tra.")

    failed_modules: list[tuple[str, str]] = []
    success_count = 0

    # 3. Chạy import song song bằng ThreadPoolExecutor để tối ưu hóa thời gian chờ I/O
    print(
        "-> Đang tiến hành phân tích nhập khẩu song song (Parallel Import Validation)..."
    )
    modules = [convert_path_to_module(f) for f in python_files]

    # Sử dụng tối đa 16 luồng song song
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # Map các tác vụ import thử
        results = executor.map(test_import_module, modules)

        for i, (module_name, (success, err_msg)) in enumerate(
            zip(modules, results, strict=True), 1
        ):
            if success:
                success_count += 1
            else:
                failed_modules.append((module_name, err_msg))

            # In tiến trình chạy
            if i % 10 == 0 or i == len(modules):
                print(f"-> Đã quét: {i}/{len(modules)} file...", end="\r", flush=True)

    print("\n----------------------------------------------------")
    print("📊 KẾT QUẢ KIỂM TRA:")
    print(f"  - Thành công (Import OK): {success_count}/{len(python_files)}")
    print(f"  - Thất bại (Lỗi crash): {len(failed_modules)}/{len(python_files)}")
    print("----------------------------------------------------")

    if failed_modules:
        print("\n❌ DANH SÁCH CÁC MODULE BỊ CRASH KHI IMPORT:")
        for mod, err in failed_modules:
            print(f"\n📌 Module: {mod}")
            print(f"   Chi tiết lỗi:\n{err}")
            print("-" * 40)
        return 1

    print(
        "\n🟢 HOÀN THÀNH: Tất cả các file Python đều được nạp sạch sẽ, không có lỗi Syntax hay NameError!"
    )
    return 0


if __name__ == "__main__":
    sys.exit(run_audit())
