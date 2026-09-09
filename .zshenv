# Runs for every zsh: login, interactive and scripts. Keep it tiny.

# Never let PATH or fpath accumulate duplicates, however many times the profile is sourced.
typeset -U path fpath
