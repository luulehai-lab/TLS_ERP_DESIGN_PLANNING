# Tên file: ui/common/qr_widget.py
# CHỨC NĂNG: Widget hiển thị mã QR Code của bản vẽ hiện hành (Hỗ trợ offline + online fallback)
# CHANGELOG:
# - 18:09:38 11/07/2026: [NEW] feat(drawing-ui): add version input field to drawing release form and update backend (Antigravity)
# - 18:05:00 11/07/2026: [NEW] Khởi tạo component QRPreviewWidget hỗ trợ sinh mã QR và lưu ảnh (Lê Thanh Vân/Antigravity)

import logging
import urllib.parse
import urllib.request
from io import BytesIO
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from ui.styles.theme import TLSTheme

logger = logging.getLogger(__name__)


class QRPreviewWidget(QGroupBox):
    """Widget hiển thị QR Code động cho Bản vẽ đang chọn.

    Hỗ trợ sinh mã QR offline và tự động fallback online nếu thiếu thư viện.
    """

    def __init__(self, parent: Any = None) -> None:
        """Khởi tạo QRPreviewWidget.

        Args:
            parent: Widget cha.
        """
        super().__init__("QR Code Bản Vẽ", parent)
        self.drawing_id: str = ""
        self.drive_link: str = ""
        self.version: str = ""
        self._init_ui()

    def _init_ui(self) -> None:
        """Thiết lập giao diện nút bấm và khung ảnh QR."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Nhãn hiển thị thông tin bản vẽ
        self.lbl_info = QLabel("Chọn bản vẽ để xem QR", self)
        self.lbl_info.setStyleSheet("font-weight: bold; color: #475569;")
        self.lbl_info.setWordWrap(True)
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)

        # Khung chứa ảnh QR Code
        self.lbl_qr = QLabel(self)
        self.lbl_qr.setFixedSize(160, 160)
        self.lbl_qr.setStyleSheet(
            "border: 1px solid #CBD5E1; background-color: #FFFFFF;"
        )
        self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_qr)

        # Nút Lưu ảnh QR Code về máy
        self.btn_save_qr = QPushButton("💾 Tải mã QR (.png)", self)
        self.btn_save_qr.setEnabled(False)
        self.btn_save_qr.setStyleSheet(TLSTheme.dark_action_button_stylesheet())
        self.btn_save_qr.clicked.connect(self._on_save_qr)
        layout.addWidget(self.btn_save_qr)

        self.clear_qr()

    def set_drawing(self, drawing_id: str, version: str, drive_link: str) -> None:
        """Sinh mã QR cho bản vẽ được chỉ định.

        Args:
            drawing_id: Mã bản vẽ.
            version: Phiên bản bản vẽ.
            drive_link: Link Google Drive để mở file PDF.
        """
        self.drawing_id = drawing_id or ""
        self.version = version or "V1"
        self.drive_link = drive_link or ""

        if not self.drawing_id:
            self.clear_qr()
            return

        self.lbl_info.setText(f"Mã: {self.drawing_id} ({self.version})")
        self.btn_save_qr.setEnabled(True)

        # Dữ liệu mã hóa: Ưu tiên link Drive để quét phát mở được luôn.
        # Nếu không có link Drive, mã hóa thông tin văn bản bản vẽ.
        qr_data = self.drive_link
        if not qr_data:
            qr_data = f"TLS-ERP|ID:{self.drawing_id}|VER:{self.version}|STATUS:VALID"

        # Sinh mã QR
        pixmap = self._generate_qr_pixmap(qr_data)
        if pixmap:
            self.lbl_qr.setPixmap(
                pixmap.scaled(
                    self.lbl_qr.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.lbl_qr.setText("⚠️ Lỗi tạo QR")

    def clear_qr(self) -> None:
        """Đưa widget về trạng thái trống."""
        self.drawing_id = ""
        self.drive_link = ""
        self.version = ""
        self.lbl_info.setText("Chọn bản vẽ để xem QR")
        self.lbl_qr.clear()
        self.lbl_qr.setText("Trống")
        self.btn_save_qr.setEnabled(False)

    def _generate_qr_pixmap(self, data: str) -> QPixmap | None:
        """Sinh mã QR dạng QPixmap hỗ trợ offline & online fallback.

        Args:
            data: Dữ liệu cần mã hóa vào mã QR.

        Returns:
            QPixmap chứa ảnh QR Code, hoặc None nếu thất bại.
        """
        # 1. Thử sinh offline bằng thư viện qrcode
        try:
            import qrcode

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qimage = QImage()
            if qimage.loadFromData(buffer.getvalue(), "PNG"):
                return QPixmap.fromImage(qimage)
        except Exception as e:
            logger.warning(
                "QRPreviewWidget: Lỗi tạo QR offline, chuyển sang fallback online: %s",
                str(e),
            )

        # 2. Fallback sinh online dùng API công cộng
        try:
            encoded_data = urllib.parse.quote(data)
            api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_data}"
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as response:
                img_data = response.read()
                qimage = QImage()
                if qimage.loadFromData(img_data):
                    return QPixmap.fromImage(qimage)
        except Exception as ex:
            logger.error(
                "QRPreviewWidget: Lỗi tạo QR online fallback: %s",
                str(ex),
                exc_info=True,
            )

        return None

    def _on_save_qr(self) -> None:
        """Xử lý tải ảnh QR Code về máy dạng file PNG."""
        if not self.drawing_id or not self.lbl_qr.pixmap():
            return

        default_name = f"QR_{self.drawing_id}_{self.version}.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu mã QR Bản Vẽ",
            default_name,
            "PNG Files (*.png);;All Files (*)",
        )

        if not file_path:
            return

        try:
            pixmap = self.lbl_qr.pixmap()
            if pixmap.save(file_path, "PNG"):
                QMessageBox.information(
                    self, "Thành công", f"Đã lưu mã QR thành công tại:\n{file_path}"
                )
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể ghi tệp tin hình ảnh.")
        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", f"Có lỗi xảy ra khi lưu tệp tin:\n{str(e)}"
            )
