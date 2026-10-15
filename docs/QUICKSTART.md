# Five-minute quickstart

Requirements: Python 3.10+ and Bash for the optional installer.

```bash
git clone https://github.com/XData-si/xdata-agenthub.git
cd xdata-agenthub
python3 -m unittest discover -s tests -v
python3 cli/xah.py list
python3 cli/xah.py doctor
mkdir -p /tmp/agenthub-demo
python3 cli/xah.py init --target /tmp/agenthub-demo --profile developer
python3 cli/xah.py audit --target /tmp/agenthub-demo
```

`init` copies a curated set of local templates. It does not download or execute third-party code. Existing files are never overwritten. For optional CLI installation run `bash scripts/install.sh` and then `~/.local/bin/xah --help`.

For security and compatibility limits, see [SECURITY.md](../SECURITY.md) and [ROADMAP.md](../ROADMAP.md).
