---
name: oauth-oidc-review
description: Review OAuth 2.x and OpenID Connect integrations — flows, PKCE, redirect URIs, token validation, scopes, sessions and logout — for common security mistakes. Use when adding SSO or social login, building an API that accepts bearer tokens, or connecting clients such as MCP servers or SPAs to an identity provider.
license: MIT
---

# OAuth 2 and OpenID Connect Review

## Goal
Confirm that the right flow is used, tokens are validated correctly and least privilege is enforced, following current best practice (OAuth 2.0 Security BCP, RFC 9700).

## Inputs
- Client types (web server, SPA, mobile, CLI, machine-to-machine), identity provider configuration, registered redirect URIs and scopes.
- Code that starts the flow, handles the callback, stores tokens and validates them in APIs.

## Procedure
1. **Flow choice.**
   | Client | Flow |
   |---|---|
   | server-side web app, SPA, mobile, CLI | Authorization Code + **PKCE (S256)** |
   | service to service | Client Credentials (or private-key JWT / mTLS client authentication) |
   | devices without a browser | Device Authorization Grant |
   Implicit flow and Resource Owner Password Credentials are findings.
2. **Authorization request.** `state` is unpredictable and verified; `nonce` is used for OIDC; PKCE verifier is high-entropy and per request.
3. **Redirect URIs.** Exact-match registration; no wildcards; no open redirects in the application after login.
4. **Token validation in APIs.** Signature using JWKS (cached, with key rotation), `iss`, `aud` (this API), `exp`/`nbf` with small clock skew, the allowed `alg` list (never `none`), then scopes or roles per endpoint. Opaque tokens use introspection.
5. **Token handling.** Access tokens are short-lived. Refresh tokens rotate and are bound or stored server-side; SPAs prefer a backend-for-frontend over storing tokens in `localStorage`. Tokens never appear in URLs or logs.
6. **Scopes and claims.** Minimal scopes; authorization decisions use verified claims, never unverified ID token contents sent by the client; an ID token is not used as an API access token.
7. **Sessions and logout.** Session cookies `HttpOnly`, `Secure`, `SameSite`; session fixation prevented on login; logout clears the local session and, where required, uses RP-initiated or back-channel logout.
8. **Client secrets.** Confidential clients only; stored in a secret manager; rotated; public clients have no secret.

## Example fixture
```python
claims = jwt.decode(token, options={"verify_signature": False})  # finding: no signature check
if claims.get("role") == "admin":                                 # finding: trusts unverified claim
    ...
```

## Acceptance checks
- Every client is mapped to a recommended flow, or the deviation is justified.
- API token validation covers signature, issuer, audience, expiry and algorithm; negative tests exist for an expired token, a wrong audience and a wrong signature.
- No tokens or secrets appear in logs, URLs or front-end storage contrary to the design.

## Output
Findings with flow diagrams where useful, configuration fixes, and negative test cases.

## Safety
Use test tenants and test accounts. Do not attempt token theft or replay against production identity providers without authorization.
