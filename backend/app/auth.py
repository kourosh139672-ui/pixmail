from typing import Any

import httpx
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9]+$")
    recovery_email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9]+$")
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=4096)


class RecoveryRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9]+$")


def _settings():
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured on the PixMail server yet.",
        )
    return settings


async def _send(method: str, path: str, *, headers: dict[str, str], json: dict[str, Any] | None = None) -> httpx.Response:
    settings = _settings()
    url = f"{settings.supabase_url.rstrip('/')}{path}"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0)) as client:
            return await client.request(method, url, headers=headers, json=json)
    except (httpx.TimeoutException, httpx.NetworkError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="PixMail could not reach the authentication service. Try again shortly.",
        ) from exc


def _public_headers() -> dict[str, str]:
    settings = _settings()
    return {
        "apikey": settings.supabase_publishable_key,
        "Content-Type": "application/json",
    }


async def _email_for_username(username: str) -> str | None:
    settings = _settings()
    if not settings.supabase_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Username login needs the PixMail server secret key to be configured.",
        )
    headers = {
        "apikey": settings.supabase_secret_key,
        "Content-Type": "application/json",
    }
    # Legacy service_role keys are JWTs and require Authorization as well.
    if settings.supabase_secret_key.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {settings.supabase_secret_key}"
    response = await _send(
        "POST",
        "/rest/v1/rpc/pixmail_auth_email_for_username",
        headers=headers,
        json={"p_username": username.lower()},
    )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="PixMail could not look up the account. Check the server-side Supabase key.",
        )
    try:
        value = response.json()
    except ValueError:
        return None
    return value if isinstance(value, str) and value else None


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> dict[str, Any]:
    _settings()
    response = await _send(
        "POST",
        "/auth/v1/signup",
        headers=_public_headers(),
        json={
            "email": str(payload.recovery_email).lower(),
            "password": payload.password,
            "data": {"username": payload.username.lower()},
        },
    )
    if response.status_code >= 400:
        # Avoid exposing Auth/Postgres internals to the mobile client.
        raise HTTPException(
            status_code=400,
            detail="Account could not be created. Check the username and recovery email, then try again.",
        )

    try:
        result = response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Invalid response from authentication service.") from exc

    session = result.get("session") or {}
    user = result.get("user") or result
    return {
        "created": True,
        "username": payload.username.lower(),
        "confirmation_required": not bool(session.get("access_token") or result.get("access_token")),
        "user_id": user.get("id"),
        "session": session or None,
        "message": (
            "Account created. Check your recovery email if confirmation is required."
            if not (session.get("access_token") or result.get("access_token"))
            else "Account created and signed in."
        ),
    }


@router.post("/login")
async def login(payload: LoginRequest) -> dict[str, Any]:
    email = await _email_for_username(payload.username)
    if not email:
        raise HTTPException(status_code=401, detail="Username or password is incorrect.")

    response = await _send(
        "POST",
        "/auth/v1/token?grant_type=password",
        headers=_public_headers(),
        json={"email": email, "password": payload.password},
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Username or password is incorrect.")
    return response.json()


@router.post("/refresh")
async def refresh(payload: RefreshRequest) -> dict[str, Any]:
    response = await _send(
        "POST",
        "/auth/v1/token?grant_type=refresh_token",
        headers=_public_headers(),
        json={"refresh_token": payload.refresh_token},
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    return response.json()


@router.get("/me")
async def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="A valid PixMail access token is required.")
    response = await _send(
        "GET",
        "/auth/v1/user",
        headers={
            **_public_headers(),
            "Authorization": authorization,
        },
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Session is invalid or expired.")
    return response.json()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(authorization: str | None = Header(default=None)) -> None:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="A valid PixMail access token is required.")
    response = await _send(
        "POST",
        "/auth/v1/logout",
        headers={
            **_public_headers(),
            "Authorization": authorization,
        },
    )
    if response.status_code >= 400:
        raise HTTPException(status_code=401, detail="Could not end this session.")


@router.post("/recover")
async def recover_password(payload: RecoveryRequest) -> dict[str, str]:
    email = await _email_for_username(payload.username)
    # Return the same public response whether or not the username exists.
    if email:
        response = await _send(
            "POST",
            "/auth/v1/recover",
            headers=_public_headers(),
            json={"email": email},
        )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=503,
                detail="Password recovery email is not available yet. The email provider may need configuration.",
            )
    return {"message": "If the account exists, password recovery instructions will be sent to its recovery email."}
