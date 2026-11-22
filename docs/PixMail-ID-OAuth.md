# PixMail ID — OAuth 2.1 implementation

## Product decision

PixMail ID is a free, public single-sign-on identity provider. Any developer may register an application and request PixMail sign-in credentials; registration is free and subject to basic abuse prevention and security checks.

The selected identity data is:
- Stable subject/user identifier (`sub` / Supabase user ID)
- PixMail internal alias (`username@pixmail.io`)

**Never expose the Supabase Auth email.** It is the private recovery/verification address.

## Email and OIDC privacy design

The `@pixmail.io` address is currently an internal alias, not an externally deliverable mailbox. It must not be described as a verified, deliverable email address.

Supabase's standard OIDC `email` scope returns the Supabase Auth email. The database Custom Access Token Hook created for PixMail replaces the `email` claim only in OAuth access-token JWTs with the internal alias and sets `email_verified=false`. It does not rewrite the OIDC ID token or UserInfo response. Therefore:
- Request `openid` only in the standard OIDC flow.
- Do **not** request the standard `email` scope while it could reveal the recovery email.
- Enable the PixMail Custom Access Token Hook in the Dashboard before issuing OAuth tokens; until enabled, do not activate OAuth for clients.
- After the OAuth access token is issued, the relying service may call the PixMail Identity endpoint below to obtain the internal alias.
- The endpoint returns `email_verified: false` and `email_type: internal_alias`; the alias is not a real mailbox.
- Never silently substitute the recovery email for the PixMail alias.

The hook runs only for OAuth-issued access tokens with a `client_id`; normal PixMail password login and recovery continue using the private Supabase Auth email internally.

## PixMail Identity endpoint

Authenticated endpoint:
`GET https://cuxioyecyvxqykymcufg.supabase.co/functions/v1/pixmail-api/auth/id`

Headers:
- `apikey: <PixMail publishable key>`
- `Authorization: Bearer <OAuth access token>`

The endpoint validates the access token with Supabase Auth and requires an OAuth `client_id` claim. It returns only:
```json
{
  "sub": "<stable Supabase user ID>",
  "email": "username@pixmail.io",
  "email_verified": false,
  "email_type": "internal_alias",
  "address_status": "internal_alias_only"
}
```
It does not return the private recovery email. This is a PixMail-specific identity response, not the standard OIDC UserInfo endpoint. The service must validate the OAuth ID token normally and use `sub` as the stable account key.

The regular `GET /auth/me` response is also minimized and no longer returns the Supabase Auth email.

## OAuth protocol

Use Supabase Auth OAuth 2.1 / OIDC Authorization Code flow with PKCE (S256). Do not use implicit flow or password grant.

Provider endpoints for project cuxioyecyvxqykymcufg:
- Authorization: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/oauth/authorize
- Token: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/oauth/token
- OIDC discovery: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/.well-known/openid-configuration
- JWKS: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/.well-known/jwks.json

## Provider setup still required in Supabase Dashboard

1. Open Authentication → Hooks (Beta).
2. Enable the **Custom Access Token** hook and select `public.pixmail_custom_access_token_hook`.
3. Confirm the hook is active before issuing OAuth tokens. The SQL function and its restricted profile-read policy are already deployed.
4. Open Authentication → OAuth Server.
5. Enable OAuth 2.1 Server.
6. Set Authorization Path to /oauth/consent.
7. Set the Auth Site URL to the HTTPS origin that hosts the PixMail consent UI.
8. Do not expose Supabase's raw dynamic client-registration endpoint to the public. PixMail will provide its own developer registration flow, validate each app's redirect URIs, and create/manage OAuth clients through a trusted server-side process.
9. For OIDC ID tokens, verify the project uses asymmetric JWT signing keys (ES256 or RS256); HS256 cannot issue OIDC ID tokens.

The hook was deployed to the database, but it is **not confirmed enabled** in the Dashboard yet.

OAuth Server is currently **not confirmed enabled**. Do not advertise PixMail ID as live until the dashboard setting and end-to-end test are complete.

## Consent UI requirements

The /oauth/consent page must:
1. Require a signed-in PixMail account; preserve authorization_id through sign-in.
2. Call supabase.auth.oauth.getAuthorizationDetails(authorization_id).
3. Display the requesting app name, exact redirect URI, and requested scopes.
4. Explain that the app receives the stable PixMail ID and the internal `@pixmail.io` alias through the PixMail Identity endpoint; it does not receive the recovery email.
5. For this version, allow only the `openid` standard OIDC scope. Reject or clearly block requests for `email`, `profile`, or `phone` until safe claim mapping is supported.
6. Offer explicit Approve and Deny actions.
7. Call approveAuthorization(authorization_id) or denyAuthorization(authorization_id).
8. Navigate only to the redirect_url returned by Supabase Auth.
9. Never ask for or reveal the user's password to the client app.

## Public developer access and API keys

PixMail ID is free for developers and is intended to be available to developers worldwide.

The developer portal will let a developer register an application and receive credentials:
- **PixMail API Key / Client ID:** public identifier for the registered app. It is not a password and cannot authenticate a user by itself.
- **Client Secret:** issued only to confidential server-side clients. It must never be embedded in Android apps, browser JavaScript, public repositories, or shared in chat.
- **Redirect URI allowlist:** exact HTTPS callback URLs (localhost may be allowed for local development only). Authorization requests with an unregistered redirect URI are rejected.
- **PKCE (S256):** required for public clients, including Android and browser apps.

Registration and basic PixMail ID sign-in are free. To protect users, PixMail may apply reasonable rate limits, automated abuse checks, and suspend malicious clients. No payment is required for a developer account or a basic client registration.

Each app gets a separate client ID and consent screen identity. The developer must provide an app name, app type, website or project URL, and redirect URI(s). Developers must not impersonate other brands or request mailbox/message access in the initial release.

The first developer registration backend and a static portal page have now been added. The portal source is `developer/index.html`; it is not publicly hosted yet. Client provisioning calls Supabase Auth's server-side OAuth admin endpoint from the PixMail Edge Function, never from browser code. Registration remains unavailable until OAuth 2.1 Server is enabled in the Supabase Dashboard.

Register each Pix service as a separate OAuth client. Use exact HTTPS redirect URIs. Use public clients with PKCE for Android/mobile and browser-only apps; use confidential clients only when a service has a trusted server capable of protecting its client secret. Keep client secrets out of mobile apps, browser bundles, source control, and chat.

Initial standard OIDC scope: `openid` only. The internal alias is fetched separately from the authenticated PixMail Identity endpoint.

## Developer registration API (initial implementation)

Base URL:
`https://cuxioyecyvxqykymcufg.supabase.co/functions/v1/pixmail-api`

The developer portal uses the authenticated PixMail account session and these routes:
- `POST /auth/login` — sign in with PixMail username/password.
- `GET /developers/apps` — list the signed-in developer's registered apps.
- `POST /developers/apps` — register an app and provision its OAuth client.

Example registration body:
```json
{
  "app_name": "Example App",
  "app_type": "public",
  "website_url": "https://example.com",
  "redirect_uris": ["https://example.com/auth/callback"]
}
```

Rules enforced by the Edge Function:
- A valid PixMail access token is required.
- App name is 2–80 characters; 1–10 exact redirect URIs are accepted.
- HTTPS is required; HTTP is allowed only for localhost development.
- Wildcards, URL credentials, and URL fragments are rejected.
- Each account can create up to 5 active apps in the initial release.
- Public clients use `client_type=public`, `token_endpoint_auth_method=none`, and PKCE.
- Confidential clients use `client_type=confidential` and `client_secret_basic`; their secret is returned only once and is never stored in the PixMail developer-app registry.
- App ownership metadata is stored in `public.pixmail_developer_apps`; RLS is enabled and direct anon/authenticated table access is revoked. Only the server-side service role can access it.

The portal source currently lives at `developer/index.html`. It includes sign-in, app registration, and an app list. GitHub Pages or another HTTPS host still needs to be configured before developers can visit it publicly.

Important: the backend's client-creation call depends on Supabase OAuth 2.1 Server being enabled. Until that dashboard setting is enabled, registration returns a safe `503` response and no client should be advertised as issued.

## Client flow

1. Generate a cryptographically random PKCE verifier and S256 challenge.
2. Generate and store a random state; verify it on callback.
3. Redirect to the authorization endpoint with response_type=code, registered client_id, exact redirect_uri, scope=openid, code_challenge, code_challenge_method=S256, and state.
4. Exchange the returned one-time code at the token endpoint using the original verifier.
5. Validate the ID token (issuer, audience, signature via JWKS, expiry, nonce if used).
6. Call the PixMail Identity endpoint with the OAuth access token to obtain the internal alias.
7. Create the local service session; use `sub`, not email, as the stable user identifier.

## Revocation and privacy

- Each service gets only its own OAuth client ID and redirect URI.
- Users must be able to revoke connected-app grants.
- Ask consent per client; do not silently grant access because the app belongs to the Pix family.
- Do not log authorization codes, access tokens, refresh tokens, ID tokens, or client secrets.
- Do not store PixMail passwords in any relying service.
- The first release grants identity only, not access to PixMail messages or mailbox contents.
- The recovery/verification email remains private and is used only for PixMail account operations.

## Implementation status

- [x] Selected internal `username@pixmail.io` alias for connected services.
- [x] Product decision: PixMail ID registration and basic sign-in will be free and open to developers worldwide, using per-app API Key / Client ID.
- [x] Build initial developer registration API, app ownership registry, redirect URI validation, Client ID provisioning, and a static portal source page.
- [ ] Publish the developer portal on an HTTPS host (GitHub Pages is not configured yet).
- [ ] Add app revocation/editing UI and stronger abuse/rate-limit controls; initial cap is 5 active apps per account.
- [x] Added authenticated PixMail Identity endpoint returning only the internal alias and stable subject.
- [x] Minimized regular `/auth/me` response so it does not return the recovery email.
- [x] Created database Custom Access Token Hook; OAuth access-token `email` claim is mapped to the internal alias and marked unverified.
- [x] Chosen standard OIDC scope: `openid` only, to avoid exposing recovery email through ID token/UserInfo.
- [ ] Enable the Custom Access Token Hook in Dashboard and verify with a real PixMail profile.
- [ ] Enable OAuth 2.1 Server in Dashboard.
- [ ] Configure and host the consent UI at the Auth Site URL + /oauth/consent.
- [ ] Confirm asymmetric JWT signing for OIDC.
- [ ] Enable OAuth 2.1 Server in Dashboard before testing developer registration.
- [ ] Register the first Pix service as an OAuth client.
- [ ] End-to-end test OAuth and identity endpoint, including denied requests and non-OAuth token rejection. No PixMail profile exists yet; the existing auth-user trigger creates a profile during signup. After the first account is registered, live alias mapping can be tested.
- [ ] Implement callback/token exchange in that service.
