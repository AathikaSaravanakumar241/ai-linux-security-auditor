"""
FastAPI application entry point for the AI Linux Security Auditor.

Architecture:
    - Integrates the audit router.
    - Standardizes all errors (404, 500, etc.) into the StandardResponse JSON format.
    - Implements request-response logging middleware with request timing.
    - Performs database initialization on application startup inside the lifecycle hook.
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import init_db
from app.routers import audit_router
from app.schemas.audit_schemas import StandardResponse, ErrorDetail

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan Event Handler (Startup / Shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Initializes logging levels and ensures all DB tables exist.
    """
    settings = get_settings()
    
    # Configure root logging level from settings
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    
    logger.info("Starting AI Linux Security Auditor backend...")
    
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.critical("Failed to initialize database: %s", exc, exc_info=True)
        
    logger.info("Backend is running and ready to accept requests.")
    yield
    logger.info("Shutting down backend services...")


# ---------------------------------------------------------------------------
# FastAPI Application Configuration
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Linux Security Auditor",
    description=(
        "Production-ready API for auditing Linux servers using Paramiko SSH "
        "and Google Gemini AI analysis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------

settings = get_settings()
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/Response Logging & Timing Middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log request paths, statuses, and performance processing time.
    """
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info(
        "Request: %s %s | Status: %d | Time: %.3fs",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    
    # Add timing header to response
    response.headers["X-Process-Time"] = f"{duration:.3f}s"
    return response


# ---------------------------------------------------------------------------
# Global Exception Handlers (Standardizing JSON Responses)
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle HTTP request validation errors and return structured validation feedback.
    """
    logger.warning("Request validation failed for %s %s: %s", request.method, request.url.path, exc.errors())
    
    error_detail = ErrorDetail(
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        details=str(exc.errors()),
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=StandardResponse(
            success=False,
            data=None,
            error=error_detail,
            timestamp=datetime.now(timezone.utc),
        ).model_dump(mode="json"),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle standard HTTPExceptions (like 404 Not Found, 405 Method Not Allowed).
    """
    logger.warning("HTTP error occurred: %d — %s", exc.status_code, exc.detail)
    
    code = "HTTP_ERROR"
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "RESOURCE_NOT_FOUND"
    elif exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        code = "METHOD_NOT_ALLOWED"
    elif exc.status_code == status.HTTP_401_UNAUTHORIZED:
        code = "UNAUTHORIZED"

    error_detail = ErrorDetail(
        code=code,
        message=str(exc.detail),
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse(
            success=False,
            data=None,
            error=error_detail,
            timestamp=datetime.now(timezone.utc),
        ).model_dump(mode="json"),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all global exception handler returning 500 status.
    """
    logger.error("Unhandled system exception: %s", exc, exc_info=True)
    
    error_detail = ErrorDetail(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected system error occurred. Please contact the administrator.",
        details=str(exc) if get_settings().LOG_LEVEL.lower() == "debug" else None,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=StandardResponse(
            success=False,
            data=None,
            error=error_detail,
            timestamp=datetime.now(timezone.utc),
        ).model_dump(mode="json"),
    )


# ---------------------------------------------------------------------------
# Health & Status Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"], response_model=StandardResponse)
@app.get("/api/health", tags=["System"], response_model=StandardResponse)
async def health_check():
    """
    Readiness probe returning backend health status.
    """
    return StandardResponse(
        success=True,
        data={"status": "healthy", "service": "ai-linux-security-auditor"},
        error=None,
    )


# ---------------------------------------------------------------------------
# Include API Routers
# ---------------------------------------------------------------------------

app.include_router(audit_router.router)
