# Install one skill for Claude Code with the dependency-free CLI and verify it against the catalog digests.
Output demos/recordings/out/install.mp4
Output demos/recordings/out/install.gif
Source demos/recordings/settings.tape

Hide
Type "cd $(mktemp -d) && export PS1='$ ' && clear" Enter
Show
Type "git clone -q https://github.com/XData-si/xdata-agenthub" Enter
Sleep 4s
Type "alias xah='python3 xdata-agenthub/cli/xah.py'" Enter
Type "xah search migration" Enter
Sleep 2s
Type "mkdir my-app && xah add database-migrations --agent claude --target my-app" Enter
Sleep 2s
Type "ls my-app/.claude/skills" Enter
Sleep 1s
Type "xah verify --target my-app" Enter
Sleep 4s
