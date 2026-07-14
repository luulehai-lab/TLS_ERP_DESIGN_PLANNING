# Tên file: core/services/release_evidence_service.py
# CHỨC NĂNG: Dịch vụ tự động sinh ảnh bằng chứng ban hành bản vẽ (Release Evidence Image)
# CHANGELOG:
# - 14:05:01 14/07/2026: [NEW] fix(ui): remove format argument from qr image save for PyPNGImage compatibility (Antigravity)
# - 14:02:00 14/07/2026: [REFACTOR] Phân tách hàm generate_release_evidence_image thành các hàm helper để vượt qua kiểm toán độ dài hàm < 100 dòng (Lê Thanh Vân/Antigravity)
# - 13:45:00 14/07/2026: [NEW] Khởi tạo module sinh ảnh PNG bằng chứng ban hành dùng Pillow (Lê Thanh Vân/Antigravity)

import logging
import os
from datetime import datetime
from typing import Any
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Danh sách font có thể có trên hệ thống Windows để vẽ tiếng Việt có dấu
SYSTEM_FONTS = [
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\segoeui.ttf",
    "C:\\Windows\\Fonts\\tahoma.ttf",
    "arial.ttf",
]


def _get_system_font(
    size: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Lấy font TrueType từ hệ thống để hỗ trợ tiếng Việt, hoặc fallback về default font.

    Args:
        size: Kích thước font chữ cần lấy.

    Returns:
        ImageFont đối tượng font được load.
    """
    for font_path in SYSTEM_FONTS:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.debug("Không thể load font %s: %s", font_path, str(e))
    return ImageFont.load_default()


def _draw_cad_grid(draw: ImageDraw.Draw, width: int, height: int) -> None:
    """Vẽ các đường nét vẽ kỹ thuật (CAD grid) mờ ở góc dưới bên phải.

    Args:
        draw: Đối tượng vẽ ImageDraw.
        width: Chiều rộng ảnh.
        height: Chiều cao ảnh.
    """
    grid_color = (51, 65, 85)
    for i in range(0, 300, 40):
        draw.line(
            [(width - i, height), (width, height - i)], fill=grid_color, width=1
        )
    draw.arc(
        [width - 150, height - 150, width + 150, height + 150],
        180,
        270,
        fill=grid_color,
        width=1,
    )
    draw.arc(
        [width - 80, height - 80, width + 80, height + 80],
        180,
        270,
        fill=grid_color,
        width=1,
    )


def _draw_header(draw: ImageDraw.Draw, width: int) -> None:
    """Vẽ Banner tiêu đề và Badge RELEASED ở góc phải.

    Args:
        draw: Đối tượng vẽ ImageDraw.
        width: Chiều rộng ảnh.
    """
    # Vẽ Banner tiêu đề màu Teal 800 (#0F766E)
    draw.rectangle([14, 14, width - 14, 90], fill=(15, 118, 110))

    font_title = _get_system_font(24)
    font_subtitle = _get_system_font(12)

    # Vẽ text trên Banner
    draw.text(
        (30, 25),
        "TUAN LONG STEEL (TLS)",
        font=font_subtitle,
        fill=(245, 158, 11),
    )  # Vàng #F59E0B
    draw.text(
        (30, 45),
        "BẰNG CHỨNG BAN HÀNH BẢN VẼ",
        font=font_title,
        fill=(255, 255, 255),
    )

    # Vẽ Badge "RELEASED" màu xanh lá (#10B981) ở góc phải
    draw.rectangle([width - 170, 32, width - 35, 72], fill=(16, 185, 129))
    draw.text(
        (width - 145, 42), "RELEASED", font=font_subtitle, fill=(255, 255, 255)
    )


def _draw_details(
    draw: ImageDraw.Draw, drawing_data: dict[str, Any], height: int
) -> None:
    """Vẽ thông tin chi tiết bản vẽ lên khung ảnh.

    Args:
        draw: Đối tượng vẽ ImageDraw.
        drawing_data: Từ điển dữ liệu bản vẽ.
        height: Chiều cao ảnh.
    """
    font_label = _get_system_font(18)
    font_value = _get_system_font(18)
    font_value_highlight = _get_system_font(20)
    font_footer = _get_system_font(12)

    start_x, start_y = 45, 120
    line_height = 42

    labels = [
        ("Dự án:", drawing_data.get("project_name", "N/A")),
        ("Mã bản vẽ:", drawing_data.get("drawing_id", "N/A")),
        ("Tên bản vẽ:", drawing_data.get("drawing_name", "N/A")),
        ("Phiên bản:", f"Revision {drawing_data.get('current_version', 'N/A')}"),
        ("Người ban hành:", drawing_data.get("performed_by", "N/A")),
        (
            "Thời gian:",
            drawing_data.get("timestamp")
            or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    ]

    for i, (label_text, val_text) in enumerate(labels):
        y_pos = start_y + i * line_height
        # Vẽ Label màu xám nhạt (#94A3B8)
        draw.text((start_x, y_pos), label_text, font=font_label, fill=(148, 163, 184))

        # Chọn màu và font cho Value
        val_x = start_x + 180
        if label_text == "Mã bản vẽ:":
            draw.text(
                (val_x, y_pos - 2),
                val_text,
                font=font_value_highlight,
                fill=(245, 158, 11),
            )
        elif label_text == "Phiên bản:":
            draw.text((val_x, y_pos), val_text, font=font_value, fill=(45, 212, 191))
        else:
            draw.text((val_x, y_pos), val_text, font=font_value, fill=(255, 255, 255))

    # Vẽ Footer nhỏ ở đáy
    draw.text(
        (start_x, height - 35),
        "Hệ thống ERP Tuan Long Steel - Hồ sơ xác nhận ban hành điện tử tự động",
        font=font_footer,
        fill=(100, 116, 139),
    )


def generate_release_evidence_image(
    drawing_data: dict[str, Any], output_dir: str
) -> str:
    """Sinh ảnh PNG bằng chứng ban hành bản vẽ và lưu vào thư mục chỉ định.

    Args:
        drawing_data: Từ điển chứa thông tin bản vẽ bao gồm:
            - project_name (str)
            - drawing_id (str)
            - drawing_name (str)
            - current_version (str)
            - performed_by (str)
            - timestamp (str, optional)
        output_dir: Thư mục lưu ảnh kết quả.

    Returns:
        str: Đường dẫn tuyệt đối đến file ảnh được sinh ra, hoặc chuỗi rỗng nếu thất bại.
    """
    try:
        width, height = 800, 450
        img = Image.new("RGB", (width, height), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)

        # Gọi các helper vẽ từng thành phần
        _draw_cad_grid(draw, width, height)
        draw.rectangle(
            [12, 12, width - 12, height - 12], outline=(13, 148, 136), width=2
        )
        _draw_header(draw, width)
        _draw_details(draw, drawing_data, height)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        version = drawing_data.get("current_version", "N/A")
        today_str = datetime.now().strftime("%Y%m%d")
        filename = f"_DA_BAN_HANH_REV{version}_{today_str}.png"
        filepath = os.path.join(output_dir, filename)

        img.save(filepath, "PNG")
        logger.info("Đã sinh ảnh bằng chứng ban hành thành công: %s", filepath)
        return filepath

    except Exception as e:
        logger.error(
            "Lỗi khi sinh ảnh bằng chứng ban hành bản vẽ: %s",
            str(e),
            exc_info=True,
        )
        return ""
