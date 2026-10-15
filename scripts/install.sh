#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${XAH_HOME:-$HOME/.local/share/xdata-agenthub}"
BIN="${XAH_BIN:-$HOME/.local/bin}"
command -v python3 >/dev/null || { echo "Python 3 is required" >&2; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
# Refuse symlinked install roots; never delete an existing backup.
for path in "$PREFIX" "$BIN"; do
  if [ -L "$path" ]; then echo "Refusing symlinked installation directory: $path" >&2; exit 1; fi
done
mkdir -p "$PREFIX" "$BIN"
for path in "$PREFIX" "$BIN"; do
  if [ ! -d "$path" ]; then echo "Not a directory: $path" >&2; exit 1; fi
done
if [ -e "$BIN/xah" ] || [ -L "$BIN/xah" ]; then
  if [ -L "$BIN/xah" ] || ! grep -q 'XData AgentHub managed launcher' "$BIN/xah" 2>/dev/null; then
    echo "Refusing to overwrite an unmanaged launcher: $BIN/xah" >&2; exit 1
  fi
fi
# Stage a full copy in a unique temporary directory, then swap it into place.
STAGE="$(mktemp -d "$PREFIX/.xah-stage.XXXXXXXX")"
BACKUP=""
cleanup() { if [ -d "$STAGE" ]; then rm -rf -- "$STAGE"; fi; }
trap cleanup EXIT
for name in cli registry skills agents instructions workflows; do
  [ ! -d "$ROOT/$name" ] || cp -R "$ROOT/$name" "$STAGE/$name"
done
python3 "$STAGE/cli/xah.py" doctor
for name in cli registry skills agents instructions workflows; do
  if [ -L "$PREFIX/$name" ]; then
    echo "Refusing symlinked existing component: $PREFIX/$name" >&2; exit 1
  fi
done
# Unique backup folder preserves the previous installation across repeated upgrades.
BACKUP="$(mktemp -d "$PREFIX/.xah-backup.XXXXXXXX")"
for name in cli registry skills agents instructions workflows; do
  if [ -e "$PREFIX/$name" ]; then mv "$PREFIX/$name" "$BACKUP/$name"; fi
  if [ -d "$STAGE/$name" ]; then mv "$STAGE/$name" "$PREFIX/$name"; fi
done
LAUNCHER="$(mktemp "$BIN/.xah-launcher.XXXXXXXX")"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# XData AgentHub managed launcher
exec python3 "$PREFIX/cli/xah.py" "\$@"
EOF
chmod 755 "$LAUNCHER"
mv -f -- "$LAUNCHER" "$BIN/xah"
echo "Installed xah to $BIN/xah"
echo "Previous version backup: $BACKUP"
echo "Add $BIN to PATH if needed."
