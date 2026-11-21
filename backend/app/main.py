from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import router as auth_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Private, PixMail-to-PixMail messaging API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {"service": "PixMail API", "status": "prototype"}


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    # This checks only the API process; it does not claim the database is ready.
    return {"status": "ok", "service": "pixmail-api"}


@app.get(f"{settings.api_v1_prefix}/status", tags=["system"])
async def api_status() -> dict[str, str]:
    configured = bool(settings.supabase_url and settings.supabase_publishable_key)
    return {
        "status": "prototype",
        "authentication": "configured" if configured else "not_configured",
        "database": "not_connected",
    }
