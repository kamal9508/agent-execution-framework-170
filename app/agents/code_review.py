"""Code review agent workflow."""
from app.models.graph import (
    GraphDefinition,
    NodeConfig,
    EdgeConfig,
    EdgeType,
    LoopConfig
)
from app.core.registry import tool_registry
from app.tools.code_analyzer import (
    extract_functions,
    check_complexity,
    detect_issues,
    suggest_improvements
)


def register_code_review_tools():
    """Register all code review tools."""
    tool_registry.register("extract_functions", extract_functions)
    tool_registry.register("check_complexity", check_complexity)
    tool_registry.register("detect_issues", detect_issues)
    tool_registry.register("suggest_improvements", suggest_improvements)


def create_code_review_graph(
    complexity_threshold: int = 10,
    quality_threshold: float = 70.0,
    max_iterations: int = 5
) -> GraphDefinition:
    """Create a code review workflow graph.

    Args:
        complexity_threshold: Maximum acceptable complexity
        quality_threshold: Minimum quality score
        max_iterations: Maximum refinement iterations

    Returns:
        Graph definition for code review
    """
    nodes = [
        NodeConfig(
            node_id="extract",
            node_type="tool",
            tool_name="extract_functions",
            config={}
        ),
        NodeConfig(
            node_id="complexity",
            node_type="tool",
            tool_name="check_complexity",
            config={"threshold": complexity_threshold}
        ),
        NodeConfig(
            node_id="detect",
            node_type="tool",
            tool_name="detect_issues",
            config={}
        ),
        NodeConfig(
            node_id="suggest",
            node_type="tool",
            tool_name="suggest_improvements",
            config={}
        ),
    ]

    edges = [
        EdgeConfig(
            from_node="extract",
            to_node="complexity",
            edge_type=EdgeType.DIRECT
        ),
        EdgeConfig(
            from_node="complexity",
            to_node="detect",
            edge_type=EdgeType.DIRECT
        ),
        EdgeConfig(
            from_node="detect",
            to_node="suggest",
            edge_type=EdgeType.DIRECT
        ),
        EdgeConfig(
            from_node="suggest",
            to_node="extract",
            edge_type=EdgeType.CONDITIONAL,
            condition=f"state.get('quality_score', 0) < {quality_threshold}"
        ),
    ]

    loops = [
        LoopConfig(
            loop_node="extract",
            condition=f"state.get('quality_score', 0) < {quality_threshold}",
            max_iterations=max_iterations
        )
    ]

    return GraphDefinition(
        name="Code Review Agent",
        description="Automated code review workflow with iterative refinement",
        nodes=nodes,
        edges=edges,
        loops=loops,
        entry_node="extract"
    )




