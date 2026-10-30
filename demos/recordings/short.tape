# Vertical (9:16) cut for a YouTube Short: search, install, verify, measured results.
Output demos/recordings/out/short.mp4
Set Shell "bash"
Set FontSize 34
Set Width 1080
Set Height 1920
Set Padding 50
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Hide
Type "cd $(mktemp -d) && git clone -q https://github.com/XData-si/xdata-agenthub && alias xah='python3 xdata-agenthub/cli/xah.py' && export PS1='$ ' && clear" Enter
Sleep 4s
Show
Type "xah search security | head -8" Enter
Sleep 3s
Type "mkdir app && xah add threat-modeling --agent claude --target app" Enter
Sleep 2s
Type "xah verify --target app" Enter
Sleep 3s
Type "clear && sed -n '71,75p' xdata-agenthub/demos/results/2026-10-29/RESULTS.md | cut -d'|' -f2-" Enter
Sleep 6s
