#  Agent Execution Framework - Complete Project Documentation

> A lightweight, async-first workflow orchestration engine built with FastAPI for automating complex multi-step processes.

##  What This Project Does

This framework allows you to:

1. **Define workflows as DAGs** (Directed Acyclic Graphs)
   - Describe complex processes visually
   - Support sequential, parallel, and conditional logic
   
2. **Execute workflows reliably**
   - Async execution for high performance
   - Built-in error handling and logging
   - Loop detection and management

3. **Integrate custom tools**
   - Register any Python function as a tool
   - Tools process workflow state
   - Extensible architecture via registry pattern

4. **Monitor execution in real-time**
   - REST API for workflow management
   - WebSocket for real-time streaming
   - Comprehensive execution logs

5. **Persist everything**
   - SQLite for dev (no setup required)
   - PostgreSQL for production
   - Full execution history

---

##  Real-World Use Cases

### Code Review Automation
```
Input: Source code
   
[Extract Functions]  [Check Complexity]  [Detect Issues]  [Suggest Improvements]
   
Output: Review report with suggestions
```

### Data Processing Pipeline
```
[Load Data]  [Clean]  [Transform]  [Validate]  [Store]
```

### ML Model Inference
```
[Preprocess]  [Feature Engineering]  [Model Inference]  [Post-process]  [Save Results]
```

### User Onboarding
```
[Create Account]  [Send Email]  [Initialize Settings]  [Log Event]
```

---

##  Quick Start

### Installation & Running (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/kamal9508/agent-execution-framework-170.git
cd agent-execution-framework-170

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python run.py

# Output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Database tables created
# INFO:     Code review tools registered
```

### Test It Works

```bash
# In another terminal
python test_api.py

# Output:
#  Health Check: 200
#  Root Endpoint: 200
#  Create Graph: 200
#  API is working correctly!
```

### View API Documentation

Open browser: **http://localhost:8000/docs**

---

##  Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** (this) | Overview & quick start | Everyone |
| **QUICK_START.md** | Practical examples & tutorials | Users getting started |
| **TECHNICAL_GUIDE.md** | Deep dives into architecture & design decisions | Developers & architects |
| **ARCHITECTURE.md** | System diagrams & data flows | System designers |
| **PROJECT_STATUS.md** | Test results & current state | Project managers |

**Reading order:**
1. Start with **README.md** (you are here)
2. Follow **QUICK_START.md** for hands-on examples
3. Dive into **TECHNICAL_GUIDE.md** for understanding
4. Reference **ARCHITECTURE.md** for system design

---

##  System Architecture

### Simple 3-Layer Architecture

```

  REST API Layer                Create graphs, execute workflows
  (FastAPI + Pydantic)       

                 

  Application Logic             Orchestrate execution
  (WorkflowEngine)              Registry pattern for tools
  (State Management)         

                 

  Data Persistence              SQLite (dev) / PostgreSQL (prod)
  (SQLAlchemy ORM)           

```

### Data Flow Example

```
1. Client POSTs workflow definition
   
2. API validates & saves to database
   
3. Client executes workflow
   
4. Engine traverses DAG
   
5. For each node: fetch tool  execute  update state
   
6. Return final results
```

---

##  Why This Approach?

### vs. Manual Python Scripts
```
 Script: Hard-coded flow, no branching, no state management
 Framework: Visual DAG, conditional logic, state shared across nodes
```

### vs. Apache Airflow
```
 Airflow: Complex setup, 100K+ lines of code, steep learning curve
 Framework: 5-minute setup, 500 lines of code, easy to learn
```

### vs. Custom Solution
```
 Custom: Reinvent error handling, logging, APIs, streaming
 Framework: All included, production-ready, extensible
```

---

##  Key Features

###  Built-In Features

| Feature | Description |
|---------|-------------|
| **Async Execution** | Non-blocking, handles 1000s of concurrent workflows |
| **DAG Support** | Visual workflow definition, no circular dependencies |
| **Conditional Branching** | If/else logic within workflows |
| **Loop Management** | Supports iteration with safeguards against infinite loops |
| **Real-time Streaming** | WebSocket for live execution updates |
| **Error Handling** | Comprehensive error logging and recovery |
| **State Management** | Shared context passed between nodes |
| **Tool Registry** | Register custom Python functions as workflow tools |
| **REST API** | Full CRUD operations for graphs and executions |
| **Automatic Docs** | Swagger UI at /docs |
| **Type Safety** | Pydantic models for validation |
| **Testing Ready** | 4 passing unit tests included |
