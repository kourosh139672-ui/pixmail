# PixMail backend

FastAPI starter for the PixMail service. The first milestone is an API skeleton; authentication, database access, and messaging are not enabled yet.

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

Open `/docs` for the interactive API documentation and `/health` for the process health check.

## Important

- `/health` confirms only that the API process responds. It does not verify PostgreSQL.
- Supabase credentials are optional placeholders at this stage. Never commit a real `.env` file or service-role key.
- Do not expose database credentials in an Android app. Database access must go through authenticated server-side operations or carefully designed Supabase RLS policies.
- PixMail's first release is internal to PixMail; external email delivery is out of scope.
- Attachment upload, user authentication, and messaging routes are not implemented yet.
