"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.logger import logger
from src.script_executor.router import router as script_router

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Scripts Manager - REST API for executing Python scripts",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(script_router, prefix=settings.api_prefix)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Scripts directory: {settings.scripts_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info(f"Shutting down {settings.app_name}")

