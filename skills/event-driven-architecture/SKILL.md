---
name: event-driven-architecture
description: Design and review event-driven systems and message queues (Kafka, RabbitMQ, SQS, NATS) — delivery guarantees, idempotent consumers, the transactional outbox, ordering, retries and dead-letter queues, schema evolution and replay. Use when introducing asynchronous messaging, debugging duplicate or lost messages, or reviewing consumers and producers.
license: MIT
---

# Event-Driven Architecture

## Goal
Messages are never silently lost, duplicates are harmless, ordering assumptions are explicit, and failures are visible and recoverable.

## Inputs
- Broker and client libraries, topics or queues, producers and consumers, message schemas, required ordering and latency, data retention.

## Procedure
1. **Classify each message**: event (fact that happened) or command (request to do something); owner of the schema; consumers.
2. **Delivery guarantees**: assume at-least-once delivery. Exactly-once exists only within narrow broker features; end-to-end effects must still be idempotent.
3. **Idempotent consumers**: deduplicate by message or business key (processed-ID table with unique constraint, or idempotent upserts); side effects (emails, payments) guarded by idempotency keys.
4. **Publish reliably**: the **transactional outbox** — write the state change and the outgoing event in the same database transaction, then relay; never "commit then publish" without recovery.
5. **Ordering**: only within a partition or message group; choose keys (for example the aggregate ID) to keep related events ordered; consumers tolerate out-of-order events across keys.
6. **Failures**: bounded retries with backoff; poison messages to a dead-letter queue with the original payload and error; alerting and a replay procedure.
7. **Schemas**: versioned (Avro, Protobuf or JSON Schema with a registry); backward-compatible changes only (add optional fields); consumers ignore unknown fields.
8. **Backpressure and capacity**: consumer lag monitoring, concurrency limits, retention long enough to recover from an outage.
9. **Data protection**: events with personal data have retention limits; avoid putting secrets or unnecessary personal data in events that are retained or replayed.

## Example fixture
```text
Order service: UPDATE orders SET status='paid'; COMMIT; then kafka.send("order-paid").
Consumer: on order-paid → send receipt email; ack after sending.
```
Expected findings: event lost if the process dies between commit and send (use outbox); duplicate delivery sends two emails (idempotency key); no DLQ for malformed events.

## Acceptance checks
- Each consumer has a documented idempotency mechanism and a test that delivers the same message twice.
- Negative case: killing the producer between state change and publish does not lose the event (outbox test).
- Lag and DLQ alerts exist, with a written replay procedure.

## Output
Message catalogue (owner, schema, key, guarantees), design changes, tests and runbook entries.

## Safety
Replaying or purging queues in production needs approval and a backup of affected messages. Do not consume production topics with test consumers that commit offsets.
