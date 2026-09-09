#!/usr/bin/env bash

# Install Homebrew if needed, then everything in ./Brewfile. Safe to re-run.

set -euo pipefail

if ! command -v brew > /dev/null 2>&1; then
	echo "Installing Homebrew"
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	eval "$(/opt/homebrew/bin/brew shellenv)"
fi

brew update
brew bundle install --file="$(dirname "${BASH_SOURCE[0]}")/Brewfile"

# Remove outdated versions from the cellar.
brew cleanup
