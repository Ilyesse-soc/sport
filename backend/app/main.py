import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, coach, health, nutrition, profile, progression, recovery, training
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.database.base import Base
from app.database.session import engine

settings = get_settings()

docs_enabled = settings.environment != "production"
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url=f"{settings.api_prefix}/openapi.json" if docs_enabled else None,
)

allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_security_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id

    body_limit = settings.max_request_body_mb * 1024 * 1024
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > body_limit:
        return JSONResponse(status_code=413, content={"detail": "Payload too large", "request_id": request_id})

    if len(request.url.query) > settings.max_query_length:
        return JSONResponse(status_code=414, content={"detail": "Query too long", "request_id": request_id})

    response = await call_next(request)
    csp = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https:; "
        "font-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self';"
    )
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Request-ID"] = request_id
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "")
    if settings.environment == "production":
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
    return JSONResponse(status_code=500, content={"detail": str(exc), "request_id": request_id})


@app.on_event("startup")
def startup() -> None:
    setup_logging()
    Base.metadata.create_all(bind=engine)


api_prefix = settings.api_prefix
app.include_router(health.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(profile.router, prefix=api_prefix)
app.include_router(nutrition.router, prefix=api_prefix)
app.include_router(training.router, prefix=api_prefix)
app.include_router(progression.router, prefix=api_prefix)
app.include_router(recovery.router, prefix=api_prefix)
app.include_router(coach.router, prefix=api_prefix)
