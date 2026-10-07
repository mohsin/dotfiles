# Mohsin’s dotfiles

Configuration for an Apple Silicon Mac used for Rust, PHP, JavaScript, Python and mobile
work, with a terminal-first workflow: Ghostty, Zellij, lazygit, Neovim and Claude Code.
Started as a fork of [Mathias Bynens’ dotfiles](https://github.com/mathiasbynens/dotfiles)
and rebuilt around zsh, a copy-based installer and a Brewfile.

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
| `claude/` | Claude Code: the global `CLAUDE.md`, the `git-commit-msg` skill, the `highlight` skills (`highlight`, `highlight-footage`, `highlight-soundtrack`, `highlight-cover`) that turn a trip into an Instagram highlight reel and cover, and the `social-media-manager` agent |
| `Brewfile`, `brew.sh` | Every Homebrew formula, cask and VS Code extension in use, grouped by purpose |
| `bootstrap.sh` | Copies everything above into the home directory |
| `.macos` | macOS defaults and a hidden-at-login Ghostty |
| `init/` | Files `.macos` and `bootstrap.sh` install: a launch agent and a Terminal.app theme |
| `bin/` | Small scripts, copied into `~/bin`, including `dotfiles` (keeps the copies and the repository in step) |
| `.vimrc`, `.vim/` | Plain Vim, for machines without Neovim |

## Installation

Clone the repository wherever you like and run the bootstrapper. It copies every dotfile
into your home directory, so the machine keeps working if the repository is moved or deleted.
Anything unknown already in the way is moved to `~/.dotfiles-backup/<timestamp>/` first.

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

To update, run `dotfiles install` (or `./bootstrap.sh` from the repository). It pulls the
latest version, copies anything new or changed, prunes copies whose file was removed, and
never overwrites a file you edited locally. Pass `-f` to skip the confirmation prompt, or `-n`
to see what would change without touching anything.

### Editing a dotfile

Edit the copy in your home directory as usual, then carry the change back:

```bash
dotfiles status   # what differs, and on which side
dotfiles diff     # the differences
dotfiles sync     # copy local edits into the repository, then commit them there
```

`bootstrap.sh` records every copy with a fingerprint in `~/.config/dotfiles/manifest`, which
is how it tells a local edit (kept, synced back on request) from a newer version in the
repository (installed). If the repository moves, run `./bootstrap.sh` once from its new
location so `dotfiles` can find it again; nothing in the home directory breaks meanwhile.

## Private and machine-specific settings

Nothing personal is committed. The bootstrapper creates these files as empty templates when
they do not exist:

- `~/.gitconfig.local`: your name, email, signing key and send-email credentials, included
  by `.gitconfig`.
- `~/.claude/CLAUDE.local.md`: private Claude Code instructions, imported by `CLAUDE.md`.
- `~/.Brewfile.local`: client and project specific packages, installed by `brew.sh` after the
  main `Brewfile`.

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
