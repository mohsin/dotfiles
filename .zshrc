# Interactive zsh configuration. Login shells run ~/.zprofile first (Homebrew on PATH),
# then this file. Exports, aliases and functions are shared with bash via the same files.

# --- Shared dotfiles ---------------------------------------------------------
# * ~/.path can be used to extend `$PATH`.
# * ~/.extra can be used for other settings you don’t want to commit.
for file in ~/.{path,exports,aliases,functions,extra}; do
	[ -r "$file" ] && [ -f "$file" ] && source "$file"
done
unset file

# --- Options -----------------------------------------------------------------
setopt auto_cd                # a bare directory name changes into it
setopt auto_pushd             # `cd` keeps a stack, so `cd -<Tab>` lists recent directories
setopt pushd_ignore_dups pushd_silent
setopt no_case_glob           # case-insensitive globbing
setopt interactive_comments   # allow # comments on the command line
setopt no_beep
setopt no_flow_control        # free Ctrl+S and Ctrl+Q for the line editor

# --- History -----------------------------------------------------------------
HISTFILE="$HOME/.zsh_history"
HISTSIZE=32768
SAVEHIST=$HISTSIZE
setopt extended_history       # save timestamps and durations
setopt inc_append_history     # write each command as it runs, not only at exit
setopt hist_ignore_dups       # skip a command identical to the previous one
setopt hist_ignore_space      # skip commands that begin with a space
setopt hist_reduce_blanks
setopt hist_verify            # show the expanded history line before running it
setopt hist_expire_dups_first

# --- Keys (mirrors the old .inputrc) -----------------------------------------
bindkey -e                                       # Emacs-style line editing, as readline did
autoload -Uz up-line-or-beginning-search down-line-or-beginning-search
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
bindkey '^[[A' up-line-or-beginning-search       # Up/Down: search history with the typed prefix
bindkey '^[OA' up-line-or-beginning-search
bindkey '^[[B' down-line-or-beginning-search
bindkey '^[OB' down-line-or-beginning-search
bindkey '^[[H' beginning-of-line                 # Home / End
bindkey '^[[F' end-of-line
bindkey '^[[1;3C' forward-word                   # Alt+Right / Alt+Left
bindkey '^[[1;3D' backward-word
bindkey '^[[3~' delete-char                      # Delete
bindkey '^[[3;3~' kill-word                      # Alt+Delete

# --- Completion --------------------------------------------------------------
autoload -Uz compinit
() {
	# Rebuild the completion dump at most once a day; otherwise trust the cache
	setopt local_options extended_glob
	if [[ -n "$HOME"/.zcompdump(#qN.mh+24) ]]; then
		compinit
	else
		compinit -C
	fi
}
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'   # case-insensitive
zstyle ':completion:*' menu select                       # arrow-key menu when there are many matches
zstyle ':completion:*' list-colors ''                    # colour matches like `ls`
zstyle ':completion:*' special-dirs true                 # complete `.` and `..`
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path "$HOME/.zcompcache"
# bun ships its completion outside any fpath directory
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

# --- Tool hooks: the slow ones load on first use ------------------------------
# nvm takes ~250ms to load. Put the default Node on PATH now (cheap) and load nvm
# itself the first time `nvm` is called.
if [ -s "/opt/homebrew/opt/nvm/nvm.sh" ]; then
	() {
		local want="$(cat "$NVM_DIR/alias/default" 2>/dev/null)"
		local -a candidates
		if [[ "$want" == (v|)<->* ]]; then
			candidates=("$NVM_DIR"/versions/node/v${want#v}*/bin(N/n))
		fi
		(( $#candidates )) || candidates=("$NVM_DIR"/versions/node/*/bin(N/n))
		(( $#candidates )) && path=("${candidates[-1]}" $path)
	}
	nvm() {
		unfunction nvm
		source "/opt/homebrew/opt/nvm/nvm.sh"
		nvm "$@"
	}
fi

# conda's shell hook takes ~300ms; defer it until `conda` is actually used.
if [ -x /opt/anaconda3/bin/conda ]; then
	conda() {
		unfunction conda
		eval "$(/opt/anaconda3/bin/conda shell.zsh hook)"
		conda "$@"
	}
fi

# gcloud's completion script takes ~500ms; load it the first time `gcloud` runs.
if [ -f "$HOME/google-cloud-sdk/completion.zsh.inc" ]; then
	gcloud() {
		unfunction gcloud
		source "$HOME/google-cloud-sdk/completion.zsh.inc"
		gcloud "$@"
	}
fi

# --- Prompt ------------------------------------------------------------------
[ -r "${ZDOTDIR:-$HOME}/.zsh_prompt" ] && source "${ZDOTDIR:-$HOME}/.zsh_prompt"
