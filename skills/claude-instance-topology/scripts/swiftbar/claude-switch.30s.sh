#!/bin/bash
# <xbar.title>Claude account switch</xbar.title>
# <xbar.desc>Shows the active Claude account and switches it with claude-switch.</xbar.desc>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
#
# Set CLAUDE_SWITCH to the claude-switch.py path if it is not on the PATH.

SWITCH="${CLAUDE_SWITCH:-$(command -v claude-switch || command -v claude-switch.py)}"
if [ -z "$SWITCH" ]; then
  echo "Claude ?"; echo "---"; echo "claude-switch not found; set CLAUDE_SWITCH in this plugin"
  exit 0
fi

STATUS=$("$SWITCH" status --json 2>&1) || { echo "Claude !"; echo "---"; echo "$STATUS" | head -3; exit 0; }

/usr/bin/python3 - "$SWITCH" "$STATUS" <<'PY'
import json, sys
switch, status = sys.argv[1], json.loads(sys.argv[2])
active = status["desktop"] or status["cli"] or "?"
print(f"Claude: {active}")
print("---")
for name in status["accounts"]:
    mark = "✓ " if name == active else "   "
    print(f'{mark}{name} | bash="{switch}" param1=use param2={name} terminal=false refresh=true')
print("---")
print(f'Terminal on {active} | bash="{switch}" param1=exec param2=-- param3=claude terminal=true')
print("Desktop running" if status["running"] else "Desktop closed")
PY
