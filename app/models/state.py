"""State models for workflow execution."""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class WorkflowState:
    """Mutable workflow state container."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize state.

        Args:
            data: Initial state data
        """
        self.data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state.

        Args:
            key: State key
            default: Default value

        Returns:
            State value or default
        """
        return self.data.get(key, default)

    def update(self, updates: Dict[str, Any]) -> None:
        """Update state with new values.

        Args:
            updates: Dictionary of updates
        """
        self.data.update(updates)

    def __getitem__(self, key: str) -> Any:
        """Get value using bracket notation."""
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set value using bracket notation."""
        self.data[key] = value


class ExecutionLog(BaseModel):
    """Execution log entry."""

    node_id: str
    timestamp: datetime
    input_state: Dict[str, Any]
    output_state: Dict[str, Any] = {}
    status: str = "pending"
    duration_ms: float = 0.0
    error: Optional[str] = None




