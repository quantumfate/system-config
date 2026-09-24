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

The seed list names every zen profile the desk drives: the default profile and
`-P Media`. One profile per identity, never one per window role: a scene's
companion browser is a second _window_ of the media profile, claimed and
placed by the desk's scene engine (it stamps the window it launched), so no
profile exists only to carry a window class. A profile per window role also
signed two sync clients into one account under the same device name, which the
account cannot tell apart.

The accent reaches every profile through the one shared `user.js` its symlink
points back at, re-rendered per palette by `theming` (pending tier: next
launch).

The link pass is idempotent across profile ages: an existing-but-unlinked
profile (created by hand mid-run of the playbook, for instance) gets its
`user.js` and chrome links laid on the next converge.
