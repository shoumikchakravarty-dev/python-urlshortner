"""FastAPI application entry point."""

from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import init_db, close_db
from app.api.routes import urls, stats
from app.utils.exceptions import (
    InvalidURLException,
    ShortCodeExistsException,
    ShortCodeNotFoundException,
    URLExpiredException,
    InvalidShortCodeException,
    DatabaseException,
    CollisionRetriesExceededException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A modern URL shortener API built with FastAPI and SQLAlchemy",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(InvalidURLException)
async def invalid_url_handler(request: Request, exc: InvalidURLException):
    """Handle invalid URL exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Invalid URL",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(ShortCodeExistsException)
async def short_code_exists_handler(request: Request, exc: ShortCodeExistsException):
    """Handle short code already exists exceptions."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Short Code Conflict",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(ShortCodeNotFoundException)
async def short_code_not_found_handler(request: Request, exc: ShortCodeNotFoundException):
    """Handle short code not found exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(URLExpiredException)
async def url_expired_handler(request: Request, exc: URLExpiredException):
    """Handle URL expired exceptions."""
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={
            "error": "URL Expired",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(InvalidShortCodeException)
async def invalid_short_code_handler(request: Request, exc: InvalidShortCodeException):
    """Handle invalid short code format exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Invalid Short Code",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(CollisionRetriesExceededException)
async def collision_retries_exceeded_handler(request: Request, exc: CollisionRetriesExceededException):
    """Handle collision retries exceeded exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle database exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Include routers
app.include_router(urls.router, prefix="/api/v1", tags=["URLs"])
app.include_router(stats.router, prefix="/api/v1", tags=["Statistics"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "message": "URL Shortener API",
        "version": settings.app_version,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }
