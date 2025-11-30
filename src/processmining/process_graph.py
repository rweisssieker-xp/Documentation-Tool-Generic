"""
Process Graph - Graph representation of process models.
Part of Feature 2: Process Mining Engine
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessNode:
    """A node in the process graph."""
    id: str
    label: str
    node_type: str  # "start", "end", "activity", "gateway"
    frequency: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessEdge:
    """An edge in the process graph."""
    id: str
    source: str
    target: str
    frequency: int = 0
    probability: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)


class ProcessGraph:
    """
    Graph representation of a process model.
    Supports various graph operations and visualizations.
    """
    
    def __init__(self, name: str = "Process Graph"):
        """
        Initialize process graph.
        
        Args:
            name: Graph name
        """
        self.name = name
        self.nodes: Dict[str, ProcessNode] = {}
        self.edges: Dict[str, ProcessEdge] = {}
        self._adjacency: Dict[str, List[str]] = defaultdict(list)
        self._reverse_adjacency: Dict[str, List[str]] = defaultdict(list)
        
        logger.info(f"ProcessGraph initialized: {name}")
    
    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str = "activity",
        frequency: int = 0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> ProcessNode:
        """
        Add a node to the graph.
        
        Args:
            node_id: Node identifier
            label: Node label
            node_type: Type of node
            frequency: Node frequency
            attributes: Additional attributes
            
        Returns:
            Created ProcessNode
        """
        node = ProcessNode(
            id=node_id,
            label=label,
            node_type=node_type,
            frequency=frequency,
            attributes=attributes or {}
        )
        self.nodes[node_id] = node
        return node
    
    def add_edge(
        self,
        source: str,
        target: str,
        frequency: int = 0,
        probability: float = 0.0,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Optional[ProcessEdge]:
        """
        Add an edge to the graph.
        
        Args:
            source: Source node ID
            target: Target node ID
            frequency: Edge frequency
            probability: Transition probability
            attributes: Additional attributes
            
        Returns:
            Created ProcessEdge or None if nodes don't exist
        """
        if source not in self.nodes or target not in self.nodes:
            logger.warning(f"Cannot add edge: nodes not found ({source} -> {target})")
            return None
        
        edge_id = f"{source}_{target}"
        edge = ProcessEdge(
            id=edge_id,
            source=source,
            target=target,
            frequency=frequency,
            probability=probability,
            attributes=attributes or {}
        )
        
        self.edges[edge_id] = edge
        self._adjacency[source].append(target)
        self._reverse_adjacency[target].append(source)
        
        return edge
    
    def get_successors(self, node_id: str) -> List[str]:
        """Get successor nodes."""
        return self._adjacency.get(node_id, [])
    
    def get_predecessors(self, node_id: str) -> List[str]:
        """Get predecessor nodes."""
        return self._reverse_adjacency.get(node_id, [])
    
    def get_start_nodes(self) -> List[str]:
        """Get nodes with no predecessors."""
        return [
            nid for nid in self.nodes
            if not self._reverse_adjacency.get(nid)
            or self.nodes[nid].node_type == "start"
        ]
    
    def get_end_nodes(self) -> List[str]:
        """Get nodes with no successors."""
        return [
            nid for nid in self.nodes
            if not self._adjacency.get(nid)
            or self.nodes[nid].node_type == "end"
        ]
    
    def find_paths(
        self,
        start: str,
        end: str,
        max_paths: int = 100
    ) -> List[List[str]]:
        """
        Find all paths between two nodes.
        
        Args:
            start: Start node ID
            end: End node ID
            max_paths: Maximum paths to find
            
        Returns:
            List of paths (each path is a list of node IDs)
        """
        paths = []
        
        def dfs(current: str, path: List[str], visited: Set[str]):
            if len(paths) >= max_paths:
                return
            
            if current == end:
                paths.append(path[:])
                return
            
            for next_node in self._adjacency.get(current, []):
                if next_node not in visited:
                    visited.add(next_node)
                    path.append(next_node)
                    dfs(next_node, path, visited)
                    path.pop()
                    visited.remove(next_node)
        
        if start in self.nodes:
            dfs(start, [start], {start})
        
        return paths
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate graph metrics."""
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "density": self._calculate_density(),
            "avg_degree": self._calculate_avg_degree(),
            "start_nodes": len(self.get_start_nodes()),
            "end_nodes": len(self.get_end_nodes()),
            "is_connected": self._is_connected()
        }
    
    def to_dot(self) -> str:
        """Export to DOT format for Graphviz."""
        lines = [f'digraph "{self.name}" {{']
        lines.append('    rankdir=LR;')
        lines.append('    node [shape=box];')
        
        # Add nodes
        for nid, node in self.nodes.items():
            shape = {
                "start": "circle",
                "end": "doublecircle",
                "gateway": "diamond",
                "activity": "box"
            }.get(node.node_type, "box")
            
            lines.append(f'    "{nid}" [label="{node.label}", shape={shape}];')
        
        # Add edges
        for edge in self.edges.values():
            label = f"{edge.frequency}" if edge.frequency else ""
            lines.append(f'    "{edge.source}" -> "{edge.target}" [label="{label}"];')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def to_mermaid(self) -> str:
        """Export to Mermaid diagram format."""
        lines = ["graph LR"]
        
        # Add nodes
        for nid, node in self.nodes.items():
            safe_id = nid.replace(" ", "_").replace("-", "_")
            
            if node.node_type == "start":
                lines.append(f"    {safe_id}(({node.label}))")
            elif node.node_type == "end":
                lines.append(f"    {safe_id}(({node.label}))")
            elif node.node_type == "gateway":
                lines.append(f"    {safe_id}{{{node.label}}}")
            else:
                lines.append(f"    {safe_id}[{node.label}]")
        
        # Add edges
        for edge in self.edges.values():
            source = edge.source.replace(" ", "_").replace("-", "_")
            target = edge.target.replace(" ", "_").replace("-", "_")
            
            if edge.frequency > 0:
                lines.append(f"    {source} -->|{edge.frequency}| {target}")
            else:
                lines.append(f"    {source} --> {target}")
        
        return "\n".join(lines)
    
    @classmethod
    def from_process_model(cls, model: Any) -> 'ProcessGraph':
        """
        Create graph from ProcessModel.
        
        Args:
            model: ProcessModel object
            
        Returns:
            ProcessGraph instance
        """
        graph = cls(name=model.name)
        
        # Add start node
        graph.add_node("_start", "Start", "start")
        
        # Add activity nodes
        for activity in model.activities:
            graph.add_node(
                activity,
                activity,
                "activity",
                model.frequency.get(activity, 0)
            )
        
        # Add end node
        graph.add_node("_end", "End", "end")
        
        # Add edges from start
        for start_act in model.start_activities:
            graph.add_edge("_start", start_act)
        
        # Add transition edges
        for from_act, to_acts in model.transitions.items():
            total = sum(1 for _ in to_acts)
            for to_act in to_acts:
                graph.add_edge(
                    from_act,
                    to_act,
                    probability=1.0 / total if total > 0 else 0
                )
        
        # Add edges to end
        for end_act in model.end_activities:
            graph.add_edge(end_act, "_end")
        
        return graph
    
    def _calculate_density(self) -> float:
        """Calculate graph density."""
        n = len(self.nodes)
        if n <= 1:
            return 0.0
        max_edges = n * (n - 1)
        return len(self.edges) / max_edges
    
    def _calculate_avg_degree(self) -> float:
        """Calculate average node degree."""
        if not self.nodes:
            return 0.0
        
        total_degree = sum(
            len(self._adjacency.get(nid, [])) + len(self._reverse_adjacency.get(nid, []))
            for nid in self.nodes
        )
        
        return total_degree / len(self.nodes)
    
    def _is_connected(self) -> bool:
        """Check if graph is weakly connected."""
        if not self.nodes:
            return True
        
        visited = set()
        start = next(iter(self.nodes))
        
        def dfs(node):
            visited.add(node)
            for neighbor in self._adjacency.get(node, []) + self._reverse_adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(start)
        return len(visited) == len(self.nodes)

