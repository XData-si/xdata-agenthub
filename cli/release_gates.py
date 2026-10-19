"""Offline release gate evaluation with explicit evidence references.

This evaluates submitted evidence; it does not authenticate CI providers.
No release, tag, or publication is performed.
"""
REQUIRED = ("unit_tests", "integration_tests", "security_review",
            "operator_walkthrough", "documentation", "ci_matrix")


def evaluate(evidence):
    if not isinstance(evidence, dict):
        raise ValueError("Release evidence must be an object")
    gates = {}
    for name in REQUIRED:
        value = evidence.get(name)
        if not isinstance(value, dict):
            gates[name] = {"passed": False, "status": "missing" if value is None else "invalid"}
            continue
        passed = (value.get("passed") is True
                  and isinstance(value.get("reference"), str)
                  and bool(value["reference"].strip())
                  and isinstance(value.get("reviewer"), str)
                  and bool(value["reviewer"].strip()))
        gates[name] = {"passed": passed, "status": "pass" if passed else "invalid"}
    return {"ready": all(gate["passed"] for gate in gates.values()), "gates": gates}
