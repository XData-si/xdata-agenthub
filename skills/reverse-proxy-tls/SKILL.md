---
name: reverse-proxy-tls
description: Review reverse proxy and TLS configuration (nginx, Caddy, Traefik, HAProxy, managed proxies) — certificates, protocols, headers, timeouts, forwarded headers and exposure of upstreams. Use when publishing a service on a domain, debugging 502/504 or certificate errors, or auditing edge security.
license: MIT
---

# Reverse Proxy and TLS Review

## Goal
Services are reachable only through the proxy, over modern TLS, with correct client information passed upstream and sensible limits.

## Inputs
- Proxy configuration, DNS records, certificate source (ACME, managed, internal CA), upstream addresses and ports.
- Whether a CDN or another proxy sits in front (affects client IP and TLS termination).

## Procedure
1. **Exposure.** Upstreams listen on private addresses or localhost only; direct access to upstream ports from the internet fails.
2. **Certificates.** Valid chain, correct names (SAN), automatic renewal tested, expiry monitored (alert at least 14 days before). For a DNS-only versus proxied CDN record, check which party presents the certificate.
3. **Protocols.** TLS 1.2 and 1.3 only; no SSLv3, TLS 1.0 or 1.1; server-preferred modern cipher suites; OCSP stapling where supported.
4. **HTTP to HTTPS** redirect; HSTS (`max-age` at least 6 months) once HTTPS works everywhere on the domain; `includeSubDomains`/`preload` only after checking every subdomain.
5. **Forwarded headers.** Set `X-Forwarded-For`, `X-Forwarded-Proto` and `Host` deliberately; the application trusts them **only** from the proxy's address; when chained behind a CDN, use the CDN's client-IP header with its IP ranges as trusted.
6. **Security headers** appropriate to the application: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `frame-ancestors` (or `X-Frame-Options`).
7. **Limits and timeouts.** Request body size, header size, upstream connect/read timeouts aligned with application timeouts, WebSocket upgrade settings where needed, rate limits on login and expensive endpoints.
8. **Admin surfaces.** Proxy dashboards and APIs are not public; protect with network restrictions plus authentication.
9. **Logging.** Access logs include the real client IP, status, upstream status and latency; no tokens in logged URLs.

## Troubleshooting map
| Symptom | Likely cause |
|---|---|
| 502 | upstream down, wrong port or protocol (HTTP vs HTTPS upstream), container not on the proxy network |
| 504 | upstream slower than the proxy read timeout |
| redirect loop | application thinks the request is HTTP (missing `X-Forwarded-Proto`) or CDN flexible SSL mode |
| certificate name mismatch | wrong server block or SNI, CDN certificate versus origin certificate |

## Example fixture
```bash
curl -sI https://app.example.com | grep -i -E 'strict-transport|content-security'
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null | openssl x509 -noout -dates -subject
nc -z -w 3 <public-ip> 8080 && echo "FINDING: upstream port publicly reachable"
```

## Acceptance checks
- External test shows TLS 1.0/1.1 rejected and a valid certificate with expiry monitoring.
- Upstream ports are not reachable from the internet (negative test).
- The application logs the real client IP, and spoofed `X-Forwarded-For` from a client is not trusted.

## Output
Findings, a configuration diff and verification commands with results.

## Safety
Test against your own domains. Reload configuration with a syntax check first (`nginx -t`, `caddy validate`) and keep the previous configuration for rollback.
