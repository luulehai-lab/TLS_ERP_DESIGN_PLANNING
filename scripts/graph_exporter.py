# Tên file: scripts/graph_exporter.py
# CHỨC NĂNG: Xuất dữ liệu đồ thị sang JSON hoặc Markdown Mermaid
# CHANGELOG:
# - 18:28:01 10/07/2026: [NEW] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:56:00 10/07/2026: [NEW] Khởi tạo module xuất đồ thị kiến trúc tách từ generate_codebase_graph.py (Lê Thanh Vân/Antigravity)

import json
from pathlib import Path
from typing import Any
from scripts.graph_core import CodebaseGraph


class GraphExporter:
    """Xuất dữ liệu đồ thị sang JSON hoặc Markdown Mermaid."""

    def __init__(self, graph: CodebaseGraph) -> None:
        """Khởi tạo exporter với đồ thị truyền vào.

        Args:
            graph: Đồ thị codebase đã phân giải liên kết.
        """
        self.graph: CodebaseGraph = graph

    def to_json(self, output_path: Path, files_cache: dict[str, Any]) -> None:
        """Xuất toàn bộ đồ thị và tệp cache vào JSON.

        Args:
            output_path: Đường dẫn tệp JSON đầu ra.
            files_cache: Dữ liệu cache của các files.
        """
        data = {
            "nodes": list(self.graph.nodes.values()),
            "edges": self.graph.edges,
            "_files_cache": files_cache,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def to_mermaid(self, focus_modules: list[str] | None = None) -> str:
        """Tạo mã Mermaid TD. Có thể lọc theo các module để giữ sơ đồ gọn gàng.

        Args:
            focus_modules: Danh sách tiền tố module cần tập trung hiển thị (lọc).

        Returns:
            Chuỗi mã đồ thị dạng Mermaid TD.
        """
        lines = ["graph TD"]
        lines.append("    classDef file fill:#f9f,stroke:#333,stroke-width:1px;")
        lines.append("    classDef cls fill:#bbf,stroke:#333,stroke-width:1px;")
        lines.append("    classDef func fill:#bfb,stroke:#333,stroke-width:1px;")

        filtered_nodes = {}
        for nid, node in self.graph.nodes.items():
            if focus_modules:
                match = False
                for mod in focus_modules:
                    if nid.startswith(mod):
                        match = True
                        break
                if not match:
                    continue
            filtered_nodes[nid] = node

        for nid, node in filtered_nodes.items():
            label = node["label"]
            ntype = node["type"]
            safe_id = nid.replace(".", "_").replace("/", "_").replace("-", "_")

            if ntype == "file":
                lines.append(f'    {safe_id}["📄 {label}"]:::file')
            elif ntype == "class":
                lines.append(f'    {safe_id}["🧩 {label}"]:::cls')
            elif ntype == "function":
                lines.append(f'    {safe_id}["⚙️ {label}()"]:::func')

        for edge in self.graph.edges:
            src, tgt, etype = edge["source"], edge["target"], edge["type"]
            if src in filtered_nodes and tgt in filtered_nodes:
                src_safe = src.replace(".", "_").replace("/", "_").replace("-", "_")
                tgt_safe = tgt.replace(".", "_").replace("/", "_").replace("-", "_")

                if etype == "contains":
                    lines.append(f"    {src_safe} -->|contains| {tgt_safe}")
                elif etype == "calls":
                    lines.append(f"    {src_safe} ==>|calls| {tgt_safe}")
                elif etype == "inherits_from":
                    lines.append(f"    {src_safe} -.->|inherits| {tgt_safe}")

        return "\n".join(lines)
