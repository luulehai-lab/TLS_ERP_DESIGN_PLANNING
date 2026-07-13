# Tên file: scripts/build_exe.py
# CHỨC NĂNG: Tự động đóng gói ứng dụng PyQt6 thành file exe bằng PyInstaller
# CHANGELOG:
# - 15:01:02 13/07/2026: [UPDATE] feat(drawing-service): sort drawings by project section code and drawing id for grouping (Antigravity)
# - 17:53:55 08/07/2026: [NEW] fix(ui): fix white text on white background in Windows Dark Mode for QLineEdit, QTableWidget, and QMessageBox (Antigravity)
# - 17:20:00 08/07/2026: [NEW] Khởi tạo script đóng gói ERP_TuanLong.exe với cấu hình tối ưu (Lê Thanh Vân/Antigravity)

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("build_exe")

# Thư mục gốc dự án
BASE_DIR: Path = Path(__file__).parent.parent.resolve()
DIST_DIR: Path = BASE_DIR / "dist"
BUILD_DIR: Path = BASE_DIR / "build"
SPEC_FILE: Path = BASE_DIR / "ERP_TuanLong.spec"


def clean_previous_builds() -> None:
    """Dọn dẹp các thư mục build, dist và spec file cũ trước khi đóng gói."""
    logger.info("Đang dọn dẹp các tệp tin và thư mục build cũ...")

    paths_to_remove = [DIST_DIR, BUILD_DIR, SPEC_FILE]
    for p in paths_to_remove:
        if p.exists():
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                logger.info("Đã xóa: %s", p)
            except Exception as e:
                logger.error("Không thể xóa %s: %s", p, str(e), exc_info=True)


def run_pyinstaller() -> bool:
    """Thực thi PyInstaller để đóng gói main.py thành file exe duy nhất.

    Returns:
        True nếu đóng gói thành công, ngược lại False.
    """
    logger.info("Bắt đầu chạy PyInstaller để đóng gói ứng dụng...")

    main_path = BASE_DIR / "main.py"
    if not main_path.exists():
        logger.error("Không tìm thấy file main.py tại %s", main_path)
        return False

    # Định nghĩa các tham số cấu hình cho PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=ERP_TuanLong",
        f"--workpath={BUILD_DIR}",
        f"--distpath={DIST_DIR}",
        # Hidden imports để đảm bảo các thư viện ORM và OAuth chạy đúng
        "--hidden-import=sqlalchemy",
        "--hidden-import=sqlalchemy.sql.default_comparator",
        "--hidden-import=psycopg2",
        "--hidden-import=dotenv",
        "--hidden-import=PyQt6",
        "--hidden-import=google.oauth2",
        "--hidden-import=google_auth_oauthlib",
        str(main_path),
    ]

    logger.info("Lệnh thực thi: %s", " ".join(cmd))
    try:
        # Chạy lệnh đóng gói và truyền log ra stdout
        result = subprocess.run(
            cmd, cwd=str(BASE_DIR), check=True, capture_output=True, text=True
        )
        logger.info(result.stdout)
        logger.info("PyInstaller hoàn thành đóng gói thành công!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Lỗi khi chạy PyInstaller!")
        logger.error("Stdout:\n%s", e.stdout)
        logger.error("Stderr:\n%s", e.stderr)
        return False


def copy_env_config() -> None:
    """Sao chép tệp .env hiện tại hoặc tạo tệp .env.example sang thư mục dist, và sao chép logo công ty."""
    logger.info("Cấu hình tệp .env cho môi trường production...")
    env_source = BASE_DIR / ".env"
    env_target = DIST_DIR / ".env"

    if env_source.exists():
        try:
            shutil.copy(env_source, env_target)
            logger.info("Đã sao chép tệp .env hiện tại sang %s", env_target)
        except Exception as e:
            logger.error("Lỗi khi sao chép .env: %s", str(e), exc_info=True)
    else:
        # Tạo tệp cấu hình mẫu nếu chưa có
        logger.warning("Không tìm thấy tệp .env nguồn. Tạo tệp cấu hình mẫu .env...")
        env_content = (
            "# Cấu hình kết nối DB (PostgreSQL Supabase)\n"
            "DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres\n\n"
            "# Cấu hình Google Drive\n"
            "GOOGLE_DRIVE_FOLDER_ID=\n\n"
            "# Cấu hình Google OAuth\n"
            "GOOGLE_CLIENT_ID=\n"
            "GOOGLE_CLIENT_SECRET=\n\n"
            "# Danh sách email được truy cập phòng Thiết kế (phân cách bằng dấu phẩy)\n"
            "DESIGN_DEPARTMENT_EMAILS=luu.lehai@gmail.com\n"
        )
        try:
            env_target.write_text(env_content, encoding="utf-8")
            logger.info("Đã tạo tệp cấu hình mẫu tại %s", env_target)
        except Exception as e:
            logger.error("Lỗi khi tạo tệp .env mẫu: %s", str(e), exc_info=True)

    # Sao chép LOGO.JPG
    logo_source = BASE_DIR / "LOGO.JPG"
    logo_target = DIST_DIR / "LOGO.JPG"
    if logo_source.exists():
        try:
            shutil.copy(logo_source, logo_target)
            logger.info("Đã sao chép tệp LOGO.JPG sang %s", logo_target)
        except Exception as e:
            logger.error("Lỗi khi sao chép LOGO.JPG: %s", str(e), exc_info=True)


def create_release_zip() -> None:
    """Nén file exe, file .env cấu hình và file LOGO.JPG thành tệp zip duy nhất để phân phối."""
    zip_path = DIST_DIR / "ERP_TuanLong_Release.zip"
    exe_file = DIST_DIR / "ERP_TuanLong.exe"
    env_file = DIST_DIR / ".env"
    logo_file = DIST_DIR / "LOGO.JPG"

    if not exe_file.exists():
        logger.error("Không tìm thấy file exe để nén: %s", exe_file)
        return

    logger.info("Đang tạo gói nén Release ZIP tại %s...", zip_path)
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Nén exe
            zipf.write(exe_file, arcname="ERP_TuanLong.exe")
            logger.info("Đã thêm ERP_TuanLong.exe vào zip")
            # Nén env
            if env_file.exists():
                zipf.write(env_file, arcname=".env")
                logger.info("Đã thêm .env vào zip")
            # Nén logo
            if logo_file.exists():
                zipf.write(logo_file, arcname="LOGO.JPG")
                logger.info("Đã thêm LOGO.JPG vào zip")
        logger.info("Đã tạo tệp phát hành thành công: %s", zip_path)
    except Exception as e:
        logger.error("Lỗi khi tạo tệp nén ZIP: %s", str(e), exc_info=True)


def main() -> None:
    """Hàm khởi chạy chính điều phối quy trình build."""
    logger.info("BẮT ĐẦU TIẾN TRÌNH ĐÓNG GÓI ERP TUẤN LONG STEEL...")
    clean_previous_builds()

    if run_pyinstaller():
        copy_env_config()
        create_release_zip()
        logger.info("ĐÓNG GÓI THÀNH CÔNG RỰC RỠ! Sẵn sàng bàn giao.")
    else:
        logger.error("ĐÓNG GÓI THẤT BẠI. Vui lòng kiểm tra nhật ký lỗi phía trên.")
        sys.exit(1)


if __name__ == "__main__":
    main()
