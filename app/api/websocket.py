"""WebSocket endpoint for streaming execution logs."""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.state import WorkflowState
from app.core.engine import WorkflowEngine
from app.database.repository import database, GraphRepository

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/execute/{graph_id}")
async def websocket_execute(websocket: WebSocket, graph_id: str):
    """Execute workflow with real-time log streaming.

    Args:
        websocket: WebSocket connection
        graph_id: Graph ID to execute
    """
    await websocket.accept()

    try:
        data = await websocket.receive_json()
        initial_state = data.get("initial_state", {})

        await websocket.send_json({
            "type": "status",
            "message": "Starting execution..."
        })

        async with database.get_session() as session:
            graph_repo = GraphRepository(session)
            graph = await graph_repo.get(graph_id)

            if not graph:
                await websocket.send_json({
                    "type": "error",
                    "message": "Graph not found"
                })
                await websocket.close()
                return

        engine = WorkflowEngine(graph)
        state = WorkflowState(data=initial_state)

        await websocket.send_json({
            "type": "started",
            "graph_id": graph_id
        })

        current_node_id = graph.entry_node
        iteration = 0
        max_iterations = 100

        while current_node_id and iteration < max_iterations:
            iteration += 1

            node = engine.nodes.get(current_node_id)
            if not node:
                break

            await websocket.send_json({
                "type": "node_start",
                "node_id": current_node_id,
                "iteration": iteration
            })

            try:
                state = await node.execute(state)

                await websocket.send_json({
                    "type": "node_complete",
                    "node_id": current_node_id,
                    "state": state.data
                })

            except Exception as e:
                await websocket.send_json({
                    "type": "node_error",
                    "node_id": current_node_id,
                    "error": str(e)
                })
                break

            next_nodes = engine._get_next_nodes(current_node_id, state)

            if not next_nodes:
                break

            current_node_id = next_nodes[0]

        await websocket.send_json({
            "type": "completed",
            "final_state": state.data,
            "iterations": iteration
        })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
