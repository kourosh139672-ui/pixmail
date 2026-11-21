# PixMail

PixMail is an independent, Android-first private messaging and mail-style application.

## Project status

**Early implementation.** The Supabase database foundation and RLS policies are deployed. A starter FastAPI backend and a GitHub Actions test workflow are in the repository. The Android app, production API routes, and deployment are not ready yet.

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
- [Backend setup](backend/README.md)

## Deployment note

GitHub Pages can host static project pages and documentation, but it cannot run the Python API or PostgreSQL database. Those components need separate hosting. Free hosting plans have resource limits and are suitable for a prototype, not an unlimited production service.
