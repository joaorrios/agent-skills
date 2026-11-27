#!/bin/sh
# SessionStart hook for Claude Code and Codex: reinjects the coordinator
# protocol and state, but only into the session registered in the state.
# Usage: resume.sh [state-file]   (reads the hook's JSON payload on stdin)

skill_dir=$(cd "$(dirname "$0")/.." && pwd)
protocol="$skill_dir/SKILL.md"

input=$(cat)
# A top-level string field: jq when present, else a sed fallback that
# takes the first field with that name, up to its first quote.
field() {
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r --arg k "$1" '.[$k] // empty' 2>/dev/null
  else
    printf '%s' "$input" | tr ',{}' '\n\n\n' | sed -n "s/^[[:space:]]*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -n 1
  fi
}
sid=$(field session_id)
source=$(field source)
[ -n "$sid" ] || exit 0

state=$1
if [ -z "$state" ]; then
  dir=${CLAUDE_PROJECT_DIR:-$(field cwd)}
  root=$(git -C "${dir:-$PWD}" rev-parse --show-toplevel 2>/dev/null) || exit 0
  state="$root/.agents/coordinator/state.md"
fi
awk -v s="- Coordinator session: \`$sid\`" 'index($0, s) == 1 { f = 1 } END { exit !f }' "$state" 2>/dev/null || exit 0

# Escape the id for the sed replacement below (\, & and the / delimiter).
sid_sed=$(printf '%s' "$sid" | sed 's/[\\&/]/\\&/g')
protocol_txt=$(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$protocol" | sed "s/\${CLAUDE_SESSION_ID}/$sid_sed/")
state_txt=$(cat "$state")

echo "This session is the project coordinator (SessionStart: ${source:-unknown})."
# Claude Code cuts hook output past ~10k characters down to a 2KB preview,
# so a state over the budget is named, not printed.
if [ "$(printf '%s' "$state_txt" | wc -m)" -gt 9000 ]; then
  echo "State too large to inject: read $state and $protocol now, then follow \"Take over or resume\"."
  exit 0
fi
echo "Before answering, follow \"Take over or resume\" in the protocol: reconcile the state with reality."
echo "Skill folder, for the protocol's relative links: $skill_dir"
echo
printf '%s\n\n' "$state_txt"
# The protocol is inlined only while everything fits; the state goes first.
if [ "$(printf '%s%s' "$protocol_txt" "$state_txt" | wc -m)" -gt 9500 ]; then
  echo "Protocol too large to inject alongside the state: read $protocol now."
else
  printf '%s\n' "$protocol_txt"
fi
exit 0
