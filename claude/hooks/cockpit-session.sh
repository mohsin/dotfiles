#!/usr/bin/env bash

# Claude Code SessionStart hook: inside a cockpit, write the session the Claude pane is on to
# the file the `cockpit` shell function resumes from next time. It runs on start, /resume and
# /clear, so the file follows the conversation that is actually open. Outside a cockpit
# (COCKPIT_SESSION_FILE unset) it does nothing.

[ -n "${COCKPIT_SESSION_FILE:-}" ] || exit 0

# A claude started from inside the cockpit's Claude (a Bash tool running `claude -p`) inherits
# the variable too; only the outermost claude may write, so count claude processes above us
pid=$PPID claudes=0
while [ "${pid:-1}" -gt 1 ]; do
	read -r ppid comm <<< "$(ps -o ppid=,comm= -p "$pid" 2> /dev/null)"
	[ "${comm##*/}" = claude ] && claudes=$((claudes + 1))
	pid=$ppid
done
[ "$claudes" -le 1 ] || exit 0

id=$(jq -r '.session_id // empty')
[ -n "$id" ] || exit 0
mkdir -p "$(dirname "$COCKPIT_SESSION_FILE")"
printf '%s\n' "$id" > "$COCKPIT_SESSION_FILE"
exit 0
