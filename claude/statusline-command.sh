#!/bin/bash
# Claude Code status line, converted from the Solarized Dark zsh prompt
# defined in ~/.zsh_prompt (sourced by ~/.zshrc).
#
# Layout mirrors the original prompt: user at host in dir on branch [status]

input=$(cat)
cwd=$(printf '%s' "$input" | jq -r '.workspace.current_dir // .cwd // empty')
[ -n "$cwd" ] || cwd="$PWD"

# Abbreviate $HOME to ~, as the original prompt's %~ does.
display_dir="${cwd/#"$HOME"/\~}"

username=$(whoami)
hostname=$(hostname -s)

# Solarized 256-colour indexes used by the original prompt.
if [ "$(id -u)" = "0" ]; then
	user_color=124   # red for root
else
	user_color=166   # orange
fi
if [ -n "$SSH_TTY" ]; then
	host_color=124   # bold red over SSH
	host_bold=1
else
	host_color=136   # yellow
	host_bold=0
fi

# Git branch and dirty-state flags, mirroring prompt_git() in ~/.zsh_prompt.
git_segment=""
if git -C "$cwd" --no-optional-locks rev-parse --is-inside-work-tree >/dev/null 2>&1; then
	branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --quiet --short HEAD 2>/dev/null \
		|| git -C "$cwd" --no-optional-locks describe --all --exact-match HEAD 2>/dev/null \
		|| git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null \
		|| echo '(unknown)')

	flags=""
	git -C "$cwd" --no-optional-locks diff --quiet --ignore-submodules --cached 2>/dev/null || flags="${flags}+"
	git -C "$cwd" --no-optional-locks diff-files --quiet --ignore-submodules -- 2>/dev/null || flags="${flags}!"
	[ -n "$(git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard --directory 2>/dev/null | head -n 1)" ] && flags="${flags}?"
	git -C "$cwd" --no-optional-locks rev-parse --verify refs/stash >/dev/null 2>&1 && flags="${flags}\$"
	[ -n "$flags" ] && flags=" [${flags}]"

	git_segment=$(printf ' \033[38;5;15mon \033[38;5;61m%s\033[38;5;33m%s\033[0m' "$branch" "$flags")
fi

if [ "$host_bold" = "1" ]; then
	host_segment=$(printf '\033[1;38;5;%sm%s\033[0m' "$host_color" "$hostname")
else
	host_segment=$(printf '\033[38;5;%sm%s\033[0m' "$host_color" "$hostname")
fi

printf '\033[38;5;%sm%s\033[38;5;15m at %s\033[38;5;15m in \033[38;5;64m%s\033[0m%s\n' \
	"$user_color" "$username" "$host_segment" "$display_dir" "$git_segment"
