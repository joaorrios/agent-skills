#!/bin/sh
# SessionStart hook for Claude Code and Codex: reinjects the coordinator
# protocol and state, but only into the session registered in the state.
# Usage: resume.sh [state-file]   (reads the hook's JSON payload on stdin)

skill_dir=$(cd "$(dirname "$0")/.." && pwd)
protocol="$skill_dir/SKILL.md"

input=$(cat)
# First string value of a top-level field; avoids depending on jq.
field() {
  printf '%s' "$input" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -n 1
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
grep -q "^- Coordinator session: \`$sid\`" "$state" 2>/dev/null || exit 0

protocol_txt=$(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$protocol" | sed "s/\${CLAUDE_SESSION_ID}/$sid/")
state_txt=$(cat "$state")

echo "This session is the project coordinator (SessionStart: ${source:-unknown})."
echo "Before answering, follow \"Take over or resume\" in the protocol: reconcile the state with reality."
echo "Skill folder, for the protocol's relative links: $skill_dir"
echo
printf '%s\n\n' "$state_txt"
# Claude Code cuts hook output past ~10k characters down to a 2KB preview,
# so the protocol is inlined only while everything fits; the state goes
# first either way.
if [ "$(printf '%s%s' "$protocol_txt" "$state_txt" | wc -m)" -gt 9500 ]; then
  echo "Protocol too large to inject alongside the state: read $protocol now."
else
  printf '%s\n' "$protocol_txt"
fi
exit 0
