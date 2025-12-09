"""Graph definition models."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from enum import Enum


class EdgeType(str, Enum):
    """Edge types in the graph."""
    DIRECT = "direct"
    CONDITIONAL = "conditional"


class NodeConfig(BaseModel):
    """Configuration for a workflow node."""

    node_id: str
    node_type: str = "tool"
    tool_name: Optional[str] = None
    config: Dict[str, Any] = {}


class EdgeConfig(BaseModel):
    """Configuration for an edge between nodes."""

    from_node: str
    to_node: str
    edge_type: EdgeType = EdgeType.DIRECT
    condition: Optional[str] = None


class LoopConfig(BaseModel):
    """Configuration for a loop in the graph."""

    loop_node: str
    condition: str
    max_iterations: int = 10


class GraphDefinition(BaseModel):
    """Complete workflow graph definition."""

    name: str
    description: Optional[str] = None
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]
    entry_node: str
    loops: List[LoopConfig] = []
    graph_id: Optional[str] = None


class GraphCreateRequest(BaseModel):
    """Request to create a graph."""

    name: str
    description: Optional[str] = None
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]
    entry_node: str
    loops: List[LoopConfig] = []


class GraphCreateResponse(BaseModel):
    """Response from graph creation."""

    graph_id: str
    message: str = "Graph created successfully"




