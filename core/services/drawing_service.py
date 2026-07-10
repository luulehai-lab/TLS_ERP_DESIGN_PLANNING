# Tên file: core/services/drawing_service.py
# CHỨC NĂNG: Xử lý các nghiệp vụ Quản lý bản vẽ (Drawing) và Nhật ký bản vẽ (DrawingLog)
# CHANGELOG:
# - 18:28:00 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 18:19:45 08/07/2026: [UPDATE] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [UPDATE] Cập nhật create_drawing hỗ trợ section_id và get_project_drawings sử dụng joinedload tối ưu (Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:15:00 02/07/2026: [NEW] Khởi tạo tầng dịch vụ quản lý bản vẽ và logs (Lê Thanh Vân/Antigravity)

import logging
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models import Drawing, DrawingLog

logger = logging.getLogger(__name__)


def create_drawing(
    db: Session, project_id: str, drawing_data: dict[str, str]
) -> Drawing | None:
    """Tạo mới bản vẽ kỹ thuật kết cấu thép thuộc một dự án cụ thể.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án sở hữu bản vẽ.
        drawing_data: Từ điển chứa thông tin bản vẽ bao gồm:
            - "drawing_id" (str): Mã bản vẽ duy nhất.
            - "drawing_name" (str): Tên bản vẽ.
            - "drive_link" (str, optional): Đường link Google Drive chứa file PDF bản vẽ.

    Returns:
        Drawing | None: Đối tượng Drawing được tạo mới, hoặc None nếu thất bại.
    """
    drawing_id = drawing_data.get("drawing_id", "")
    drawing_name = drawing_data.get("drawing_name", "")
    drive_link = drawing_data.get("drive_link")
    section_id = drawing_data.get("section_id")

    logger.info(
        "Yêu cầu ban hành bản vẽ mới: ProjectID=%s, DrawingID=%s, Name=%s, SectionID=%s",
        project_id,
        drawing_id,
        drawing_name,
        section_id,
    )
    try:
        # Kiểm tra trùng lặp bản vẽ
        existing = db.query(Drawing).filter(Drawing.drawing_id == drawing_id).first()
        if existing:
            logger.warning(
                "Không thể tạo bản vẽ. Bản vẽ ID '%s' đã tồn tại.", drawing_id
            )
            return existing

        db_drawing = Drawing(
            drawing_id=drawing_id,
            project_id=project_id,
            drawing_name=drawing_name,
            drive_link=drive_link,
            status="Chờ triển khai",
            section_id=section_id,
        )
        db.add(db_drawing)

        # Ghi log lịch sử ban hành bản vẽ lần đầu
        db_log = DrawingLog(
            drawing_id=drawing_id,
            version="V1",
            action="Ban hành",
            performed_by="Kỹ sư Thiết kế",  # Giá trị mặc định khi ban hành
            note="Khởi tạo bản vẽ và ban hành lần đầu",
        )
        db.add(db_log)

        db.commit()
        db.refresh(db_drawing)
        logger.info("Ban hành bản vẽ thành công: ID=%s", drawing_id)
        return db_drawing
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi tạo bản vẽ ID '%s': %s",
            drawing_id,
            str(e),
            exc_info=True,
        )
        return None


def update_drawing_status(
    db: Session, drawing_id: str, update_data: dict[str, Any]
) -> Drawing | None:
    """Cập nhật trạng thái bản vẽ và tự động ghi log lịch sử thay đổi (DrawingLog).

    Args:
        db: Session kết nối database hiện thời.
        drawing_id: Mã bản vẽ cần cập nhật.
        update_data: Từ điển chứa thông tin cập nhật bao gồm:
            - "status" (str): Trạng thái mới (ví dụ: "Đang sản xuất", "Đã hoàn thành").
            - "performed_by" (str): Người thực hiện hành động này.
            - "note" (str, optional): Ghi chú lý do thay đổi.

    Returns:
        Drawing | None: Đối tượng Drawing sau cập nhật, hoặc None nếu thất bại.
    """
    status = update_data.get("status", "")
    performed_by = update_data.get("performed_by", "")
    note = update_data.get("note", "")

    logger.info(
        "Yêu cầu cập nhật bản vẽ ID=%s: Trạng thái=%s, Thực hiện bởi=%s",
        drawing_id,
        status,
        performed_by,
    )
    try:
        drawing = db.query(Drawing).filter(Drawing.drawing_id == drawing_id).first()
        if not drawing:
            logger.warning("Không tìm thấy bản vẽ ID '%s' để cập nhật.", drawing_id)
            return None

        # Cập nhật trạng thái bản vẽ
        drawing.status = status

        # Ghi nhận log lịch sử thay đổi
        db_log = DrawingLog(
            drawing_id=drawing_id,
            version=drawing.current_version,
            action=f"Chuyển trạng thái -> {status}",
            performed_by=performed_by,
            note=note,
        )
        db.add(db_log)

        db.commit()
        db.refresh(drawing)
        logger.info("Cập nhật bản vẽ thành công: ID=%s", drawing_id)
        return drawing
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi cập nhật bản vẽ ID '%s': %s",
            drawing_id,
            str(e),
            exc_info=True,
        )
        return None


def get_project_drawings(db: Session, project_id: str) -> list[Drawing]:
    """Lấy toàn bộ danh sách bản vẽ của một dự án cụ thể.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần lấy danh sách bản vẽ.

    Returns:
        list[Drawing]: Danh sách bản vẽ tìm thấy của dự án.
    """
    logger.debug("Lấy danh sách bản vẽ của dự án ID=%s", project_id)
    try:
        from sqlalchemy.orm import joinedload

        return (
            db.query(Drawing)
            .filter(Drawing.project_id == project_id)
            .options(joinedload(Drawing.section))
            .all()
        )
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi cơ sở dữ liệu khi truy vấn danh sách bản vẽ dự án ID '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def create_drawing_safe(project_id: str, drawing_data: dict[str, str]) -> Drawing | None:
    """Tạo mới bản vẽ tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án sở hữu bản vẽ.
        drawing_data: Từ điển chứa thông tin bản vẽ.

    Returns:
        Drawing đối tượng được tạo mới hoặc None.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return create_drawing(db, project_id, drawing_data)
    finally:
        db.close()


def get_project_drawings_safe(project_id: str) -> list[Drawing]:
    """Lấy danh sách bản vẽ của dự án tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án.

    Returns:
        Danh sách bản vẽ tìm thấy.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_project_drawings(db, project_id)
    finally:
        db.close()

