# PixMail ID — OAuth 2.1 implementation

## Product decision

PixMail ID is the single-sign-on identity provider for first-party Pix services and, later, approved third-party clients.

The selected access level is **email**:
- OpenID Connect identity (openid)
- email claim (email)
- stable subject/user identifier (sub / Supabase user ID)

Do not request profile, phone, contacts, mailbox, or message access in this first version.

## Important email distinction

The current PixMail account model uses Supabase Auth email as the account recovery/verification email. The planned username@pixmail.io address is currently only an internal alias and is not an externally deliverable mailbox.

Supabase's standard email scope returns the Supabase Auth email. It does not automatically return the planned @pixmail.io alias. Before production, product owner must choose whether the email claim should expose:
1. the verified recovery email; or
2. the PixMail alias (which must be clearly marked as an internal address until real mail hosting exists).

Never silently substitute one for the other.

## OAuth protocol

Use Supabase Auth OAuth 2.1 / OIDC Authorization Code flow with PKCE (S256). Do not use implicit flow or password grant.

Provider endpoints for project cuxioyecyvxqykymcufg:
- Authorization: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/oauth/authorize
- Token: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/oauth/token
- OIDC discovery: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/.well-known/openid-configuration
- JWKS: https://cuxioyecyvxqykymcufg.supabase.co/auth/v1/.well-known/jwks.json

## Provider setup still required in Supabase Dashboard

1. Open Authentication → OAuth Server.
2. Enable OAuth 2.1 Server.
3. Set Authorization Path to /oauth/consent.
4. Set the Auth Site URL to the HTTPS origin that hosts the PixMail consent UI.
5. Keep dynamic client registration disabled for the first-party Pix ecosystem.
6. For OIDC ID tokens, verify the project uses asymmetric JWT signing keys (ES256 or RS256); HS256 cannot issue OIDC ID tokens.

OAuth Server is currently **not confirmed enabled**. Do not advertise PixMail ID as live until the dashboard setting and end-to-end test are complete.

## Consent UI requirements

The /oauth/consent page must:
1. Require a signed-in PixMail account; preserve authorization_id through sign-in.
2. Call supabase.auth.oauth.getAuthorizationDetails(authorization_id).
3. Display the requesting app name, exact redirect URI, and requested scopes.
4. Explain that the app will receive the user's stable ID and email claim.
5. Offer explicit Approve and Deny actions.
6. Call approveAuthorization(authorization_id) or denyAuthorization(authorization_id).
7. Navigate only to the redirect_url returned by Supabase Auth.
8. Never ask for or reveal the user's password to the client app.

## OAuth client registration policy

Register each Pix service as a separate OAuth client. Use exact HTTPS redirect URIs. Use public clients with PKCE for Android/mobile and browser-only apps; use confidential clients only when a service has a trusted server capable of protecting its client secret. Keep client secrets out of mobile apps, browser bundles, source control, and chat.

Initial requested scopes: openid email. Do not include profile unless separately approved.

## Client flow

1. Generate a cryptographically random PKCE verifier and S256 challenge.
2. Generate and store a random state; verify it on callback.
3. Redirect to the authorization endpoint with response_type=code, registered client_id, exact redirect_uri, scope=openid email, code_challenge, code_challenge_method=S256, and state.
4. Exchange the returned one-time code at the token endpoint using the original verifier.
5. Validate the ID token (issuer, audience, signature via JWKS, expiry, nonce if used).
6. Create the local service session; do not treat the email address alone as a stable user identifier. Use sub.

## Revocation and privacy

- Each service gets only its own OAuth client ID and redirect URI.
- Users must be able to revoke connected-app grants.
- Ask consent per client; do not silently grant access because the app belongs to the Pix family.
- Do not log authorization codes, access tokens, refresh tokens, ID tokens, or client secrets.
- Do not store PixMail passwords in any relying service.
- The first release grants identity/email only, not access to PixMail messages or mailbox contents.

## Implementation status

- [x] Confirmed active Supabase project and existing PixMail Edge Functions.
- [x] Chosen minimum OAuth scopes: openid email.
- [ ] Decide whether email claim is verified recovery email or internal @pixmail.io alias.
- [ ] Enable OAuth 2.1 Server in Dashboard.
- [ ] Configure and host the consent UI at the Auth Site URL + /oauth/consent.
- [ ] Confirm asymmetric JWT signing for OIDC.
- [ ] Register the first Pix service as an OAuth client.
- [ ] Implement callback/token exchange in that service.
- [ ] Test approve, deny, state mismatch, expired code, refresh, and grant revocation.
