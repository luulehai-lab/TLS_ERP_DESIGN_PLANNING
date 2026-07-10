# Tên file: scripts/audit_duplication.py
# CHỨC NĂNG: Phân tích so sánh trùng lặp logic thuật toán (AST similarity) trong codebase.
# CHANGELOG:
# - 18:28:00 10/07/2026: [NEW] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:45:00 10/07/2026: [NEW] Tách thuật toán check logic duplication từ scripts/audit_code_quality.py sang module riêng (Lê Thanh Vân/Antigravity)

import ast
import copy
import difflib
from typing import Any


class DuplicationChecker:
    """Hệ thống phân tích AST nâng cao để phát hiện trùng lặp logic thuật toán."""

    @staticmethod
    def normalize_ast_structure(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Chuẩn hóa cây AST của hàm nhằm so sánh độ tương đồng logic."""

        class ASTNormalizer(ast.NodeTransformer):
            def visit_Name(self, n):
                return ast.Name(id="var", ctx=n.ctx)

            def visit_Constant(self, n):
                return ast.Constant(value="const")

            def visit_arg(self, n):
                return ast.arg(arg="var_arg", annotation=None)

        copied = copy.deepcopy(node)
        # Loại bỏ docstring khỏi cây để so sánh thuần logic
        if copied.body and isinstance(copied.body[0], ast.Expr):
            val = copied.body[0].value
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                copied.body.pop(0)

        normalizer = ASTNormalizer()
        normalized = normalizer.visit(copied)
        return ast.dump(normalized)

    @classmethod
    def check_logic_duplication(
        cls, function_signatures: list[dict[str, Any]], similarity_threshold: float = 0.75
    ) -> list[dict[str, Any]]:
        """So sánh các hàm để phát hiện trùng lặp logic thuật toán (AST Similarity).

        Sử dụng kỹ thuật sắp xếp theo độ dài AST kết hợp cửa sổ trượt (sliding window)
        và Jaccard Similarity 3-gram để lọc sớm cực nhanh.
        """
        duplicates = []

        # 1. Loại bỏ các hàm quá ngắn trước để giảm kích thước tập dữ liệu
        valid_sigs = [sig for sig in function_signatures if len(sig["ast_str"]) >= 4000]

        # 2. Sắp xếp các hàm theo độ dài của chuỗi AST tăng dần
        valid_sigs.sort(key=lambda x: len(x["ast_str"]))

        # 3. Tiền tính toán n-grams để tối ưu hóa bộ lọc Jaccard
        ngrams_cache = {}
        for sig in valid_sigs:
            s = sig["ast_str"]
            ngrams_cache[id(sig)] = set(s[i : i + 3] for i in range(len(s) - 2)) if len(s) >= 3 else set()

        # 4. Duyệt so sánh với kỹ thuật break-early dựa trên độ dài
        for i in range(len(valid_sigs)):
            sig1 = valid_sigs[i]
            len1 = len(sig1["ast_str"])
            set1 = ngrams_cache[id(sig1)]

            for j in range(i + 1, len(valid_sigs)):
                sig2 = valid_sigs[j]
                len2 = len(sig2["ast_str"])

                # break-early dựa trên độ dài lý thuyết tối đa
                if len2 > 1.667 * len1:
                    break

                # Nếu thuộc cùng 1 file và tên giống nhau (đè/overload) thì bỏ qua
                if sig1["file"] == sig2["file"] and sig1["func_name"] == sig2["func_name"]:
                    continue

                # Bỏ qua các hàm thiết lập UI đặc thù PyQt6
                ui_funcs = {"setupui", "retranslateui", "paintevent", "initui", "init_ui"}
                if sig1["func_name"].lower() in ui_funcs or sig2["func_name"].lower() in ui_funcs:
                    continue

                # Lọc sớm Jaccard Similarity trên 3-grams
                set2 = ngrams_cache[id(sig2)]
                union_len = len(set1.union(set2))
                if union_len > 0:
                    jaccard = len(set1.intersection(set2)) / union_len
                    if jaccard < 0.65:
                        continue
                else:
                    continue

                # Sử dụng difflib để so sánh độ tương đồng chuỗi AST chi tiết
                ratio = difflib.SequenceMatcher(None, sig1["ast_str"], sig2["ast_str"]).ratio()
                if ratio >= similarity_threshold:
                    duplicates.append(
                        {
                            "file1": sig1["file"],
                            "func1": sig1["func_name"],
                            "line1": sig1["line"],
                            "file2": sig2["file"],
                            "func2": sig2["func_name"],
                            "line2": sig2["line"],
                            "similarity": round(ratio * 100, 1),
                        }
                    )
        return duplicates
