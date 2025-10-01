"""FastAPI backend for Aker Investment Platform."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .endpoints import cache, markets, portfolio, reports


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Aker Investment Platform API...")
    yield
    # Shutdown
    print("👋 Shutting down API...")


# Create FastAPI application
app = FastAPI(
    title="Aker Investment Platform API",
    description="REST API for real estate investment screening and analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(markets.router, prefix="/api/markets", tags=["markets"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(cache.router, prefix="/api/cache", tags=["cache"])


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "Aker Investment Platform API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "aker-platform-api"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "path": str(request.url),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

