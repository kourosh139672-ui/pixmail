# PixMail

PixMail is an independent, Android-first private messaging and mail-style application.

## Project status

**Early implementation.** The Supabase database foundation and RLS policies are deployed. Supabase Edge Function `pixmail-api` is deployed with registration, username/password login, session refresh, current-user, logout, password-recovery, and health routes. A separate `pixmail-health` test function is also deployed. Live end-to-end authentication tests and the Android app are not complete.

## Product scope

- Private messages between PixMail users and group conversations (no public channels)
- Mailbox-style folders: Inbox, Sent, Drafts, Archive, Spam, Starred, and Trash
- Attachments and per-user delivery/read state
- Search by subject and sender
- Blocking, reports, and notifications
- Persian and English interface
- Light, dark, and system themes
- Android application built with Kotlin
- Python backend using FastAPI and Supabase PostgreSQL

PixMail is initially an internal service: messages are delivered only to PixMail accounts. External delivery to Gmail, Outlook, and other mail providers is out of scope for the first release.

## Addressing

The planned address format is `username@pixmail.io`. This becomes a real, publicly reachable email address only after the domain is registered and mail infrastructure is configured. Until then, it is an internal PixMail identifier.

## Supabase Edge API\n\nBase URL: `https://cuxioyecyvxqykymcufg.supabase.co/functions/v1/pixmail-api`\n\nRoutes: `GET /health`, `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`, `POST /auth/logout`, and `POST /auth/recover`. Registration uses a recovery email for Supabase Auth and returns a planned `username@pixmail.io` internal alias. This alias is not yet a real externally deliverable mailbox.\n\n## Documentation

- [Architecture and implementation status](ARCHITECTURE.md)
- [Supabase schema and security notes](supabase/README.md)
- [Backend setup and deployment](backend/README.md)

## Deployment

The current API runs on Supabase Edge Functions; Render is not required for this deployment.
