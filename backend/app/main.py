from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Private, PixMail-to-PixMail messaging API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {"service": "PixMail API", "status": "starting"}


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    # This checks the API process only; it does not claim the database is ready.
    return {"status": "ok", "service": "pixmail-api"}


@app.get(f"{settings.api_v1_prefix}/status", tags=["system"])
async def api_status() -> dict[str, str]:
    return {"status": "prototype", "database": "not_connected"}
