# Tên file: core/services/section_service.py
# CHỨC NĂNG: Cung cấp các nghiệp vụ CRUD quản lý Hạng mục Dự án (ProjectSection)
# CHANGELOG:
# - 18:28:00 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 15:24:09 10/07/2026: [UPDATE] feat(auth): support auto login with SessionManager (Antigravity)
# - 15:20:00 10/07/2026: [UPDATE] Thêm hàm update_section để chỉnh sửa thông tin hạng mục (Lê Thanh Vân/Antigravity)
# - 15:15:00 10/07/2026: [UPDATE] Cập nhật create_section nhận details chứa vai trò designer_email (Lê Thanh Vân/Antigravity)
# - 18:19:45 08/07/2026: [NEW] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:08:00 08/07/2026: [NEW] Khởi tạo tầng dịch vụ quản lý Hạng mục Dự án (Antigravity)

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models import ProjectSection

logger = logging.getLogger(__name__)


def create_section(
    db: Session,
    project_id: str,
    details: dict[str, str | None],
) -> ProjectSection | None:
    """Tạo mới một hạng mục dự án trong cơ sở dữ liệu.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án liên kết.
        details: Dictionary chứa thông tin hạng mục ('code', 'name', 'designer').

    Returns:
        ProjectSection | None: Hạng mục được tạo mới hoặc None nếu thất bại.
    """
    section_code = details.get("code", "").strip()
    section_name = details.get("name", "").strip()
    designer_email = details.get("designer")

    logger.info(
        "Yêu cầu tạo hạng mục mới: ProjectID=%s, Code=%s, Name=%s, Designer=%s",
        project_id,
        section_code,
        section_name,
        designer_email,
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
            designer_email=designer_email,
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


def update_section(
    db: Session,
    section_id: int,
    details: dict[str, str | None],
) -> ProjectSection | None:
    """Cập nhật thông tin chi tiết của hạng mục dự án hiện có.

    Args:
        db: Session kết nối database hiện thời.
        section_id: Khóa chính của hạng mục cần cập nhật.
        details: Dictionary chứa thông tin hạng mục ('name', 'designer').

    Returns:
        ProjectSection | None: Đối tượng ProjectSection sau khi cập nhật, hoặc None nếu thất bại.
    """
    section_name = details.get("name", "").strip()
    designer_email = details.get("designer")

    logger.info(
        "Yêu cầu cập nhật hạng mục: ID=%d, Name=%s, Designer=%s",
        section_id,
        section_name,
        designer_email,
    )
    try:
        section = (
            db.query(ProjectSection)
            .filter(ProjectSection.section_id == section_id)
            .first()
        )
        if not section:
            logger.warning("Không tìm thấy hạng mục ID=%d để cập nhật.", section_id)
            return None

        section.section_name = section_name
        section.designer_email = designer_email

        db.commit()
        db.refresh(section)
        logger.info("Cập nhật hạng mục thành công: ID=%d", section_id)
        return section
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi cập nhật hạng mục ID=%d: %s",
            section_id,
            str(e),
            exc_info=True,
        )
        return None


def list_project_sections_safe(project_id: str) -> list[ProjectSection]:
    """Lấy danh sách hạng mục tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án cần lấy danh sách hạng mục.

    Returns:
        Danh sách các hạng mục tìm thấy.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return list_project_sections(db, project_id)
    finally:
        db.close()


def delete_section_safe(section_id: int) -> bool:
    """Xóa hạng mục tự động quản lý vòng đời Session (Safe).

    Args:
        section_id: Khóa chính hạng mục cần xóa.

    Returns:
        True nếu xóa thành công, ngược lại False.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return delete_section(db, section_id)
    finally:
        db.close()


def create_section_safe(
    project_id: str, code: str, name: str, designer: str | None
) -> ProjectSection | None:
    """Tạo hạng mục mới tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án liên kết.
        code: Mã hạng mục mới.
        name: Tên hạng mục mới.
        designer: Email thiết kế phụ trách.

    Returns:
        Hạng mục được tạo hoặc None nếu lỗi.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return create_section(
            db, project_id, {"code": code, "name": name, "designer": designer}
        )
    finally:
        db.close()


def update_section_safe(
    section_id: int, name: str, designer: str | None
) -> ProjectSection | None:
    """Cập nhật hạng mục tự động quản lý vòng đời Session (Safe).

    Args:
        section_id: Khóa chính hạng mục.
        name: Tên mới của hạng mục.
        designer: Email thiết kế phụ trách mới.

    Returns:
        Đối tượng sau khi cập nhật hoặc None.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return update_section(db, section_id, {"name": name, "designer": designer})
    finally:
        db.close()

