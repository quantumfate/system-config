# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Zen browser provisioning gained per-profile container identities: each
  profile's `containers.json` now declares the containers its default-container
  choice can use (Main: Personal, Studying, Productivity, Research and
  Sensitive Research; Dofus: Dofus; Media: Social Media, Gaming, Anime,
  Shopping). The merge (`roles/browser/files/merge_containers.py`) is by name —
  existing identities keep their ids, icon and color, and missing ones are
  appended — and never writes the default-container choice itself, which stays
  a Zen UI decision.
- Zen password and autofill machinery is fully off: the address autofill pref
  is no longer enabled and the credit-card and address form-fill extensions
  are disabled, so Proton Pass is the only credential surface.
- Zen search is DuckDuckGo-only: the default engine (normal and private) and
  the urlbar placeholder are DuckDuckGo and every other engine is hidden from
  the one-off search bar. The engine list itself remains a UI-owned file.
- Zen config provisioning moved from the chezmoi-flavoured
  `~/.config/zen-chezmoi` shared directory into a new `roles/browser`. It owns
  the shared config (seed templates formerly in `roles/theming`, plus the
  static logo and mod-registry assets), the named-profile creation and the
  per-profile links, absorbing the old `roles/browser_profiles`. The shared
  directory is now `~/.config/zen/shared`; `,theme.sh apply_zen` only writes
  the runtime accent (palette CSS and `user.js` accent) and no longer
  overwrites the provisioned CSS, so per-profile CSS edits survive.
- Catppuccin themes for btop, foot, rofi, zathura, spicetify and wlogout moved
  from `roles/theming` to `.chezmoiexternal.toml` in the dotfiles, next to the
  configs that include them. `roles/chezmoi` installs `chezmoi-externals.timer`
  to refresh them between playbook runs.
- Zen never restores the last session: `browser.startup.page = 1`,
  `browser.sessionstore.resume_from_crash = false`,
  `browser.sessionstore.resume_session_once = false` and
  `browser.sessionstore.max_resumed_crashes = 0` together block the normal,
  crash, update-restart and repeated-crash restore paths, so an unclean exit
  (shutting the machine down with Zen still running) no longer replays every
  window that was open at the next launch.

### Fixed

- `roles/theming` failed on a fresh `$HOME`: rsync could not create nested theme
  directories, and nothing created `~/.config/zen-chezmoi` since `user.js` moved
  out of chezmoi. Theme archives are no longer re-extracted on every run.
- `roles/reset` moves the dotfiles source clone into the reset archive instead
  of deleting it, so uncommitted or unpushed dotfiles work survives a flush.
- `quantum-laptop` no longer disables the `display_manager` role. The laptop
  kept sddm (nothing had enabled greetd in its place), so the always-on
  `cleanup` role stopped and disabled a live sddm mid-run — killing the
  graphical seat and black-screening the session. The laptop now converges on
  sddm exactly like the desktop, and the now-empty `laptop_packages` set no
  longer drags in greetd-tuigreet.
