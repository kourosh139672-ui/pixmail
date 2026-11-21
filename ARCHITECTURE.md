# PixMail — Architecture and implementation status

## 1. Product definition

PixMail is an independent, Android-first mail-style messaging service. The first release supports communication only between PixMail accounts. Sending to or receiving from Gmail, Outlook, or other external email providers is out of scope.

The planned account address is `username@pixmail.io`. Until the domain is registered and mail infrastructure is configured, this is an internal identifier only—not a working public email address.

## 2. Technology

| Layer | Choice | Responsibility |
|---|---|---|
| Android client | Kotlin | Native Android application |
| Backend API | Python + FastAPI | Authenticated business logic and messaging |
| Database | Supabase PostgreSQL 17 | Profiles, conversations, messages, mailbox state |
| Identity | Supabase Auth | Account identity and authentication |
| File storage | Private object storage (not configured yet) | Attachments and media |
| API transport | HTTPS / JSON | Client-server communication |
| Notifications | Push provider (not selected) | New-message notifications |

GitHub Pages can host static documentation or a landing page; it cannot run FastAPI or PostgreSQL.

## 3. Product modules

- Authentication and account recovery
- Mailbox: Inbox, Sent, Drafts, Archive, Spam, Trash, Starred
- Messaging: compose, reply, internal forward, read/delivery state
- Private conversations and groups (no channels)
- Attachments: images, video, files and audio
- Profiles and username lookup
- Search by subject and sender in the first release
- Blocking, spam signals and abuse reports
- Persian/English, light/dark/system theme and notifications

## 4. Database implementation

The Supabase project is active and the first database schema has been applied. Supabase Auth is the identity source; passwords are not stored in PixMail tables.

Current public tables:
- `profiles`: username, optional display/full name, avatar and timestamps; profile ID references `auth.users`.
- `conversations`: private or group conversation and creator.
- `conversation_members`: membership and role.
- `messages`: message content, optional subject, content type and edit/global-delete metadata.
- `mailbox_items`: one row per message per user, keeping read, archive, trash, spam, star and local-delete state separate for each participant.
- `attachments`: metadata and private storage path; actual object storage is not configured.
- `user_blocks`: private block list.
- `reports`: abuse reports and review status.
- `user_settings`: locale, theme and notification preferences.
- `device_sessions`: device records; a database trigger keeps at most two active records per account when the backend registers a new device.

The unused channel tables were removed. All ten current public tables have RLS enabled. Authenticated users have narrowly scoped access; sensitive writes such as conversation creation, membership changes, message delivery, attachment metadata and device registration are reserved for the trusted backend. The server must verify the user's Supabase access token and authorize every operation before using its server-side database credential.

## 5. Security baseline and limitations

- HTTPS for every client-server connection.
- Supabase Auth handles password storage and account identity.
- RLS is enabled on every PixMail public table.
- Message and mailbox visibility is user-specific; one user's archive/trash/delete state does not change another user's mailbox copy.
- Service/secret credentials must remain on the server and must never be embedded in Android or committed to Git.
- Upload size is constrained to 100 MB in attachment metadata; the real storage bucket and upload authorization are not configured yet.
- The two-device database rule applies when trusted backend device-registration writes occur; full token/session revocation still needs backend implementation.
- Rate limits, spam automation, quota enforcement and backup scheduling still need implementation.

### Optional end-to-end encryption

E2EE remains disabled. It must not be presented as available until key creation, recovery, group encryption and multi-device key management have been designed and reviewed.

## 6. Product limits and deployment realities

Targets: 100 MB maximum attachment size, 1 GB mailbox quota per user, up to two active devices and weekly backups. These are product goals, not guarantees of free hosting. The selected provider's actual storage, bandwidth, compute and backup limits must be enforced.

“Unlimited scale” is a long-term design goal, not a property of a free plan.

## 7. API areas

- `/auth`: registration, login, refresh, logout and recovery
- `/users`: profile and username lookup
- `/conversations`: direct and group conversations
- `/messages`: send/list/read/delete/archive
- `/attachments`: authorized upload/download
- `/search`: subject and sender search
- `/blocks`, `/reports`, `/settings`

The current FastAPI code is only a starter with health/status endpoints. These business routes are not implemented yet.

## 8. Implementation phases

1. Repository and API foundation — started.
2. Database foundation and RLS — applied; security advisor currently reports no findings.
3. Backend authentication and messaging endpoints — next.
4. Kotlin Android app shell and mailbox UI.
5. Private object storage, attachments and groups.
6. Search, spam handling, blocking, notifications and localization.
7. Security review, backup/restore tests and deployment.
8. Public beta with explicit quotas and monitoring.

## 9. Out of scope for the first release

- External email delivery to Gmail, Outlook or arbitrary mail servers.
- Public SMTP/IMAP compatibility.
- Public channels.
- Promising unlimited storage, bandwidth or uptime.
- Enabling E2EE before key management and recovery are ready.
