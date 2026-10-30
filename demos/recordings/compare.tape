# Replays recorded answers from demos/results/2026-10-29 (no live model call): same model and prompt, without and
# with the skill. Every line shown is a grep over the published answers.
Output demos/recordings/out/compare.mp4
Output demos/recordings/out/compare.gif
Source demos/recordings/settings.tape
Set FontSize 24

Hide
Type "cd demos/results/2026-10-29/answers && export PS1='$ ' && clear" Enter
Show
Type "# Shell review. Does the answer say that ShellCheck was not run?" Enter
Type "grep -i -c -E 'not run.*shellcheck|run it or shellcheck' shell-*.txt" Enter
Sleep 4s
Type "grep -h -i -m1 'shellcheck' shell-skill-1.txt" Enter
Sleep 4s
Type "# Code review. Is there a residual-risk section?" Enter
Type "grep -i -c 'residual risk' review-*.txt" Enter
Sleep 4s
Type "# Production migration. Is approval required before the change?" Enter
Type "grep -h -i -m1 'approval' migration-baseline-*.txt || echo '(baseline: no approval step)'" Enter
Sleep 3s
Type "grep -h -i -m1 'approval' migration-skill-2.txt" Enter
Sleep 4s
Type "clear && sed -n '67,76p' ../RESULTS.md" Enter
Sleep 7s
