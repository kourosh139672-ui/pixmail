# PixMail

PixMail is an independent, Android-first private messaging and mail-style application.

## Project status

**Early implementation.** The Supabase database foundation and RLS policies are deployed. FastAPI source includes Supabase Auth registration, username/password login, session refresh, current-user, logout and password-recovery routes. A Render deployment blueprint and GitHub Actions tests are configured. The backend is not deployed until the Render setup is completed, and the Android app is not built yet.

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

## Documentation

- [Architecture and implementation status](ARCHITECTURE.md)
- [Supabase schema and security notes](supabase/README.md)
- [Backend setup and deployment](backend/README.md)

## Deployment

A free Render blueprint is included. Start it using [Deploy PixMail on Render](https://render.com/deploy?repo=https://github.com/kourosh139672-ui/pixmail). Free web services sleep after 15 minutes of inactivity and are suitable for prototypes, not production. GitHub Pages cannot run the Python API or PostgreSQL database.
