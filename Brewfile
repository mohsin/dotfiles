# Homebrew manifest for an Apple Silicon Mac. Install everything with `./brew.sh`
# (or `brew bundle`), see what is missing with `brew bundle check`, and regenerate
# a raw dump to compare against with `brew bundle dump --file=/tmp/Brewfile`.
#
# Only tools that get used directly are listed; libraries arrive as dependencies.

tap "shivammathur/php"   # PHP 7.x builds that homebrew/core no longer ships

# --- Shell and core utilities -------------------------------------------------
brew "bash"                # modern Bash for scripts (the login shell is zsh)
brew "bash-completion@2"
brew "coreutils"           # GNU core utilities, g-prefixed
brew "findutils"           # GNU find, xargs, locate
brew "gnu-sed"
brew "grep"
brew "moreutils"           # sponge, ts, vipe and friends
brew "screen"
brew "tree"
brew "wget"
brew "jq"
brew "dos2unix"
brew "fdupes"              # find duplicate files
brew "flock"
brew "progress"            # progress bar for cp, mv, dd and other coreutils
brew "watchexec"           # run a command when files change
brew "just"                # project-local command runner
brew "pngpaste"            # paste the clipboard image to a file
brew "asciinema"           # record terminal sessions

# --- Terminal cockpit ---------------------------------------------------------
cask "ghostty"             # terminal emulator; quick terminal replaces the iTerm hotkey window
brew "neovim"              # $EDITOR
brew "lazygit"             # git TUI
brew "zellij"              # multiplexer with layouts and floating panes
cask "font-jetbrains-mono-nerd-font"   # icons for lazygit, zellij and nvim plugins

# --- Editors and AI -----------------------------------------------------------
cask "zed"                 # secondary GUI editor (adopt the hand-installed app once: brew install --cask --adopt zed)
cask "claude"
cask "claude-code@latest"

# --- Git and version control --------------------------------------------------
brew "gh"
brew "hub"                 # `g` alias
brew "git-lfs"
brew "git-filter-repo"
brew "git-quick-stats"
brew "bfg"                 # strip large files or secrets from history
brew "gnupg"               # commit signing
brew "pinentry-mac"
brew "subversion"
cask "meld"                # difftool and mergetool

# --- Languages, runtimes and package managers ---------------------------------
brew "nvm"                 # Node versions; the default one is put on PATH by ~/.zshrc
brew "pnpm"
brew "deno"
brew "pyenv"               # Python versions
brew "pipx"
brew "poetry"
brew "keyring"
brew "jsonschema"
cask "miniforge"           # conda, loaded lazily by ~/.zshrc
brew "composer"
brew "php", link: false
brew "php@8.3", link: true
brew "shivammathur/php/php@7.3", trusted: true
brew "shivammathur/php/php@7.4", trusted: true
brew "phpunit"
brew "wp-cli"
brew "openjdk@11"          # first on PATH
brew "openjdk@17"          # Gradle and Android builds
brew "kotlin"
brew "gradle"
brew "cocoapods"
brew "kdoctor"             # Kotlin Multiplatform environment check
cask "flutter"
brew "bacon"               # background cargo check
brew "cmake"
brew "binutils"

# --- Databases and local services ---------------------------------------------
brew "mariadb", restart_service: :changed
brew "postgresql@18", restart_service: :changed
brew "postgis"
brew "libpq", link: true   # psql and pg_dump without picking a server version
brew "memcached", restart_service: :changed
brew "nginx", restart_service: :changed
brew "dnsmasq"             # Laravel Valet
brew "phpmyadmin"
brew "mongosh"
brew "supabase"
brew "asimov", restart_service: :changed   # keep dependency folders out of Time Machine

# --- Cloud, containers and deployment -----------------------------------------
cask "docker-desktop"
brew "kubernetes-cli"
brew "helm"
brew "minikube"
brew "cmctl"               # cert-manager
brew "aws-sam-cli"
brew "k6"                  # load testing
brew "certbot"
brew "lsyncd"              # live directory sync to remote hosts
brew "lftp"
cask "lando"
cask "ngrok"
brew "zola"                # static site generators
brew "mdbook"

# --- Media and documents ------------------------------------------------------
brew "ffmpeg"
brew "yt-dlp"              # `video` and `audio` aliases
brew "imagemagick"         # also drives bin/undupe
brew "vips"
brew "tesseract"           # OCR
brew "poppler"             # pdftotext, pdfinfo
brew "ghostscript"         # `mergepdf` alias
brew "qpdf"
brew "pandoc"              # `mdcopy` function
brew "graphviz"
brew "potrace"             # bitmap to vector
brew "woff2"
brew "advancecomp"         # recompress PNG and ZIP

# --- Security, reverse engineering and networking -----------------------------
brew "tor"                 # `starttor` function
brew "i2p"
cask "mitmproxy"
brew "apktool"
brew "dex2jar"
brew "jadx"
brew "bundletool"
brew "cifer"
brew "testdisk"            # data recovery
brew "putty"
brew "libusbmuxd", args: ["HEAD"]         # iOS device tooling (HEAD builds track new iOS releases)
brew "libimobiledevice", args: ["HEAD"]
brew "ios-webkit-debug-proxy", args: ["HEAD"]
cask "blobsaver"
cask "macfuse"

# --- VS Code (kept only for Xdebug, Jupyter and .NET debugging) ----------------
vscode "bradlc.vscode-tailwindcss"
vscode "dart-code.dart-code"
vscode "dart-code.flutter"
vscode "dbaeumer.vscode-eslint"
vscode "denoland.vscode-deno"
vscode "docker.docker"
vscode "formulahendry.code-runner"
vscode "fwcd.kotlin"
vscode "golang.go"
vscode "james-yu.latex-workshop"
vscode "ms-azuretools.vscode-containers"
vscode "ms-azuretools.vscode-docker"
vscode "ms-dotnettools.csdevkit"
vscode "ms-dotnettools.csharp"
vscode "ms-dotnettools.vscode-dotnet-runtime"
vscode "ms-dotnettools.vscodeintellicode-csharp"
vscode "ms-python.debugpy"
vscode "ms-python.isort"
vscode "ms-python.python"
vscode "ms-python.vscode-pylance"
vscode "ms-python.vscode-python-envs"
vscode "ms-toolsai.jupyter"
vscode "ms-toolsai.jupyter-keymap"
vscode "ms-toolsai.jupyter-renderers"
vscode "ms-toolsai.vscode-jupyter-cell-tags"
vscode "ms-toolsai.vscode-jupyter-slideshow"
vscode "ms-vscode-remote.remote-containers"
vscode "ms-vscode-remote.remote-ssh"
vscode "ms-vscode-remote.remote-ssh-edit"
vscode "ms-vscode-remote.remote-wsl"
vscode "ms-vscode-remote.vscode-remote-extensionpack"
vscode "ms-vscode.makefile-tools"
vscode "ms-vscode.remote-explorer"
vscode "ms-vscode.remote-server"
vscode "neptunedesign.vs-slug"
vscode "nuxt.mdc"
vscode "octref.vetur"
vscode "rust-lang.rust-analyzer"
vscode "syler.sass-indented"
vscode "vue.volar"
vscode "wakatime.vscode-wakatime"
vscode "xdebug.php-debug"

# --- Language-level globals ---------------------------------------------------
go "github.com/go-delve/delve/cmd/dlv"
go "github.com/ramya-rao-a/go-outline"
go "golang.org/x/tools/cmd/goimports"
go "github.com/uudashr/gopkgs/v2/cmd/gopkgs"
go "golang.org/x/tools/gopls"
go "honnef.co/go/tools/cmd/staticcheck"
go "github.com/ddz/whatsapp-media-decrypt"
cargo "cargo-readme"
cargo "sqlx-cli"
cargo "systemfd"
cargo "vtracer"
cargo "laterite-cli"       # own crates
cargo "laterite-site"
npm "@railway/cli"
