# Tên file: core/models.py
# CHỨC NĂNG: Khai báo cấu trúc bảng cơ sở dữ liệu SQLAlchemy cho dự án ERP
# CHANGELOG:
# - 14:34:36 11/07/2026: [REFACTOR] refactor(ui-modularity): complete modular refactoring of codebase graph tools and adopt UI-Backend Separation rules (Antigravity)
# - 14:30:00 11/07/2026: [UPDATE] Thêm cột notes (ghi chú) vào model Drawing (Antigravity)
# - 15:08:00 10/07/2026: [UPDATE] Bổ sung designer_email vào model ProjectSection (Lê Thanh Vân/Antigravity)
# - 14:49:00 10/07/2026: [UPDATE] Bổ sung cột sales_email và designer_email vào model Project (Lê Thanh Vân/Antigravity)
# - 18:19:45 08/07/2026: [UPDATE] feat(ui): split design tab into project management and drawing release views (Antigravity)
# - 18:07:00 08/07/2026: [NEW] Khởi tạo model ProjectSection và liên kết cột section_id trong Drawing (Antigravity)
# - 11:49:13 02/07/2026: [NEW] Cập nhật mã nguồn (Antigravity)
# - 11:44:00 02/07/2026: [UPDATE] Đánh index cho các khóa ngoại drawing_id và bổ sung docstrings cho __repr__ (Lê Thanh Vân/Antigravity)
# - 10:59:00 02/07/2026: [NEW] Khởi tạo các bảng Projects, Drawings, DrawingLogs, BOMDetails (Lê Thanh Vân/Antigravity)

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.database import Base


class Project(Base):
    """
    Model quản lý thông tin dự án kết cấu thép.
    """

    __tablename__ = "projects"

    project_id = Column(String(50), primary_key=True, index=True)
    project_name = Column(String(200), nullable=False)
    status = Column(
        String(50), default="Khởi tạo"
    )  # Khởi tạo, Đang chạy, Tạm dừng, Hoàn thành
    sales_email = Column(
        String(100), nullable=True
    )  # Email của nhân viên Kinh doanh (Sales)
    designer_email = Column(
        String(100), nullable=True
    )  # Email của nhân viên Thiết kế chủ trì
    created_at = Column(DateTime, default=datetime.utcnow)

    # Các quan hệ
    drawings = relationship(
        "Drawing", back_populates="project", cascade="all, delete-orphan"
    )
    sections = relationship(
        "ProjectSection", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Đại diện dạng chuỗi của đối tượng Project.

        Returns:
            str: Chuỗi thông tin dự án.
        """
        return f"<Project(id='{self.project_id}', name='{self.project_name}', status='{self.status}', sales='{self.sales_email}', designer='{self.designer_email}')>"


class ProjectSection(Base):
    """
    Model quản lý các hạng mục (NX1, NX2, MN...) của một dự án kết cấu thép.
    """

    __tablename__ = "project_sections"

    section_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        String(50),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_code = Column(String(50), nullable=False)  # Ví dụ: NX1, NX2...
    section_name = Column(String(150), nullable=False)  # Ví dụ: Nhà xưởng 1...
    designer_email = Column(String(100), nullable=True)  # Email kỹ sư thiết kế phụ trách hạng mục này

    # Các quan hệ
    project = relationship("Project", back_populates="sections")
    drawings = relationship("Drawing", back_populates="section")

    def __repr__(self) -> str:
        """Đại diện dạng chuỗi của đối tượng ProjectSection.

        Returns:
            str: Chuỗi thông tin hạng mục.
        """
        return f"<ProjectSection(id={self.section_id}, project='{self.project_id}', code='{self.section_code}', name='{self.section_name}', designer='{self.designer_email}')>"


class Drawing(Base):
    """
    Model quản lý bản vẽ hoặc cấu kiện chính cần triển khai sản xuất.
    """

    __tablename__ = "drawings"

    drawing_id = Column(String(50), primary_key=True, index=True)
    project_id = Column(
        String(50),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False,
    )
    drawing_name = Column(String(200), nullable=False)
    notes = Column(String(500), nullable=True)  # Ghi chú kỹ thuật khi ban hành
    drive_link = Column(
        String(500), nullable=True
    )  # Đường link file PDF trên Google Drive
    current_version = Column(String(10), default="V1")
    file_hash = Column(
        String(64), nullable=True
    )  # MD5/SHA256 của file để kiểm soát thay đổi
    status = Column(
        String(50), default="Chờ triển khai"
    )  # Chờ triển khai, Đang sản xuất, Đã hoàn thành
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    section_id = Column(
        Integer,
        ForeignKey("project_sections.section_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Các quan hệ
    project = relationship("Project", back_populates="drawings")
    section = relationship("ProjectSection", back_populates="drawings")
    logs = relationship(
        "DrawingLog", back_populates="drawing", cascade="all, delete-orphan"
    )
    bom_details = relationship(
        "BOMDetail", back_populates="drawing", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Đại diện dạng chuỗi của đối tượng Drawing.

        Returns:
            str: Chuỗi thông tin bản vẽ.
        """
        return f"<Drawing(id='{self.drawing_id}', name='{self.drawing_name}', status='{self.status}')>"


class DrawingLog(Base):
    """
    Model lưu vết toàn bộ lịch sử thao tác, phê duyệt và thay đổi thông tin bản vẽ.
    """

    __tablename__ = "drawing_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    drawing_id = Column(
        String(50),
        ForeignKey("drawings.drawing_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(String(10), nullable=False)
    action = Column(
        String(100), nullable=False
    )  # Ban hành, In bản vẽ, Thay đổi sơn, Chuyển xưởng...
    performed_by = Column(String(100), nullable=False)  # Tên kỹ sư/người thao tác
    note = Column(
        String(500), nullable=True
    )  # Ghi chú hoặc lý do thay đổi (đổi màu sơn, mác thép...)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Các quan hệ
    drawing = relationship("Drawing", back_populates="logs")

    def __repr__(self) -> str:
        """Đại diện dạng chuỗi của đối tượng DrawingLog.

        Returns:
            str: Chuỗi thông tin lịch sử bản vẽ.
        """
        return f"<DrawingLog(id={self.log_id}, drawing='{self.drawing_id}', action='{self.action}', user='{self.performed_by}')>"


class BOMDetail(Base):
    """
    Model quản lý danh mục vật tư chi tiết (BOM) bóc tách từ bản vẽ (Giai đoạn 2).
    """

    __tablename__ = "bom_details"

    bom_id = Column(Integer, primary_key=True, autoincrement=True)
    drawing_id = Column(
        String(50),
        ForeignKey("drawings.drawing_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mark = Column(String(50), nullable=False)  # Ký hiệu cấu kiện phụ (M1, B1...)
    profile = Column(
        String(100), nullable=False
    )  # Quy cách thép (H200x200x8x12, PL10...)
    weight = Column(Float, nullable=False)  # Trọng lượng đơn vị (kg)
    quantity = Column(Integer, nullable=False)  # Số lượng cấu kiện phụ
    steel_grade = Column(String(50), nullable=False)  # Mác thép (Q355B, SS400...)
    paint_spec = Column(
        String(100), nullable=True
    )  # Quy cách sơn (Sơn chống rỉ Alkyd, Sơn Epoxy...)

    # Các quan hệ
    drawing = relationship("Drawing", back_populates="bom_details")

    def __repr__(self) -> str:
        """Đại diện dạng chuỗi của đối tượng BOMDetail.

        Returns:
            str: Chuỗi thông tin chi tiết BOM.
        """
        return f"<BOMDetail(id={self.bom_id}, drawing='{self.drawing_id}', mark='{self.mark}', profile='{self.profile}')>"
