# PixMail — Initial Architecture

## 1. Product definition

PixMail is an Android-first, independent mail-style messaging service. In its first release, users can communicate only with other PixMail users. Delivery to Gmail, Outlook, or other external email providers is not included.

The planned address format is `username@pixmail.io`. Until the domain is registered and configured, this is only an internal identifier, not a working public email address.

## 2. Technology choices

| Layer | Choice | Responsibility |
|---|---|---|
| Android client | Kotlin | Native Android app and local UI |
| Backend API | Python + FastAPI | Authentication, users, conversations, messages, attachments |
| Database | PostgreSQL | Accounts, metadata, conversations, message records, settings |
| File storage | Separate object storage | Uploaded attachments and media |
| API transport | HTTPS / JSON | Client-server communication |
| Notifications | Push provider, selected during deployment | New-message notifications |

GitHub Pages may host static documentation or a landing page. It cannot host the FastAPI process or PostgreSQL database.

## 3. Main application modules

- Authentication: sign-up, sign-in, sign-out, password reset, session management
- Mailbox: Inbox, Sent, Drafts, Archive, Spam, Trash
- Messaging: compose, reply, forward, read status, delivery status
- Conversations: one-to-one conversations and groups
- Attachments: upload, download, file-size validation, access checks
- Contacts and profiles: username, optional display name, profile settings
- Search: subject/title and sender search for the initial release
- Safety: block controls, spam detection, abuse reporting, rate limits
- Settings: Persian/English, light/dark/system theme, notifications, privacy

## 4. Initial data model

Core PostgreSQL tables are expected to include:

- `users`: user ID, normalized username, password hash, optional display name, recovery email, account status, timestamps
- `sessions`: user ID, hashed refresh token, device label, expiry and revocation timestamps
- `conversations`: conversation ID, type (direct/group), title, creator, timestamps
- `conversation_members`: conversation ID, user ID, role, join/leave timestamps
- `messages`: message ID, conversation ID, sender ID, subject, encrypted/plain payload metadata, timestamps
- `message_recipients`: message ID, recipient ID, delivery/read timestamps, per-user mailbox state
- `attachments`: attachment ID, message ID, storage key, MIME type, byte size, checksum
- `user_blocks`: blocker ID, blocked user ID, created timestamp
- `reports`: reporter, target, reason, review status, timestamps
- `user_settings`: locale, theme, notification preferences

The final schema must be reviewed before migrations are created. Message deletion needs per-user mailbox state so that deleting a message from one user's mailbox does not accidentally erase another user's copy.

## 5. Security baseline

- HTTPS for every client-server connection
- Passwords stored only as strong salted password hashes (Argon2id or an equivalent maintained password-hashing algorithm)
- Short-lived access tokens and securely stored, revocable refresh sessions
- Server-side authorization checks for every conversation, message, and attachment
- Upload size/type validation and randomized storage keys
- Rate limits for sign-in, registration, message sending, and uploads
- Automated spam signals and user reporting
- Secrets stored in deployment environment variables, never committed to Git
- Regular dependency updates and security logging without recording message contents or passwords

### Optional end-to-end encryption

The selected product direction includes standard transport/storage protections plus optional end-to-end encryption (E2EE) for selected conversations or messages.

E2EE must be designed before implementation, not added as a cosmetic toggle. The server must never receive users' private encryption keys. When content is end-to-end encrypted, the server cannot read or full-text-search that content. Group encryption and multi-device key management require additional protocol design. The initial prototype should keep the E2EE feature disabled until its key lifecycle and recovery behavior have been reviewed.

## 6. Product limits and deployment realities

The planned product settings include a 100 MB maximum attachment size, 1 GB mailbox quota per user, up to two active devices per account, and weekly backups. These are product targets, not guarantees of free hosting. The server must enforce lower operational limits whenever the selected free provider requires them.

A free-tier prototype will have storage, bandwidth, compute, uptime, and backup limits. “Unlimited scale” is a long-term design goal, not a property of a free plan.

## 7. API areas

Initial API groups:

- `/auth`: registration, login, refresh, logout, password reset
- `/users`: profile and username lookup
- `/conversations`: create/list direct and group conversations
- `/messages`: send/list/read/delete/archive messages
- `/attachments`: upload and download authorized attachments
- `/search`: search supported mailbox metadata
- `/blocks`: block and unblock users
- `/reports`: submit abuse reports
- `/settings`: locale, theme, notification and privacy preferences

All endpoints require input validation, authentication where appropriate, authorization, and consistent error responses.

## 8. Implementation phases

1. Repository foundation: documentation, backend skeleton, configuration example, tests and CI checks.
2. Backend MVP: PostgreSQL schema, registration/login, sessions, direct messages, mailbox states.
3. Android MVP: Kotlin app shell, authentication screens, inbox, compose and conversation view.
4. Attachments and groups: object storage, group membership, upload/download authorization.
5. Product features: search, spam handling, blocking, notifications, themes and localization.
6. Security hardening: threat review, E2EE protocol design, backup/restore tests, deployment review.
7. Public beta: deploy to a free-tier environment with explicit quotas and monitoring.

## 9. Out of scope for the first release

- Sending or receiving email through Gmail, Outlook, or arbitrary external mail servers
- Public SMTP/IMAP compatibility
- Promising unlimited storage, bandwidth, or uptime
- Enabling E2EE before key management and recovery are properly designed
