#!/usr/bin/env bash

# Install the dotfiles by symlinking them into $HOME, so that editing ~/.zshrc edits this
# repository and nothing can drift. Anything already in the way is moved to
# ~/.dotfiles-backup/<timestamp>/ first. Safe to re-run at any time.
#
# Usage: ./bootstrap.sh [-f|--force] [-n|--dry-run]
#   -f  skip the confirmation prompt
#   -n  print what would change without touching anything

set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP="$HOME/.dotfiles-backup/$(date +%Y%m%d-%H%M%S)"
DRY_RUN=0
FORCE=0

for arg in "$@"; do
	case "$arg" in
		-f|--force) FORCE=1 ;;
		-n|--dry-run) DRY_RUN=1 ;;
		*) echo "Unknown option: $arg" >&2; exit 1 ;;
	esac
done

# Top-level entries that stay in the repository instead of being linked into $HOME:
# repo metadata, scripts you run from here, and directories that get special handling below.
SKIP=(.git .gitignore .DS_Store .editorconfig .macos .osx .claude .config .vim)

# Execute a command, or do nothing on a dry run (the callers already describe each change).
run() {
	(( DRY_RUN )) || "$@"
}

# Move whatever is at $1 out of the way. Stale symlinks are simply removed; real files and
# directories are moved into the backup directory, keeping their path relative to $HOME.
backup() {
	local target="$1"
	if [ -L "$target" ]; then
		run rm "$target"
	elif [ -e "$target" ]; then
		local dest="$BACKUP/${target#$HOME/}"
		echo "  backup: $target -> $dest"
		run mkdir -p "$(dirname "$dest")"
		run mv "$target" "$dest"
	fi
}

# Symlink $1 (in the repo) to $2 (in $HOME), unless that link already exists.
link() {
	local src="$1" dst="$2"
	if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
		return
	fi
	backup "$dst"
	echo "  link:   $dst -> $src"
	run mkdir -p "$(dirname "$dst")"
	run ln -s "$src" "$dst"
}

if (( ! FORCE && ! DRY_RUN )); then
	read -r -p "This replaces dotfiles in $HOME with symlinks into $DOTFILES (originals are backed up). Continue? (y/n) " -n 1
	echo
	[[ $REPLY =~ ^[Yy]$ ]] || exit 0
fi

if (( ! DRY_RUN )); then
	echo "Updating the repository"
	git -C "$DOTFILES" pull --ff-only origin main || echo "  (could not fast-forward; continuing with the local checkout)"
fi

echo "Linking dotfiles from $DOTFILES into $HOME"

# 1. Every top-level dotfile
for src in "$DOTFILES"/.*; do
	name="$(basename "$src")"
	[ "$name" = "." ] || [ "$name" = ".." ] && continue
	[[ " ${SKIP[*]} " == *" $name "* ]] && continue
	link "$src" "$HOME/$name"
done

# 2. ~/bin: one link per script, so personal scripts kept alongside them survive
for src in "$DOTFILES"/bin/*; do
	link "$src" "$HOME/bin/$(basename "$src")"
done

# 3. Vim: colours and syntax come from the repo; backups, swaps and undo history stay local
for dir in colors syntax; do
	link "$DOTFILES/.vim/$dir" "$HOME/.vim/$dir"
done
run mkdir -p "$HOME/.vim/backups" "$HOME/.vim/swaps" "$HOME/.vim/undo"

# 4. ~/.config/<app>: one link per application directory
if [ -d "$DOTFILES/.config" ]; then
	for src in "$DOTFILES"/.config/*/; do
		src="${src%/}"
		link "$src" "$HOME/.config/$(basename "$src")"
	done
fi

# 5. Files this layout supersedes
if [ -e "$HOME/.gitignore" ] || [ -L "$HOME/.gitignore" ]; then
	echo "  retire: ~/.gitignore (the global excludes file is now ~/.gitignore_global)"
	backup "$HOME/.gitignore"
fi

# Ghostty also reads ~/Library/Application Support/com.mitchellh.ghostty/config, and that copy
# wins over ~/.config/ghostty/config, so move a leftover one out of the way.
ghostty_local="$HOME/Library/Application Support/com.mitchellh.ghostty/config"
if [ -e "$ghostty_local" ] && [ ! -L "$ghostty_local" ]; then
	echo "  retire: ~/Library/Application Support/com.mitchellh.ghostty/config (superseded by ~/.config/ghostty/config)"
	backup "$ghostty_local"
fi

# 6. Launch agents shipped in init/ (copied, not linked: launchd is happier with real files)
for src in "$DOTFILES"/init/*.plist; do
	[ -e "$src" ] || continue
	label="$(basename "$src" .plist)"
	dst="$HOME/Library/LaunchAgents/$label.plist"
	if [ -e "$dst" ] && cmp -s "$src" "$dst"; then
		continue
	fi
	echo "  agent:  $label"
	run mkdir -p "$HOME/Library/LaunchAgents"
	run cp "$src" "$dst"
	run launchctl bootout "gui/$(id -u)/$label" 2> /dev/null || true
	run launchctl bootstrap "gui/$(id -u)" "$dst"
done

# 7. Private git settings that the repository never contains
if [ ! -f "$HOME/.gitconfig.local" ]; then
	echo "  create: ~/.gitconfig.local (fill in your identity and signing key)"
	if (( ! DRY_RUN )); then
		umask 077
		cat > "$HOME/.gitconfig.local" <<'LOCAL'
# Machine-specific git settings, included by ~/.gitconfig. Never commit this file.

[user]

	name =
	email =
	signingkey =
LOCAL
	fi
fi

# 8. The completion cache was built against the old fpath; rebuild it on the next shell start
echo "  reset:  ~/.zcompdump (completion cache)"
run rm -f "$HOME"/.zcompdump*

echo "Done. Open a new terminal or run: exec zsh -l"
