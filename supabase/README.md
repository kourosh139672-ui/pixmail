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
- A server-side secret key must never be shipped in the Android app or committed to this repository.
- A service-only RPC resolves a PixMail username to its Supabase Auth recovery email; execution is granted only to `service_role`.
- The Auth profile trigger reads the requested username from signup metadata and creates the corresponding profile.
- New public tables require explicit Data API grants. The current schema grants the authenticated role only intended user-facing operations and grants server-side access to `service_role`.

## Current limitations

- FastAPI now contains source routes for registration, username/password login, token refresh, current-user, logout and password recovery. They are not deployed yet and require environment configuration.
- A private object-storage bucket is not configured, so attachment uploads are not active.
- The 100 MB attachment metadata limit is present, but per-user 1 GB quota enforcement is not implemented.
- Device records are limited to two active rows when inserted by the trusted backend. Backend token/session revocation is still to be implemented.
- Auth confirmation and password recovery emails still depend on Supabase Auth email/SMTP configuration. PixMail-to-PixMail message delivery remains separate.
- Backups, push notifications, spam automation and E2EE are not active.

The last security advisor check returned no findings. Performance advisor findings currently concern indexes not yet used because the new tables are empty; recheck after real workload data exists.
