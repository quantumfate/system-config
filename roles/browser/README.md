# browser

Single owner of Zen (and Firefox) provisioning: renders the shared prefs and
chrome assets from this role's templates/files into `browser_config_src`,
creates the named Zen profiles, and symlinks the shared files into every
profile. Absorbed the old `browser_profiles` role and the theming role's Zen
templates, so nothing about the browser config lives outside this role
anymore — the `zen-chezmoi` directory and the chezmoi-flavoured naming are
gone. The one other writer of the shared directory is `,theme.sh apply_zen`
(the scripts checkout), which owns the runtime palette accent.

- **Vars** `browser_config_src` (group_vars/all/main.yml — shared with the
  scripts repo via `,theme.sh`); role defaults hold the accent hex, profile
  lists and link extras.
- **Tag** `dotfiles`, `browser`
- **Order** after `roles/theming`: the floating zen templates reference the
  `theme_*` font vars that role's defaults provide.

## One shared config, many profiles

Every profile links back to the same `user.js`, chrome CSS and palette file,
so a palette switch (or a CSS fix) is written once and read everywhere. The
runtime accent lands in `browser_config_src/zen-palette.css` and in `user.js`
(via `,theme.sh`), which the profile links pick up on the next launch —
`user.js` and chrome CSS are read at startup, so a running Zen needs a restart
to see them. Nothing here overwrites the CSS at runtime, which is what makes
per-profile live edits (Browser Toolbox, a Stylus-style userstyle manager)
survive: break a profile's link to diverge, or add profile-local CSS through
the existing `@import` seams.

## Zen profiles are first-class names, created here

The seed list names every zen profile the desk drives: the default profile,
`-P Media`/`-P Dofus` and the two pokemon companions (`-P pokemon-left`/
`-P pokemon-right`). One profile per identity, never one per window role —
except where a scene genuinely needs two windows it must tell apart: the
pokemon scene keeps a browser open on each side of the emulator, and a shared
profile would make both windows the same WM_CLASS, which the scene cannot
disambiguate. A profile per window role also signed two sync clients into one
account under the same device name, which the account cannot tell apart, so
even that case gets separate profiles rather than a second window of one.

The link pass is idempotent across profile ages: an existing-but-unlinked
profile (created by hand mid-run of the playbook, for instance) gets its
`user.js` and chrome links laid on the next converge.

## Container identities are provisioned per profile

Each Zen profile gets the container identities its default-container choice can
pick from, written into the profile's own `containers.json` (the flat v6 file
Zen owns by name). The merge (`files/merge_containers.py`) is by name: an
identity already present keeps its `userContextId`, icon and color — site
associations and user-picked ids survive a re-converge — and a missing one is
appended with a fresh id and the declared seed icon/color. The declared set
lives in `zen_containers` (defaults), keyed by profile name as `profiles.ini`
names it. The DEFAULT container itself is never provisioned: it is a Zen UI
choice the user makes after converging, stored outside `containers.json`.

## Seed vs live

The templates and assets render the SEED flavour (static accent, fonts from
`roles/theming`). The last task re-asserts the theme store over the seed with
`,theme.sh apply` — the same hand-back `roles/theming` performs — so a
converge never reverts a palette the store already resolved.
