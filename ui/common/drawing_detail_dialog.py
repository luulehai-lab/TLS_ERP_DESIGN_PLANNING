# Tên file: ui/common/drawing_detail_dialog.py
# CHỨC NĂNG: Cửa sổ xem chi tiết thông tin bản vẽ kỹ thuật và hỗ trợ in ấn PDF
# CHANGELOG:
# - 10:57:18 15/07/2026: [NEW] refactor(report): modularize report service and implement visual drawing timeline (Antigravity)
# - 10:30:00 15/07/2026: [UPDATE] Chuyển đổi gọi doc.print_() thành doc.print() để tương thích hoàn toàn với PyQt6 (Lê Thanh Vân/Antigravity)
# - 10:10:00 15/07/2026: [NEW] Khởi tạo dialog xem chi tiết bản vẽ có hỗ trợ in PDF kèm QR code (Lê Thanh Vân/Antigravity)

import logging
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QWidget,
)
from PyQt6.QtPrintSupport import QPrinter

from ui.styles.theme import TLSTheme
from ui.common.qr_widget import QRWidget

logger = logging.getLogger(__name__)


class DrawingDetailDialog(QDialog):
    """Cửa sổ dialog hiển thị thông tin chi tiết của một bản vẽ.

    Hỗ trợ hiển thị mã QR Code liên kết Drive và xuất in ấn thông tin PDF.
    """

    def __init__(self, parent: QWidget, drawing_data: dict) -> None:
        """Khởi tạo DrawingDetailDialog.

        Args:
            parent: Widget cha.
            drawing_data: Dictionary chứa thông tin bản vẽ thô.
        """
        super().__init__(parent)
        self.drawing: dict = drawing_data
        self.setWindowTitle(f"Chi tiết bản vẽ: {self.drawing['drawing_id']}")
        self.resize(650, 550)
        self.setMinimumSize(550, 450)
        self.setStyleSheet(TLSTheme.content_view_stylesheet())
        self._init_ui()

    def _init_ui(self) -> None:
        """Khởi tạo các thành phần giao diện của Dialog."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Tiêu đề Dialog
        title_label = QLabel("THÔNG TIN CHI TIẾT BẢN VẼ KỸ THUẬT", self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E293B;")
        layout.addWidget(title_label)

        # Layout chính chia làm 2 phần: Thông tin bên trái, QR Code bên phải
        main_content_layout = QHBoxLayout()
        main_content_layout.setSpacing(20)

        # Phần bên trái: Thông tin dạng nhãn và Ghi chú
        info_widget = QWidget(self)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)

        # Các trường thông tin
        info_layout.addWidget(
            self._create_info_row("Dự Án:", self.drawing.get("project_id") or "---")
        )
        info_layout.addWidget(
            self._create_info_row("Mã Bản Vẽ:", self.drawing["drawing_id"])
        )
        info_layout.addWidget(
            self._create_info_row(
                "Hạng Mục:", self.drawing.get("section_name") or "---"
            )
        )
        info_layout.addWidget(
            self._create_info_row("Tên Bản Vẽ:", self.drawing["drawing_name"])
        )
        info_layout.addWidget(
            self._create_info_row("Trạng Thái:", self.drawing["status"])
        )
        info_layout.addWidget(
            self._create_info_row("Phiên Bản:", self.drawing["current_version"])
        )

        # Link Drive
        drive_link = self.drawing.get("drive_link") or ""
        link_widget = QWidget(self)
        link_layout = QHBoxLayout(link_widget)
        link_layout.setContentsMargins(0, 0, 0, 0)
        link_layout.addWidget(QLabel("<b>Link Drive:</b>", link_widget), 1)

        if drive_link and drive_link.startswith("http"):
            lbl_link = QLabel(
                f'<a href="{drive_link}">Mở liên kết Drive</a>', link_widget
            )
            lbl_link.setOpenExternalLinks(True)
            lbl_link.setStyleSheet("color: #1B76FF; text-decoration: underline;")
            link_layout.addWidget(lbl_link, 3)
        else:
            link_layout.addWidget(QLabel("Chưa có liên kết", link_widget), 3)
        info_layout.addWidget(link_widget)

        # Thời gian
        info_layout.addWidget(
            self._create_info_row(
                "Thời gian Ban hành:",
                self._format_time(self.drawing.get("released_at")),
            )
        )
        info_layout.addWidget(
            self._create_info_row(
                "Thời gian chuyển xưởng:",
                self._format_time(self.drawing.get("factory_transferred_at")),
            )
        )

        # Ghi chú kỹ thuật (QTextEdit cuộn)
        info_layout.addWidget(QLabel("<b>Ghi chú kỹ thuật:</b>", info_widget))
        self.txt_notes = QTextEdit(info_widget)
        self.txt_notes.setReadOnly(True)
        self.txt_notes.setText(self.drawing.get("notes") or "Không có ghi chú.")
        self.txt_notes.setStyleSheet(
            "background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px; padding: 5px;"
        )
        self.txt_notes.setMaximumHeight(100)
        info_layout.addWidget(self.txt_notes)

        main_content_layout.addWidget(info_widget, 3)

        # Phần bên phải: QR Code
        qr_widget_container = QWidget(self)
        qr_layout = QVBoxLayout(qr_widget_container)
        qr_layout.setContentsMargins(0, 0, 0, 0)
        qr_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.qr_code = QRWidget(qr_widget_container, size=150)
        if drive_link and drive_link.startswith("http"):
            self.qr_code.generate_qr(drive_link)
        else:
            self.qr_code.generate_qr(f"Drawing ID: {self.drawing['drawing_id']}")

        qr_layout.addWidget(self.qr_code)
        qr_layout.addWidget(
            QLabel(
                "<center><small>Quét mã để mở nhanh bản vẽ</small></center>",
                qr_widget_container,
            )
        )
        main_content_layout.addWidget(qr_widget_container, 2)

        layout.addLayout(main_content_layout)

        # Nút Hành động ở cuối
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        self.btn_print = QPushButton("🖨️ In chi tiết (PDF)", self)
        self.btn_print.setStyleSheet(TLSTheme.primary_button_stylesheet())
        self.btn_print.clicked.connect(self._export_pdf)
        actions_layout.addWidget(self.btn_print)

        self.btn_close = QPushButton("Đóng", self)
        self.btn_close.setStyleSheet(TLSTheme.secondary_button_stylesheet())
        self.btn_close.clicked.connect(self.accept)
        actions_layout.addWidget(self.btn_close)

        layout.addLayout(actions_layout)

    def _create_info_row(self, label: str, value: str) -> QWidget:
        """Tạo hàng thông tin gồm label và giá trị.

        Args:
            label: Tiêu đề thông tin.
            value: Nội dung giá trị.

        Returns:
            QWidget chứa hàng thông tin.
        """
        widget = QWidget(self)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl_title = QLabel(f"<b>{label}</b>", widget)
        lbl_value = QLabel(value, widget)
        lbl_value.setWordWrap(True)

        layout.addWidget(lbl_title, 1)
        layout.addWidget(lbl_value, 3)
        return widget

    def _format_time(self, time_val: any) -> str:
        """Định dạng thời gian sang chuỗi hiển thị.

        Args:
            time_val: Giá trị thời gian cần định dạng.

        Returns:
            str: Chuỗi thời gian đã định dạng.
        """
        if not time_val:
            return "---"
        if isinstance(time_val, str):
            # Nếu đã là string dạng ISO, cố gắng parse
            try:
                time_val = datetime.fromisoformat(time_val.replace("Z", "+00:00"))
            except ValueError:
                return time_val
        # Cộng 7 tiếng múi giờ Việt Nam
        local_time = time_val + timedelta(hours=7)
        return local_time.strftime("%d/%m/%y %H:%M:%S")

    def _export_pdf(self) -> None:
        """Xuất thông tin bản vẽ kèm mã QR Code sang file PDF."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu File PDF chi tiết bản vẽ",
            f"Bản vẽ_{self.drawing['drawing_id']}.pdf",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        try:
            # Lấy mã QR Code dạng base64
            qr_pixmap = self.qr_code.get_qr_pixmap()
            qr_base64 = ""
            if not qr_pixmap.isNull():
                ba = QByteArray()
                buffer = QBuffer(ba)
                buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                qr_pixmap.save(buffer, "PNG")
                qr_base64 = ba.toBase64().data().decode("utf-8")

            # Xây dựng nội dung HTML cho file PDF
            html_content = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: #1E293B;
                        margin: 20mm;
                    }}
                    .header {{
                        text-align: center;
                        border-bottom: 3px solid #0F172A;
                        padding-bottom: 5mm;
                        margin-bottom: 10mm;
                    }}
                    .title {{
                        font-size: 26pt;
                        font-weight: bold;
                        color: #0F172A;
                        text-transform: uppercase;
                    }}
                    .subtitle {{
                        font-size: 13pt;
                        color: #64748B;
                        margin-top: 2mm;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 10mm;
                    }}
                    th, td {{
                        padding: 5mm 6mm;
                        text-align: left;
                        font-size: 12pt;
                        line-height: 1.5;
                    }}
                    th {{
                        background-color: #F1F5F9;
                        font-weight: bold;
                        width: 30%;
                        border: 1px solid #E2E8F0;
                    }}
                    td {{
                        border: 1px solid #E2E8F0;
                        width: 70%;
                    }}
                    .qr-section {{
                        text-align: center;
                        margin-top: 30mm;
                    }}
                    .qr-code {{
                        width: 45mm;
                        height: 45mm;
                        border: 1px solid #CBD5E1;
                        padding: 2mm;
                        background: white;
                    }}
                    .footer {{
                        margin-top: 15mm;
                        text-align: center;
                        font-size: 9pt;
                        color: #94A3B8;
                        border-top: 1px solid #E2E8F0;
                        padding-top: 3mm;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">Chi Tiết Bản Vẽ Kỹ Thuật</div>
                    <div class="subtitle">TUẤN LONG STEEL - HỆ THỐNG ERP THIẾT KẾ - KẾ HOẠCH</div>
                </div>

                <table>
                    <tr>
                        <th>Dự Án</th>
                        <td><strong>{self.drawing.get("project_id") or "---"}</strong></td>
                    </tr>
                    <tr>
                        <th>Mã Bản Vẽ</th>
                        <td><strong>{self.drawing["drawing_id"]}</strong></td>
                    </tr>
                    <tr>
                        <th>Hạng Mục</th>
                        <td>{self.drawing.get("section_name") or "---"}</td>
                    </tr>
                    <tr>
                        <th>Tên Bản Vẽ</th>
                        <td>{self.drawing["drawing_name"]}</td>
                    </tr>
                    <tr>
                        <th>Trạng Thái</th>
                        <td>{self.drawing["status"]}</td>
                    </tr>
                    <tr>
                        <th>Phiên Bản</th>
                        <td>{self.drawing["current_version"]}</td>
                    </tr>
                    <tr>
                        <th>Link Drive</th>
                        <td>{self.drawing.get("drive_link") or "Chưa có liên kết"}</td>
                    </tr>
                    <tr>
                        <th>Thời gian Ban hành</th>
                        <td>{self._format_time(self.drawing.get("released_at"))}</td>
                    </tr>
                    <tr>
                        <th>Thời gian chuyển xưởng</th>
                        <td>{self._format_time(self.drawing.get("factory_transferred_at"))}</td>
                    </tr>
                    <tr>
                        <th>Ghi chú kỹ thuật</th>
                        <td style="white-space: pre-wrap;">{self.drawing.get("notes") or "Không có ghi chú."}</td>
                    </tr>
                </table>
            """

            if qr_base64:
                html_content += f"""
                <div class="qr-section">
                    <img class="qr-code" src="data:image/png;base64,{qr_base64}" />
                    <div style="font-size: 12px; color: #64748B; margin-top: 5px;">Quét mã QR để truy cập bản vẽ thiết kế gốc trên Google Drive</div>
                </div>
                """

            html_content += f"""
                <div class="footer">
                    Tài liệu được xuất tự động từ Hệ thống ERP Tuan Long Steel ngày {datetime.now().strftime("%d/%m/%Y lúc %H:%M:%S")}.
                </div>
            </body>
            </html>
            """

            # Thực hiện render in PDF qua QTextDocument và QPrinter
            from PyQt6.QtGui import QTextDocument

            doc = QTextDocument()
            doc.setHtml(html_content)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageMargins(printer.pageLayout().margins())  # Giữ lề mặc định

            doc.print(printer)

            QMessageBox.information(
                self,
                "In PDF thành công",
                f"Đã xuất file PDF chi tiết bản vẽ thành công tại:\n{file_path}",
            )
            logger.info(
                "DrawingDetailDialog: Đã in PDF bản vẽ ID=%s thành công.",
                self.drawing["drawing_id"],
            )
        except Exception as ex:
            logger.error("DrawingDetailDialog: Lỗi in PDF: %s", str(ex), exc_info=True)
            QMessageBox.critical(
                self,
                "Lỗi in PDF",
                f"Không thể xuất file PDF do lỗi:\n{str(ex)}",
            )
