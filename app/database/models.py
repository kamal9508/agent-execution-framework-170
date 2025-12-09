"""Database models."""
from sqlalchemy import Column, String, JSON, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class ExecutionStatusEnum(str, enum.Enum):
    """Execution status enum for database."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GraphModel(Base):
    """Database model for graphs."""

    __tablename__ = "graphs"

    graph_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ExecutionModel(Base):
    """Database model for executions."""

    __tablename__ = "executions"

    run_id = Column(String, primary_key=True, index=True)
    graph_id = Column(String, nullable=False, index=True)
    status = Column(Enum(ExecutionStatusEnum), nullable=False)
    initial_state = Column(JSON, nullable=False)
    final_state = Column(JSON, nullable=True)
    logs = Column(JSON, nullable=False, default=[])
    error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
