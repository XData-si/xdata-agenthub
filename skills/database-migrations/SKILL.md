---
name: database-migrations
description: Plan and review schema and data migrations that deploy without downtime or data loss, using expand-contract, batching and tested rollback. Use when adding, renaming or removing columns, tables, indexes or constraints, or backfilling data.
license: MIT
---

# Zero-Downtime Database Migrations

## Goal
Change the schema while old and new application versions run side by side, with a verified way back.

## Inputs
- Migration files and the ORM or migration tool in use.
- Table sizes and row counts, write rate, replication setup, database engine and version.
- Deployment model: rolling, blue-green, or a single instance with a restart.

## Procedure
1. **Classify each change.**
   | Change | Risk |
   |---|---|
   | add nullable column, new table | low |
   | add index on a large table | locks writes unless built concurrently/online |
   | add NOT NULL, foreign key, check constraint | full-table validation, may lock |
   | rename or drop column or table | breaks running code |
   | change type | table rewrite on many engines |
2. **Apply expand–contract.** *Expand:* add the new structure alongside the old. *Migrate:* deploy code that writes both and reads new with fallback; backfill. *Contract:* after every instance runs the new code, remove the old structure in a later release.
3. **Use online operations.** PostgreSQL: `CREATE INDEX CONCURRENTLY`, `ADD CONSTRAINT … NOT VALID` followed by `VALIDATE CONSTRAINT`, set `lock_timeout` so a migration fails fast instead of queueing behind long transactions. MySQL: online DDL or a tool such as gh-ost or pt-online-schema-change.
4. **Backfill in batches.** Batches by primary-key range (for example 1–10k rows), commit per batch, throttle, make it resumable and idempotent, and monitor replication lag.
5. **Plan rollback.** For each step write the down-path. Irreversible steps (drops, lossy type changes) need a backup or an export of the affected data, verified restorable.
6. **Rehearse** on a production-sized copy: measure duration and locks, and check the query plans of critical queries.
7. **Release and observe.** Error rate, latency, locks and replication lag during and after; proceed to contract only after a stable period.

## Example fixture
```sql
-- Rename users.fullname -> users.display_name without downtime
ALTER TABLE users ADD COLUMN display_name text;            -- release 1 (expand)
-- app writes both, reads display_name with fallback to fullname
UPDATE users SET display_name = fullname
 WHERE id BETWEEN $1 AND $2 AND display_name IS NULL;      -- batched backfill
-- release 2: app reads/writes display_name only
ALTER TABLE users DROP COLUMN fullname;                    -- release 3 (contract)
```

## Common rationalizations
| Rationalization | Reality |
|---|---|
| The table is small, locking is fine. | Tables grow, and even a small table blocks every query queued behind a long transaction. Set lock_timeout and measure. |
| We'll roll back if it breaks. | Many schema changes (drops, lossy type changes) cannot be rolled back without a backup. Plan the down-path first. |
| We can rename the column in one release. | Running instances of the old version will fail. Use expand–contract across releases. |

## Acceptance checks
- No step breaks the currently deployed application version.
- Long-locking statements are replaced by online variants or scheduled with explicit approval.
- Backfill is idempotent and resumable; batch size and duration were measured.
- Rollback is documented per step; irreversible steps have a verified backup.

## Output
Ordered migration plan across releases, scripts, rehearsal measurements and a rollback plan.

## Safety
Never run migrations against production without approval and a fresh backup. Do not drop data "because it seems unused" without evidence of no reads.
