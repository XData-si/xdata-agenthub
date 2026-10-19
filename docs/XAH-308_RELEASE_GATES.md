# XAH-308 release readiness

`xah release-check --evidence evidence.json --json` is a **local evidence checklist**,
not an attestation service. It does not query GitHub, verify signatures, or
authenticate reviewers. A zero exit status means only that every declared
gate contains `passed: true`, a nonblank `reference`, and a nonblank
`reviewer`. An untrusted evidence file can still lie.

Example input (illustrative references, **not actual release approval**):

```json
{
  "unit_tests": {"passed": true, "reference": "https://example.org/ci/123", "reviewer": "release-owner"},
  "integration_tests": {"passed": true, "reference": "https://example.org/ci/123", "reviewer": "release-owner"},
  "security_review": {"passed": true, "reference": "https://example.org/review/1", "reviewer": "security-owner"},
  "operator_walkthrough": {"passed": true, "reference": "https://example.org/demo/1", "reviewer": "operator"},
  "documentation": {"passed": true, "reference": "https://example.org/docs/1", "reviewer": "release-owner"},
  "ci_matrix": {"passed": true, "reference": "https://example.org/ci/123", "reviewer": "release-owner"}
}
```

Before RC1: independently inspect references, confirm branch/head SHA, verify
CI across the supported matrix, complete recovery security review, run
adapter-native acceptance, check documentation and migrations, and obtain
explicit release-owner approval. **Do not publish or tag automatically.**
