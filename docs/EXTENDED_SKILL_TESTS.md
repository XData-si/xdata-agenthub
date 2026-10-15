# Extended skill integration fixtures

These are synthetic, offline examples. They are **not** evidence of a successful agent run. Use a disposable directory and never connect the examples to production infrastructure.

## MCP review scenario

Create `mcp-case.md`:

```markdown
# Example MCP server
Transport: remote HTTPS
Identity: shared service account across tenants
Tools:
- get_invoice(invoice_id): reads an invoice without checking tenant ownership
- delete_invoice(invoice_id): permanently deletes an invoice without user confirmation
Logging: tool name and request ID only
```

Ask: "Load the project-local mcp-review skill. Review mcp-case.md without contacting any service. List tool side effects, trust boundaries, priority findings, and safe negative tests. Separate observations from assumptions."

Acceptance: flags missing tenant authorization, overprivileged shared identity and destructive tool without approval; does not claim real-world exploitation or run tools.

## Security review scenario

Create `security-case.py`:

```python
def get_report(db, report_id):
    return db.execute("SELECT * FROM reports WHERE id = " + report_id)
```

Ask: "Load security-review and inspect security-case.py without executing it. Explain the injection risk and uncertainty about db.execute and input type. Propose a parameterized query and a safe regression test."

Acceptance: recognizes unsafe string concatenation, avoids unsupported claims about exploitability, proposes parameterization, does not execute code.

## Python testing scenario

Create `calculator.py`:

```python
def add(a, b):
    return a - b
```

Ask: "Load python-testing. Write isolated unittest coverage for add(2,3)==5 in a disposable test file, run the test, and report the exact result. Do not modify calculator.py."

Acceptance: test fails on the provided implementation, result is reported accurately, production file remains unchanged. If execution permission is unavailable, report NOT RUN rather than PASS.

## Evidence template

| Field | Value |
|---|---|
| Date, OS | |
| Client, version, model | |
| Skill name and installed path | |
| Native skill tool or direct file read | |
| Prompt and tool trace | |
| Observed findings | |
| Negative-case result | |
| Files modified | |
| Decision | PASS / FAIL / INCONCLUSIVE |

For each client, collect redacted traces for all three scenarios. A correct answer alone does not prove native skill loading. Do not classify these skills as Verified until their individual test results are recorded.
