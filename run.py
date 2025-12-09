#!/usr/bin/env python
"""
Entry point for running the agent-execution-framework API server.
This script properly sets up the Python path and starts the FastAPI server.
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn

    # Change to project directory
    os.chdir(project_root)

    # Start the Uvicorn server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
