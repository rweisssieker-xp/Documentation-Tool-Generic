"""
Context Cloud - Creates visual context representation.
Part of Feature 1: Smart Context Capture
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ContextNode:
    """A node in the context cloud."""
    id: str
    node_type: str  # "window", "action", "data", "app", "file"
    label: str
    weight: float  # Importance 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)
    connections: List[str] = field(default_factory=list)


@dataclass
class ContextCloud:
    """
    A visual representation of context around a documentation step.
    Connects windows, actions, data, and applications.
    """
    
    step_id: str
    timestamp: datetime
    nodes: Dict[str, ContextNode] = field(default_factory=dict)
    center_node_id: Optional[str] = None
    
    def add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        weight: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextNode:
        """
        Add a node to the context cloud.
        
        Args:
            node_id: Unique node identifier
            node_type: Type of node
            label: Display label
            weight: Importance weight
            metadata: Additional data
            
        Returns:
            Created ContextNode
        """
        node = ContextNode(
            id=node_id,
            node_type=node_type,
            label=label,
            weight=weight,
            metadata=metadata or {}
        )
        self.nodes[node_id] = node
        return node
    
    def connect(self, node1_id: str, node2_id: str) -> bool:
        """
        Connect two nodes.
        
        Args:
            node1_id: First node ID
            node2_id: Second node ID
            
        Returns:
            True if connected successfully
        """
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return False
        
        if node2_id not in self.nodes[node1_id].connections:
            self.nodes[node1_id].connections.append(node2_id)
        
        if node1_id not in self.nodes[node2_id].connections:
            self.nodes[node2_id].connections.append(node1_id)
        
        return True
    
    def set_center(self, node_id: str) -> None:
        """Set the center node of the cloud."""
        if node_id in self.nodes:
            self.center_node_id = node_id
    
    def get_connected_nodes(self, node_id: str) -> List[ContextNode]:
        """Get all nodes connected to a specific node."""
        if node_id not in self.nodes:
            return []
        
        return [
            self.nodes[conn_id]
            for conn_id in self.nodes[node_id].connections
            if conn_id in self.nodes
        ]
    
    def get_nodes_by_type(self, node_type: str) -> List[ContextNode]:
        """Get all nodes of a specific type."""
        return [n for n in self.nodes.values() if n.node_type == node_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "step_id": self.step_id,
            "timestamp": self.timestamp.isoformat(),
            "center_node": self.center_node_id,
            "nodes": {
                nid: {
                    "id": n.id,
                    "type": n.node_type,
                    "label": n.label,
                    "weight": n.weight,
                    "metadata": n.metadata,
                    "connections": n.connections
                }
                for nid, n in self.nodes.items()
            }
        }
    
    def to_mermaid(self) -> str:
        """Generate Mermaid diagram representation."""
        lines = ["graph LR"]
        
        # Add nodes with styling
        type_styles = {
            "window": "([{}])",
            "action": "[/{}\\]",
            "data": "[({})]",
            "app": "{{{}}}",
            "file": ">{}]"
        }
        
        for nid, node in self.nodes.items():
            style = type_styles.get(node.node_type, "[{}]")
            label = node.label.replace('"', "'")[:30]
            safe_id = nid.replace("-", "_").replace(" ", "_")
            lines.append(f"    {safe_id}{style.format(label)}")
        
        # Add connections
        added = set()
        for nid, node in self.nodes.items():
            safe_id = nid.replace("-", "_").replace(" ", "_")
            for conn in node.connections:
                safe_conn = conn.replace("-", "_").replace(" ", "_")
                edge = tuple(sorted([safe_id, safe_conn]))
                if edge not in added:
                    lines.append(f"    {safe_id} --- {safe_conn}")
                    added.add(edge)
        
        # Style center node
        if self.center_node_id:
            safe_center = self.center_node_id.replace("-", "_").replace(" ", "_")
            lines.append(f"    style {safe_center} fill:#f9f,stroke:#333,stroke-width:4px")
        
        return "\n".join(lines)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class ContextCloudBuilder:
    """
    Builds context clouds from collected context data.
    """
    
    def __init__(self):
        """Initialize context cloud builder."""
        logger.info("ContextCloudBuilder initialized")
    
    def build_from_context(
        self,
        step_id: str,
        context_data: Dict[str, Any]
    ) -> ContextCloud:
        """
        Build a context cloud from context data.
        
        Args:
            step_id: Step identifier
            context_data: Context data dictionary
            
        Returns:
            ContextCloud object
        """
        cloud = ContextCloud(
            step_id=step_id,
            timestamp=datetime.now()
        )
        
        # Add window node (center)
        window = context_data.get("window", {})
        if window:
            window_id = f"window_{step_id}"
            cloud.add_node(
                node_id=window_id,
                node_type="window",
                label=window.get("title", "Unknown Window")[:50],
                weight=1.0,
                metadata={"process": window.get("process")}
            )
            cloud.set_center(window_id)
            
            # Add app node
            if window.get("process"):
                app_id = f"app_{window.get('process')}"
                cloud.add_node(
                    node_id=app_id,
                    node_type="app",
                    label=window.get("process"),
                    weight=0.8
                )
                cloud.connect(window_id, app_id)
        
        # Add action nodes from history
        history = context_data.get("history", [])
        prev_action_id = None
        
        for i, action in enumerate(history[-5:]):  # Last 5 actions
            action_id = f"action_{step_id}_{i}"
            cloud.add_node(
                node_id=action_id,
                node_type="action",
                label=action[:30],
                weight=0.5 + (i * 0.1)
            )
            
            if prev_action_id:
                cloud.connect(prev_action_id, action_id)
            if i == len(history[-5:]) - 1 and cloud.center_node_id:
                cloud.connect(action_id, cloud.center_node_id)
            
            prev_action_id = action_id
        
        # Add clipboard node
        clipboard = context_data.get("clipboard")
        if clipboard:
            clip_id = f"clipboard_{step_id}"
            cloud.add_node(
                node_id=clip_id,
                node_type="data",
                label=f"Clipboard: {clipboard[:20]}...",
                weight=0.6,
                metadata={"content": clipboard[:200]}
            )
            if cloud.center_node_id:
                cloud.connect(clip_id, cloud.center_node_id)
        
        # Add tab nodes
        tabs = context_data.get("tabs", [])
        for i, tab in enumerate(tabs[:5]):  # Max 5 tabs
            tab_id = f"tab_{step_id}_{i}"
            cloud.add_node(
                node_id=tab_id,
                node_type="window",
                label=tab.get("title", "Tab")[:30],
                weight=0.4,
                metadata={"browser": tab.get("browser")}
            )
        
        logger.debug(f"Built context cloud with {len(cloud.nodes)} nodes")
        return cloud
    
    def merge_clouds(
        self,
        clouds: List[ContextCloud]
    ) -> ContextCloud:
        """
        Merge multiple context clouds into one.
        
        Args:
            clouds: List of context clouds
            
        Returns:
            Merged ContextCloud
        """
        if not clouds:
            return ContextCloud(step_id="merged", timestamp=datetime.now())
        
        merged = ContextCloud(
            step_id="merged",
            timestamp=datetime.now()
        )
        
        # Add all nodes with unique prefixes
        for i, cloud in enumerate(clouds):
            for nid, node in cloud.nodes.items():
                new_id = f"c{i}_{nid}"
                merged.add_node(
                    node_id=new_id,
                    node_type=node.node_type,
                    label=node.label,
                    weight=node.weight,
                    metadata=node.metadata
                )
                
                # Update connections with new IDs
                for conn in node.connections:
                    new_conn = f"c{i}_{conn}"
                    if new_conn in merged.nodes:
                        merged.connect(new_id, new_conn)
        
        # Connect clouds sequentially
        for i in range(len(clouds) - 1):
            if clouds[i].center_node_id and clouds[i+1].center_node_id:
                merged.connect(
                    f"c{i}_{clouds[i].center_node_id}",
                    f"c{i+1}_{clouds[i+1].center_node_id}"
                )
        
        return merged

