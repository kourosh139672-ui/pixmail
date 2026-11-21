# PixMail database

The initial PixMail schema is deployed to the connected Supabase PostgreSQL 17 project.

## Tables

`profiles`, `conversations`, `conversation_members`, `messages`, `mailbox_items`, `attachments`, `user_blocks`, `reports`, `user_settings`, and `device_sessions`.

The old empty channel tables were removed because channels are not part of the PixMail product scope.

## Security model

- Supabase Auth is the source of user identity; `profiles.id` references `auth.users.id`.
- RLS is enabled on all ten public tables, with 25 policies currently configured.
- The `anon` role has no table privileges on these PixMail tables.
- Authenticated users can read only mailbox copies assigned to their own account and the member roster of conversations they belong to.
- Mailbox status fields are user-specific; clients cannot change mailbox/message ownership or globally delete messages.
- The FastAPI backend is intended to perform privileged writes after validating the user's access token and checking authorization.
- A server-side credential must never be shipped in the Android app or committed to this repository.
- New public tables require explicit Data API grants. The current schema grants the authenticated role only intended user-facing operations and grants server-side access to `service_role`.

## Current limitations

- The FastAPI project currently contains health/status endpoints only; auth and messaging routes are not wired up.
- A private object-storage bucket is not configured, so attachment uploads are not active.
- The 100 MB attachment metadata limit is present, but per-user 1 GB quota enforcement is not implemented.
- Device records are limited to two active rows when inserted by the trusted backend. Backend token/session revocation is still to be implemented.
- Backups, push notifications, spam automation and E2EE are not active.

The last security advisor check returned no findings. Performance advisor findings currently concern indexes not yet used because the new tables are empty; recheck after real workload data exists.
