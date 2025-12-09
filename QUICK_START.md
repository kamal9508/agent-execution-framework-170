# Agent Execution Framework - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Start the Server
```bash
cd agent-execution-framework-170
python run.py
```

Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Database tables created
INFO:     Code review tools registered
```

### 2. Check It's Working
Open your browser: **http://localhost:8000/docs**

You'll see the interactive API documentation (Swagger UI)

### 3. Test the API
```bash
python test_api.py
```

Output:
```
✓ Health Check: 200
✓ Root Endpoint: 200
✓ Create Graph: 200
✓ API is working correctly!
```

---

## 📚 Common Examples

### Example 1: Simple Sequential Workflow

**Goal:** Extract text → Translate → Store

**1. Define the graph:**
```bash
curl -X POST "http://localhost:8000/graphs/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Translation Pipeline",
    "description": "Extract text and translate it",
    "nodes": [
      {
        "node_id": "extract",
        "name": "Extract Text",
        "type": "process",
        "tool": "extract_text"
      },
      {
        "node_id": "translate",
        "name": "Translate",
        "type": "process",
        "tool": "translate_text"
      },
      {
        "node_id": "store",
        "name": "Store Result",
        "type": "end",
        "tool": null
      }
    ],
    "edges": [
      {"from_node": "extract", "to_node": "translate", "type": "normal"},
      {"from_node": "translate", "to_node": "store", "type": "normal"}
    ],
    "entry_node": "extract"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Translation Pipeline",
  ...
}
```

**2. Execute it:**
```bash
GRAPH_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST "http://localhost:8000/executions/run" \
  -H "Content-Type: application/json" \
  -d "{
    \"graph_id\": \"$GRAPH_ID\",
    \"initial_state\": {
      \"text\": \"Hello World\",
      \"source_lang\": \"en\",
      \"target_lang\": \"es\"
    }
  }"
```

Response:
```json
{
  "run_id": "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6"
}
```

**3. Get results:**
```bash
RUN_ID="a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6"

curl "http://localhost:8000/executions/result/$RUN_ID"
```

Response:
```json
{
  "run_id": "a1b2c3d4...",
  "status": "completed",
  "result": {
    "state": {
      "text": "Hello World",
      "extracted_text": "Hello World",
      "translated_text": "Hola Mundo",
      "source_lang": "en",
      "target_lang": "es"
    },
    "logs": [
      {
        "timestamp": "2025-12-10T12:00:00",
        "node_id": "extract",
        "status": "completed",
        "duration_ms": 50
      },
      {
        "timestamp": "2025-12-10T12:00:00.100",
        "node_id": "translate",
        "status": "completed",
        "duration_ms": 150
      }
    ]
  }
}
```

---

### Example 2: Conditional Workflow (If/Else)

**Goal:** Check complexity → If high, optimize; else accept

**Define the graph:**
```python
import httpx
import asyncio

async def create_conditional_workflow():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/graphs/create",
            json={
                "name": "Code Quality Check",
                "nodes": [
                    {
                        "node_id": "analyze",
                        "name": "Analyze Code",
                        "type": "process",
                        "tool": "analyze_code"
                    },
                    {
                        "node_id": "optimize",
                        "name": "Optimize (High Complexity)",
                        "type": "process",
                        "tool": "optimize_code"
                    },
                    {
                        "node_id": "accept",
                        "name": "Accept (Low Complexity)",
                        "type": "end",
                        "tool": null
                    }
                ],
                "edges": [
                    # ← This is the conditional edge!
                    {
                        "from_node": "analyze",
                        "to_node": "optimize",
                        "type": "conditional",
                        "condition": "complexity > 10"
                    },
                    # Default path (no condition = always taken)
                    {
                        "from_node": "analyze",
                        "to_node": "accept",
                        "type": "normal"
                    }
                ],
                "entry_node": "analyze"
            }
        )
        
        graph = response.json()
        graph_id = graph["id"]
        
        # Execute with low complexity code
        exec_response = await client.post(
            "http://localhost:8000/executions/run",
            json={
                "graph_id": graph_id,
                "initial_state": {
                    "code": "def add(a, b):\n    return a + b",
                    "complexity": 2  # ← Low, so goes to "accept"
                }
            }
        )
        
        run_id = exec_response.json()["run_id"]
        
        # Check result
        result_response = await client.get(
            f"http://localhost:8000/executions/result/{run_id}"
        )
        
        result = result_response.json()
        print(f"Execution path: analyze → accept (complexity is low)")
        print(f"Final state: {result['result']['state']}")

asyncio.run(create_conditional_workflow())
```

**Output:**
```
Execution path: analyze → accept (complexity is low)
Final state: {
  'code': '...',
  'complexity': 2,
  'analysis': {...},
  'status': 'accepted'
}
```

**Try with high complexity:**
```python
# Change to: "complexity": 15
# Now it takes the path: analyze → optimize → (end)
```

---

### Example 3: Real-time Streaming with WebSocket

**Goal:** Watch execution progress in real-time

**Python client:**
```python
import asyncio
import websockets
import json

async def watch_execution():
    graph_id = "your-graph-id"
    
    # Connect to WebSocket
    async with websockets.connect(
        f"ws://localhost:8000/ws/execute/{graph_id}"
    ) as websocket:
        # Receive events as they happen
        async for message in websocket:
            event = json.loads(message)
            
            if event["type"] == "node_start":
                print(f"▶ Starting node: {event['node_id']}")
            
            elif event["type"] == "node_complete":
                print(f"✓ Completed node: {event['node_id']}")
                print(f"  Output: {event['output']}")
            
            elif event["type"] == "node_error":
                print(f"✗ Error in node: {event['node_id']}")
                print(f"  Error: {event['error']}")
            
            elif event["type"] == "execution_complete":
                print(f"✓ Execution finished!")
                print(f"  Total time: {event['duration_ms']}ms")
                break

asyncio.run(watch_execution())
```

**Output (live as it executes):**
```
▶ Starting node: extract
✓ Completed node: extract
  Output: {'functions': [...]}

▶ Starting node: analyze
✓ Completed node: analyze
  Output: {'complexity': {...}}

▶ Starting node: detect
✓ Completed node: detect
  Output: {'issues': [...]}

✓ Execution finished!
  Total time: 342ms
```

---

### Example 4: Add Your Own Custom Tool

**Step 1: Define your tool function**
```python
# In app/tools/custom_tools.py

async def my_sentiment_analyzer(state):
    """Analyze sentiment of text in state"""
    text = state.get("text", "")
    
    # Your analysis logic
    if "good" in text.lower() or "great" in text.lower():
        sentiment = "positive"
        score = 0.9
    elif "bad" in text.lower() or "terrible" in text.lower():
        sentiment = "negative"
        score = 0.1
    else:
        sentiment = "neutral"
        score = 0.5
    
    return {
        "sentiment": sentiment,
        "sentiment_score": score,
        "analyzed_at": datetime.now().isoformat()
    }
```

**Step 2: Register it**
```python
# In app/agents/code_review.py or app/main.py

from app.core.registry import tool_registry
from app.tools.custom_tools import my_sentiment_analyzer

# Register the tool
tool_registry.register("sentiment_analyzer", my_sentiment_analyzer)
```

**Step 3: Use it in a workflow**
```json
{
  "nodes": [
    {
      "node_id": "analyze",
      "name": "Analyze Sentiment",
      "type": "process",
      "tool": "sentiment_analyzer"  # ← Use your tool!
    }
  ],
  ...
}
```

**Step 4: Execute**
```bash
curl -X POST "http://localhost:8000/executions/run" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "your-graph-id",
    "initial_state": {
      "text": "This project is great!"
    }
  }'
```

**Result:**
```json
{
  "sentiment": "positive",
  "sentiment_score": 0.9,
  "analyzed_at": "2025-12-10T12:00:00.123456"
}
```

---

## 🐛 Debugging

### See Server Logs
```bash
# In the terminal where run.py is running
# You'll see:
# INFO:     Started server process [12345]
# 2025-12-10 12:00:00,123 - app.main - INFO - Database tables created
# 2025-12-10 12:00:00,200 - app.main - INFO - Code review tools registered
```

### Check Database
```bash
# View all graphs created
python -c "
import sqlite3
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('SELECT id, name FROM graph_model')
for row in cursor.fetchall():
    print(f'Graph: {row[0][:8]}... - {row[1]}')
"
```

### Run Tests
```bash
pytest -v tests/

# See output
# tests/test_basic.py::test_root_returns_welcome_message PASSED
# tests/test_basic.py::test_health_check PASSED
# tests/test_engine.py::test_simple_workflow PASSED
# tests/test_engine.py::test_conditional_workflow PASSED
```

---

## 📖 File Structure

```
agent-execution-framework-170/
├── app/
│   ├── main.py                 ← FastAPI app entry point
│   ├── config.py               ← Configuration
│   ├── api/
│   │   ├── routes/
│   │   │   ├── graph.py        ← Graph CRUD endpoints
│   │   │   └── execution.py    ← Execution endpoints
│   │   └── websocket.py        ← WebSocket streaming
│   ├── core/
│   │   ├── engine.py           ← WorkflowEngine (main logic)
│   │   ├── node.py             ← Node definition
│   │   └── registry.py         ← Tool registry
│   ├── database/
│   │   ├── models.py           ← ORM models
│   │   └── repository.py       ← Database access
│   ├── models/
│   │   ├── graph.py            ← Graph Pydantic models
│   │   ├── execution.py        ← Execution models
│   │   └── state.py            ← State & logging models
│   ├── tools/
│   │   └── code_analyzer.py    ← Built-in code analysis tools
│   └── agents/
│       └── code_review.py      ← Code review workflow
├── tests/
│   ├── test_basic.py           ← API tests
│   └── test_engine.py          ← Engine tests
├── requirements.txt            ← Dependencies
├── run.py                       ← Server startup script
├── test_api.py                 ← API testing script
└── README.md                   ← Project documentation
```

---

## 🎯 Next Steps

### To Learn More:
1. Read `TECHNICAL_GUIDE.md` for deep dives
2. Check `example_usage.py` for code examples
3. Explore `app/core/engine.py` to understand execution flow
4. Modify `app/config.py` to change settings

### To Build More:
1. Create custom tools in `app/tools/`
2. Register them in `app/main.py`
3. Use them in workflow graphs
4. Test with `test_api.py`

### To Deploy:
1. Change `DATABASE_URL` in `.env` to PostgreSQL
2. Run `docker-compose up --build`
3. Access API at your server's address

---

## 💡 Tips & Tricks

### Tip 1: Reuse Graphs
Once you create a graph, execute it multiple times with different initial states:
```bash
# Same graph, different inputs
curl -X POST ".../executions/run" -d '{"graph_id": "X", "initial_state": {...}}'
curl -X POST ".../executions/run" -d '{"graph_id": "X", "initial_state": {...}}'
curl -X POST ".../executions/run" -d '{"graph_id": "X", "initial_state": {...}}'
```

### Tip 2: Debug with Logs
Each execution generates detailed logs:
```json
{
  "logs": [
    {
      "node_id": "extract",
      "status": "completed",
      "duration_ms": 50,
      "input": {...},
      "output": {...}
    }
  ]
}
```

### Tip 3: Chain Workflows
Create workflows that call other workflows:
```
Workflow A (main)
  ├── Node 1 (calls Workflow B)
  └── Node 2 (processes result)
```

### Tip 4: Conditional Loops
```json
{
  "condition": "retry_count < 3"
}
```
Retry a node up to 3 times before moving on.

---

## ❓ FAQ

**Q: Can I run multiple workflows at once?**
A: Yes! Each execution is independent and async. Run 100 workflows simultaneously.

**Q: What if a tool fails?**
A: Execution stops, logs the error, and returns status "failed" with error details.

**Q: Can I modify a graph after creating it?**
A: Currently: delete and recreate. Future: add PATCH endpoint to modify.

**Q: How do I scale this?**
A: Use PostgreSQL + multiple API servers + load balancer.

**Q: Can I use this for machine learning pipelines?**
A: Yes! Your ML models are tools. Register them and build pipelines.

---

*Happy workflow building! 🚀*
