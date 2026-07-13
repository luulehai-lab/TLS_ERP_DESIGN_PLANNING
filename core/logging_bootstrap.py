# Tên file: core/logging_bootstrap.py
# CHỨC NĂNG: Khởi tạo cấu hình logging toàn cục, excepthook, và redirect stdout/stderr cho dự án ERP.
# CHANGELOG:
# - 15:24:39 13/07/2026: [UPDATE] feat(branding): add LOGO.JPG image to sidebar and login windows and bundle it in release zip (Antigravity)
# - 09:42:18 13/07/2026: [NEW] feat(report): add visual report dashboard with charts, fix combobox/permission bugs and install global exception hook (Antigravity)
# - 09:39:00 13/07/2026: [NEW] Tạo mới module bootstrap_logging hỗ trợ TeeStream và bẫy lỗi Thread phụ cho app ERP. (Antigravity)

import logging
import logging.handlers
import os
import sys
import threading
from typing import Any, TextIO


class DummyStream:
    """Stream dummy câm lặng để tránh lỗi ghi file trên môi trường windowed đóng gói."""

    def write(self, message: str) -> int:
        return len(message)

    def flush(self) -> None:
        pass

    @property
    def encoding(self) -> str:
        return "utf-8"

    @property
    def errors(self) -> str | None:
        return None


class TeeStream:
    """Stream wrapper để nhân bản output ra cả stream gốc và logger."""

    def __init__(self, original_stream: TextIO, logger_func: Any) -> None:
        """Khởi tạo TeeStream.

        Args:
            original_stream: Stream gốc (như sys.__stdout__ hoặc sys.__stderr__).
            logger_func: Hàm log tương ứng (ví dụ: logger.info hoặc logger.error).
        """
        self.original_stream = original_stream
        self.logger_func = logger_func
        self._lock = threading.Lock()

    def write(self, message: str) -> int:
        """Ghi dữ liệu ra stream gốc và chuyển tiếp đến logger.

        Args:
            message: Chuỗi thông điệp cần ghi.

        Returns:
            Số byte đã ghi vào stream gốc.
        """
        if not message:
            return 0
        with self._lock:
            # Ghi trực tiếp ra console thật nếu tồn tại
            if self.original_stream is not None:
                try:
                    self.original_stream.write(message)
                except Exception:
                    pass
            # Loại bỏ ký tự xuống dòng thừa ở cuối khi gửi sang logger
            clean_msg = message.rstrip()
            if clean_msg:
                self.logger_func(clean_msg)
        return len(message)

    def flush(self) -> None:
        """Đẩy toàn bộ dữ liệu trong bộ đệm ra stream gốc."""
        if self.original_stream is not None:
            try:
                self.original_stream.flush()
            except Exception:
                pass

    @property
    def encoding(self) -> str:
        """Lấy bảng mã encoding của stream gốc.

        Returns:
            Tên bảng mã.
        """
        return getattr(self.original_stream, "encoding", "utf-8") if self.original_stream else "utf-8"

    @property
    def errors(self) -> str | None:
        """Lấy cơ chế xử lý lỗi (errors handling) của stream gốc.

        Returns:
            Cơ chế xử lý lỗi.
        """
        return getattr(self.original_stream, "errors", None) if self.original_stream else None


def _handle_unhandled_exception(
    exc_type: type[BaseException], exc_value: BaseException, exc_traceback: Any
) -> None:
    """Xử lý ngoại lệ không bắt được (Unhandled Exceptions) trên Main Thread.

    Args:
        exc_type: Loại ngoại lệ.
        exc_value: Giá trị ngoại lệ.
        exc_traceback: Traceback đối tượng.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger("CRITICAL_CRASH")
    logger.critical(
        "Ngoại lệ nghiêm trọng không được xử lý trên Main Thread!",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def _handle_thread_exception(args: Any) -> None:
    """Xử lý ngoại lệ không bắt được trên các Thread phụ.

    Args:
        args: Đối tượng chứa thông tin exception của thread.
    """
    logger = logging.getLogger("THREAD_CRASH")
    logger.critical(
        f"Ngoại lệ nghiêm trọng không được xử lý trên Thread: {args.thread.name if args.thread else 'Unknown'}",
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


def bootstrap_logging(
    log_dir: str = "logs", log_file: str = "app_run.log", level: int = logging.INFO
) -> None:
    """Cấu hình Root Logger toàn cục, thiết lập Rotating File theo ngày, bẫy Exception và redirect stdout/stderr.

    Args:
        log_dir: Thư mục chứa file log.
        log_file: Tên file log chính.
        level: Cấp độ log mặc định.
    """
    # 1. Tạo thư mục chứa log
    log_dir_path = os.path.abspath(log_dir)
    os.makedirs(log_dir_path, exist_ok=True)
    log_path = os.path.join(log_dir_path, log_file)

    # 2. Định nghĩa Format
    log_format = "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)

    # 3. Cấu hình Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Xóa các handler cũ nếu có
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # 4. File Handler (Timed Rotating: Theo ngày, giữ tối đa 30 ngày)
    try:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_path,
            when="D",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    except Exception as e:
        if sys.__stderr__ is not None:
            try:
                sys.__stderr__.write(f"Không thể khởi tạo File Logger: {e}\n")
            except Exception:
                pass

    # 5. Console Handler (Chỉ ghi ra console gốc nếu tồn tại để tránh crash khi chạy exe windowed)
    if sys.__stdout__ is not None:
        console_handler = logging.StreamHandler(sys.__stdout__)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)

    # 6. Thiết lập bẫy Exception
    sys.excepthook = _handle_unhandled_exception
    threading.excepthook = _handle_thread_exception

    # 7. Bắt log từ Warnings
    logging.captureWarnings(True)

    # 8. Redirect sys.stdout và sys.stderr để hứng mọi print()
    if sys.stdout is not None and sys.__stdout__ is not None:
        sys.stdout = TeeStream(sys.__stdout__, logging.getLogger("STDOUT").info)  # type: ignore
    else:
        sys.stdout = DummyStream()  # type: ignore

    if sys.stderr is not None and sys.__stderr__ is not None:
        sys.stderr = TeeStream(sys.__stderr__, logging.getLogger("STDERR").error)  # type: ignore
    else:
        sys.stderr = DummyStream()  # type: ignore

    logging.getLogger("SystemBootstrap").info(
        "Hệ thống logging toàn cục đã được khởi động thành công (UTF-8, Day-Rotate)."
    )
