# Agent Execution Framework

A lightweight, minimal LangGraph‑style workflow engine that lets you define nodes (steps), connect them into directed workflows, maintain shared state, and execute workflows — all via clean, async-ready APIs built on FastAPI.

---

## ⚙️ What Is This

Many backend systems — automation pipelines, agent orchestrators, etc. — require the ability to define dynamic flows where steps run in sequence or conditionally, share data, and can be triggered via external APIs. Agent Execution Framework provides exactly this:

- Define **nodes** (units of work / tasks) that can modify shared state.
- Connect nodes to form a **directed graph** (workflow).
- Expose REST APIs to create workflows, add nodes, connect them, and trigger execution.
- Support **async execution**, enabling I/O-heavy or long-running tasks.
- Simple JSON/DB-backed storage — no heavyweight infrastructure required.
- Modular, extensible codebase: easy to add new kinds of nodes, future enhancements.

---

## 📦 Features

- ✅ Create workflows via API
- ✅ Add nodes dynamically to a workflow
- ✅ Connect nodes to define execution order (directed graph)
- ✅ Maintain shared state across the workflow execution
- ✅ Trigger workflow execution via REST API
- ✅ Async-ready node execution
- ✅ Modular folder structure for ease of extension
- ✅ Simple local JSON/db storage
- ✅ Docker support (Dockerfile + docker-compose)
- ✅ Test suite included

---

agent-execution-framework/
│
├── app/ # Main application
│ ├── api/ # Route handlers (workflows, nodes)
│ ├── core/ # Config, settings, utility code
│ ├── engine/ # Workflow engine logic
│ ├── models/ # Node & workflow data models
│ ├── schemas/ # Pydantic schemas for request/response
│ ├── tools/ # Helper utilities / tools used by nodes
│ ├── db/ # Local JSON/db storage
│ ├── main.py # FastAPI entry-point
│ └── init.py
│
├── tests/ # Test cases
├── requirements.txt # Dependencies
├── Dockerfile # Docker build config
├── docker-compose.yml # Docker compose setup
└── README.md # Project README


---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pip` for installing dependencies
- (Optional) Docker & Docker Compose

### Quick Install & Run

```bash
# Clone repo
git clone https://github.com/kamal9508/agent-execution-framework-170.git
cd agent-execution-framework-170

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # Linux / macOS
# venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload

# Build Docker image
docker build -t agent-engine .

# Run with docker-compose
docker-compose up --build


## 🗂 Project Structure

📡 API Endpoints
Endpoint	Method	Description
/workflow/create	POST	Create a new workflow
/workflow/{id}/node	POST	Add nodes to a workflow
/workflow/{id}/connect	POST	Connect nodes (define flow)
/workflow/{id}/run	POST	Execute workflow
/workflow/{id}/state	GET	Get workflow state

🔧 Workflow Diagram

Example workflow:

   +---------+      +---------+      +---------+
   | Node A  | ---> | Node B  | ---> | Node C  |
   +---------+      +---------+      +---------+
         \                              /
          \                            /
           ------> Node D -------------


Node A: Start node, initializes workflow state

Node B / Node C: Sequential steps that modify the shared state

Node D: Optional parallel or conditional node

State flows along the arrows, updated by each node, until workflow completes.

🔧 Usage Example
# Example: Simple workflow execution
workflow_id = create_workflow("MyWorkflow")
add_node(workflow_id, "NodeA", func=node_a)
add_node(workflow_id, "NodeB", func=node_b)
add_node(workflow_id, "NodeC", func=node_c)
connect_nodes(workflow_id, "NodeA", "NodeB")
connect_nodes(workflow_id, "NodeB", "NodeC")
run_workflow(workflow_id)
state = get_workflow_state(workflow_id)
print(state)


📚 Tech Stack & Dependencies
Layer	Technology
Web API / Server	FastAPI, Uvicorn
Data Validation / Schemas	Pydantic
Async support	Python async / await
Storage	Local JSON / lightweight DB files
Containerization	Docker, Docker Compose
Testing	pytest
Language	Python 3.8+

🧑‍💻 Use Cases

Backend developers embedding workflow logic in microservices

Data engineers or automation engineers creating lightweight pipelines

Students exploring workflow orchestration, async programming, and REST APIs

Building agent-based systems, ETL-like flows, or job pipelines

📈 Why This Project

Minimal, lightweight workflow engine

Modular & extensible code

Docker support for easy deployment

Clean, async-ready API design

Ideal for learning or building small-to-medium workflow systems
📄 License

MIT License — feel free to use, modify, and extend.

