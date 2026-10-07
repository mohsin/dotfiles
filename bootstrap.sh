#!/usr/bin/env bash

# Install the dotfiles by copying them into $HOME, so the machine keeps working wherever this
# repository is moved (or if it is deleted). Each copy is recorded with a fingerprint in
# ~/.config/dotfiles/manifest, which tells a local edit apart from a newer version in the
# repository: local edits are never overwritten (`dotfiles sync` carries them back here),
# untouched copies are updated, and anything unknown already in the way is moved to
# ~/.dotfiles-backup/<timestamp>/ first. Safe to re-run at any time.
#
# Usage: ./bootstrap.sh [-f|--force] [-n|--dry-run]
#   -f  skip the confirmation prompt
#   -n  print what would change without touching anything

set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP="$HOME/.dotfiles-backup/$(date +%Y%m%d-%H%M%S)"
STATE="$HOME/.config/dotfiles"
MANIFEST="$STATE/manifest"
NEW_MANIFEST="$(mktemp)"
trap 'rm -f "$NEW_MANIFEST"' EXIT
DRY_RUN=0
FORCE=0

for arg in "$@"; do
	case "$arg" in
		-f|--force) FORCE=1 ;;
		-n|--dry-run) DRY_RUN=1 ;;
		*) echo "Unknown option: $arg" >&2; exit 1 ;;
	esac
done

# Top-level entries that stay in the repository instead of being copied into $HOME:
# repo metadata, scripts you run from here, and directories that get special handling below.
SKIP=(.git .gitignore .DS_Store .editorconfig .macos .config .vim)

# Execute a command, or do nothing on a dry run (the callers already describe each change).
run() {
	(( DRY_RUN )) || "$@"
}

# Content fingerprint of a file or directory, ignoring Finder and Python caches.
# bin/dotfiles has the same function; keep the two in step.
fingerprint() {
	if [ -d "$1" ]; then
		(cd "$1" && find . -type f ! -name .DS_Store ! -path '*/__pycache__/*' -print0 \
			| LC_ALL=C sort -z | xargs -0 shasum) | shasum | cut -c1-40
	elif [ -e "$1" ]; then
		shasum < "$1" | cut -c1-40
	fi
}

# The fingerprint a path had when it was last installed, from the previous run's manifest.
recorded() {
	[ -f "$MANIFEST" ] || return 0
	awk -F'\t' -v d="$1" '$1 == d { print $3 }' "$MANIFEST"
}

# Move whatever is at $1 out of the way. Symlinks are simply removed; real files and
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

# Copy $1 (in the repo) to $2 (in $HOME) and record it in the manifest.
install() {
	local src="$1" dst="$2" rel="${2#$HOME/}" want have was verb="copy:  "
	want="$(fingerprint "$src")"
	if [ -L "$dst" ]; then
		echo "  unlink: $dst (replaced by a copy)"
		run rm "$dst"
	elif [ -e "$dst" ]; then
		have="$(fingerprint "$dst")"
		was="$(recorded "$rel")"
		if [ "$have" = "$want" ]; then
			printf '%s\t%s\t%s\n' "$rel" "${src#$DOTFILES/}" "$want" >> "$NEW_MANIFEST"
			return
		elif [ -n "$was" ] && [ "$have" != "$was" ]; then
			echo "  kept:   $dst has local edits (dotfiles diff to compare, dotfiles sync to keep them)"
			printf '%s\t%s\t%s\n' "$rel" "${src#$DOTFILES/}" "$was" >> "$NEW_MANIFEST"
			return
		elif [ -n "$was" ]; then
			verb="update:"
			run rm -rf "$dst"
		else
			backup "$dst"
		fi
	fi
	echo "  $verb $dst"
	run mkdir -p "$(dirname "$dst")"
	if [ -d "$src" ]; then
		run rsync -a --exclude .DS_Store --exclude __pycache__ "$src/" "$dst/"
	else
		run cp -p "$src" "$dst"
	fi
	printf '%s\t%s\t%s\n' "$rel" "${src#$DOTFILES/}" "$want" >> "$NEW_MANIFEST"
}

if (( ! FORCE && ! DRY_RUN )); then
	read -r -p "This copies dotfiles from $DOTFILES into $HOME (anything unknown in the way is backed up, local edits are kept). Continue? (y/n) " -n 1
	echo
	[[ $REPLY =~ ^[Yy]$ ]] || exit 0
fi

if (( ! DRY_RUN )); then
	echo "Updating the repository"
	git -C "$DOTFILES" pull --ff-only origin main || echo "  (could not fast-forward; continuing with the local checkout)"
fi

echo "Copying dotfiles from $DOTFILES into $HOME"

# 1. Every top-level dotfile
for src in "$DOTFILES"/.*; do
	name="$(basename "$src")"
	[ "$name" = "." ] || [ "$name" = ".." ] && continue
	[[ " ${SKIP[*]} " == *" $name "* ]] && continue
	install "$src" "$HOME/$name"
done

# 2. ~/bin: one copy per script, so personal scripts kept alongside them survive
for src in "$DOTFILES"/bin/*; do
	install "$src" "$HOME/bin/$(basename "$src")"
done

# 3. Vim: colours and syntax come from the repo; backups, swaps and undo history stay local
for dir in colors syntax; do
	install "$DOTFILES/.vim/$dir" "$HOME/.vim/$dir"
done
run mkdir -p "$HOME/.vim/backups" "$HOME/.vim/swaps" "$HOME/.vim/undo"

# 4. ~/.config/<app>: one copy per application directory, unless the directory carries a
#    .per-file marker, meaning the app keeps generated files next to its config: then each
#    versioned file is installed on its own and the rest of the app's directory is left alone.
if [ -d "$DOTFILES/.config" ]; then
	for src in "$DOTFILES"/.config/*/; do
		src="${src%/}"
		app="$(basename "$src")"
		if [ -e "$src/.per-file" ]; then
			for file in "$src"/*; do
				install "$file" "$HOME/.config/$app/$(basename "$file")"
			done
		else
			install "$src" "$HOME/.config/$app"
		fi
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

# 6. Claude Code: ~/.claude also holds sessions, caches and plugins, so install item by item.
#    Top-level files are copied directly; each entry inside hooks/, agents/ and skills/ goes
#    into the matching folder, leaving anything local-only (such as branded skills) untouched.
for src in "$DOTFILES"/claude/*; do
	name="$(basename "$src")"
	if [ -d "$src" ]; then
		for child in "$src"/*; do
			install "$child" "$HOME/.claude/$name/$(basename "$child")"
		done
	else
		install "$src" "$HOME/.claude/$name"
	fi
done

# 7. Copies whose source left the repository (a retired script or config): removed when
#    untouched, backed up when edited locally
if [ -f "$MANIFEST" ]; then
	while IFS=$'\t' read -r rel _ was; do
		awk -F'\t' -v d="$rel" '$1 == d { found = 1 } END { exit !found }' "$NEW_MANIFEST" && continue
		dst="$HOME/$rel"
		[ -e "$dst" ] || continue
		if [ "$(fingerprint "$dst")" = "$was" ]; then
			echo "  prune:  $dst (its file left the repository)"
			run rm -rf "$dst"
		else
			echo "  retire: $dst (left the repository but has local edits)"
			backup "$dst"
		fi
	done < "$MANIFEST"
fi

# Broken links left over from the symlink era, pointing into a dotfiles checkout
for dir in "$HOME" "$HOME/bin" "$HOME/.config" "$HOME/.config"/* "$HOME/.vim" \
	"$HOME/.claude" "$HOME/.claude/skills" "$HOME/.claude/agents" "$HOME/.claude/hooks"; do
	[ -d "$dir" ] || continue
	for lnk in "$dir"/.[!.]* "$dir"/*; do
		[ -L "$lnk" ] && [ ! -e "$lnk" ] || continue
		case "$(readlink "$lnk")" in
			*/dotfiles/*)
				echo "  prune:  $lnk (broken link from the old symlink setup)"
				run rm "$lnk"
				;;
		esac
	done
done

# 8. Launch agents shipped in init/ (launchd wants real files outside the manifest's care)
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

# 9. Private git settings that the repository never contains
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

# Private Claude Code instructions, imported by claude/CLAUDE.md
if [ ! -f "$HOME/.claude/CLAUDE.local.md" ]; then
	echo "  create: ~/.claude/CLAUDE.local.md (private instructions imported by CLAUDE.md)"
	if (( ! DRY_RUN )); then
		mkdir -p "$HOME/.claude"
		printf '# Local Instructions\n\nPrivate or machine-specific instructions for Claude Code. Imported by ~/.claude/CLAUDE.md, never committed.\n' > "$HOME/.claude/CLAUDE.local.md"
	fi
fi

# 10. Remember what was installed and from where, for the next run and for bin/dotfiles
if (( ! DRY_RUN )); then
	mkdir -p "$STATE"
	cp "$NEW_MANIFEST" "$MANIFEST"
	printf '%s\n' "$DOTFILES" > "$STATE/source"
fi

# 11. The completion cache was built against the old fpath; rebuild it on the next shell start
echo "  reset:  ~/.zcompdump (completion cache)"
run rm -f "$HOME"/.zcompdump*

echo "Done. Open a new terminal or run: exec zsh -l"
