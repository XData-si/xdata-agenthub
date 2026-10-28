# STRIDE quick reference

| Category | Violated property | Typical questions | Typical mitigations |
|---|---|---|---|
| **S**poofing | Authentication | Can someone pretend to be a user, service or agent? Are tokens bound and short-lived? | strong authentication, mTLS between services, token audience checks |
| **T**ampering | Integrity | Can data in transit, at rest or in a queue be modified? Is client input trusted? | TLS, signatures or MACs, server-side validation, immutable logs |
| **R**epudiation | Non-repudiation | Can an actor deny an action? Are logs complete and tamper-evident? | audit logs with actor, time and request ID; append-only storage |
| **I**nformation disclosure | Confidentiality | Where can data leak: errors, logs, caches, model output, backups? | least privilege, encryption, redaction, output filtering |
| **D**enial of service | Availability | What exhausts CPU, memory, connections, quotas or money (LLM tokens)? | rate limits, quotas, timeouts, budgets, autoscaling limits |
| **E**levation of privilege | Authorization | Can a user or agent reach admin functions, other tenants' data or more powerful tools? | authorization checks per object, tenant isolation, scoped tool permissions, approval steps |

## Additional prompts for AI agents and tool integrations
- Can untrusted content (web pages, documents, tickets) reach the model as instructions?
- Which tools have side effects, and does any run without human approval?
- Can model output be rendered as HTML or Markdown that loads remote resources (exfiltration)?
- Are credentials available to the agent broader than the task requires?
