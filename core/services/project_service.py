# Tên file: core/services/project_service.py
# CHỨC NĂNG: Cung cấp các nghiệp vụ CRUD quản lý Dự án (Project)
# CHANGELOG:
# - 16:38:10 11/07/2026: [UPDATE] test(ke-hoach): add UI unit tests for performer combobox validation (Antigravity)
# - 15:17:43 11/07/2026: [UPDATE] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 14:57:00 11/07/2026: [UPDATE] Eager load sections trong list_active_projects cho phân quyền (Antigravity)
# - 15:33:49 10/07/2026: [UPDATE] feat(ui): add edit mode and designer roles for projects and sections (Antigravity)
# - 15:28:00 10/07/2026: [UPDATE] Thêm hàm delete_project để xóa dự án theo ID (Lê Thanh Vân/Antigravity)
# - 15:24:09 10/07/2026: [UPDATE] feat(auth): support auto login with SessionManager (Antigravity)
# - 15:03:00 10/07/2026: [UPDATE] Thêm hàm update_project để chỉnh sửa thông tin dự án (Lê Thanh Vân/Antigravity)
# - 14:55:00 10/07/2026: [UPDATE] Cập nhật create_project nhận thêm sales_email và designer_email (Lê Thanh Vân/Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:12:00 02/07/2026: [NEW] Khởi tạo tầng dịch vụ quản lý dự án (Lê Thanh Vân/Antigravity)

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models import Project

logger = logging.getLogger(__name__)


def create_project(
    db: Session,
    project_id: str,
    project_name: str,
    roles: dict[str, str | None] | None = None,
) -> Project | None:
    """Tạo mới một dự án kết cấu thép trong cơ sở dữ liệu.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã định danh duy nhất của dự án (ví dụ: TLS-01726).
        project_name: Tên chi tiết của dự án.
        roles: Dictionary chứa thông tin vai trò, ví dụ: {'sales': email, 'designer': email}.

    Returns:
        Project: Đối tượng Project được tạo mới nếu thành công, hoặc None nếu thất bại.
    """
    logger.info(
        "Yêu cầu tạo dự án mới: ID=%s, Name=%s, Roles=%s",
        project_id,
        project_name,
        roles,
    )
    sales_email = roles.get("sales") if roles else None
    designer_email = roles.get("designer") if roles else None

    try:
        # Kiểm tra xem dự án đã tồn tại hay chưa
        existing = db.query(Project).filter(Project.project_id == project_id).first()
        if existing:
            logger.warning(
                "Không thể tạo dự án. Dự án có ID '%s' đã tồn tại.", project_id
            )
            return existing

        db_project = Project(
            project_id=project_id,
            project_name=project_name,
            sales_email=sales_email,
            designer_email=designer_email,
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        logger.info("Tạo dự án thành công: ID=%s", project_id)
        return db_project
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi tạo dự án ID '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return None


def get_project(db: Session, project_id: str) -> Project | None:
    """Tìm kiếm dự án theo ID duy nhất.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần tìm kiếm.

    Returns:
        Project | None: Đối tượng Project tìm thấy, hoặc None nếu không tồn tại.
    """
    logger.debug("Truy vấn dự án: ID=%s", project_id)
    try:
        return db.query(Project).filter(Project.project_id == project_id).first()
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi cơ sở dữ liệu khi tìm kiếm dự án ID '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return None


def list_active_projects(db: Session) -> list[Project]:
    """Lấy danh sách các dự án đang chạy hoặc mới khởi tạo (không bao gồm dự án đã hoàn thành).

    Args:
        db: Session kết nối database hiện thời.

    Returns:
        list[Project]: Danh sách các dự án thỏa mãn điều kiện.
    """
    logger.debug("Lấy danh sách dự án đang hoạt động")
    try:
        from sqlalchemy.orm import joinedload

        return (
            db.query(Project)
            .filter(Project.status != "Hoàn thành")
            .options(joinedload(Project.sections))
            .all()
        )
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi cơ sở dữ liệu khi lấy danh sách dự án: %s", str(e), exc_info=True
        )
        return []


def update_project_status(db: Session, project_id: str, status: str) -> Project | None:
    """Cập nhật trạng thái vận hành của dự án.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần cập nhật.
        status: Trạng thái mới (Khởi tạo, Đang chạy, Tạm dừng, Hoàn thành).

    Returns:
        Project | None: Đối tượng Project sau khi cập nhật, hoặc None nếu cập nhật thất bại.
    """
    logger.info(
        "Yêu cầu cập nhật trạng thái dự án: ID=%s, Status=%s", project_id, status
    )
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            logger.warning(
                "Không tìm thấy dự án ID '%s' để cập nhật trạng thái.", project_id
            )
            return None

        project.status = status
        db.commit()
        db.refresh(project)
        logger.info(
            "Cập nhật trạng thái dự án thành công: ID=%s, Status=%s", project_id, status
        )
        return project
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi cập nhật trạng thái dự án ID '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return None


def update_project(
    db: Session,
    project_id: str,
    project_name: str,
    roles: dict[str, str | None] | None = None,
) -> Project | None:
    """Cập nhật thông tin chi tiết của dự án kết cấu thép hiện có.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã định danh duy nhất của dự án cần cập nhật.
        project_name: Tên mới chi tiết của dự án.
        roles: Dictionary chứa vai trò, ví dụ: {'sales': email, 'designer': email}.

    Returns:
        Project | None: Đối tượng Project sau khi cập nhật, hoặc None nếu thất bại.
    """
    logger.info(
        "Yêu cầu cập nhật dự án: ID=%s, Name=%s, Roles=%s",
        project_id,
        project_name,
        roles,
    )
    sales_email = roles.get("sales") if roles else None
    designer_email = roles.get("designer") if roles else None

    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            logger.warning("Không tìm thấy dự án ID '%s' để cập nhật.", project_id)
            return None

        project.project_name = project_name
        project.sales_email = sales_email
        project.designer_email = designer_email

        db.commit()
        db.refresh(project)
        logger.info("Cập nhật dự án thành công: ID=%s", project_id)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi cập nhật dự án ID '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return None


def delete_project(db: Session, project_id: str) -> bool:
    """Xóa dự án khỏi cơ sở dữ liệu dựa trên project_id.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã dự án cần xóa.

    Returns:
        bool: True nếu xóa thành công, False nếu thất bại.
    """
    logger.info("Yêu cầu xóa dự án: %s", project_id)
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            logger.warning("Không tìm thấy dự án '%s' để xóa.", project_id)
            return False

        db.delete(project)
        db.commit()
        logger.info("Xóa dự án '%s' thành công.", project_id)
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            "Lỗi cơ sở dữ liệu khi xóa dự án '%s': %s",
            project_id,
            str(e),
            exc_info=True,
        )
        return False


def delete_project_safe(project_id: str) -> bool:
    """Xóa dự án tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án cần xóa.

    Returns:
        True nếu xóa thành công, ngược lại False.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return delete_project(db, project_id)
    finally:
        db.close()


def create_project_safe(
    project_id: str,
    project_name: str,
    roles: dict[str, str | None] | None = None,
) -> Project | None:
    """Tạo dự án mới tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án mới.
        project_name: Tên dự án mới.
        roles: Dictionary chứa các email vai trò.

    Returns:
        Project đối tượng được tạo hoặc None nếu lỗi.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return create_project(db, project_id, project_name, roles)
    finally:
        db.close()


def update_project_safe(
    project_id: str,
    project_name: str,
    roles: dict[str, str | None] | None = None,
) -> Project | None:
    """Cập nhật thông tin dự án tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án cần cập nhật.
        project_name: Tên dự án mới.
        roles: Dictionary chứa các email vai trò mới.

    Returns:
        Project đối tượng sau cập nhật hoặc None.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return update_project(db, project_id, project_name, roles)
    finally:
        db.close()


def get_project_safe(project_id: str) -> Project | None:
    """Nạp dữ liệu dự án tự động quản lý vòng đời Session (Safe).

    Args:
        project_id: Mã dự án cần lấy thông tin.

    Returns:
        Project đối tượng tìm thấy hoặc None.
    """
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        return db.query(Project).filter(Project.project_id == project_id).first()
    finally:
        db.close()


def is_email_authorized(email: str) -> bool:
    """Kiểm tra email có quyền truy cập hệ thống hay không.

    Email hợp lệ nếu là admin hoặc được gán vào ít nhất 1 dự án
    (sales_email, designer_email, hoặc section designer_email).

    Args:
        email: Địa chỉ email cần kiểm tra.

    Returns:
        True nếu email được phép truy cập, False nếu không.
    """
    from core.database import SessionLocal
    from core.models import ProjectSection

    # Admin và phòng Kế hoạch luôn được phép truy cập
    email_lower = email.lower()
    if email_lower in ["luu.lehai@gmail.com", "phongkehoachkythuat25@gmail.com"]:
        return True

    db = SessionLocal()
    try:
        email_lower = email.lower()

        # Kiểm tra sales_email hoặc designer_email ở cấp Project
        project_match = (
            db.query(Project)
            .filter(
                (Project.sales_email.ilike(email_lower))
                | (Project.designer_email.ilike(email_lower))
            )
            .first()
        )
        if project_match:
            return True

        # Kiểm tra designer_email ở cấp Section (hạng mục)
        section_match = (
            db.query(ProjectSection)
            .filter(ProjectSection.designer_email.ilike(email_lower))
            .first()
        )
        return section_match is not None
    except SQLAlchemyError as e:
        logger.error(
            "Lỗi khi kiểm tra quyền truy cập email '%s': %s",
            email,
            str(e),
            exc_info=True,
        )
        return False
    finally:
        db.close()
