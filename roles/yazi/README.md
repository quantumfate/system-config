# yazi

Installs the plugins declared in `~/.config/yazi/package.toml`.

- **Tag** `dotfiles`, `yazi`

chezmoi writes that file, so this role must run after it. Locally modified
plugins are left alone by `ya pkg install`.
