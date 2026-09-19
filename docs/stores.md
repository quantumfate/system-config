# The store registry — declarations vs observations

Every store the desk keeps lives under `$QF_STORE` (default
`$XDG_STATE_HOME/quantum-store`, exported by env-hyprland and read
by every runtime through its own `Store`/lib). The distinction the
privacy model rests on (see `docs/hyprfocus.md`, "What may be committed"):

- a **declaration** says what the desk should be — configuration, meant to
  be read, safe to commit;
- an **observation** says what was actually done — a diary. Personal
  information regardless of how mundane any single record looks.

The classification is named in each schema (`"classification"`), so a new
store has to declare which it is, and the gate test in quickshell pins
this list against the schemas: it fails when a schema's class and this
table disagree, or when a schema ships without a class at all.

## The registry

| store                        | kind        | what it is                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| hyprfocus.json               | declaration | the whole desk's declaration: resources, scenes, mode policy, leases                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| mood-policy.json             | declaration | per-mood policy (notifications, launches, background work, scene reachability)                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| theme.json                   | declaration | the theme pointer: palette, day/night, scale, wallpapers the user bound                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| hyprfocus.json (packs)       | declaration | theme packs: assets/packs/\*.json, committed with the code they name                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| sound.json                   | declaration | sound defaults and the declared pool                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| notify-prefs.json            | declaration | the DND choice — the desk saying what it should do (LEO-281 split)                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| projects.json                | declaration | which projects exist and what each opens: path, kitty window template, workspace (`,proj.sh sync` populates it from a filesystem scan; `,proj.sh` reads it at runtime), plus dashboard metadata (kind, study, priority)                                                                                                                                                                                                                                                                                                                        |
| focus.json                   | observation | the pointer: `{mode, until, source, set_at, previous}` — the active mode, who set it, when, and (for a timed mode) the open-ended mode it was layered over, so expiry can fall back to it instead of to `work`                                                                                                                                                                                                                                                                                                                                 |
| notifications.json           | observation | message content: summaries and bodies, capped at 100 entries, erasable (Clear)                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| theme.result.json            | observation | what an apply actually did — the truth the shell reports                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| whichkey.json                | declaration | a cache of the binding trees the compositor declares; derived, no behaviour                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| scene-policy/veto.json       | observation | resources refusing to stop, in their own words (LEO-256)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| scene-policy/last.json       | observation | what the last transition held back (LEO-256)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| scene-policy/log.jsonl       | observation | every transition decision and outcome (LEO-241 curates; no schema yet)                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| scene-policy/applied.json    | observation | the last applied state, what got stopped, to hand back (no schema yet)                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| hyprfocus-held.json          | observation | windows a mode parked, with their recorded origins — an open-history                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| dofus/team.json              | declaration | the declared team rotation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| nvim/tools.json              | observation | tool presence per host, probe results with a generated_at                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| obsidian/ui.json + tags.json | observation | editor state and tags derived from use (owned by the scripts repo's stores)                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| hypr/monitor-profile.json    | declaration | host monitor data                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| geometry.json                | declaration | per-monitor base left/right outer gap, published by conf/host.lua's `build()` (LEO-340); the bar mirrors it as its side inset, falling back to `Theme.barInset*2` when a monitor has no entry. Base gap only — never the transient solo widen from `hypr/events/solo_gaps.lua`. Also carries `roles: {primary, secondary}` (LEO-368), the host's monitor-role -> connected output map, so the bar reads a role instead of guessing it from the gaps map's key order; an unconnected or ignored output is omitted, never defaulted onto a role. |

Schemas without a row here, or a row without a schema, are a defect of
the registry, not of the store: the gate test pins the schemas and the
table against each other. The scene-policy workspace's rows/applied/last
are named in schemas/scene-policy.schema.json (LEO-241); veto.json and
hyprfocus-held.json still carry their kind from this table only.

## Re-seeding a declaration (LEO-337)

Version 3 replaced `workspaces` deltas with per-mode `scenes: [{name, monitor}]`
and made `neutral` hidden. A version-2 store reseeds once on the next
`,hyprfocus seed`; hand edits to it are replaced (the compositor refuses a
pre-v3 mode with `missing_scenes` until then).

`hyprfocus.json` is the one store re-seeded automatically, and only forward:
`,hyprfocus seed <file>` (`hypr/bin/,hyprfocus`) compares the stored
`version` against the file being seeded, and when the store's is lower it
replaces the store once, without `--force`. A stored `version` equal to or
higher than the file being seeded still refuses without `--force` — the
store is edited at runtime, and a store already at the current version may
carry hand-tuned fields a blind overwrite would discard.

This is the only reseed path; nothing else — the compositor's Lua side
included — carries a second copy of this logic. A version bump is warranted
even when the declaration's _shape_ is unchanged, whenever shipped content
(scene sets, mode deltas, presentation) has drifted enough that a store
seeded from an older file no longer matches what the host configs expect —
which is what happened when the workspace names changed but
`assets/hyprfocus.default.json`'s `version` did not, and the CLI had no
comparison to catch it. See `hyprfocus.md`'s "The one idea" for what the
declaration governs, and the quickshell sibling's `schemas/hyprfocus.schema.json`
for the `version` field itself.

`,hyprfocus seed` itself still has no way to _locate_ the shipped default —
every call site passes the source path explicitly (see
`hyprfocus-handoff.md`). `hypr/lib/maintenance.lua` closes that gap for the
one caller that matters at session start: it resolves the sibling
`quickshell` checkout's `assets/hyprfocus.default.json` relative to its own
file location (the same convention the test suite already uses), compares
its `version` against the store's, and calls `,hyprfocus seed` only when the
store is missing or behind — logging the action as `stage=maintenance`
(`hypr/lib/trace.lua`) either way. A sibling checkout that is not there
(no `quickshell` next to `hypr`) is silently skipped, not an error.

## Never resurrect a retired document (LEO-399)

Every store's QML side (`quickshell/services/Store.qml`) adopts a legacy
pre-`quantum-store` document the first time its target file is missing, then
renames the legacy file to `<name>.json.migrated` so it can never be
re-applied. That rename is not enough on its own: the `legacy` FileView it
reads from had no `watchChanges`, so a long-running shell process kept
whatever it read there at startup in memory forever — including a document
already retired on disk. Wiping a store mid-session (or any other way its
target file goes missing again) could then resurrect exactly the document
the rename was supposed to retire for good; this is what brought
`hyprfocus.json`, `focus.json` and `theme.json` all back with year-old
content within seconds of a deliberate wipe.

The fix is two-layered:

- `Store.qml`'s `legacy` FileView now watches its own file, so `text()`
  reflects the file's CURRENT state (gone once retired), not whatever it
  read once. This alone fixes every store.
- `hyprfocus.json` additionally opts out of legacy adoption outright
  (`Store { legacyMigration: false }` in `Hyprfocus.qml`, `NO_LEGACY` in
  `hypr/lib/store.lua`): it is the one **declaration**, and a missing
  declaration must leave the engine inert and say so, never invent one —
  belt and braces, not reliance on the general fix alone.
