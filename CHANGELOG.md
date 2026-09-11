# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Catppuccin themes for btop, foot, rofi, zathura, spicetify and wlogout moved
  from `roles/theming` to `.chezmoiexternal.toml` in the dotfiles, next to the
  configs that include them. `roles/chezmoi` installs `chezmoi-externals.timer`
  to refresh them between playbook runs.

### Fixed

- `roles/theming` failed on a fresh `$HOME`: rsync could not create nested theme
  directories, and nothing created `~/.config/zen-chezmoi` since `user.js` moved
  out of chezmoi. Theme archives are no longer re-extracted on every run.
- `roles/reset` moves the dotfiles source clone into the reset archive instead
  of deleting it, so uncommitted or unpushed dotfiles work survives a flush.
