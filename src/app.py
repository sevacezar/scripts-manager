"""Main FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.config import settings
from src.database import close_db, init_db
from src.file_storage.router import router as file_storage_router
from src.logger import get_logger
from src.script_executor.router import router as script_router
from src.auth.router import router as auth_router
from src.scripts_manager.router import router as scripts_manager_router


logger = get_logger(__name__)

# Path to static frontend files
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"


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

# Include API routers (before static files - order matters!)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(scripts_manager_router, prefix=settings.api_prefix)
app.include_router(script_router, prefix=settings.api_prefix)
app.include_router(file_storage_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve static frontend files
if STATIC_DIR.exists():
    # Mount static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")
    
    # Root endpoint - serve index.html
    @app.get("/")
    async def serve_root():
        """Serve React SPA index.html for root path."""
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(
                str(index_path),
                media_type="text/html",
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
            )
        return {"error": "Frontend not built"}
    
    # Fallback for React Router - serve index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve React SPA. All non-API routes return index.html.
        React Router handles client-side routing.
        """
        # Skip API routes, assets, and system routes
        excluded_prefixes = ["api", "docs", "redoc", "openapi.json", "assets"]
        
        if any(full_path.startswith(prefix) for prefix in excluded_prefixes):
            return None
        
        # Check if it's a static file request (favicon, etc.)
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # For all other paths - return index.html (React Router will handle routing)
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(
                str(index_path),
                media_type="text/html",
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
            )
        
        # Frontend not built
        return {
            "error": "Frontend not built",
            "message": "Run 'npm run build' in frontend directory",
        }
    
    logger.info("Frontend static files enabled", static_dir=str(STATIC_DIR))
else:
    logger.warning(
        "Frontend static files not found",
        static_dir=str(STATIC_DIR),
        message="Frontend will not be served. Build frontend with 'npm run build'",
    )

