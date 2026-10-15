"""Offline smoke gate for catalog, upgrade, rollback, and evidence validation."""
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "cli/xah.py"
sys.path.insert(0, str(ROOT / "cli"))
from compat_evidence import validate_evidence
from installed_manifest import load_manifest, _digest, save_manifest
from update_apply import apply_update


def cli(*args, expected=0):
    result = subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT,
                            capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError(f"xah {args}: expected {expected}, got {result.returncode}: {result.stdout} {result.stderr}")
    return result


def main():
    validate_evidence(json.loads((ROOT / "tests/fixtures/agent_compatibility_evidence.json").read_text(encoding="utf-8")))
    cli("doctor")
    with tempfile.TemporaryDirectory() as d:
        target = pathlib.Path(d)
        cli("add", "code-review", "--target", d)
        before = (target / ".xah-installed.json").read_bytes()
        cli("update", "code-review", "--target", d, "--dry-run")
        assert (target / ".xah-installed.json").read_bytes() == before
        tracked = target / "skills/code-review/SKILL.md"
        tracked.write_text("local edit", encoding="utf-8")
        cli("update", "code-review", "--target", d, "--dry-run", expected=2)
        cli("update", "code-review", "--target", d, "--apply", expected=1)
        assert tracked.read_text(encoding="utf-8") == "local edit"
    with tempfile.TemporaryDirectory() as d:
        target = pathlib.Path(d)
        dest = target / "tracked.txt"
        src = target / "new.txt"
        dest.write_bytes(b"old")
        src.write_bytes(b"new")
        save_manifest(target, {"schema_version": 1, "files": {
            "tracked.txt": {"sha256": _digest(dest), "item_id": "fixture"}}})
        original_manifest = (target / ".xah-installed.json").read_bytes()
        try:
            apply_update(target, "fixture", [(src, dest)], fail_after=1)
        except RuntimeError as exc:
            if "Injected update failure" not in str(exc):
                raise
        else:
            raise AssertionError("Failure injection did not fire")
        assert dest.read_bytes() == b"old"
        assert (target / ".xah-installed.json").read_bytes() == original_manifest
    print("Offline upgrade, rollback, schema and compatibility-evidence smoke gate passed")


if __name__ == "__main__":
    main()
