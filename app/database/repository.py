"""Database repository for persistence."""
import uuid
import json
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.database.models import Base, GraphModel, ExecutionModel, ExecutionStatusEnum
from app.models.graph import GraphDefinition
from app.models.execution import ExecutionResult, ExecutionStatus
from app.models.state import ExecutionLog
from app.config import settings


class Database:
    """Database connection manager."""

    def __init__(self):
        """Initialize database."""
        self.engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_pre_ping=True
        )
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self):
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    def get_session(self) -> AsyncSession:
        """Get database session."""
        return self.SessionLocal()


database = Database()


class GraphRepository:
    """Repository for graph operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: Database session
        """
        self.session = session

    async def create(self, graph: GraphDefinition) -> str:
        """Create a new graph.

        Args:
            graph: Graph definition

        Returns:
            Graph ID
        """
        graph_id = graph.graph_id or str(uuid.uuid4())

        db_graph = GraphModel(
            graph_id=graph_id,
            name=graph.name,
            description=graph.description,
            definition=json.loads(graph.model_dump_json())
        )

        self.session.add(db_graph)
        await self.session.commit()

        return graph_id

    async def get(self, graph_id: str) -> Optional[GraphDefinition]:
        """Get graph by ID.

        Args:
            graph_id: Graph ID

        Returns:
            Graph definition or None
        """
        result = await self.session.execute(
            select(GraphModel).where(GraphModel.graph_id == graph_id)
        )
        db_graph = result.scalar_one_or_none()

        if not db_graph:
            return None

        return GraphDefinition.model_validate(db_graph.definition)

    async def list(self, limit: int = 100) -> List[GraphDefinition]:
        """List all graphs.

        Args:
            limit: Maximum number of results

        Returns:
            List of graph definitions
        """
        result = await self.session.execute(
            select(GraphModel).limit(limit)
        )
        db_graphs = result.scalars().all()

        return [GraphDefinition.model_validate(g.definition) for g in db_graphs]

    async def delete(self, graph_id: str) -> bool:
        """Delete a graph.

        Args:
            graph_id: Graph ID

        Returns:
            True if deleted
        """
        result = await self.session.execute(
            select(GraphModel).where(GraphModel.graph_id == graph_id)
        )
        db_graph = result.scalar_one_or_none()

        if db_graph:
            await self.session.delete(db_graph)
            await self.session.commit()
            return True

        return False


class ExecutionRepository:
    """Repository for execution operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.

        Args:
            session: Database session
        """
        self.session = session

    async def create(
        self,
        graph_id: str,
        initial_state: dict
    ) -> str:
        """Create a new execution.

        Args:
            graph_id: Graph ID
            initial_state: Initial state

        Returns:
            Run ID
        """
        run_id = str(uuid.uuid4())

        db_execution = ExecutionModel(
            run_id=run_id,
            graph_id=graph_id,
            status=ExecutionStatusEnum.PENDING,
            initial_state=initial_state,
            logs=[]
        )

        self.session.add(db_execution)
        await self.session.commit()

        return run_id

    async def update_status(
        self,
        run_id: str,
        status: ExecutionStatus,
        final_state: Optional[dict] = None,
        logs: Optional[List[ExecutionLog]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Update execution status.

        Args:
            run_id: Run ID
            status: New status
            final_state: Final state
            logs: Execution logs
            error: Error message

        Returns:
            True if updated
        """
        result = await self.session.execute(
            select(ExecutionModel).where(ExecutionModel.run_id == run_id)
        )
        db_execution = result.scalar_one_or_none()

        if not db_execution:
            return False

        db_execution.status = ExecutionStatusEnum(status.value)

        if final_state is not None:
            db_execution.final_state = final_state

        if logs is not None:
            db_execution.logs = [json.loads(
                log.model_dump_json()) for log in logs]

        if error is not None:
            db_execution.error = error

        if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            db_execution.completed_at = datetime.utcnow()

        await self.session.commit()
        return True

    async def get(self, run_id: str) -> Optional[ExecutionResult]:
        """Get execution by ID.

        Args:
            run_id: Run ID

        Returns:
            Execution result or None
        """
        result = await self.session.execute(
            select(ExecutionModel).where(ExecutionModel.run_id == run_id)
        )
        db_execution = result.scalar_one_or_none()

        if not db_execution:
            return None

        logs = [ExecutionLog.model_validate(log) for log in db_execution.logs]

        return ExecutionResult(
            run_id=db_execution.run_id,
            graph_id=db_execution.graph_id,
            status=ExecutionStatus(db_execution.status.value),
            initial_state=db_execution.initial_state,
            final_state=db_execution.final_state or {},
            logs=logs,
            started_at=db_execution.started_at,
            completed_at=db_execution.completed_at,
            error=db_execution.error
        )
