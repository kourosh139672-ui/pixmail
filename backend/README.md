# PixMail backend

FastAPI backend starter with Supabase Auth registration, username-based login, refresh, current-user, logout and password-recovery routes.

## Easiest prototype deployment: Render

A deployment blueprint is included at the repository root in `render.yaml`.

1. Open the [PixMail Render blueprint](https://render.com/deploy?repo=https://github.com/kourosh139672-ui/pixmail).
2. Sign in to Render and connect the GitHub repository if asked.
3. Review the service named `pixmail-api` and select the Free plan.
4. Render reads `render.yaml`, installs the Python requirements and starts Uvicorn.
5. Before creating the service, enter the two secret environment values when Render asks:
   - `SUPABASE_PUBLISHABLE_KEY`: the project's publishable key.
   - `SUPABASE_SECRET_KEY`: a Supabase secret key, used only by the backend for the username-to-recovery-email lookup RPC.
6. Deploy. When Render reports success, open the service URL followed by `/health`. A successful response confirms that the API process is running.

The Supabase secret key bypasses RLS. Never put it in the Android app, a public repository, screenshots, logs, or client-side configuration. Enter it only in Render's private environment-variable form. Do not send it in chat.

The free Render web service sleeps after 15 minutes without traffic and may take around a minute to wake up. It is for prototype/testing, not a production guarantee. See [Render's free service limitations](https://render.com/docs/free).

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

- This is backend source code committed to GitHub; it is not deployed until the Render setup above is completed.
- Add rate limiting and abuse protection before public release.
- Configure Supabase Auth email confirmation, SMTP, password policy and redirect URLs before production use.
- The Android client, messaging endpoints, storage bucket, push notifications and production deployment are not ready.
- `/health` checks only the API process; it does not verify a database connection.
