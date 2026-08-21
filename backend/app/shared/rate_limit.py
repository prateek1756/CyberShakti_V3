"""In-process rate limiter. Thresholds are interim (ADR-026) and env-configurable."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings

_buckets: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and settings.ENVIRONMENT.lower() not in ("prod", "production"):
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _limit_for_path(path: str) -> int:
    auth_prefixes = (
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/password-reset",
        "/api/v1/auth/2fa",
        "/api/v1/auth/refresh",
    )
    if any(path.startswith(p) for p in auth_prefixes):
        return settings.RATE_LIMIT_AUTH_PER_MINUTE
    return settings.RATE_LIMIT_DEFAULT_PER_MINUTE


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        if request.url.path in ("/health", "/health/live"):
            return await call_next(request)

        key = (_client_ip(request), request.url.path)
        limit = _limit_for_path(request.url.path)
        now = time.monotonic()
        window = 60.0
        bucket = _buckets[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please wait and try again.",
                },
                headers={"Retry-After": "60"},
            )
        bucket.append(now)
        return await call_next(request)
