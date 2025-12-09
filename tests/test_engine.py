"""Tests for workflow engine."""
import pytest
from app.models.graph import GraphDefinition, NodeConfig, EdgeConfig, EdgeType
from app.models.state import WorkflowState
from app.core.engine import WorkflowEngine
from app.core.registry import tool_registry


def add_one(state: WorkflowState, **kwargs):
    """Test tool that adds 1 to counter."""
    counter = state.get("counter", 0)
    return {"counter": counter + 1}


def multiply_by_two(state: WorkflowState, **kwargs):
    """Test tool that multiplies counter by 2."""
    counter = state.get("counter", 0)
    return {"counter": counter * 2}


@pytest.fixture
def setup_tools():
    """Setup test tools."""
    tool_registry.register("add_one", add_one)
    tool_registry.register("multiply_by_two", multiply_by_two)
    yield
    tool_registry.clear()


@pytest.mark.asyncio
async def test_simple_workflow(setup_tools):
    """Test simple linear workflow."""
    graph = GraphDefinition(
        name="Simple Test",
        nodes=[
            NodeConfig(node_id="add", node_type="tool", tool_name="add_one"),
            NodeConfig(node_id="multiply", node_type="tool", tool_name="multiply_by_two"),
        ],
        edges=[
            EdgeConfig(from_node="add", to_node="multiply"),
        ],
        entry_node="add"
    )

    engine = WorkflowEngine(graph)
    initial_state = WorkflowState(data={"counter": 5})

    final_state, logs = await engine.execute(initial_state)

    assert final_state.get("counter") == 12
    assert len(logs) == 2


@pytest.mark.asyncio
async def test_conditional_workflow(setup_tools):
    """Test workflow with conditional branching."""
    def check_value(state: WorkflowState, **kwargs):
        return state

    tool_registry.register("check", check_value)

    graph = GraphDefinition(
        name="Conditional Test",
        nodes=[
            NodeConfig(node_id="add", node_type="tool", tool_name="add_one"),
            NodeConfig(node_id="check", node_type="tool", tool_name="check"),
            NodeConfig(node_id="multiply", node_type="tool", tool_name="multiply_by_two"),
        ],
        edges=[
            EdgeConfig(from_node="add", to_node="check"),
            EdgeConfig(
                from_node="check",
                to_node="multiply",
                edge_type=EdgeType.CONDITIONAL,
                condition="state.get('counter', 0) > 5"
            ),
        ],
        entry_node="add"
    )

    engine = WorkflowEngine(graph)
    initial_state = WorkflowState(data={"counter": 5})

    final_state, logs = await engine.execute(initial_state)

    assert final_state.get("counter") == 12




