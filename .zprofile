# Login shells only. Put Homebrew on PATH (and its completions on fpath) before anything else;
# everything interactive lives in ~/.zshrc.
[ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv zsh)"

# Environment (PATH, EDITOR, …) belongs to the login shell so that non-interactive `zsh -l -c`
# gets it too. ~/.zshrc sources it again for non-login interactive shells; ~/.zshenv deduplicates PATH.
[ -r "$HOME/.exports" ] && source "$HOME/.exports"
