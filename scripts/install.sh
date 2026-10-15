#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${XAH_HOME:-$HOME/.local/share/xdata-agenthub}"
BIN="${XAH_BIN:-$HOME/.local/bin}"
command -v python3 >/dev/null || { echo "Python 3 is required" >&2; exit 1; }
mkdir -p "$PREFIX" "$BIN"
for name in cli registry skills agents instructions workflows; do
  if [ -d "$ROOT/$name" ]; then
    rm -rf "$PREFIX/$name.tmp"
    cp -R "$ROOT/$name" "$PREFIX/$name.tmp"
    if [ -e "$PREFIX/$name" ]; then mv "$PREFIX/$name" "$PREFIX/$name.previous"; fi
    mv "$PREFIX/$name.tmp" "$PREFIX/$name"
  fi
done
cat > "$BIN/xah" <<EOF
#!/usr/bin/env bash
exec python3 "$PREFIX/cli/xah.py" "\$@"
EOF
chmod 755 "$BIN/xah"
echo "Installed xah to $BIN/xah"
echo "Add $BIN to PATH if needed."
