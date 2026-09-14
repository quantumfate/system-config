# browser_profiles

Symlinks the shared prefs into every Zen and Firefox profile, creating the
profiles first by starting each browser once headless.

- **Vars** `browser_roots`, `browser_profile_excludes`, `zen_profile_extras`
  (defaults); the prefs source `browser_config_src` is in
  `group_vars/all/main.yml`.
- **Tag** `dotfiles`, `browser`

`roles/theming` renders the `user.js` this role links — hence the shared var,
and hence this role running after it.

## Zen profiles are first-class names, created here

The seed list names every zen profile the desk drives: the default profile,
`-P Media`, and `-P GamingMedia`. GamingMedia is not an alias: zen is
single-instance per profile, and the gaming scene's companion
(`zen-twilight -P GamingMedia --name zen-gaming-media`, LEO-296) launches that
profile as its own process — its window class `zen-gaming-media` is pinned to
`name:gaming` by hypr's windowrules, and the accent reaches it through the one
shared `user.js` its `user.js` symlink points back at, re-rendered per palette
by `theming` (pending tier: next launch).

The link pass is idempotent across profile ages: an existing-but-unlinked
profile (created by hand mid-run of the playbook, for instance) gets its
`user.js` and chrome links laid on the next converge.
