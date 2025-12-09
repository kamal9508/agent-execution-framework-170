"""Node abstraction for workflow."""
from typing import Callable, Any, Dict, Optional
import asyncio
from app.models.state import WorkflowState


class Node:
    """Represents a single node in the workflow."""

    def __init__(
        self,
        node_id: str,
        func: Callable,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize node.

        Args:
            node_id: Unique identifier
            func: Function to execute
            config: Additional configuration
        """
        self.node_id = node_id
        self.func = func
        self.config = config or {}

    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute node function with current state.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        if asyncio.iscoroutinefunction(self.func):
            result = await self.func(state, **self.config)
        else:
            result = self.func(state, **self.config)

        if isinstance(result, dict):
            state.update(result)
        elif isinstance(result, WorkflowState):
            state = result

        return state

    def __repr__(self) -> str:
        return f"Node(id={self.node_id}, func={self.func.__name__})"
