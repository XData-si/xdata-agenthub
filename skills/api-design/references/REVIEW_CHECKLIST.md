# API review checklist

Use alongside [API Design](../SKILL.md). Record endpoint, evidence and status for each question.

| Area | Verification |
|---|---|
| Identity | Is caller identity established server-side? |
| Authorization | Is resource ownership or tenant scope enforced on each request? |
| Validation | Are malformed inputs and unknown fields handled consistently? |
| Idempotency | Are retries of mutating operations safe? |
| Pagination | Is ordering stable and page size bounded? |
| Compatibility | Are breaking changes documented and versioned? |
| Operations | Are errors traceable without leaking secrets? |

## Example negative test
Given two isolated tenants, create a resource as tenant A, then request it using tenant B's credentials. Expect an authorization failure without disclosing the resource's existence or data. Run only in an authorized test environment.
