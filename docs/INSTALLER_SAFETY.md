# Installer safety and recovery

The installer is intended for local user accounts on Linux/macOS with Bash and Python 3.10+. It is not a package manager and does not require sudo.

## Installation
```bash
bash scripts/install.sh
~/.local/bin/xah doctor
```

Optional environment variables: `XAH_HOME` for data (default `~/.local/share/xdata-agenthub`) and `XAH_BIN` for the launcher (default `~/.local/bin`).

## Upgrades
Each installation creates a uniquely named `.xah-backup.*` directory under `XAH_HOME`. Previous component directories are moved there before new components are installed. The installer refuses to overwrite an unmanaged `xah` launcher.

Backups consume disk space; review them manually after verifying a successful upgrade. Do not delete backups until you are satisfied that the current installation works.

## Recovery
1. Inspect the printed backup path.
2. Stop running `xah` commands.
3. Move the current component directories aside.
4. Restore component directories from the chosen backup.
5. Run `~/.local/bin/xah doctor`.

Do not perform recovery by copying an entire backup folder over your home directory.

## Known limitations
- This is not a fully atomic multi-directory upgrade. An interruption between directory moves may leave a partial installation; restore from backup.
- The managed-launcher marker is not a cryptographic ownership check.
- The script assumes the chosen installation directories are controlled by the current user and are not concurrently modified by an attacker.
- Windows native shells are not yet supported; use WSL for evaluation.
- Runtime agent compatibility still needs independent verification.

## Release gate
Before recommending public installation, run `python3 -m unittest discover -s tests -v`, repeat installation in disposable directories, inspect symlink edge cases, and test Linux and macOS.
