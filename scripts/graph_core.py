# Tên file: scripts/graph_core.py
# CHỨC NĂNG: Xây dựng đồ thị logic codebase và thuật toán truy vết tác động sửa đổi
# CHANGELOG:
# - 18:28:01 10/07/2026: [NEW] docs(rules): enforce strict UI/Backend separation and no duplicate QSS constraint (Antigravity)
# - 17:56:00 10/07/2026: [NEW] Khởi tạo module Đồ thị kiến trúc tách từ generate_codebase_graph.py (Lê Thanh Vân/Antigravity)

from pathlib import Path
from typing import Any


class CodebaseGraph:
    """Quản lý Đồ thị Tri thức (Nodes & Edges), kết nối các thực thể và phân tích tác động."""

    def __init__(self) -> None:
        """Khởi tạo đồ thị rỗng."""
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, str]] = []
        self.adjacency_list: dict[str, set[str]] = {}  # Đồ thị xuôi
        self.reverse_adjacency_list: dict[
            str, set[str]
        ] = {}  # Đồ thị ngược để tìm Impact

    def add_node(self, node_id: str, label: str, node_type: str, **kwargs: Any) -> None:
        """Thêm node mới vào đồ thị.

        Args:
            node_id: ID định danh độc nhất cho Node.
            label: Nhãn hiển thị của Node.
            node_type: Loại node (file, class, function).
            **kwargs: Các thuộc tính mở rộng khác (file_path, line...).
        """
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "type": node_type,
            **kwargs,
        }

    def add_edge(self, source: str, target: str, edge_type: str) -> None:
        """Thêm một cạnh (cung liên kết) giữa hai node.

        Args:
            source: ID node nguồn.
            target: ID node đích.
            edge_type: Loại liên kết (contains, calls, inherits_from).
        """
        edge = {"source": source, "target": target, "type": edge_type}
        if edge not in self.edges:
            self.edges.append(edge)

            if source not in self.adjacency_list:
                self.adjacency_list[source] = set()
            self.adjacency_list[source].add(target)

            if target not in self.reverse_adjacency_list:
                self.reverse_adjacency_list[target] = set()
            self.reverse_adjacency_list[target].add(source)

    def resolve_relationships(self, parsers_data: list[dict[str, Any]]) -> None:
        """Kết hợp dữ liệu từ tất cả file đã parse để tạo liên kết đồ thị logic.

        Args:
            parsers_data: Danh sách dữ liệu parser trích xuất từ các files.
        """
        # Bước 1: Tạo các node File, Class và Function định nghĩa sẵn
        for pdata in parsers_data:
            module_name = pdata["module_name"]
            file_path = pdata["file_path"]
            self.add_node(
                module_name, Path(file_path).name, "file", file_path=file_path
            )

            for cls in pdata["classes"]:
                self.add_node(
                    cls["id"],
                    cls["name"],
                    "class",
                    file_path=file_path,
                    line=cls["line"],
                )
                self.add_edge(module_name, cls["id"], "contains")

                # Liên kết kế thừa (Inheritance)
                for base in cls["bases"]:
                    resolved_base = self._resolve_class_by_name_from_data(base, pdata)
                    if resolved_base:
                        self.add_edge(cls["id"], resolved_base, "inherits_from")

            for func in pdata["functions"]:
                self.add_node(
                    func["id"],
                    func["name"],
                    "function",
                    file_path=file_path,
                    line=func["line"],
                )
                self.add_edge(func["parent_id"], func["id"], "contains")

        # Bước 2: Phân tích các lệnh gọi hàm (Calls) để tạo các cạnh CALLS
        for pdata in parsers_data:
            for call in pdata["calls"]:
                caller_id = call["caller"]
                call_name = call["call_name"]
                caller_obj = call["caller_obj"]

                target_id = self._resolve_call_target_from_data(
                    call_name, caller_obj, pdata
                )
                if target_id:
                    self.add_edge(caller_id, target_id, "calls")

    def _resolve_class_by_name_from_data(
        self, class_name: str, pdata: dict[str, Any]
    ) -> str | None:
        """Tìm ID đầy đủ của Class dựa trên tên gọi và danh sách imports.

        Args:
            class_name: Tên của Class cần phân giải.
            pdata: Dữ liệu parser của tệp tin hiện tại chứa tham chiếu.

        Returns:
            ID đầy đủ dạng chuỗi của Class nếu tìm thấy, ngược lại trả về None.
        """
        # 1. Tìm trong chính file hiện tại
        local_id = f"{pdata['module_name']}.{class_name}"
        if local_id in self.nodes:
            return local_id

        # 2. Tìm qua các imports
        for imp in pdata["imports"]:
            if imp["type"] == "from" and imp["name"] == class_name:
                target_module = imp["module"]
                return f"{target_module}.{class_name}"
            elif imp["type"] == "direct" and imp["asname"] == class_name:
                return imp["name"]
            elif imp["type"] == "direct" and imp["name"].endswith(f".{class_name}"):
                return imp["name"]

        # 3. Quét toàn bộ đồ thị xem có Class nào trùng tên độc nhất không
        matches = [
            nid
            for nid, node in self.nodes.items()
            if node["type"] == "class" and node["label"] == class_name
        ]
        if len(matches) == 1:
            return matches[0]

        return None

    def _resolve_call_target_from_data(
        self, call_name: str, caller_obj: str | None, pdata: dict[str, Any]
    ) -> str | None:
        """Dựa trên Type Hints hoặc quy tắc cấu trúc để suy luận phương thức đích.

        Args:
            call_name: Tên hàm được gọi.
            caller_obj: Đối tượng gọi hàm (self, class instance, module...).
            pdata: Dữ liệu parser của tệp tin hiện tại chứa lệnh gọi.

        Returns:
            ID đầy đủ dạng chuỗi của phương thức đích nếu suy luận thành công, ngược lại trả về None.
        """
        # caller_id là hàm chứa cuộc gọi hiện tại
        caller_func = next(
            (f for f in pdata["functions"] if f["id"] == pdata.get("current_function")),
            None,
        )
        caller_id = caller_func["id"] if caller_func else pdata["module_name"]

        # Trường hợp 1: self.method()
        if caller_obj == "self":
            # Tìm class hiện tại chứa caller
            current_class = None
            for cls in pdata["classes"]:
                if caller_id.startswith(f"{cls['id']}."):
                    current_class = cls["id"]
                    break

            if current_class:
                target_id = f"{current_class}.{call_name}"
                if target_id in self.nodes:
                    return target_id

                # Kiểm tra xem có kế thừa từ class cha nào không
                cls_node = next(
                    (c for c in pdata["classes"] if c["id"] == current_class), None
                )
                if cls_node:
                    for base in cls_node["bases"]:
                        base_id = self._resolve_class_by_name_from_data(base, pdata)
                        if base_id:
                            parent_target = f"{base_id}.{call_name}"
                            if parent_target in self.nodes:
                                return parent_target

        # Trường hợp 2: Biến nội bộ có Type Hint rõ ràng trong hàm gọi
        if caller_obj:
            caller_func = next(
                (f for f in pdata["functions"] if f["id"] == caller_id), None
            )
            if caller_func and caller_obj in caller_func.get("args_hints", {}):
                hint = caller_func["args_hints"][caller_obj]
                class_id = self._resolve_class_by_name_from_data(hint, pdata)
                if class_id:
                    target_id = f"{class_id}.{call_name}"
                    if target_id in self.nodes:
                        return target_id

        # Trường hợp 3: Gọi hàm tự do được import trực tiếp
        resolved_func = self._resolve_class_by_name_from_data(call_name, pdata)
        if resolved_func and resolved_func in self.nodes:
            return resolved_func

        # Trường hợp 4: Quét toàn bộ đồ thị tìm Method trùng tên độc nhất
        matches = [
            nid
            for nid, node in self.nodes.items()
            if node["type"] == "function" and node["label"] == call_name
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1 and caller_obj:
            for match in matches:
                if caller_obj.lower() in match.lower():
                    return match

        return None

    def find_impact(self, target_node_id: str) -> list[dict[str, Any]]:
        """Tìm kiếm ngược (BFS) để tìm tất cả thực thể bị ảnh hưởng trực tiếp/gián tiếp.

        Args:
            target_node_id: ID node mục tiêu muốn truy vết tác động.

        Returns:
            Danh sách các dictionary mô tả thực thể bị ảnh hưởng và mối quan hệ.
        """
        if target_node_id not in self.nodes:
            return []

        visited: set[str] = set()
        queue: list[str] = [target_node_id]
        impact_chain: list[dict[str, Any]] = []

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            callers = self.reverse_adjacency_list.get(current, set())
            for caller in callers:
                if caller not in visited and caller not in queue:
                    queue.append(caller)
                    edge_type = "calls"
                    for edge in self.edges:
                        if edge["source"] == caller and edge["target"] == current:
                            edge_type = edge["type"]
                            break

                    impact_chain.append(
                        {
                            "node": self.nodes[caller],
                            "impact_on": self.nodes[current]["id"],
                            "relation": edge_type,
                        }
                    )

        return impact_chain
