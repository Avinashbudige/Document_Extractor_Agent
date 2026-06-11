"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from src.api.routers import documents, extractions, batches, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting Document Extraction Agent API")
    yield
    # Shutdown
    logger.info("Shutting down Document Extraction Agent API")


# Create FastAPI application
app = FastAPI(
    title="Document Extraction Agent",
    description="Intelligent document processing system for extracting structured data from business documents",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions."""
    logger.error(f"ValueError: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "INVALID_INPUT",
                "message": str(exc),
                "timestamp": request.state.timestamp if hasattr(request.state, 'timestamp') else None
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": request.state.timestamp if hasattr(request.state, 'timestamp') else None
            }
        }
    )


# Include routers
app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(documents.router, prefix="/v1", tags=["documents"])
app.include_router(extractions.router, prefix="/v1", tags=["extractions"])
app.include_router(batches.router, prefix="/v1", tags=["batches"])


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "service": "Document Extraction Agent",
        "version": "1.0.0",
        "status": "running"
    }
