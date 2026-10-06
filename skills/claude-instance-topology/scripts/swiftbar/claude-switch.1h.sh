#!/bin/bash
# <xbar.title>Claude account switch</xbar.title>
# <xbar.desc>Shows the active Claude account and switches it with claude-switch.</xbar.desc>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.refreshOnOpen>true</swiftbar.refreshOnOpen>
#
# Set CLAUDE_SWITCH to the claude-switch.py path if it is not on the PATH.

SWITCH="${CLAUDE_SWITCH:-$(command -v claude-switch || command -v claude-switch.py)}"
if [ -z "$SWITCH" ]; then
  echo "Claude ?"; echo "---"; echo "claude-switch not found; set CLAUDE_SWITCH in this plugin"
  exit 0
fi

"$SWITCH" sync-launchd >/dev/null 2>&1  # restores the Dock's account after a login
STATUS=$("$SWITCH" status --json 2>&1) || { echo "Claude !"; echo "---"; echo "$STATUS" | head -3; exit 0; }

/usr/bin/python3 - "$SWITCH" "$STATUS" <<'PY'
import json, sys
switch, status = sys.argv[1], json.loads(sys.argv[2])
labels = status.get("labels", {})
active = status["desktop"] or status["cli"]
title = labels.get(active, active or "?").replace("|", "/")
print(f"Claude: {title}")
print("---")
for name in status["accounts"]:
    mark = "✓ " if name == active else "   "
    label = labels.get(name, name).replace("|", "/")
    print(f'{mark}{label} | bash="{switch}" param1=use param2={name} terminal=false refresh=true')
print("---")
print(f'Terminal on {title} | bash="{switch}" param1=exec param2=-- param3=claude terminal=true')
print("Desktop running" if status["running"] else "Desktop closed")
PY
