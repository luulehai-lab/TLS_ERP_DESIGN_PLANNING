# Tên file: core/services/report_history_service.py
# CHỨC NĂNG: Cung cấp dịch vụ thống kê và chi tiết lịch sử bản vẽ (lượt tải, dòng đời)
# CHANGELOG:
# - 20:05:49 14/07/2026: [NEW] fix(drive): resolve personal Google Drive upload storage quota limit by adopting user OAuth2 credentials (Antigravity)
# - 18:10:00 14/07/2026: [NEW] Khởi tạo tệp tin dịch vụ lịch sử báo cáo để phân tách từ report_service.py tránh phình file (Lê Thanh Vân/Antigravity)

import logging
from datetime import datetime
from typing import Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.models import Drawing, DrawingLog
from core.services.report_service import _apply_permission_filter

logger = logging.getLogger(__name__)


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


def _parse_drawing_lifecycle_logs(
    logs: list[DrawingLog],
) -> tuple[datetime | None, str, datetime | None, str, datetime | None, str]:
    """Phân tích danh sách log của bản vẽ để trích xuất các mốc thời gian.

    Args:
        logs: Danh sách DrawingLog xếp theo thứ tự tăng dần.

    Returns:
        tuple: (issued_at, issued_by, factory_at, factory_by, completed_at, completed_by)
    """
    issued_at = None
    issued_by = ""
    factory_at = None
    factory_by = ""
    completed_at = None
    completed_by = ""

    for log in logs:
        action = log.action or ""
        # Chuyển UTC sang giờ Việt Nam (+7) để hiển thị trực quan chính xác
        from datetime import timedelta

        log_time_vn = log.timestamp + timedelta(hours=7) if log.timestamp else None

        if "Ban hành" in action or "Khởi tạo" in action or "Nâng cấp" in action:
            issued_at = log_time_vn
            issued_by = log.performed_by
        elif (
            "Chuyển trạng thái -> Đang sản xuất" in action
            or action == "Xác nhận đã chuyển xuống xưởng"
        ):
            factory_at = log_time_vn
            factory_by = log.performed_by
        elif "Chuyển trạng thái -> Đã hoàn thành" in action:
            completed_at = log_time_vn
            completed_by = log.performed_by

    return (
        issued_at,
        issued_by,
        factory_at,
        factory_by,
        completed_at,
        completed_by,
    )


def get_drawing_lifecycle_history(
    db: Session, project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Truy vấn danh sách bản vẽ kèm lịch sử mốc thời gian (Ban hành, Chuyển xưởng, Hoàn thành) phục vụ báo cáo trực quan.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần thống kê.
        user_email: Email người dùng đăng nhập để lọc quyền.

    Returns:
        list[dict[str, Any]]: Danh sách bản vẽ kèm mốc thời gian dòng đời.
    """
    logger.info(
        "Lấy lịch sử dòng đời bản vẽ: ProjectID=%s, Email=%s",
        project_id,
        user_email,
    )
    try:
        query = db.query(Drawing)
        query = _apply_permission_filter(db, query, project_id, user_email)
        drawings = query.all()

        result = []
        for d in drawings:
            logs = (
                db.query(DrawingLog)
                .filter(DrawingLog.drawing_id == d.drawing_id)
                .order_by(DrawingLog.timestamp.asc())
                .all()
            )

            # Phân tích log lấy các mốc
            (
                issued_at,
                issued_by,
                factory_at,
                factory_by,
                completed_at,
                completed_by,
            ) = _parse_drawing_lifecycle_logs(logs)

            # Fallback nếu trạng thái hiện tại là Đang sản xuất hoặc Đã hoàn thành nhưng không tìm thấy log chuyển trạng thái
            from datetime import timedelta

            vn_now = (
                d.updated_at + timedelta(hours=7)
                if d.updated_at
                else datetime.utcnow() + timedelta(hours=7)
            )
            if not issued_at:
                issued_at = vn_now
                issued_by = "Kỹ sư Thiết kế"
            if d.status in ["Đang sản xuất", "Đã hoàn thành"] and not factory_at:
                factory_at = vn_now
                factory_by = "Phòng Kế hoạch"
            if d.status == "Đã hoàn thành" and not completed_at:
                completed_at = vn_now
                completed_by = "Quản đốc Xưởng"

            # Định dạng chuỗi ngày hiển thị ngắn gọn DD/MM/YY HH:MM
            issued_str = issued_at.strftime("%d/%m/%y %H:%M") if issued_at else ""
            factory_str = factory_at.strftime("%d/%m/%y %H:%M") if factory_at else ""
            completed_str = (
                completed_at.strftime("%d/%m/%y %H:%M") if completed_at else ""
            )

            result.append(
                {
                    "drawing_id": d.drawing_id,
                    "drawing_name": d.drawing_name,
                    "version": d.current_version,
                    "status": d.status,
                    "issued_at": issued_str,
                    "issued_by": issued_by,
                    "factory_at": factory_str,
                    "factory_by": factory_by,
                    "completed_at": completed_str,
                    "completed_by": completed_by,
                }
            )

        result.sort(key=lambda x: x["drawing_id"])
        return result
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi lấy lịch sử dòng đời bản vẽ dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def get_drawing_lifecycle_history_safe(
    project_id: str, user_email: str
) -> list[dict[str, Any]]:
    """Truy vấn an toàn lịch sử mốc thời gian dòng đời của bản vẽ tự động quản lý Session.

    Args:
        project_id: Mã dự án.
        user_email: Email người dùng.

    Returns:
        list[dict[str, Any]]: Danh sách dòng đời bản vẽ.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return get_drawing_lifecycle_history(db, project_id, user_email)
    finally:
        db.close()
