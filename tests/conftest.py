# Tên file: tests/conftest.py
# CHỨC NĂNG: Cấu hình chung và Fixtures cho hệ thống Testing (pytest) của ERP.
# CHANGELOG:
# - 15:17:43 11/07/2026: [NEW] feat(ke-hoach): replace performer text input with dropdown and enforce selection (Antigravity)
# - 14:18:00 11/07/2026: [NEW] Thiết lập môi trường và cấu hình pytest cho ERP. (Antigravity)

import os
import sys

# Thêm project root vào path để có thể import các module nội bộ của ERP
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
