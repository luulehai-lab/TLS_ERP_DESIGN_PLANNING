# Tên file: core/services/section_service.py
# CHỨC NĂNG: Cung cấp các nghiệp vụ CRUD quản lý Hạng mục Dự án (ProjectSection)
# CHANGELOG:
# - 18:19:45 08/07/2026: [NEW] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [NEW] Khởi tạo tầng dịch vụ quản lý Hạng mục Dự án (Antigravity)

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models import ProjectSection

logger = logging.getLogger(__name__)


def create_section(
    db: Session, project_id: str, section_code: str, section_name: str
) -> ProjectSection | None:
    """Tạo mới một hạng mục dự án trong cơ sở dữ liệu.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án liên kết.
        section_code: Kí hiệu hạng mục (ví dụ: NX1, NX2).
        section_name: Tên hạng mục chi tiết (ví dụ: Nhà xưởng 1).

    Returns:
        ProjectSection | None: Hạng mục được tạo mới hoặc None nếu thất bại.
    """
    logger.info(
        "Yêu cầu tạo hạng mục mới: ProjectID=%s, Code=%s, Name=%s",
        project_id,
        section_code,
        section_name,
    )
    try:
        # Kiểm tra xem mã hạng mục trong dự án này đã tồn tại hay chưa
        existing = (
            db.query(ProjectSection)
            .filter(
                ProjectSection.project_id == project_id,
                ProjectSection.section_code == section_code,
            )
            .first()
        )
        if existing:
            logger.warning(
                "Hạng mục có mã '%s' đã tồn tại trong dự án '%s'.",
                section_code,
                project_id,
            )
            return existing

        db_section = ProjectSection(
            project_id=project_id,
            section_code=section_code,
            section_name=section_name,
        )
        db.add(db_section)
        db.commit()
        db.refresh(db_section)
        logger.info("Tạo hạng mục thành công: Code=%s", section_code)
        return db_section
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi tạo hạng mục code '%s': %s",
            section_code,
            str(e),
            exc_info=True,
        )
        return None


def list_project_sections(db: Session, project_id: str) -> list[ProjectSection]:
    """Lấy danh sách các hạng mục thuộc một dự án nhất định.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần lấy danh sách hạng mục.

    Returns:
        list[ProjectSection]: Danh sách các hạng mục tìm thấy.
    """
    logger.debug("Lấy danh sách hạng mục của dự án: %s", project_id)
    try:
        return (
            db.query(ProjectSection)
            .filter(ProjectSection.project_id == project_id)
            .order_by(ProjectSection.section_code)
            .all()
        )
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi cơ sở dữ liệu khi lấy danh sách hạng mục dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return []


def delete_section(db: Session, section_id: int) -> bool:
    """Xóa một hạng mục ra khỏi hệ thống theo ID.

    Args:
        db: Session kết nối database hiện thời.
        section_id: Khóa chính của hạng mục cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu thất bại.
    """
    logger.info("Yêu cầu xóa hạng mục: ID=%d", section_id)
    try:
        section = (
            db.query(ProjectSection)
            .filter(ProjectSection.section_id == section_id)
            .first()
        )
        if not section:
            logger.warning("Không tìm thấy hạng mục ID=%d để xóa.", section_id)
            return False

        db.delete(section)
        db.commit()
        logger.info("Xóa hạng mục thành công: ID=%d", section_id)
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi xóa hạng mục ID=%d: %s",
            section_id,
            str(e),
            exc_info=True,
        )
        return False
