# Tên file: core/services/project_service.py
# CHỨC NĂNG: Cung cấp các nghiệp vụ CRUD quản lý Dự án (Project)
# CHANGELOG:
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:12:00 02/07/2026: [NEW] Khởi tạo tầng dịch vụ quản lý dự án (Lê Thanh Vân/Antigravity)

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models import Project

logger = logging.getLogger(__name__)


def create_project(db: Session, project_id: str, project_name: str) -> Project | None:
    """Tạo mới một dự án kết cấu thép trong cơ sở dữ liệu.

    Args:
        db: Session kết nối database hiện thời.
        project_id: Mã định danh duy nhất của dự án (ví dụ: TLS-01726).
        project_name: Tên chi tiết của dự án.

    Returns:
        Project: Đối tượng Project được tạo mới nếu thành công, hoặc None nếu thất bại.
    """
    logger.info("Yêu cầu tạo dự án mới: ID=%s, Name=%s", project_id, project_name)
    try:
        # Kiểm tra xem dự án đã tồn tại hay chưa
        existing = db.query(Project).filter(Project.project_id == project_id).first()
        if existing:
            logger.warning(
                "Không thể tạo dự án. Dự án có ID '%s' đã tồn tại.", project_id
            )
            return existing

        db_project = Project(project_id=project_id, project_name=project_name)
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
        return db.query(Project).filter(Project.status != "Hoàn thành").all()
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
