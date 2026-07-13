# Tên file: ui/styles/theme.py
# CHỨC NĂNG: Hệ thống Design Token và QSS Generator dùng chung cho ứng dụng ERP TK-KH TLS
# CHANGELOG:
# - 14:25:54 13/07/2026: [UPDATE] feat(search): implement project and drawing search with client-side filters (Antigravity)
# - 18:09:38 11/07/2026: [UPDATE] feat(drawing-ui): add version input field to drawing release form and update backend (Antigravity)
# - 18:28:01 10/07/2026: [UPDATE] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:29:28 10/07/2026: [NEW] fix(ui): resolve QSplitter sidebar resize and save column/splitter state (Antigravity)
# - 17:26:00 10/07/2026: [NEW] Khởi tạo hệ thống theme và QSS dùng chung (Lê Thanh Vân/Antigravity)


class TLSTheme:
    """Hệ thống Design Token và QSS Generator dùng chung cho ứng dụng.

    Cung cấp các màu sắc chuẩn và các chuỗi stylesheet QSS thống nhất.
    """

    # --- COLOR PALETTE (Design Tokens) ---
    SLATE_900 = "#0F172A"
    SLATE_800 = "#1E293B"
    SLATE_700 = "#334155"
    SLATE_600 = "#475569"
    SLATE_500 = "#64748B"
    SLATE_100 = "#F1F5F9"
    SLATE_50 = "#F8FAFC"

    SKY_700 = "#0369A1"
    SKY_600 = "#0284C7"
    SKY_400 = "#38BDF8"
    SKY_100 = "#E0F2FE"
    SKY_50 = "#F0F9FF"

    WHITE = "#FFFFFF"
    BORDER_COLOR = "#E2E8F0"
    BORDER_FOCUS = "#38BDF8"
    TEXT_MAIN = "#0F172A"
    TEXT_MUTED = "#475569"

    @classmethod
    def get_common_qss(cls) -> str:
        """Trả về QSS chung cho các widget thông dụng (GroupBox, Label, Input, Table...).

        Returns:
            Chuỗi stylesheet QSS dùng chung.
        """
        return f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                color: {cls.SLATE_700};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: {cls.WHITE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 5px;
            }}
            QLabel {{
                font-size: 13px;
                color: {cls.TEXT_MUTED};
                font-weight: 500;
            }}
            QLineEdit, QComboBox {{
                border: 1px solid #CBD5E1;
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: {cls.SLATE_50};
                color: {cls.TEXT_MAIN};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {cls.BORDER_FOCUS};
                background-color: {cls.WHITE};
                color: {cls.TEXT_MAIN};
            }}
            QTableWidget {{
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: 6px;
                background-color: {cls.WHITE};
                color: {cls.TEXT_MAIN};
                gridline-color: #F1F5F9;
                font-size: 13px;
            }}
            QTableWidget::item {{
                color: {cls.TEXT_MAIN};
            }}
            QTableWidget::item:selected {{
                background-color: {cls.SKY_400};
                color: {cls.TEXT_MAIN};
            }}
            QHeaderView::section {{
                background-color: {cls.SLATE_100};
                color: {cls.TEXT_MUTED};
                padding: 6px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }}
            QMessageBox {{
                background-color: {cls.WHITE};
            }}
            QMessageBox QLabel {{
                color: {cls.TEXT_MAIN};
            }}
            QMessageBox QPushButton {{
                background-color: {cls.SLATE_100};
                color: {cls.TEXT_MAIN};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: 5px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: bold;
                min-width: 70px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {cls.BORDER_COLOR};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: #CBD5E1;
            }}
        """

    @classmethod
    def main_window_stylesheet(cls) -> str:
        """Trả về stylesheet QSS hoàn chỉnh cho MainWindow.

        Returns:
            Chuỗi stylesheet QSS của MainWindow.
        """
        common = cls.get_common_qss()
        return (
            common
            + f"""
            QMainWindow {{
                background-color: {cls.SLATE_50};
            }}
            #sidebar {{
                background-color: {cls.SLATE_900};
                border-right: 1px solid {cls.SLATE_800};
            }}
            #brandLabel {{
                color: #F1F5F9;
                font-size: 18px;
                font-weight: 800;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1px;
                margin-top: 5px;
            }}
            #subBrandLabel {{
                color: {cls.SKY_400};
                font-size: 12px;
                font-weight: 600;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-top: 2px;
            }}
            #projectList {{
                background-color: transparent;
                border: none;
                outline: none;
                margin-top: 5px;
            }}
            #projectList::item {{
                color: #94A3B8;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 4px;
            }}
            #projectList::item:hover {{
                background-color: {cls.SLATE_800};
                color: #F8FAFC;
            }}
            #projectList::item:selected {{
                background-color: {cls.SKY_400};
                color: {cls.SLATE_900};
            }}
            #headerBar {{
                background-color: {cls.WHITE};
                border-bottom: 1px solid {cls.BORDER_COLOR};
                min-height: 60px;
                max-height: 60px;
            }}
            #headerProjectLabel {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 700;
                color: {cls.SLATE_900};
            }}
            #navButton {{
                color: {cls.TEXT_MUTED};
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                margin-left: 8px;
            }}
            #navButton:hover {{
                color: {cls.SKY_600};
                background-color: {cls.SKY_50};
            }}
            #navButton:checked {{
                background-color: {cls.SKY_100};
                color: {cls.SKY_700};
            }}
        """
        )

    @classmethod
    def content_view_stylesheet(cls) -> str:
        """Trả về stylesheet QSS hoàn chỉnh cho các View nghiệp vụ con.

        Returns:
            Chuỗi stylesheet QSS của các View con.
        """
        common = cls.get_common_qss()
        return (
            common
            + f"""
            QPushButton {{
                background-color: {cls.SLATE_900};
                color: {cls.WHITE};
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cls.SLATE_800};
            }}
            QPushButton:pressed {{
                background-color: #020617;
            }}
        """
        )

    @classmethod
    def login_stylesheet(cls) -> str:
        """Trả về stylesheet QSS hoàn chỉnh cho LoginWindow (Dark theme).

        Returns:
            Chuỗi stylesheet QSS của Login.
        """
        return f"""
            QMainWindow {{
                background-color: {cls.SLATE_900};
            }}
            #loginCard {{
                background-color: {cls.SLATE_800};
                border: 1px solid {cls.SLATE_700};
                border-radius: 12px;
            }}
            #brandLabel {{
                color: #F8FAFC;
                font-size: 24px;
                font-weight: 800;
                font-family: 'Segoe UI', Arial, sans-serif;
                letter-spacing: 1px;
            }}
            #subBrandLabel {{
                color: {cls.SKY_400};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            #introLabel {{
                color: #94A3B8;
                font-size: 13px;
            }}
            #statusLabel {{
                color: #64748B;
                font-size: 12px;
                margin-top: 10px;
                min-height: 40px;
            }}
            #loginButton {{
                background-color: {cls.WHITE};
                color: {cls.SLATE_900};
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }}
            #loginButton:hover {{
                background-color: {cls.SLATE_100};
            }}
            #loginButton:pressed {{
                background-color: #CBD5E1;
            }}
            #loginButton:disabled {{
                background-color: {cls.SLATE_600};
                color: #94A3B8;
            }}
            QMessageBox {{
                background-color: {cls.SLATE_800};
            }}
            QMessageBox QLabel {{
                color: #F8FAFC;
            }}
            QMessageBox QPushButton {{
                background-color: {cls.WHITE};
                color: {cls.SLATE_900};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-width: 70px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {cls.SLATE_100};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: #CBD5E1;
            }}
        """

    @classmethod
    def avatar_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho Avatar của User ở Header.

        Returns:
            Chuỗi stylesheet QSS của Avatar.
        """
        return f"""
            background-color: {cls.SKY_400};
            color: {cls.SLATE_900};
            font-weight: bold;
            font-size: 13px;
            border-radius: 14px;
            min-width: 28px;
            max-width: 28px;
            min-height: 28px;
            max-height: 28px;
            qproperty-alignment: 'AlignCenter';
        """

    @classmethod
    def logout_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút Đăng xuất ở Header.

        Returns:
            Chuỗi stylesheet QSS của nút Đăng xuất.
        """
        return f"""
            background-color: {cls.SLATE_100};
            color: #EF4444;
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 11px;
            font-weight: bold;
        """

    @classmethod
    def new_project_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút Tạo dự án mới ở Sidebar.

        Returns:
            Chuỗi stylesheet QSS của nút Tạo dự án mới.
        """
        return f"""
            QPushButton {{
                background-color: {cls.SKY_600};
                color: {cls.WHITE};
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
                margin: 5px 0px;
            }}
            QPushButton:hover {{
                background-color: {cls.SKY_700};
            }}
        """

    @classmethod
    def refresh_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút Làm mới bảng bản vẽ.

        Returns:
            Chuỗi stylesheet QSS của nút Làm mới.
        """
        return f"""
            QPushButton {{
                background-color: {cls.SKY_600};
                color: {cls.WHITE};
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cls.SKY_700};
            }}
        """

    @classmethod
    def project_dialog_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho QDialog tạo/sửa dự án.

        Returns:
            Chuỗi stylesheet QSS của Dialog tạo dự án.
        """
        return f"""
            QDialog {{
                background-color: {cls.WHITE};
            }}
            QLabel {{
                font-size: 13px;
                color: {cls.TEXT_MUTED};
                font-weight: bold;
            }}
            QLineEdit, QComboBox {{
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: 5px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: {cls.SLATE_50};
                color: {cls.TEXT_MAIN};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {cls.BORDER_FOCUS};
                background-color: {cls.WHITE};
                color: {cls.TEXT_MAIN};
            }}
            QPushButton {{
                font-size: 13px;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 5px;
            }}
        """

    @classmethod
    def save_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút Lưu thay đổi dự án.

        Returns:
            Chuỗi stylesheet QSS của nút Lưu thay đổi.
        """
        return f"""
            QPushButton {{
                background-color: {cls.SLATE_900};
                color: {cls.WHITE};
                border: none;
                border-radius: 5px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cls.SLATE_800};
            }}
        """

    @classmethod
    def dark_action_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút hành động tối màu (ví dụ nút tải QR).

        Returns:
            Chuỗi stylesheet QSS của nút hành động tối màu.
        """
        return f"""
            QPushButton {{
                background-color: {cls.SLATE_900};
                color: {cls.WHITE};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cls.SLATE_800};
            }}
            QPushButton:disabled {{
                background-color: #E2E8F0;
                color: #94A3B8;
            }}
        """

    @classmethod
    def secondary_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút hành động phụ (secondary button).

        Returns:
            Chuỗi stylesheet QSS của nút phụ.
        """
        return f"""
            QPushButton {{
                background-color: {cls.SLATE_600};
                color: {cls.WHITE};
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {cls.SLATE_700};
            }}
            QPushButton:disabled {{
                background-color: #E2E8F0;
                color: #94A3B8;
            }}
        """

    @classmethod
    def cancel_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút Hủy/Tạo mới hạng mục.

        Returns:
            Chuỗi stylesheet QSS của nút Hủy/Tạo mới.
        """
        return f"""
            QPushButton {{
                background-color: {cls.SLATE_500};
                color: {cls.WHITE};
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cls.SLATE_700};
            }}
        """

    @classmethod
    def delete_button_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho nút Xóa hạng mục.

        Returns:
            Chuỗi stylesheet QSS của nút Xóa hạng mục.
        """
        return f"""
            QPushButton {{
                background-color: #EF4444;
                color: {cls.WHITE};
                border: none;
                border-radius: 4px;
                padding: 3px 10px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """

    @classmethod
    def splitter_stylesheet(cls) -> str:
        """Trả về stylesheet QSS cho QSplitter chính.

        Returns:
            Chuỗi stylesheet QSS của QSplitter.
        """
        return f"""
            QSplitter::handle {{
                background-color: {cls.BORDER_COLOR};
            }}
            QSplitter::handle:hover {{
                background-color: {cls.BORDER_FOCUS};
            }}
        """

