from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings, validate_runtime_security
from app.shared.rate_limit import RateLimitMiddleware

validate_runtime_security()

app = FastAPI(
    title="CyberShakti v3 API",
    description="AI-Powered Digital Safety & Cybersecurity Platform API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None
)

app.add_middleware(RateLimitMiddleware)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
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
