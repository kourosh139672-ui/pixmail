# PixMail

PixMail is an independent, Android-first private messaging and mail-style application.

## Project status

Early planning / architecture stage. The repository currently contains the project documentation; the production backend and Android application have not been implemented yet.

## Product scope

- Private messages between PixMail users and group conversations
- Mailbox-style folders: Inbox, Sent, Drafts, Archive, Spam, and Trash
- Attachments, message status, search, blocking, and notifications
- Persian and English interface
- Light and dark themes
- Android application built with Kotlin
- Python backend using FastAPI and PostgreSQL

PixMail is initially an internal service: messages are delivered only to PixMail accounts. External delivery to Gmail, Outlook, and other mail providers is out of scope for the first release.

## Addressing

The planned address format is `username@pixmail.io`. This address becomes a real, publicly reachable email address only after the domain is registered and mail infrastructure is configured. Until then, it is an internal PixMail identifier.

## Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for the initial architecture, security model, and implementation phases.

## Important deployment note

GitHub Pages can host static project pages and documentation, but it cannot run the Python API or PostgreSQL database. Those components need a separate backend/database host. Free hosting plans have resource limits and are suitable for a prototype, not an unlimited production service.
