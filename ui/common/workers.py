# Tên file: ui/common/workers.py
# CHỨC NĂNG: Khai báo các luồng phụ xử lý bất đồng bộ (QThread Workers)
# CHANGELOG:
# - 11:39:58 14/07/2026: [FIX] fix(drawing-ui): click on drive link column to open in browser for download (Antigravity)
# - 11:32:00 14/07/2026: [NEW] Di chuyển ReportLoaderThread từ bao_cao_view.py sang để tối ưu modularity (Lê Thanh Vân/Antigravity)
# - 14:25:54 13/07/2026: [UPDATE] feat(search): implement project and drawing search with client-side filters (Antigravity)
# - 15:17:43 11/07/2026: [UPDATE] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 14:57:00 11/07/2026: [UPDATE] Bổ sung section_designer_emails và section_designer_email vào loader threads (Antigravity)
# - 14:34:36 11/07/2026: [REFACTOR] refactor(ui-modularity): complete modular refactoring of codebase graph tools and adopt UI-Backend Separation rules (Antigravity)
# - 14:30:00 11/07/2026: [UPDATE] Bổ sung trường notes vào DrawingLoaderThread serialize (Antigravity)
# - 14:58:00 10/07/2026: [UPDATE] Cập nhật ProjectLoaderThread để lấy thêm sales_email và designer_email (Lê Thanh Vân/Antigravity)
# - 18:19:45 08/07/2026: [UPDATE] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [UPDATE] Cập nhật DrawingLoaderThread để nạp thêm section_name của bản vẽ (Antigravity)
# - 16:40:16 08/07/2026: [UPDATE] feat(auth): add Google OAuth2 login with department-based access control (Antigravity)
# - 16:35:00 08/07/2026: [NEW] Thêm class DatabasePrewarmerThread làm ấm connection pool db khi mở app (Lê Thanh Vân/Antigravity)
# - 13:38:53 08/07/2026: [UPDATE] feat(db): add script to enable Row-Level Security and update code graph (Antigravity)
# - 13:35:00 08/07/2026: [UPDATE] Bổ sung kiểm tra kết nối thô db.execute(text("SELECT 1")) để ném exception khi mất kết nối mạng thay vì trả về list rỗng (Lê Thanh Vân/Antigravity)
# - 13:25:00 08/07/2026: [NEW] Bổ sung ProjectLoaderThread để tải danh sách dự án bất đồng bộ tránh treo UI chính (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:32:00 02/07/2026: [NEW] Khởi tạo luồng phụ tải bản vẽ ngầm tránh block UI Thread (Lê Thanh Vân/Antigravity)

import logging
from PyQt6.QtCore import QThread, pyqtSignal

from core.database import SessionLocal
from core.services import drawing_service, project_service

logger = logging.getLogger(__name__)


class DatabasePrewarmerThread(QThread):
    """Luồng phụ làm nóng (pre-warm) connection pool tới database.

    Giúp chuẩn bị sẵn kết nối mạng tới Supabase Cloud ngay khi app khởi động,
    tránh làm đơ giao diện do nghẽn GIL khi tạo kết nối đầu tiên lúc vào MainWindow.
    """

    def run(self) -> None:
        """Thực thi câu lệnh truy vấn SELECT 1 để làm nóng connection pool."""
        logger.info("Khởi động tiến trình làm nóng Connection Pool database ngầm...")
        db = SessionLocal()
        try:
            from sqlalchemy import text

            db.execute(text("SELECT 1"))
            logger.info(
                "Làm nóng Connection Pool database thành công. Kết nối đã sẵn sàng."
            )
        except Exception as e:
            logger.warning("Không thể làm nóng Connection Pool database: %s", str(e))
        finally:
            db.close()


class ProjectLoaderThread(QThread):
    """Luồng phụ chuyên trách tải danh sách dự án từ cơ sở dữ liệu cloud.

    Giúp giao diện người dùng không bị treo khi khởi động ứng dụng trong môi trường
    mạng yếu/chậm.
    """

    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self) -> None:
        """Khởi tạo luồng tải dự án ngầm."""
        super().__init__()

    def run(self) -> None:
        """Thực thi câu lệnh truy vấn danh sách dự án ở luồng phụ."""
        logger.info("Bắt đầu tải danh sách dự án ngầm từ Cloud database...")
        db = SessionLocal()
        try:
            from sqlalchemy import text

            db.execute(text("SELECT 1"))
            projects = project_service.list_active_projects(db)

            # Bóc tách sang danh sách dict thô để truyền an toàn qua Signal,
            # tránh DetachedInstanceError khi session bị đóng.
            raw_projects = []
            for p in projects:
                # Thu thập danh sách designer email từ các hạng mục
                section_emails = list(
                    {s.designer_email.lower() for s in p.sections if s.designer_email}
                )
                raw_projects.append(
                    {
                        "project_id": p.project_id,
                        "project_name": p.project_name,
                        "status": p.status,
                        "sales_email": p.sales_email,
                        "designer_email": p.designer_email,
                        "section_designer_emails": section_emails,
                    }
                )

            logger.info(
                "Tải xong danh sách dự án ngầm (Tìm thấy %d dự án)",
                len(raw_projects),
            )
            self.finished.emit(raw_projects)
        except Exception as e:
            logger.error(
                "Lỗi trong lúc truy vấn dự án ở luồng phụ: %s",
                str(e),
                exc_info=True,
            )
            self.error.emit(str(e))
        finally:
            db.close()


class DrawingLoaderThread(QThread):
    """Luồng phụ chuyên trách tải danh sách bản vẽ từ cơ sở dữ liệu cloud.

    Giúp giao diện người dùng (UI Thread) luôn mượt mà và phản hồi ngay lập tức
    khi thay đổi dự án được chọn trên Sidebar.
    """

    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, project_id: str) -> None:
        """Khởi tạo luồng tải bản vẽ ngầm.

        Args:
            project_id: Mã dự án cần truy vấn danh sách bản vẽ.
        """
        super().__init__()
        self.project_id = project_id

    def run(self) -> None:
        """Thực thi câu lệnh truy vấn ở luồng phụ."""
        logger.info("Bắt đầu tải bản vẽ ngầm cho dự án: %s", self.project_id)
        db = SessionLocal()
        try:
            drawings = drawing_service.get_project_drawings(db, self.project_id)

            # Bóc tách sang danh sách dict thô để truyền an toàn qua Signal,
            # tránh DetachedInstanceError khi session bị đóng.
            raw_drawings = []
            for d in drawings:
                raw_drawings.append(
                    {
                        "drawing_id": d.drawing_id,
                        "drawing_name": d.drawing_name,
                        "notes": d.notes or "",
                        "status": d.status,
                        "current_version": d.current_version,
                        "drive_link": d.drive_link,
                        "updated_at": d.updated_at,
                        "section_name": d.section.section_name if d.section else "",
                        "section_designer_email": (
                            d.section.designer_email if d.section else ""
                        )
                        or "",
                        "project_sales_email": (
                            d.project.sales_email if d.project else ""
                        )
                        or "",
                    }
                )

            logger.info(
                "Tải xong bản vẽ ngầm cho dự án: %s (Tìm thấy %d bản vẽ)",
                self.project_id,
                len(raw_drawings),
            )
            self.finished.emit(raw_drawings)
        except Exception as e:
            logger.error(
                "Lỗi trong lúc truy vấn bản vẽ ở luồng phụ cho dự án '%s': %s",
                self.project_id,
                str(e),
                exc_info=True,
            )
            self.error.emit(str(e))
        finally:
            db.close()


class DriveUploadWorker(QThread):
    """Luồng phụ chuyên trách upload file hoặc thư mục lên Google Drive ngầm.

    Giúp giao diện không bị treo đơ (Not Responding) khi đang upload các bản vẽ PDF
    hoặc thư mục bản vẽ dung lượng lớn lên Google Drive qua mạng.
    """

    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, local_path: str, parent_folder_id: str) -> None:
        """Khởi tạo luồng upload.

        Args:
            local_path: Đường dẫn file hoặc thư mục cục bộ cần upload.
            parent_folder_id: ID thư mục Google Drive đích.
        """
        super().__init__()
        self.local_path = local_path
        self.parent_folder_id = parent_folder_id

    def run(self) -> None:
        """Thực thi upload ở luồng phụ."""
        import os
        from core.services import drive_service

        logger.info(
            "DriveUploadWorker: Bắt đầu tải lên Google Drive. Nguồn cục bộ='%s', Thư mục đích='%s'",
            self.local_path,
            self.parent_folder_id,
        )
        try:
            if not self.local_path or not os.path.exists(self.local_path):
                self.error.emit("Đường dẫn tệp tin hoặc thư mục cục bộ không tồn tại.")
                return

            if not self.parent_folder_id:
                self.error.emit(
                    "Chưa cấu hình ID thư mục Google Drive đích (GOOGLE_DRIVE_FOLDER_ID)."
                )
                return

            self.progress.emit(
                "Đang kết nối tới Google Drive API và tải lên dữ liệu..."
            )

            if os.path.isdir(self.local_path):
                link = drive_service.upload_local_directory(
                    self.local_path, self.parent_folder_id
                )
            else:
                link = drive_service.upload_single_file(
                    self.local_path, self.parent_folder_id
                )

            if link:
                logger.info("DriveUploadWorker: Tải lên thành công. Link='%s'", link)
                self.finished.emit(link)
            else:
                logger.error(
                    "DriveUploadWorker: Upload thất bại (Drive API trả về None)."
                )
                self.error.emit(
                    "Đã xảy ra lỗi trong quá trình upload lên Google Drive. Vui lòng kiểm tra lại log."
                )
        except Exception as e:
            logger.error(
                "DriveUploadWorker: Lỗi nghiêm trọng trong luồng upload: %s",
                str(e),
                exc_info=True,
            )
            self.error.emit(str(e))


class ReportLoaderThread(QThread):
    """Luồng chạy ngầm để nạp dữ liệu báo cáo bất đồng bộ tránh gây treo UI."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, project_id: str, user_email: str) -> None:
        """Khởi tạo ReportLoaderThread.

        Args:
            project_id: Mã dự án.
            user_email: Email người dùng đăng nhập.
        """
        super().__init__()
        self.project_id = project_id
        self.user_email = user_email

    def run(self) -> None:
        """Thực thi luồng nạp dữ liệu thống kê từ PostgreSQL."""
        try:
            from core.services.report_service import (
                get_drawing_status_stats_safe,
                get_section_drawing_stats_safe,
                get_designer_productivity_stats_safe,
                get_release_timeline_stats_safe,
                get_drawing_download_summary_safe,
            )

            stats = {
                "status": get_drawing_status_stats_safe(
                    self.project_id, self.user_email
                ),
                "sections": get_section_drawing_stats_safe(
                    self.project_id, self.user_email
                ),
                "designers": get_designer_productivity_stats_safe(
                    self.project_id, self.user_email
                ),
                "timeline": get_release_timeline_stats_safe(
                    self.project_id, self.user_email
                ),
                "downloads": get_drawing_download_summary_safe(
                    self.project_id, self.user_email
                ),
            }
            self.finished.emit(stats)
        except Exception as e:
            logger.error(
                "ReportLoaderThread: Lỗi nạp dữ liệu: %s", str(e), exc_info=True
            )
            self.error.emit(str(e))

