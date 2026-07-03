"""
main.py
FastAPI application entry point.
Full endpoints will be wired in Phase 5; this shell confirms the app starts correctly.
"""
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.models import HealthResponse, ErrorResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Multi-Agent Stock Research System starting up...")
    logger.info(f"   CORS origins: {settings.cors_origins_list}")
    logger.info(f"   Groq model  : {settings.groq_model}")
    yield
    logger.info("🛑 Multi-Agent Stock Research System shutting down...")

app = FastAPI(
    title="Multi-Agent Stock Research System",
    description=(
        "AI-powered financial research platform using multiple specialized agents "
        "to deliver comprehensive stock analysis reports."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ─── Request timing middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.time() - start:.3f}s"
    return response


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Returns service health status."""
    return HealthResponse(status="ok", version="1.0.0")


# ─── Root ─────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "service": "Multi-Agent Stock Research System",
        "status": "running",
        "docs": "/docs",
    }


# ─── Research endpoint (stub — Phase 5) ──────────────────────────────────────
@app.post("/api/research", tags=["Research"])
async def research(request: Request):
    """
    POST /api/research
    Runs the full multi-agent research pipeline for a given ticker.
    Full implementation: Phase 5.
    """
    return JSONResponse(
        status_code=501,
        content={"error": "Not implemented", "detail": "Research endpoint will be available in Phase 5"},
    )


# ─── History endpoint (stub — Phase 6) ───────────────────────────────────────
@app.get("/api/history", tags=["History"])
async def history():
    """
    GET /api/history
    Returns paginated list of past research reports.
    Full implementation: Phase 6.
    """
    return JSONResponse(
        status_code=501,
        content={"error": "Not implemented", "detail": "History endpoint will be available in Phase 6"},
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
