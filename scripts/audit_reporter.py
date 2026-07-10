# Tên file: scripts/audit_reporter.py
# CHỨC NĂNG: Cung cấp các tiện ích định dạng và lưu trữ báo cáo kiểm toán chất lượng mã nguồn (Clean Code Audit).
# CHANGELOG:
# - 18:28:00 10/07/2026: [NEW] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:41:00 10/07/2026: [NEW] Khởi tạo module phụ trợ phân tách từ scripts/audit_code_quality.py để giảm dòng (Lê Thanh Vân/Antigravity)

import json
from pathlib import Path
from typing import Any


def generate_markdown_report(
    reports: list[dict[str, Any]],
    duplicates: list[dict[str, Any]],
    score: float,
    *,
    th_coverage: float,
    total_errors: int,
    total_warnings: int,
    total_funcs: int,
    total_th_pass: int,
) -> str:
    """Tạo báo cáo chất lượng mã nguồn dưới dạng Markdown."""
    status_emoji = "🟢" if score >= 8.0 else ("⚠️" if score >= 5.0 else "🚨")
    lines = [
        "# 🛡️ BÁO CÁO KIỂM TOÁN CHẤT LƯỢNG MÃ NGUỒN (CLEAN CODE AUDIT)",
        "",
        f"* Điểm chất lượng mã nguồn: {status_emoji} **{score:.1f}/10.0**",
        f"* Độ bao phủ Type Hints: **{th_coverage:.1f}%** ({total_th_pass}/{total_funcs} hàm)",
        f"* Tổng số Lỗi nặng (High Error): **{total_errors}**",
        f"* Tổng số Cảnh báo (Warning): **{total_warnings}**",
        "",
    ]

    if total_errors > 0:
        lines.append("## ❌ CÁC LỖI NẶNG CẦN SỬA NGAY (BLOCK COMMIT)")
        lines.append("| File | Dòng | Loại lỗi | Chi tiết vi phạm |")
        lines.append("| :--- | :---: | :--- | :--- |")
        for r in reports:
            for err in r["errors"]:
                lines.append(f"| `{r['file']}` | {err['line']} | `{err['type']}` | {err['msg']} |")
        lines.append("")

    has_warnings = any(len(r["warnings"]) > 0 for r in reports)
    if has_warnings:
        lines.append("## ⚠️ CÁC CẢNH BÁO TỐI ƯU (WARNING)")
        lines.append("| File | Dòng | Loại cảnh báo | Chi tiết |")
        lines.append("| :--- | :---: | :--- | :--- |")
        for r in reports:
            for warn in r["warnings"]:
                lines.append(f"| `{r['file']}` | {warn['line']} | `{warn['type']}` | {warn['msg']} |")
        lines.append("")

    if duplicates:
        lines.append("## 🔌 CẢNH BÁO LẶP LOGIC THUẬT TOÁN (AST SIMILARITY)")
        lines.append("| File 1 (Hàm 1) | File 2 (Hàm 2) | Độ tương đồng | Khuyến nghị |")
        lines.append("| :--- | :--- | :---: | :--- |")
        for d in duplicates:
            lines.append(
                f"| `{d['file1']}`: {d['func1']} (dòng {d['line1']}) | `{d['file2']}`: {d['func2']} (dòng {d['line2']}) | **{d['similarity']}%** | Gộp logic chung vào `core/word_architect.py` hoặc `core/utils/` |"
            )
        lines.append("")

    lines.append("=" * 80)
    lines.append("")
    return "\n".join(lines)


def generate_json_report(
    reports: list[dict[str, Any]],
    duplicates: list[dict[str, Any]],
    score: float,
    *,
    th_coverage: float,
    total_errors: int,
    total_warnings: int,
    total_funcs: int,
    total_th_pass: int,
) -> dict[str, Any]:
    """Tạo báo cáo chất lượng mã nguồn định dạng JSON."""
    return {
        "score": round(score, 2),
        "type_hint_coverage": round(th_coverage, 2),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "total_funcs": total_funcs,
        "total_th_pass": total_th_pass,
        "reports": reports,
        "duplicates": duplicates,
    }


def save_report_to_file(
    output_path_str: str,
    report_format: str,
    md_report: str,
    json_report: dict[str, Any],
) -> None:
    """Lưu nội dung báo cáo chất lượng mã nguồn ra tệp tin tương ứng."""
    output_path = Path(output_path_str)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    base_path = output_path
    suffix = output_path.suffix.lower()
    if suffix in {".md", ".json"}:
        base_path = output_path.with_suffix("")

    written_files = []
    if report_format in {"md", "both"}:
        md_file = base_path.with_suffix(".md") if report_format == "both" or suffix != ".json" else output_path
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_report)
        written_files.append(str(md_file))

    if report_format in {"json", "both"}:
        json_file = base_path.with_suffix(".json") if report_format == "both" or suffix != ".md" else output_path
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
        written_files.append(str(json_file))

    print(f"\n[OK] Đã xuất báo cáo chất lượng mã nguồn ra: {', '.join(written_files)}")
