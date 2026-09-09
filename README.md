# Saifur’s dotfiles

This fork of [Mathias Bynens dotfiles](https://github.com/mathiasbynens/dotfiles) is a custom dotfiles build tailored to my preferences of a OS X development machine. Suggestions or hacks that are more effective are welcome.

## Installation

**Warning:** If you want to give these dotfiles a try, you should first fork this repository, review the code, and remove things you don’t want or need. Don’t blindly use my settings unless you know what that entails. Use at your own risk!

### Using Git and the bootstrap script

Clone the repository wherever you like. The bootstrapper symlinks every dotfile into your home
directory, so editing `~/.zshrc` edits the repository and nothing can drift. Anything already in
the way is moved to `~/.dotfiles-backup/<timestamp>/` first.

```bash
git clone git@github.com:mohsin/dotfiles.git && cd dotfiles && ./bootstrap.sh
```

To update, `cd` into your local `dotfiles` repository and run it again. It pulls the latest
version, links anything new, and skips what is already linked:

```bash
./bootstrap.sh
```

Pass `-f` to skip the confirmation prompt, or `-n` to see what would change without touching
anything.

Private git settings (your name, email, signing key, send-email credentials) live in
`~/.gitconfig.local`, which `.gitconfig` includes and which is never committed. The bootstrapper
creates an empty template if the file does not exist.

### Specify the `$PATH`

If `~/.path` exists, it will be sourced along with the other files, before any feature testing (such as [detecting which version of `ls` is being used](https://github.com/mathiasbynens/dotfiles/blob/aff769fd75225d8f2e481185a71d5e05b76002dc/.aliases#L21-L26)) takes place.

Here’s an example `~/.path` file that adds `/usr/local/bin` to the `$PATH`:

```bash
export PATH="/usr/local/bin:$PATH"
```

### Add custom commands without creating a new fork

If `~/.extra` exists, it will be sourced along with the other files. You can use this to add a few custom commands without the need to fork this entire repository, or to add commands you don’t want to commit to a public repository.

My `~/.extra` looks something like this:

```bash
# Git credentials
# Not in the repository, to prevent people from accidentally committing under my name
GIT_AUTHOR_NAME="Mathias Bynens"
GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
git config --global user.name "$GIT_AUTHOR_NAME"
GIT_AUTHOR_EMAIL="mathias@mailinator.com"
GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
git config --global user.email "$GIT_AUTHOR_EMAIL"
```

You could also use `~/.extra` to override settings, functions and aliases from my dotfiles repository. It’s probably better to [fork this repository](https://github.com/mathiasbynens/dotfiles/fork) instead, though.

### Sensible macOS defaults

When setting up a new Mac, you may want to set some sensible macOS defaults:

```bash
./.macos
```

### Install Homebrew formulae

When setting up a new Mac, you may want to install some common [Homebrew](https://brew.sh/) formulae (after installing Homebrew, of course):

```bash
./brew.sh
```
