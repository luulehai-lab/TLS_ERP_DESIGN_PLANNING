# Tên file: core/services/report_service.py
# CHỨC NĂNG: Cung cấp các dịch vụ truy vấn và thống kê dữ liệu báo cáo (có phân quyền)
# CHANGELOG:
# - 11:39:58 14/07/2026: [FIX] fix(drawing-ui): click on drive link column to open in browser for download (Antigravity)
# - 11:26:00 14/07/2026: [NEW] Bổ sung dịch vụ thống kê tổng lượt tải và lịch sử chi tiết của bản vẽ (Lê Thanh Vân/Antigravity)
# - 18:49:30 11/07/2026: [NEW] feat(drawing-version-qr): implement drawing revision logic and dynamic QR code panel (Antigravity)
# - 18:15:00 11/07/2026: [NEW] Khởi tạo tầng dịch vụ báo cáo report_service.py (Lê Thanh Vân/Antigravity)

import logging
from datetime import datetime
from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.models import Drawing, ProjectSection, DrawingLog, Staff

logger = logging.getLogger(__name__)


def _apply_permission_filter(
    db: Session, query: Any, project_id: str, user_email: str
) -> Any:
    """Helper nội bộ áp dụng bộ lọc phân quyền 2 tầng cho truy vấn Drawing.

    Args:
        db: Session DB.
        query: Query SQLAlchemy hiện hành trên model Drawing.
        project_id: Mã dự án.
        user_email: Email người dùng đăng nhập.

    Returns:
        Query đã được apply filter phân quyền.
    """
    user_email_lower = user_email.lower()
    staff = db.query(Staff).filter(Staff.email.ilike(user_email_lower)).first()
    role = staff.role if staff else None

    # Admin hoặc Kế hoạch được quyền xem toàn bộ dữ liệu dự án
    if (
        role in ["Admin", "Kế hoạch"]
        or user_email_lower == "luu.lehai@gmail.com"
        or user_email_lower == "phongkehoachkythuat25@gmail.com"
    ):
        return query.filter(Drawing.project_id == project_id)

    # Kỹ sư Thiết kế chỉ thấy bản vẽ thuộc hạng mục mình phụ trách hoặc không gán hạng mục
    if role == "Thiết kế":
        return (
            query.filter(Drawing.project_id == project_id)
            .outerjoin(ProjectSection, Drawing.section_id == ProjectSection.section_id)
            .filter(
                (ProjectSection.designer_email.ilike(user_email_lower))
                | (Drawing.section_id.is_(None))
            )
        )

    # Vai trò khác (ví dụ: Kinh doanh) xem được toàn bộ bản vẽ của dự án họ có quyền
    return query.filter(Drawing.project_id == project_id)


def get_drawing_status_stats(
    db: Session, project_id: str, user_email: str
) -> dict[str, int]:
    """Thống kê số lượng bản vẽ theo từng trạng thái (phân quyền).

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần thống kê.
        user_email: Email người dùng đăng nhập để lọc quyền.

    Returns:
        dict[str, int]: Từ điển map giữa Trạng thái và Số lượng bản vẽ.
    """
    logger.info(
        "Thống kê trạng thái bản vẽ: ProjectID=%s, Email=%s", project_id, user_email
    )
    result = {"Chờ triển khai": 0, "Đang sản xuất": 0, "Đã hoàn thành": 0}
    try:
        query = db.query(Drawing.status, func.count(Drawing.drawing_id))
        query = _apply_permission_filter(db, query, project_id, user_email)
        stats = query.group_by(Drawing.status).all()

        for status_name, count in stats:
            if status_name in result:
                result[status_name] = count
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi thống kê trạng thái bản vẽ dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
    return result


def get_section_drawing_stats(
    db: Session, project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê số lượng bản vẽ theo trạng thái của từng Hạng mục (phân quyền).

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần thống kê.
        user_email: Email người dùng đăng nhập để lọc quyền.

    Returns:
        list[dict[str, Any]]: Danh sách thống kê của từng hạng mục.
    """
    logger.info(
        "Thống kê bản vẽ theo Hạng mục: ProjectID=%s, Email=%s",
        project_id,
        user_email,
    )
    user_email_lower = user_email.lower()
    staff = db.query(Staff).filter(Staff.email.ilike(user_email_lower)).first()
    role = staff.role if staff else None

    try:
        # Lấy danh sách hạng mục
        sec_query = db.query(ProjectSection).filter(
            ProjectSection.project_id == project_id
        )

        # Nếu là Thiết kế, chỉ lấy các hạng mục do kỹ sư này phụ trách
        if (
            role == "Thiết kế"
            and user_email_lower != "luu.lehai@gmail.com"
            and user_email_lower != "phongkehoachkythuat25@gmail.com"
        ):
            sec_query = sec_query.filter(
                ProjectSection.designer_email.ilike(user_email_lower)
            )

        sections = sec_query.all()
        sec_stats = []

        for sec in sections:
            # Query đếm số lượng bản vẽ của hạng mục này
            query = db.query(Drawing.status, func.count(Drawing.drawing_id)).filter(
                Drawing.section_id == sec.section_id
            )
            stats = query.group_by(Drawing.status).all()

            status_dict = {"Chờ triển khai": 0, "Đang sản xuất": 0, "Đã hoàn thành": 0}
            for status_name, count in stats:
                if status_name in status_dict:
                    status_dict[status_name] = count

            sec_stats.append(
                {
                    "section_code": sec.section_code,
                    "section_name": sec.section_name,
                    "stats": status_dict,
                }
            )

        # Thêm mục "Chung" (không gán hạng mục) nếu có bản vẽ
        unassigned_query = db.query(
            Drawing.status, func.count(Drawing.drawing_id)
        ).filter(Drawing.project_id == project_id, Drawing.section_id.is_(None))
        unassigned_stats = unassigned_query.group_by(Drawing.status).all()

        if unassigned_stats:
            status_dict = {"Chờ triển khai": 0, "Đang sản xuất": 0, "Đã hoàn thành": 0}
            has_drawings = False
            for status_name, count in unassigned_stats:
                if status_name in status_dict:
                    status_dict[status_name] = count
                    if count > 0:
                        has_drawings = True

            if has_drawings:
                sec_stats.append(
                    {
                        "section_code": "CHUNG",
                        "section_name": "Bản vẽ chung (Chưa phân loại)",
                        "stats": status_dict,
                    }
                )

        return sec_stats
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi thống kê bản vẽ theo hạng mục dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def get_designer_productivity_stats(
    db: Session, project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê năng suất ban hành bản vẽ của các Kỹ sư Thiết kế (phân quyền).

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án.
        user_email: Email người dùng để lọc quyền.

    Returns:
        list[dict[str, Any]]: Thống kê số lượng bản vẽ thiết kế đã xử lý.
    """
    logger.info(
        "Thống kê năng suất thiết kế: ProjectID=%s, Email=%s", project_id, user_email
    )
    user_email_lower = user_email.lower()
    staff = db.query(Staff).filter(Staff.email.ilike(user_email_lower)).first()
    role = staff.role if staff else None

    try:
        # Lấy danh sách các email designer phụ trách hạng mục trong dự án này
        designer_query = (
            db.query(ProjectSection.designer_email)
            .filter(ProjectSection.project_id == project_id)
            .distinct()
        )

        # Nếu là Thiết kế, họ chỉ thấy năng suất của chính mình
        if (
            role == "Thiết kế"
            and user_email_lower != "luu.lehai@gmail.com"
            and user_email_lower != "phongkehoachkythuat25@gmail.com"
        ):
            designer_query = designer_query.filter(
                ProjectSection.designer_email.ilike(user_email_lower)
            )

        designer_emails = [r[0] for r in designer_query.all() if r[0]]

        if not designer_emails and role == "Thiết kế":
            # Đề phòng trường hợp chưa gán hạng mục nhưng designer muốn xem
            designer_emails = [user_email_lower]

        stats_list = []
        for email in designer_emails:
            email_lower = email.lower()
            # Lấy tên kỹ sư
            staff = db.query(Staff).filter(Staff.email.ilike(email_lower)).first()
            name = staff.name if staff else email.split("@")[0].capitalize()

            # Thống kê bản vẽ của designer này
            query = db.query(Drawing.status, func.count(Drawing.drawing_id)).join(
                ProjectSection, Drawing.section_id == ProjectSection.section_id
            )
            query = query.filter(
                Drawing.project_id == project_id,
                ProjectSection.designer_email.ilike(email_lower),
            )
            stats = query.group_by(Drawing.status).all()

            total = 0
            production = 0
            completed = 0
            for status_name, count in stats:
                total += count
                if status_name == "Đang sản xuất":
                    production = count
                elif status_name == "Đã hoàn thành":
                    completed = count

            stats_list.append(
                {
                    "designer_email": email_lower,
                    "designer_name": name,
                    "total": total,
                    "production": production,
                    "completed": completed,
                }
            )

        return stats_list
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi thống kê năng suất thiết kế dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def get_release_timeline_stats(
    db: Session, project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê tần suất ban hành bản vẽ theo dòng thời gian (phân quyền).

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án.
        user_email: Email người dùng để lọc quyền.

    Returns:
        list[dict[str, Any]]: Danh sách thống kê ngày và số lượng bản vẽ ban hành.
    """
    logger.info(
        "Thống kê tiến độ ban hành theo thời gian: ProjectID=%s, Email=%s",
        project_id,
        user_email,
    )
    try:
        # Query lấy log "Ban hành" của bản vẽ thuộc dự án
        query = (
            db.query(DrawingLog.timestamp)
            .join(Drawing, DrawingLog.drawing_id == Drawing.drawing_id)
            .filter(DrawingLog.action == "Ban hành")
        )
        query = _apply_permission_filter(db, query, project_id, user_email)
        logs = query.all()

        # Nhóm theo ngày (YYYY-MM-DD)
        date_counts = {}
        for (ts,) in logs:
            if isinstance(ts, datetime):
                # Chuyển UTC sang giờ Việt Nam (+7) để thống kê chính xác ngày thực tế
                from datetime import timedelta

                local_ts = ts + timedelta(hours=7)
                date_str = local_ts.strftime("%Y-%m-%d")
                date_counts[date_str] = date_counts.get(date_str, 0) + 1

        # Sắp xếp theo thứ tự ngày tăng dần
        sorted_dates = sorted(date_counts.keys())
        timeline = [{"date": d, "count": date_counts[d]} for d in sorted_dates]

        return timeline
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi thống kê tiến độ ban hành dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def get_drawing_status_stats_safe(project_id: str, user_email: str) -> dict[str, int]:
    """Thống kê trạng thái bản vẽ an toàn tự động đóng mở Session.

    Args:
        project_id: Mã dự án.
        user_email: Email người dùng.

    Returns:
        dict[str, int]: Kết quả thống kê.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_drawing_status_stats(db, project_id, user_email)
    finally:
        db.close()


def get_section_drawing_stats_safe(
    project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê hạng mục bản vẽ an toàn tự động đóng mở Session.

    Args:
        project_id: Mã dự án.
        user_email: Email người dùng.

    Returns:
        list[dict[str, Any]]: Kết quả thống kê.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_section_drawing_stats(db, project_id, user_email)
    finally:
        db.close()


def get_designer_productivity_stats_safe(
    project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê năng suất thiết kế an toàn tự động đóng mở Session.

    Args:
        project_id: Mã dự án.
        user_email: Email người dùng.

    Returns:
        list[dict[str, Any]]: Kết quả thống kê.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_designer_productivity_stats(db, project_id, user_email)
    finally:
        db.close()


def get_release_timeline_stats_safe(
    project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê tiến độ thời gian an toàn tự động đóng mở Session.

    Args:
        project_id: Mã dự án.
        user_email: Email người dùng.

    Returns:
        list[dict[str, Any]]: Kết quả thống kê.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_release_timeline_stats(db, project_id, user_email)
    finally:
        db.close()


def get_drawing_download_summary(
    db: Session, project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê tổng số lượt tải của từng bản vẽ thuộc dự án (có phân quyền).

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án.
        user_email: Email người dùng đăng nhập.

    Returns:
        list[dict[str, Any]]: Danh sách thống kê lượt tải của bản vẽ.
    """
    logger.info(
        "Truy vấn thống kê lượt tải bản vẽ: ProjectID=%s, Email=%s",
        project_id,
        user_email,
    )
    try:
        # Query các bản vẽ thuộc dự án được phân quyền
        query = db.query(Drawing)
        query = _apply_permission_filter(db, query, project_id, user_email)
        drawings = query.all()

        stats_list = []
        for d in drawings:
            # Đếm số log có action = "Mở liên kết Drive"
            count = (
                db.query(func.count(DrawingLog.log_id))
                .filter(
                    DrawingLog.drawing_id == d.drawing_id,
                    DrawingLog.action == "Mở liên kết Drive",
                )
                .scalar()
                or 0
            )
            stats_list.append(
                {
                    "drawing_id": d.drawing_id,
                    "drawing_name": d.drawing_name,
                    "version": d.current_version,
                    "download_count": count,
                }
            )
        # Sắp xếp lượt tải giảm dần, mã bản vẽ tăng dần
        stats_list.sort(key=lambda x: (-x["download_count"], x["drawing_id"]))
        return stats_list
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi thống kê lượt tải bản vẽ dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def get_drawing_download_details(db: Session, drawing_id: str) -> list[dict[str, Any]]:
    """Lấy chi tiết lịch sử các lần tải của bản vẽ cụ thể.

    Args:
        db: Session kết nối database hiện thời.
        drawing_id: Mã bản vẽ.

    Returns:
        list[dict[str, Any]]: Danh sách lịch sử chi tiết.
    """
    logger.info("Truy vấn chi tiết lượt tải của bản vẽ: ID=%s", drawing_id)
    try:
        logs = (
            db.query(DrawingLog)
            .filter(
                DrawingLog.drawing_id == drawing_id,
                DrawingLog.action == "Mở liên kết Drive",
            )
            .order_by(DrawingLog.timestamp.desc(), DrawingLog.log_id.desc())
            .all()
        )

        details = []
        for log in logs:
            # Chuyển đổi timezone UTC sang Việt Nam (+7) để hiển thị chính xác
            from datetime import timedelta

            local_time = log.timestamp + timedelta(hours=7)
            time_str = local_time.strftime("%d/%m/%y_%H:%M:%S")

            details.append(
                {
                    "performed_by": log.performed_by,
                    "timestamp": time_str,
                    "version": log.version,
                    "note": log.note or "",
                }
            )
        return details
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi lấy chi tiết lượt tải bản vẽ ID '%s': %s",
            drawing_id,
            str(e),
            exc_info=True,
        )
        return []


def get_drawing_download_summary_safe(
    project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Thống kê lượt tải bản vẽ an toàn tự động đóng mở Session.

    Args:
        project_id: Mã dự án.
        user_email: Email người dùng.

    Returns:
        list[dict[str, Any]]: Kết quả thống kê.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_drawing_download_summary(db, project_id, user_email)
    finally:
        db.close()


def get_drawing_download_details_safe(drawing_id: str) -> list[dict[str, Any]]:
    """Lấy chi tiết lượt tải bản vẽ an toàn tự động đóng mở Session.

    Args:
        drawing_id: Mã bản vẽ.

    Returns:
        list[dict[str, Any]]: Kết quả lịch sử chi tiết.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_drawing_download_details(db, drawing_id)
    finally:
        db.close()
