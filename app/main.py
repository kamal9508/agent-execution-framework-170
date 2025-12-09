"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.repository import database
from app.agents.code_review import register_code_review_tools
from app.api.routes import graph, execution
from app.api import websocket

logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.

    Args:
        app: FastAPI application
    """
    logger.info("Starting application...")

    await database.create_tables()
    logger.info("Database tables created")

    register_code_review_tools()
    logger.info("Code review tools registered")

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A lightweight workflow engine for building agent-based systems",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph.router)
app.include_router(execution.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Agent Workflow Engine API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
