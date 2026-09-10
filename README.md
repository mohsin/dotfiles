# Mohsin’s dotfiles

Configuration for an Apple Silicon Mac used for Rust, PHP, JavaScript, Python and mobile
work, with a terminal-first workflow: Ghostty, Zellij, lazygit, Neovim and Claude Code.
Started as a fork of [Mathias Bynens’ dotfiles](https://github.com/mathiasbynens/dotfiles)
and rebuilt around zsh, symlinks and a Brewfile.

**Warning:** these are personal settings. Fork the repository, read what a file does, and
remove what you do not want before running anything. Use at your own risk.

## What is in here

| Path | Purpose |
|---|---|
| `.zshenv`, `.zprofile`, `.zshrc`, `.zsh_prompt` | zsh: options, history, completion, a Solarized prompt with git status, and lazy loading for nvm, conda and gcloud so a shell starts in about 50 ms |
| `.exports`, `.aliases`, `.functions` | Environment, PATH, aliases and helper functions shared by zsh and bash |
| `.bash_profile`, `.bash_prompt`, `.bashrc`, `.inputrc` | The same setup for bash, kept as a fallback |
| `.gitconfig`, `.gitignore_global`, `.gitattributes` | Git aliases, Meld as diff and merge tool, Zed for commit messages, global excludes |
| `.config/ghostty/` | Terminal: Solarized Dark, JetBrains Mono Nerd Font, a window pinned to the top of the screen on Option+Space |
| `.config/zellij/` | Multiplexer, locked by default so Ctrl keys reach the program in the pane; the `cockpit` layout opens Claude Code, lazygit and a shell |
| `.config/lazygit/` | Git TUI with Nerd Font icons |
| `.config/nvim/` | Neovim on LazyVim with language extras for every stack in use and Claude Code inside the editor |
| `.config/zed/` | Zed as the secondary editor, Sublime Text keymap, same theme and font |
| `claude/` | Claude Code: the global `CLAUDE.md` and the `git-commit-msg` skill |
| `Brewfile`, `brew.sh` | Every Homebrew formula, cask and VS Code extension in use, grouped by purpose |
| `bootstrap.sh` | Links everything above into the home directory |
| `.macos` | macOS defaults and a hidden-at-login Ghostty |
| `init/` | Files `.macos` and `bootstrap.sh` install: a launch agent and a Terminal.app theme |
| `bin/` | Small scripts, linked into `~/bin` |
| `.vimrc`, `.vim/` | Plain Vim, for machines without Neovim |

## Installation

Clone the repository wherever you like and run the bootstrapper. It symlinks every dotfile
into your home directory, so editing `~/.zshrc` edits the repository and nothing can drift.
Anything already in the way is moved to `~/.dotfiles-backup/<timestamp>/` first.

```bash
git clone git@github.com:mohsin/dotfiles.git && cd dotfiles && ./bootstrap.sh
```

Then, on a new machine:

```bash
./brew.sh   # installs Homebrew if needed, then everything in the Brewfile
./.macos    # macOS defaults; read it first, it asks for sudo
```

Two things macOS will not let a script do: add Ghostty under System Settings, Privacy &
Security, Accessibility, so its global Option+Space hotkey works, and open Neovim once so
LazyVim installs its language servers.

To update, `cd` into the repository and run `./bootstrap.sh` again. It pulls the latest
version, links anything new, prunes links whose file was removed, and skips what is already
in place. Pass `-f` to skip the confirmation prompt, or `-n` to see what would change without
touching anything.

## Private and machine-specific settings

Nothing personal is committed. The bootstrapper creates these files as empty templates when
they do not exist:

- `~/.gitconfig.local`: your name, email, signing key and send-email credentials, included
  by `.gitconfig`.
- `~/.claude/CLAUDE.local.md`: private Claude Code instructions, imported by `CLAUDE.md`.

Two more are sourced by the shell if present, and never created:

- `~/.path` extends `$PATH` before anything else runs.
- `~/.extra` holds settings, functions and aliases you do not want in a public repository,
  and can override anything in this one.

## Daily use

- **Option+Space** shows or hides Ghostty. **Option+Shift+Space** drops a quick terminal from
  the top of the screen for a one-off command.
- **`cockpit`** opens the Zellij layout in the current project: Claude Code on the left, lazygit
  and a shell on the right. Inside Zellij it opens as a new tab. **Ctrl+G** unlocks Zellij’s own
  keys; **Ctrl+G, G** pops lazygit as a floating pane.
- **`zj`** attaches to one persistent Zellij session from any window.
- **`lg`** is lazygit. Commit messages open in Zed.
- **`nvim`** is `$EDITOR`. Space is the leader; **Space, A, C** toggles Claude Code inside it.

## Thanks to…

* [Mathias Bynens](https://mathiasbynens.be/) and the [original dotfiles](https://github.com/mathiasbynens/dotfiles) this repository grew out of
* The [LazyVim](https://www.lazyvim.org/) and [claudecode.nvim](https://github.com/coder/claudecode.nvim) authors
