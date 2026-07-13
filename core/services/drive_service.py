# Tên file: core/services/drive_service.py
# CHỨC NĂNG: Xử lý tương tác Google Drive API (tạo thư mục, tải tệp, cấp quyền chia sẻ)
# CHANGELOG:
# - 14:25:54 13/07/2026: [NEW] feat(search): implement project and drawing search with client-side filters (Antigravity)
# - 14:10:00 13/07/2026: [NEW] Khởi tạo drive_service.py quản lý upload bản vẽ bằng Service Account (Antigravity)

import os
import logging
from typing import Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config

logger = logging.getLogger(__name__)


def _get_drive_service() -> Any:
    """Khởi tạo và trả về đối tượng kết nối Google Drive API v3.

    Returns:
        Đối tượng service kết nối Google Drive API hoặc None nếu lỗi.
    """
    credentials_file = config.GOOGLE_SERVICE_ACCOUNT_FILE
    if not credentials_file or not os.path.exists(credentials_file):
        logger.error(
            "DriveService: Không tìm thấy tệp tin xác thực Service Account tại '%s'",
            credentials_file,
        )
        return None

    try:
        scopes = ["https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=scopes
        )
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        logger.error(
            "DriveService: Lỗi khởi tạo Google Drive Service: %s",
            str(e),
            exc_info=True,
        )
        return None


def create_drive_folder(folder_name: str, parent_id: str) -> str | None:
    """Tạo một thư mục con trên Google Drive.

    Args:
        folder_name: Tên thư mục cần tạo.
        parent_id: ID thư mục cha chứa thư mục mới này.

    Returns:
        str | None: ID thư mục vừa tạo, hoặc None nếu lỗi.
    """
    service = _get_drive_service()
    if not service:
        return None

    logger.info(
        "DriveService: Tạo thư mục '%s' trong thư mục cha ID='%s'",
        folder_name,
        parent_id,
    )
    try:
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id] if parent_id else [],
        }
        folder = (
            service.files()
            .create(body=file_metadata, fields="id, webViewLink")
            .execute()
        )
        folder_id = folder.get("id")
        logger.info("DriveService: Đã tạo thư mục thành công. ID='%s'", folder_id)
        return folder_id
    except Exception as e:
        logger.error(
            "DriveService: Lỗi khi tạo thư mục Google Drive: %s",
            str(e),
            exc_info=True,
        )
        return None


def set_anyone_read_permission(file_id: str) -> bool:
    """Thiết lập quyền đọc công khai cho bất kỳ ai có liên kết (anyoneWithLink).

    Args:
        file_id: ID của file hoặc thư mục trên Google Drive.

    Returns:
        bool: True nếu thiết lập thành công, ngược lại False.
    """
    service = _get_drive_service()
    if not service:
        return False

    logger.info(
        "DriveService: Thiết lập quyền truy cập công khai cho tệp ID='%s'", file_id
    )
    try:
        permission = {"type": "anyone", "role": "reader"}
        service.permissions().create(fileId=file_id, body=permission).execute()
        logger.info("DriveService: Đã cấp quyền xem công khai thành công.")
        return True
    except Exception as e:
        logger.error(
            "DriveService: Lỗi thiết lập quyền truy cập trên Drive: %s",
            str(e),
            exc_info=True,
        )
        return False


def upload_single_file(local_file_path: str, parent_id: str) -> str | None:
    """Tải một file cục bộ lên thư mục chỉ định của Google Drive và chia sẻ công khai.

    Args:
        local_file_path: Đường dẫn tệp tin cục bộ.
        parent_id: ID thư mục Google Drive cha để lưu tệp tin.

    Returns:
        str | None: Đường link chia sẻ webViewLink của tệp tin, hoặc None nếu lỗi.
    """
    service = _get_drive_service()
    if not service:
        return None

    if not os.path.exists(local_file_path):
        logger.error(
            "DriveService: File cục bộ không tồn tại: '%s'", local_file_path
        )
        return None

    file_name = os.path.basename(local_file_path)
    logger.info(
        "DriveService: Tải file '%s' lên thư mục cha ID='%s'", file_name, parent_id
    )
    try:
        file_metadata = {
            "name": file_name,
            "parents": [parent_id] if parent_id else [],
        }
        media = MediaFileUpload(local_file_path, resumable=True)
        uploaded_file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )

        file_id = uploaded_file.get("id")
        share_link = uploaded_file.get("webViewLink")

        # Thiết lập quyền chia sẻ công khai
        set_anyone_read_permission(file_id)

        logger.info("DriveService: Tải tệp thành công. Link: %s", share_link)
        return share_link
    except Exception as e:
        logger.error(
            "DriveService: Lỗi trong quá trình upload tệp: %s",
            str(e),
            exc_info=True,
        )
        return None


def upload_local_directory(local_dir_path: str, parent_id: str) -> str | None:
    """Tạo thư mục trên Drive, tải toàn bộ tệp bên trong lên và chia sẻ công khai.

    Args:
        local_dir_path: Đường dẫn thư mục cục bộ.
        parent_id: ID thư mục Google Drive cha.

    Returns:
        str | None: Đường link webViewLink của thư mục Google Drive vừa tạo, hoặc None nếu lỗi.
    """
    service = _get_drive_service()
    if not service:
        return None

    if not os.path.isdir(local_dir_path):
        logger.error(
            "DriveService: Thư mục cục bộ không hợp lệ: '%s'", local_dir_path
        )
        return None

    dir_name = os.path.basename(local_dir_path.rstrip("/\\"))
    # Tạo thư mục tương ứng trên Drive
    drive_folder_id = create_drive_folder(dir_name, parent_id)
    if not drive_folder_id:
        return None

    logger.info(
        "DriveService: Upload thư mục cục bộ '%s' thành thư mục Drive ID='%s'",
        local_dir_path,
        drive_folder_id,
    )
    try:
        # Lấy link webViewLink của thư mục vừa tạo
        folder_info = (
            service.files()
            .get(fileId=drive_folder_id, fields="webViewLink")
            .execute()
        )
        folder_link = folder_info.get("webViewLink")

        # Duyệt và upload tất cả file con cấp 1 (không đệ quy sâu để tránh quá tải)
        for item in os.listdir(local_dir_path):
            item_path = os.path.join(local_dir_path, item)
            if os.path.isfile(item_path):
                # Upload file con vào thư mục vừa tạo
                upload_single_file_no_share(service, item_path, drive_folder_id)

        # Cấp quyền cho thư mục cha (thư mục vừa tạo), tự động áp dụng cho các file con bên trong
        set_anyone_read_permission(drive_folder_id)

        logger.info(
            "DriveService: Tải thư mục thành công. Link: %s", folder_link
        )
        return folder_link
    except Exception as e:
        logger.error(
            "DriveService: Lỗi trong quá trình upload thư mục: %s",
            str(e),
            exc_info=True,
        )
        return None


def upload_single_file_no_share(service: Any, local_file_path: str, parent_id: str) -> str | None:
    """Tải tệp tin lên nhưng không set quyền riêng biệt (dành cho hàm upload thư mục để tránh API calls liên tục).

    Args:
        service: Google Drive API service client.
        local_file_path: Đường dẫn tệp tin cục bộ.
        parent_id: ID thư mục Google Drive cha.

    Returns:
        str | None: ID tệp tin vừa tải, hoặc None nếu lỗi.
    """
    try:
        file_name = os.path.basename(local_file_path)
        file_metadata = {
            "name": file_name,
            "parents": [parent_id] if parent_id else [],
        }
        media = MediaFileUpload(local_file_path, resumable=True)
        uploaded_file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        return uploaded_file.get("id")
    except Exception as e:
        logger.error(
            "DriveService: Lỗi upload tệp con '%s': %s",
            local_file_path,
            str(e),
        )
        return None
