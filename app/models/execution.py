"""Execution models."""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from app.models.state import ExecutionLog


class ExecutionStatus(str, Enum):
    """Execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionRunRequest(BaseModel):
    """Request to run a graph."""

    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class ExecutionRunResponse(BaseModel):
    """Response after running a graph."""

    run_id: str
    status: ExecutionStatus
    message: str = "Execution started"


class ExecutionResult(BaseModel):
    """Result of a workflow execution."""

    run_id: str
    graph_id: str
    status: ExecutionStatus
    initial_state: Dict[str, Any]
    final_state: Dict[str, Any]
    logs: List[ExecutionLog] = Field(default_factory=list)
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class ExecutionStateResponse(BaseModel):
    """Response for getting execution state."""

    run_id: str
    status: ExecutionStatus
    current_state: Dict[str, Any]
    logs: List[ExecutionLog]




