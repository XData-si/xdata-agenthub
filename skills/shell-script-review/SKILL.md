---
name: shell-script-review
description: Review and harden Bash/POSIX shell scripts for quoting, error handling, injection, portability and safe file operations. Use when writing or reviewing install scripts, CI steps, cron jobs or any script that runs with elevated privileges.
license: MIT
---

# Shell Script Review

## Goal
Scripts that fail loudly, handle unusual input safely and do not destroy data by accident.

## Inputs
- The script, its interpreter (`sh`, `bash`, version), where it runs (CI, cron, container, user machine) and with which privileges.
- Inputs: arguments, environment variables, files, network responses.

## Procedure
1. **Run ShellCheck** and treat warnings as findings unless justified inline.
2. **Shebang and mode.** Correct interpreter; for Bash use `set -euo pipefail` and understand its limits (`-e` is ignored inside conditions and some subshells).
3. **Quoting.** Every expansion quoted (`"$var"`, `"$@"`); arrays for argument lists; no unquoted `$(…)` in paths.
4. **Injection.** No `eval` on external input; no building commands by string concatenation; use `--` before untrusted filenames; validate input against an allowlist.
5. **Destructive operations.** Guard `rm -rf` with non-empty checks (`${dir:?}`), refuse `/` and `$HOME`, and prefer deleting a known temp directory created with `mktemp -d` plus `trap … EXIT` cleanup.
6. **Secrets.** Never pass secrets as command-line arguments (visible in `ps`); read them from stdin or files with `0600` permissions; disable `set -x` around them.
7. **Remote content.** Never pipe a download straight into a shell; download to a file, verify the checksum or signature, then execute.
8. **Portability.** If the shebang is `/bin/sh`, avoid bashisms (`[[ ]]`, arrays, `local` on some shells); watch GNU vs BSD differences (`sed -i`, `date`, `readlink -f`).
9. **Idempotency and exit codes.** Safe to re-run; meaningful exit status; errors go to stderr.

## Example fixture
```bash
#!/bin/sh
rm -rf $BUILD_DIR/*        # empty BUILD_DIR deletes from /
for f in `ls *.log`; do    # breaks on spaces, globbing
  eval "gzip $f"           # injection via filename
done
```
Expected findings: unguarded `rm -rf` with an unquoted variable, parsing `ls`, `eval` on a filename, missing error handling.

## Acceptance checks
- ShellCheck clean or every exception is justified.
- No unquoted expansions in commands touching files.
- Destructive commands are guarded; temporary files are cleaned up with `trap`.
- Secrets never appear in arguments or trace output.
- Tested with a filename containing spaces and with an empty variable (negative cases).

## Output
Findings by severity with line references, a patched script or diff, and the test commands used.

## Safety
Review destructive scripts in a disposable directory or container. Do not run unknown scripts with root privileges to "see what they do".
