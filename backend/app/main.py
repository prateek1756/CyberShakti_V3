import os
import sys
from contextlib import asynccontextmanager

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings, validate_runtime_security
from app.shared.rate_limit import RateLimitMiddleware

validate_runtime_security()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler: auto-create database tables & seed demo user in dev mode if using SQLite."""
    if "sqlite" in settings.DATABASE_URL.lower():
        try:
            from app.shared.database import engine, AsyncSessionLocal
            from app.shared.models import Base, User
            from app.shared.security import hash_password
            from sqlalchemy import select

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # Seed default demo account
            async with AsyncSessionLocal() as session:
                demo_email = "user@cybershakti.in"
                existing = (await session.execute(select(User).where(User.email == demo_email))).scalar_one_or_none()
                if not existing:
                    session.add(User(
                        email=demo_email,
                        password_hash=hash_password("CyberShakti@123"),
                        email_verified=True,
                        is_active=True,
                    ))
                    await session.commit()
        except Exception as exc:
            print(f"[Lifespan] Auto-creation/seeding warning: {exc}")
    yield


app = FastAPI(
    title="CyberShakti API",
    description="AI-Powered Digital Safety & Cybersecurity Platform API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan
)

# Add RateLimitMiddleware first so CORSMiddleware runs BEFORE RateLimitMiddleware in Starlette's middleware stack
app.add_middleware(RateLimitMiddleware)

# CORS Middleware Setup (supports localhost, 127.0.0.1, and local network IPs in dev mode)
if settings.ENVIRONMENT.lower() == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition", "Content-Type", "Content-Length"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        expose_headers=["Content-Disposition", "Content-Type", "Content-Length"],
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Global handler for Pydantic validation errors returning standardized error envelope."""
    details = exc.errors() if settings.DEBUG else None
    body = {
        "error_code": "VALIDATION_ERROR",
        "message": "Input validation failed",
    }
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body)


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health probe endpoint."""
    payload = {"status": "healthy", "version": "1.0.0"}
    if settings.DEBUG:
        payload["environment"] = settings.ENVIRONMENT
    return payload


@app.get("/health/live", tags=["Health"])
async def liveness_probe():
    return {"status": "alive"}


# Import and register module API routers
from app.users_auth import router as auth_router
from app.detect_analyze import router as detect_router
from app.protect import router as protect_router
from app.assist_respond import router as assist_router
from app.learn_prevent import router as learn_router
from app import tasks_router

app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(detect_router.router, prefix="/api/v1/detect", tags=["Detect & Analyze"])
app.include_router(protect_router.router, prefix="/api/v1/protect", tags=["Protect"])
app.include_router(assist_router.router, prefix="/api/v1/assist", tags=["Assist & Respond"])
app.include_router(learn_router.router, prefix="/api/v1/learn", tags=["Learn & Prevent"])
app.include_router(tasks_router.router, prefix="/api/v1", tags=["Async Tasks"])
