# browser_profiles

Symlinks the shared prefs into every Zen and Firefox profile, creating the
profiles first by starting each browser once headless.

- **Vars** `browser_roots`, `browser_profile_excludes`, `zen_profile_extras`
  (defaults); the prefs source `browser_config_src` is in
  `group_vars/all/main.yml`.
- **Tag** `dotfiles`, `browser`

`roles/theming` renders the `user.js` this role links — hence the shared var,
and hence this role running after it.
