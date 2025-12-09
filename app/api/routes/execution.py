"""Execution routes."""
import asyncio
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution import (
    ExecutionRunRequest,
    ExecutionRunResponse,
    ExecutionResult,
    ExecutionStatus,
    ExecutionStateResponse
)
from app.models.state import WorkflowState
from app.core.engine import WorkflowEngine
from app.database.repository import database, GraphRepository, ExecutionRepository

router = APIRouter(prefix="/executions", tags=["execution"])
logger = logging.getLogger(__name__)


async def get_db() -> AsyncSession:
    """Get database session."""
    async with database.get_session() as session:
        yield session


async def execute_workflow_background(
    run_id: str,
    graph_id: str,
    initial_state: dict
):
    """Execute workflow in background.

    Args:
        run_id: Run ID
        graph_id: Graph ID
        initial_state: Initial state
    """
    async with database.get_session() as session:
        graph_repo = GraphRepository(session)
        exec_repo = ExecutionRepository(session)

        try:
            await exec_repo.update_status(run_id, ExecutionStatus.RUNNING)

            graph = await graph_repo.get(graph_id)
            if not graph:
                raise ValueError("Graph not found")

            engine = WorkflowEngine(graph)
            state = WorkflowState(data=initial_state)

            final_state, logs = await engine.execute(state)

            await exec_repo.update_status(
                run_id,
                ExecutionStatus.COMPLETED,
                final_state=final_state.data,
                logs=logs
            )

            logger.info(f"Execution {run_id} completed successfully")

        except Exception as e:
            logger.error(f"Execution {run_id} failed: {e}", exc_info=True)
            await exec_repo.update_status(
                run_id,
                ExecutionStatus.FAILED,
                error=str(e)
            )


@router.post("/run", response_model=ExecutionRunResponse)
async def run_graph(
    request: ExecutionRunRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """Run a workflow graph.

    Args:
        request: Execution request
        background_tasks: Background task manager
        session: Database session

    Returns:
        Execution response
    """
    try:
        graph_repo = GraphRepository(session)
        graph = await graph_repo.get(request.graph_id)

        if not graph:
            raise HTTPException(status_code=404, detail="Graph not found")

        exec_repo = ExecutionRepository(session)
        run_id = await exec_repo.create(
            graph_id=request.graph_id,
            initial_state=request.initial_state
        )

        background_tasks.add_task(
            execute_workflow_background,
            run_id,
            request.graph_id,
            request.initial_state
        )

        return ExecutionRunResponse(
            run_id=run_id,
            status=ExecutionStatus.PENDING,
            message="Execution started"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/state/{run_id}", response_model=ExecutionStateResponse)
async def get_execution_state(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get current execution state.

    Args:
        run_id: Run ID
        session: Database session

    Returns:
        Execution state
    """
    exec_repo = ExecutionRepository(session)
    result = await exec_repo.get(run_id)

    if not result:
        raise HTTPException(status_code=404, detail="Execution not found")

    return ExecutionStateResponse(
        run_id=result.run_id,
        status=result.status,
        current_state=result.final_state or result.initial_state,
        logs=result.logs
    )


@router.get("/result/{run_id}", response_model=ExecutionResult)
async def get_execution_result(
    run_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get execution result.

    Args:
        run_id: Run ID
        session: Database session

    Returns:
        Execution result
    """
    exec_repo = ExecutionRepository(session)
    result = await exec_repo.get(run_id)

    if not result:
        raise HTTPException(status_code=404, detail="Execution not found")

    return result
