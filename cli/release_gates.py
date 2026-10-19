"""Offline pre-release gate evaluation from explicit evidence.

This does not publish releases, create tags, or claim external CI success.
"""
REQUIRED = ("unit_tests", "integration_tests", "security_review",
            "operator_walkthrough", "documentation", "ci_matrix")

def evaluate(evidence):
    if not isinstance(evidence, dict):
        raise ValueError("Release evidence must be an object")
    gates = {}
    for name in REQUIRED:
        value = evidence.get(name)
        gates[name] = {"passed": value is True, "status":
                       "pass" if value is True else "fail" if value is False else "missing"}
    return {"ready": all(gate["passed"] for gate in gates.values()), "gates": gates}
