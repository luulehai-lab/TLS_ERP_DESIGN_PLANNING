# 🛡️ BÁO CÁO KIỂM TOÁN CHẤT LƯỢNG MÃ NGUỒN (CLEAN CODE AUDIT)

* Điểm chất lượng mã nguồn: 🟢 **10.0/10.0**
* Độ bao phủ Type Hints: **100.0%** (158/158 hàm)
* Tổng số Lỗi nặng (High Error): **0**
* Tổng số Cảnh báo (Warning): **15**

## ⚠️ CÁC CẢNH BÁO TỐI ƯU (WARNING)
| File | Dòng | Loại cảnh báo | Chi tiết |
| :--- | :---: | :--- | :--- |
| `core/models.py` | 57 | `MULTIPLE_CLASSES_IN_FILE` | Tệp tin chứa 5 Class ở cấp module. Khuyến nghị tách mỗi file chỉ chứa 1 Class chính. |
| `core/services/auth_service.py` | 295 | `MULTIPLE_CLASSES_IN_FILE` | Tệp tin chứa 3 Class ở cấp module. Khuyến nghị tách mỗi file chỉ chứa 1 Class chính. |
| `core/services/drawing_service.py` | 18 | `FUNCTION_TOO_LONG` | Hàm `create_drawing` dài 70 dòng, vượt quá giới hạn mềm 50 dòng. |
| `core/services/drawing_service.py` | 90 | `FUNCTION_TOO_LONG` | Hàm `update_drawing_status` dài 58 dòng, vượt quá giới hạn mềm 50 dòng. |
| `core/services/project_service.py` | 20 | `FUNCTION_TOO_LONG` | Hàm `create_project` dài 55 dòng, vượt quá giới hạn mềm 50 dòng. |
| `core/services/section_service.py` | 18 | `FUNCTION_TOO_LONG` | Hàm `create_section` dài 64 dòng, vượt quá giới hạn mềm 50 dòng. |
| `ui/login_window.py` | 75 | `MULTIPLE_CLASSES_IN_FILE` | Tệp tin chứa 2 Class ở cấp module. Khuyến nghị tách mỗi file chỉ chứa 1 Class chính. |
| `ui/sidebar.py` | 263 | `FUNCTION_TOO_LONG` | Hàm `_confirm_and_delete_project` dài 52 dòng, vượt quá giới hạn mềm 50 dòng. |
| `ui/common/base_drawing_view.py` | 165 | `FUNCTION_TOO_LONG` | Hàm `_on_drawings_loaded` dài 60 dòng, vượt quá giới hạn mềm 50 dòng. |
| `ui/common/workers.py` | 49 | `MULTIPLE_CLASSES_IN_FILE` | Tệp tin chứa 3 Class ở cấp module. Khuyến nghị tách mỗi file chỉ chứa 1 Class chính. |
| `ui/styles/theme.py` | 36 | `FUNCTION_TOO_LONG` | Hàm `get_common_qss` dài 87 dòng, vượt quá giới hạn mềm 50 dòng. |
| `ui/styles/theme.py` | 125 | `FUNCTION_TOO_LONG` | Hàm `main_window_stylesheet` dài 86 dòng, vượt quá giới hạn mềm 50 dòng. |
| `ui/styles/theme.py` | 242 | `FUNCTION_TOO_LONG` | Hàm `login_stylesheet` dài 81 dòng, vượt quá giới hạn mềm 50 dòng. |
| `ui/views/thiet_ke_view.py` | 135 | `FUNCTION_TOO_LONG` | Hàm `_on_create_drawing` dài 53 dòng, vượt quá giới hạn mềm 50 dòng. |
| `ui/views/du_an/section_widget.py` | 187 | `FUNCTION_TOO_LONG` | Hàm `load_sections` dài 55 dòng, vượt quá giới hạn mềm 50 dòng. |

================================================================================
