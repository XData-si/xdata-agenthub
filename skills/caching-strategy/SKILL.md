---
name: caching-strategy
description: Design and review caching (Redis, Memcached, CDN, HTTP and in-process caches) — what to cache, keys and invalidation, TTLs, stampede protection, per-user data isolation and failure behaviour. Use when adding a cache to fix latency or load, or when stale data, cache stampedes or data leaks between users appear.
license: MIT
---

# Caching Strategy

## Goal
A cache that measurably reduces latency or load, never serves one user's data to another, and degrades gracefully when it fails.

## Inputs
- Latency and load measurements, read/write ratio, data freshness requirements, data sensitivity, cache technology and topology.

## Procedure
1. **Justify**: measure the expensive operation and its hit pattern first; caching hides problems that indexes or query fixes would solve better.
2. **Choose the layer**: HTTP caching (`Cache-Control`, `ETag`) and CDN for public content; shared cache (Redis) for computed results shared across instances; in-process cache for small, hot, immutable data.
3. **Keys**: include every input that changes the result — tenant, user or permission scope, locale, version. Missing a dimension is a data leak.
4. **Freshness**: TTLs based on how stale data may be; explicit invalidation on writes (delete-on-write, versioned keys); document the consistency guarantee you accept.
5. **Stampede protection**: request coalescing or locks for recomputation, TTL jitter, stale-while-revalidate for expensive keys.
6. **Sizing and eviction**: memory limits and eviction policy (for example `allkeys-lru`) chosen deliberately; monitor hit ratio, evictions and memory.
7. **Failure behaviour**: timeouts on cache calls; on cache failure fall back to the source with protection (rate limits) rather than failing requests; avoid making the cache a hidden single point of failure.
8. **Security**: authentication and TLS for networked caches; no public exposure; sensitive values encrypted or not cached; `Cache-Control: private, no-store` for personal responses at the HTTP layer.

## Example fixture
```text
GET /api/me/dashboard cached in CDN for 60 s with key = URL path only.
```
Expected findings: personal dashboard cached under a shared key — users see each other's data; must be `private`/`no-store` or keyed by user at the application cache.

## Acceptance checks
- Hit ratio and latency measured before and after, with the same workload.
- Negative case: two users requesting the same personalised endpoint receive their own data (test through the full cache path).
- Cache outage test: the service stays available within agreed degraded latency.

## Output
Cache design (layer, keys, TTL, invalidation), measurements, configuration and tests.

## Safety
Flushing production caches can overload the database; schedule with approval and monitoring. Never expose cache ports publicly.
