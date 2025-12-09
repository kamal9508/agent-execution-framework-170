"""Core workflow engine."""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from app.models.graph import GraphDefinition, EdgeType, LoopConfig
from app.models.state import WorkflowState, ExecutionLog
from app.models.execution import ExecutionStatus
from app.core.node import Node
from app.core.registry import tool_registry
from app.config import settings

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Engine for executing workflow graphs."""

    def __init__(self, graph: GraphDefinition):
        """Initialize engine with graph definition.

        Args:
            graph: Graph definition
        """
        self.graph = graph
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[str]] = {}
        self.conditional_edges: Dict[str, List[tuple[str, str]]] = {}
        self.loops: Dict[str, LoopConfig] = {}
        self._build_graph()

    def _build_graph(self) -> None:
        """Build internal graph structure."""
        for node_config in self.graph.nodes:
            tool_func = None

            if node_config.tool_name:
                tool_func = tool_registry.get(node_config.tool_name)
                if not tool_func:
                    raise ValueError(
                        f"Tool not found: {node_config.tool_name}")
            else:
                tool_func = lambda state, **kwargs: state

            node = Node(
                node_id=node_config.node_id,
                func=tool_func,
                config=node_config.config
            )
            self.nodes[node_config.node_id] = node

        for edge in self.graph.edges:
            if edge.edge_type == EdgeType.DIRECT:
                if edge.from_node not in self.edges:
                    self.edges[edge.from_node] = []
                self.edges[edge.from_node].append(edge.to_node)
            elif edge.edge_type == EdgeType.CONDITIONAL:
                if edge.from_node not in self.conditional_edges:
                    self.conditional_edges[edge.from_node] = []
                self.conditional_edges[edge.from_node].append(
                    (edge.to_node, edge.condition or "")
                )

        for loop in self.graph.loops:
            self.loops[loop.loop_node] = loop

        logger.info(
            f"Built graph with {len(self.nodes)} nodes, {len(self.edges)} edges")

    def _evaluate_condition(self, condition: str, state: WorkflowState) -> bool:
        """Evaluate a condition against current state.

        Args:
            condition: Condition expression
            state: Current state

        Returns:
            Evaluation result
        """
        try:
            scope = {"state": state.data}
            return eval(condition, {"__builtins__": {}}, scope)
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    def _get_next_nodes(self, current_node: str, state: WorkflowState) -> List[str]:
        """Determine next nodes to execute.

        Args:
            current_node: Current node ID
            state: Current state

        Returns:
            List of next node IDs
        """
        next_nodes = []

        if current_node in self.conditional_edges:
            for to_node, condition in self.conditional_edges[current_node]:
                if self._evaluate_condition(condition, state):
                    next_nodes.append(to_node)
                    break

        if not next_nodes and current_node in self.edges:
            next_nodes = self.edges[current_node]

        return next_nodes

    async def execute(
        self,
        initial_state: WorkflowState,
        max_iterations: Optional[int] = None
    ) -> tuple[WorkflowState, List[ExecutionLog]]:
        """Execute the workflow.

        Args:
            initial_state: Initial workflow state
            max_iterations: Maximum loop iterations

        Returns:
            Tuple of (final state, execution logs)
        """
        max_iter = max_iterations or settings.max_loop_iterations
        state = initial_state
        logs: List[ExecutionLog] = []
        visited_counts: Dict[str, int] = {}

        current_node_id = self.graph.entry_node
        iteration = 0

        while current_node_id and iteration < max_iter:
            iteration += 1

            visited_counts[current_node_id] = visited_counts.get(
                current_node_id, 0) + 1

            if current_node_id in self.loops:
                loop_config = self.loops[current_node_id]

                if not self._evaluate_condition(loop_config.condition, state):
                    logger.info(f"Exiting loop at node {current_node_id}")
                    break

                if visited_counts[current_node_id] > loop_config.max_iterations:
                    logger.warning(
                        f"Max loop iterations reached for {current_node_id}")
                    break

            node = self.nodes.get(current_node_id)
            if not node:
                logger.error(f"Node not found: {current_node_id}")
                break

            start_time = datetime.now(tz=timezone.utc)
            log_entry = ExecutionLog(
                node_id=current_node_id,
                timestamp=start_time,
                input_state=state.data.copy()
            )

            try:
                logger.info(f"Executing node: {current_node_id}")
                state = await node.execute(state)
                log_entry.output_state = state.data.copy()
                log_entry.status = "success"
            except Exception as e:
                logger.error(f"Node execution failed: {e}", exc_info=True)
                log_entry.status = "error"
                log_entry.error = str(e)
                logs.append(log_entry)
                raise
            finally:
                end_time = datetime.now(tz=timezone.utc)
                log_entry.duration_ms = (
                    end_time - start_time).total_seconds() * 1000

            logs.append(log_entry)

            next_nodes = self._get_next_nodes(current_node_id, state)

            if not next_nodes:
                logger.info(
                    f"Reached end of workflow at node {current_node_id}")
                break

            current_node_id = next_nodes[0]

        if iteration >= max_iter:
            logger.warning(f"Maximum iterations ({max_iter}) reached")

        return state, logs
