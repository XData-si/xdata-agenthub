---
name: gdpr-dsar-handling
description: Handle GDPR data subject requests end to end — access, rectification, erasure, restriction, portability and objection — with identity verification, data discovery across systems, deadlines, exemptions and evidence. Use when building a request process, automating erasure or export across services, or answering a specific request. Not legal advice.
license: MIT
---

# GDPR Data Subject Request Handling

## Goal
Answer every request completely, on time and safely: the right person gets the right data, deletions propagate everywhere they must, and decisions are documented.

## Inputs
- Records of processing activities, system and data inventory (databases, SaaS tools, backups, logs, analytics, email), identity data available for verification, data protection officer contact, retention obligations.

## Procedure
1. **Intake**: one documented channel; log the request with date of receipt — the default deadline is **one month**, extendable by two further months for complex or numerous requests with notice to the person within the first month.
2. **Verify identity** proportionately (for example via an existing logged-in account or matching known data); do not collect more data than needed to verify; never disclose data to an unverified requester.
3. **Classify the right**: access (Art. 15), rectification (16), erasure (17), restriction (18), portability (20), objection (21). Clarify scope with the person if unclear.
4. **Discover data** across all systems from the inventory, including processors' systems; search by every identifier (email, user ID, customer number, phone).
5. **Apply exemptions and limits**: legal retention (for example accounting records), rights of others in the data (redact third parties), legal claims; document the reasoning.
6. **Approve before acting**: the data protection officer or a designated operator approves the plan (systems, data, actions) before any erasure or disclosure; erasure is irreversible and a fraudulent request can cause harm.
7. **Execute**:
   - access/portability: complete, structured export (machine-readable for portability) plus the information required by Art. 15 (purposes, recipients, retention, source, rights);
   - erasure: delete or anonymise in live systems, propagate to processors and derived data (search indexes, caches, analytics); for trained models and ML features decide per system with legal and technical input whether removal or retraining is required; backups expire through their retention instead of selective deletion, with restore procedures that re-apply deletions.
8. **Respond** in clear language through a secure channel to the verified recipient, after confirming the destination; explain any refusal and the right to complain to the supervisory authority.
9. **Evidence**: keep a minimal record of the request, actions and response date (without re-collecting the erased data).

## Example fixture
```text
Erasure request from customer 4711. Systems: CRM (delete), billing (retain invoices 10 years — restrict instead), newsletter SaaS (delete via API), search index (reindex), analytics (pseudonymous IDs — delete mapping), backups (expire in 35 days; deletion log re-applied on restore).
```

## Acceptance checks
- Every system in the inventory was checked, with result per system recorded.
- The response date is within the deadline, or an extension notice was sent in time.
- Negative case: a test request from an unverified email address does not receive personal data.

## Output
Request record, per-system actions, response letter or export package, process improvements.

## Safety
Exports contain personal data: deliver them securely and delete working copies. This is not legal advice; involve the data protection officer for refusals, exemptions and unusual requests. Agents may prepare discovery results and draft responses, but never execute erasure or send personal data without the recorded approval in step 6.
