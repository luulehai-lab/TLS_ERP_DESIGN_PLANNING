# Tên file: core/services/drawing_service.py
# CHỨC NĂNG: Xử lý các nghiệp vụ Quản lý bản vẽ (Drawing) và Nhật ký bản vẽ (DrawingLog)
# CHANGELOG:
# - 10:57:17 15/07/2026: [REFACTOR] refactor(report): modularize report service and implement visual drawing timeline (Antigravity)
# - 10:45:00 15/07/2026: [UPDATE] Sử dụng kwargs để khởi tạo Drawing một cách an toàn nhằm bỏ qua released_at khi chưa di trú thành công (Lê Thanh Vân/Antigravity)
# - 09:58:00 15/07/2026: [UPDATE] Cập nhật get_project_drawings tự động phân tích DrawingLog để lấy chính xác thời gian ban hành/chuyển xưởng khi chưa di trú thành công (Lê Thanh Vân/Antigravity)
# - 09:50:00 15/07/2026: [UPDATE] Kiểm tra cờ HAS_RELEASED_AT / HAS_FACTORY_TRANSFERRED_AT trước khi gán để tránh lỗi crash khi lưu dữ liệu (Lê Thanh Vân/Antigravity)
# - 09:10:00 15/07/2026: [UPDATE] Cập nhật create_drawing, revise_drawing và update_drawing_status để lưu released_at và factory_transferred_at (Lê Thanh Vân/Antigravity)
# - 11:39:58 14/07/2026: [FIX] fix(drawing-ui): click on drive link column to open in browser for download (Antigravity)
# - 11:25:00 14/07/2026: [NEW] Bổ sung các hàm ghi log lượt mở liên kết tải bản vẽ (Lê Thanh Vân/Antigravity)
# - 14:58:03 13/07/2026: [UPDATE] feat(project-ui): support local_path attribute for projects and auto open path on drawing release (Antigravity)
# - 18:09:38 11/07/2026: [UPDATE] feat(drawing-ui): add version input field to drawing release form and update backend (Antigravity)
# - 18:03:00 11/07/2026: [UPDATE] Bổ sung hàm revise_drawing và revise_drawing_safe hỗ trợ cập nhật phiên bản (Lê Thanh Vân/Antigravity)
# - 17:59:58 11/07/2026: [FIX] fix(staff-ui): resolve AttributeError by calling reload_planners on save and delete (Antigravity)
# - 17:50:00 11/07/2026: [UPDATE] Bổ sung trường current_version khi ban hành bản vẽ mới (Lê Thanh Vân/Antigravity)
# - 14:34:36 11/07/2026: [REFACTOR] refactor(ui-modularity): complete modular refactoring of codebase graph tools and adopt UI-Backend Separation rules (Antigravity)
# - 14:30:00 11/07/2026: [UPDATE] Thêm xử lý trường notes khi ban hành bản vẽ (Antigravity)
# - 18:19:45 08/07/2026: [UPDATE] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [UPDATE] Cập nhật create_drawing hỗ trợ section_id và get_project_drawings sử dụng joinedload tối ưu (Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:15:00 02/07/2026: [NEW] Khởi tạo tầng dịch vụ quản lý bản vẽ và logs (Lê Thanh Vân/Antigravity)

from datetime import datetime
import logging
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models import Drawing, DrawingLog, ProjectSection

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
            - "notes" (str, optional): Ghi chú kỹ thuật khi ban hành.

    Returns:
        Drawing | None: Đối tượng Drawing được tạo mới, hoặc None nếu thất bại.
    """
    drawing_id = drawing_data.get("drawing_id", "")
    drawing_name = drawing_data.get("drawing_name", "")
    drive_link = drawing_data.get("drive_link")
    notes = drawing_data.get("notes")
    section_id = drawing_data.get("section_id")
    version = drawing_data.get("current_version", "V1") or "V1"

    logger.info(
        "Yêu cầu ban hành bản vẽ mới: ProjectID=%s, DrawingID=%s, Name=%s, SectionID=%s, Version=%s",
        project_id,
        drawing_id,
        drawing_name,
        section_id,
        version,
    )
    try:
        # Kiểm tra trùng lặp bản vẽ
        existing = db.query(Drawing).filter(Drawing.drawing_id == drawing_id).first()
        if existing:
            logger.warning(
                "Không thể tạo bản vẽ. Bản vẽ ID '%s' đã tồn tại.", drawing_id
            )
            return existing

        from core.database import HAS_RELEASED_AT

        drawing_kwargs = {
            "drawing_id": drawing_id,
            "project_id": project_id,
            "drawing_name": drawing_name,
            "notes": notes,
            "drive_link": drive_link,
            "current_version": version,
            "status": "Chờ triển khai",
            "section_id": section_id,
        }
        if HAS_RELEASED_AT:
            drawing_kwargs["released_at"] = datetime.utcnow()

        db_drawing = Drawing(**drawing_kwargs)
        db.add(db_drawing)

        # Ghi log lịch sử ban hành bản vẽ lần đầu
        db_log = DrawingLog(
            drawing_id=drawing_id,
            version=version,
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
        if status == "Đang sản xuất":
            from core.database import HAS_FACTORY_TRANSFERRED_AT

            if HAS_FACTORY_TRANSFERRED_AT:
                drawing.factory_transferred_at = datetime.utcnow()

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
    """Lấy toàn bộ danh sách bản vẽ của một dự án cụ thể, sắp xếp theo hạng mục và mã bản vẽ.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần lấy danh sách bản vẽ.

    Returns:
        list[Drawing]: Danh sách bản vẽ tìm thấy của dự án.
    """
    logger.debug("Lấy danh sách bản vẽ của dự án ID=%s", project_id)
    try:
        from sqlalchemy.orm import joinedload

        drawings = (
            db.query(Drawing)
            .outerjoin(ProjectSection, Drawing.section_id == ProjectSection.section_id)
            .filter(Drawing.project_id == project_id)
            .options(joinedload(Drawing.section))
            .order_by(
                ProjectSection.section_code.asc().nulls_last(),
                Drawing.drawing_id.asc(),
            )
            .all()
        )

        # Điền động released_at và factory_transferred_at từ DrawingLog nếu chưa di trú thành công hoặc giá trị trên DB bị NULL (đối với các bản vẽ cũ)
        from core.database import HAS_RELEASED_AT, HAS_FACTORY_TRANSFERRED_AT

        # Lọc ra các bản vẽ cần nạp động thông tin lịch sử
        need_fallback_drawings = [
            d
            for d in drawings
            if (not HAS_RELEASED_AT or d.__dict__.get("released_at") is None)
            or (
                not HAS_FACTORY_TRANSFERRED_AT
                or d.__dict__.get("factory_transferred_at") is None
            )
        ]

        if need_fallback_drawings:
            drawing_ids = [d.drawing_id for d in need_fallback_drawings]
            if drawing_ids:
                from core.models import DrawingLog

                # Lấy tất cả logs của các bản vẽ này
                all_logs = (
                    db.query(DrawingLog)
                    .filter(DrawingLog.drawing_id.in_(drawing_ids))
                    .order_by(DrawingLog.timestamp.asc())
                    .all()
                )

                # Gom log theo từng drawing_id
                logs_by_drawing = {}
                for log in all_logs:
                    logs_by_drawing.setdefault(log.drawing_id, []).append(log)

                # Phân tích log để lấy thời gian ban hành và chuyển xưởng
                for d in need_fallback_drawings:
                    d_logs = logs_by_drawing.get(d.drawing_id, [])

                    # 1. Thời gian Ban hành (released_at)
                    if not HAS_RELEASED_AT or d.__dict__.get("released_at") is None:
                        ban_hanh_log = None
                        for log in d_logs:
                            if (
                                "Ban hành" in log.action
                                or "Khởi tạo" in log.action
                                or "Nâng cấp" in log.action
                            ):
                                ban_hanh_log = log
                                break
                        if not ban_hanh_log and d_logs:
                            ban_hanh_log = d_logs[0]
                        # Gán thẳng vào __dict__ để tránh lazy loading crash và tránh đánh dấu dirty
                        d.__dict__["released_at"] = (
                            ban_hanh_log.timestamp if ban_hanh_log else d.updated_at
                        )

                    # 2. Thời gian chuyển xưởng (factory_transferred_at)
                    if (
                        not HAS_FACTORY_TRANSFERRED_AT
                        or d.__dict__.get("factory_transferred_at") is None
                    ):
                        chuyen_xuong_log = None
                        for log in d_logs:
                            if (
                                "Đang sản xuất" in log.action
                                or "Chuyển trạng thái -> Đang sản xuất" in log.action
                            ):
                                chuyen_xuong_log = log
                                break
                        d.__dict__["factory_transferred_at"] = (
                            chuyen_xuong_log.timestamp if chuyen_xuong_log else None
                        )

        return drawings
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi cơ sở dữ liệu khi truy vấn danh sách bản vẽ dự án ID '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def create_drawing_safe(
    project_id: str, drawing_data: dict[str, str]
) -> Drawing | None:
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


def get_drawing(db: Session, drawing_id: str) -> Drawing | None:
    """Lấy thông tin chi tiết một bản vẽ dựa vào ID.

    Args:
        db: Session kết nối database hiện thời.
        drawing_id: Mã bản vẽ cần tìm.

    Returns:
        Drawing | None: Đối tượng Drawing tìm thấy, hoặc None.
    """
    try:
        return db.query(Drawing).filter(Drawing.drawing_id == drawing_id).first()
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi cơ sở dữ liệu khi truy vấn bản vẽ ID '%s': %s",
            drawing_id,
            str(e),
            exc_info=True,
        )
        return None


def get_drawing_safe(drawing_id: str) -> Drawing | None:
    """Lấy thông tin bản vẽ tự động quản lý vòng đời Session (Safe).

    Args:
        drawing_id: Mã bản vẽ.

    Returns:
        Drawing đối tượng hoặc None.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_drawing(db, drawing_id)
    finally:
        db.close()


def revise_drawing(
    db: Session, drawing_id: str, revise_data: dict[str, Any]
) -> Drawing | None:
    """Nâng cấp phiên bản (Revise) bản vẽ đã tồn tại trên hệ thống.

    Args:
        db: Session kết nối database hiện thời.
        drawing_id: Mã bản vẽ cần nâng cấp phiên bản.
        revise_data: Từ điển chứa thông tin phiên bản mới bao gồm:
            - "current_version" (str): Mã phiên bản mới.
            - "drive_link" (str, optional): Đường link Google Drive chứa file PDF bản vẽ mới.
            - "notes" (str, optional): Ghi chú lý do thay đổi phiên bản.
            - "performed_by" (str): Người thực hiện hành động này.

    Returns:
        Drawing | None: Đối tượng Drawing sau khi nâng cấp, hoặc None nếu thất bại.
    """
    version = revise_data.get("current_version", "V2")
    drive_link = revise_data.get("drive_link")
    notes = revise_data.get("notes")
    performed_by = revise_data.get("performed_by", "Kỹ sư Thiết kế")

    logger.info(
        "Yêu cầu nâng cấp phiên bản bản vẽ ID=%s lên %s bởi %s",
        drawing_id,
        version,
        performed_by,
    )
    try:
        drawing = db.query(Drawing).filter(Drawing.drawing_id == drawing_id).first()
        if not drawing:
            logger.warning(
                "Không tìm thấy bản vẽ ID '%s' để nâng cấp phiên bản.", drawing_id
            )
            return None

        # Lưu lại thông tin phiên bản cũ vào log trước khi cập nhật đè
        old_version = drawing.current_version
        old_link = drawing.drive_link or "Không có link"

        # Cập nhật thông tin bản vẽ
        drawing.current_version = version
        if drive_link is not None:
            drawing.drive_link = drive_link
        if notes is not None:
            drawing.notes = notes
        drawing.status = "Chờ triển khai"  # Reset về chờ triển khai
        from core.database import HAS_RELEASED_AT

        if HAS_RELEASED_AT:
            drawing.released_at = datetime.utcnow()

        # Ghi log lịch sử thay đổi phiên bản
        db_log = DrawingLog(
            drawing_id=drawing_id,
            version=version,
            action=f"Nâng cấp phiên bản: {old_version} -> {version}",
            performed_by=performed_by,
            note=f"Link cũ: {old_link}. Ghi chú mới: {notes or ''}",
        )
        db.add(db_log)

        db.commit()
        db.refresh(drawing)
        logger.info(
            "Nâng cấp phiên bản bản vẽ thành công: ID=%s, Version=%s",
            drawing_id,
            version,
        )
        return drawing
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi nâng cấp phiên bản bản vẽ ID '%s': %s",
            drawing_id,
            str(e),
            exc_info=True,
        )
        return None


def revise_drawing_safe(drawing_id: str, revise_data: dict[str, Any]) -> Drawing | None:
    """Nâng cấp phiên bản bản vẽ tự động quản lý vòng đời Session (Safe).

    Args:
        drawing_id: Mã bản vẽ.
        revise_data: Từ điển chứa dữ liệu nâng cấp phiên bản.

    Returns:
        Drawing đối tượng sau khi nâng cấp hoặc None.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return revise_drawing(db, drawing_id, revise_data)
    finally:
        db.close()


def log_drawing_download(
    db: Session, drawing_id: str, performed_by: str, note: str = ""
) -> DrawingLog | None:
    """Ghi log lịch sử mở liên kết Drive tải bản vẽ.

    Args:
        db: Session kết nối database hiện thời.
        drawing_id: Mã bản vẽ.
        performed_by: Email người thực hiện hành động.
        note: Ghi chú bổ sung.

    Returns:
        DrawingLog | None: Đối tượng DrawingLog được tạo hoặc None.
    """
    logger.info(
        "Ghi log tải bản vẽ: ID=%s, User=%s",
        drawing_id,
        performed_by,
    )
    try:
        # Lấy phiên bản hiện tại từ DB
        drawing = db.query(Drawing).filter(Drawing.drawing_id == drawing_id).first()
        version = drawing.current_version if drawing else "V1"

        db_log = DrawingLog(
            drawing_id=drawing_id,
            version=version,
            action="Mở liên kết Drive",
            performed_by=performed_by,
            note=note,
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi ghi log tải bản vẽ ID '%s' bởi '%s': %s",
            drawing_id,
            performed_by,
            str(e),
            exc_info=True,
        )
        return None


def log_drawing_download_safe(
    drawing_id: str, performed_by: str, note: str = ""
) -> DrawingLog | None:
    """Ghi log tải bản vẽ an toàn tự động đóng mở Session.

    Args:
        drawing_id: Mã bản vẽ.
        performed_by: Email người thực hiện.
        note: Ghi chú bổ sung.

    Returns:
        DrawingLog | None: Đối tượng log được tạo hoặc None.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return log_drawing_download(db, drawing_id, performed_by, note)
    finally:
        db.close()
