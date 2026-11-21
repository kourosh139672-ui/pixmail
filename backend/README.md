# PixMail backend

FastAPI backend starter with Supabase Auth registration, username-based login, refresh, current-user, logout and password-recovery routes.

## Run locally

Python 3.11 or newer is recommended.

```bash
cd backend
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open `/docs` for interactive API documentation and `/health` for the process health check.

## Supabase configuration

Set these environment variables on the backend host:

- `SUPABASE_URL`: the project API URL.
- `SUPABASE_PUBLISHABLE_KEY`: the project's publishable key.
- `SUPABASE_SECRET_KEY`: a Supabase secret key, used only by the backend for the username-to-recovery-email lookup RPC.

The secret key bypasses RLS. Never put it in the Android app, a public repository, logs, or client-side configuration. The example file deliberately leaves both keys blank.

## Authentication behavior

- Registration uses the user's recovery email with Supabase Auth and stores the chosen PixMail username in Auth user metadata. A database trigger creates the matching profile.
- Login accepts username and password. The backend privately resolves the account's recovery email using a service-only database function, then delegates password verification to Supabase Auth.
- Refresh, current-user, logout and password recovery are proxied to Supabase Auth.
- Passwords are never stored in PixMail tables.
- Supabase email confirmation and password recovery depend on the project's Auth email/SMTP settings. Configure a reliable email provider before inviting real users.
- Store refresh tokens securely on Android (Android Keystore-backed encrypted storage); never print or log tokens.

## API routes

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/recover`

Registration requires a username (3–30 English letters/digits), recovery email and password (10–128 characters).

## Current limitations

- This is backend source code committed to GitHub; it is not deployed or running yet.
- Add rate limiting and abuse protection before public release.
- Configure Supabase Auth email confirmation, SMTP, password policy and redirect URLs before production use.
- The Android client, messaging endpoints, storage bucket, push notifications and production deployment are not ready.
- `/health` checks only the API process; it does not verify a database connection.
