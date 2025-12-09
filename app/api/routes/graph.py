"""Graph management routes."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.graph import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphDefinition
)
from app.database.repository import database, GraphRepository

router = APIRouter(prefix="/graphs", tags=["graphs"])


async def get_db() -> AsyncSession:
    """Get database session."""
    async with database.get_session() as session:
        yield session


@router.post("/create", response_model=GraphCreateResponse)
async def create_graph(
    request: GraphCreateRequest,
    session: AsyncSession = Depends(get_db)
):
    """Create a new workflow graph.

    Args:
        request: Graph creation request
        session: Database session

    Returns:
        Graph creation response
    """
    try:
        graph = GraphDefinition(
            name=request.name,
            description=request.description,
            nodes=request.nodes,
            edges=request.edges,
            loops=request.loops,
            entry_node=request.entry_node
        )

        repo = GraphRepository(session)
        graph_id = await repo.create(graph)

        return GraphCreateResponse(
            graph_id=graph_id,
            message="Graph created successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{graph_id}", response_model=GraphDefinition)
async def get_graph(
    graph_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get a graph by ID.

    Args:
        graph_id: Graph ID
        session: Database session

    Returns:
        Graph definition
    """
    repo = GraphRepository(session)
    graph = await repo.get(graph_id)

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    return graph


@router.get("/", response_model=list[GraphDefinition])
async def list_graphs(
    limit: int = 100,
    session: AsyncSession = Depends(get_db)
):
    """List all graphs.

    Args:
        limit: Maximum number of results
        session: Database session

    Returns:
        List of graphs
    """
    repo = GraphRepository(session)
    return await repo.list(limit=limit)


@router.delete("/{graph_id}")
async def delete_graph(
    graph_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Delete a graph.

    Args:
        graph_id: Graph ID
        session: Database session

    Returns:
        Deletion confirmation
    """
    repo = GraphRepository(session)
    deleted = await repo.delete(graph_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Graph not found")

    return {"message": "Graph deleted successfully"}
