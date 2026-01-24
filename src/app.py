"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import close_db, init_db
from src.file_storage.router import router as file_storage_router
from src.logger import get_logger
from src.script_executor.router import router as script_router
from src.auth.router import router as auth_router


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
    )
    logger.info("Scripts directory configured", scripts_dir=str(settings.scripts_dir))
    
    # Initialize database in development
    if settings.environment == "development":
        await init_db()
        logger.info("Database initialized for development")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application", app_name=settings.app_name)
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Scripts Manager - REST API for executing Python scripts",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(script_router, prefix=settings.api_prefix)
app.include_router(file_storage_router, prefix=settings.api_prefix)


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

