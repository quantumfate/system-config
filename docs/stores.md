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

| store                        | kind        | what it is                                                                     |
| ---------------------------- | ----------- | ------------------------------------------------------------------------------ |
| hyprfocus.json               | declaration | the whole desk's declaration: resources, scenes, mode policy, leases           |
| mood-policy.json             | declaration | per-mood policy (notifications, launches, background work, scene reachability) |
| scenes.json                  | declaration | the scene document: window geometry per mode                                   |
| theme.json                   | declaration | the theme pointer: palette, day/night, scale, wallpapers the user bound        |
| hyprfocus.json (packs)       | declaration | theme packs: assets/packs/\*.json, committed with the code they name           |
| sound.json                   | declaration | sound defaults and the declared pool                                           |
| notify-prefs.json            | declaration | the DND choice — the desk saying what it should do (LEO-281 split)             |
| focus.json                   | observation | the pointer: the active mode, who set it, when — a diary of how the desk moved |
| notifications.json           | observation | message content: summaries and bodies, capped at 100 entries, erasable (Clear) |
| theme.result.json            | observation | what an apply actually did — the truth the shell reports                       |
| whichkey.json                | declaration | a cache of the binding trees the compositor declares; derived, no behaviour    |
| scene-policy/veto.json       | observation | resources refusing to stop, in their own words (LEO-256)                       |
| scene-policy/last.json       | observation | what the last transition held back (LEO-256)                                   |
| scene-policy/log.jsonl       | observation | every transition decision and outcome (LEO-241 curates; no schema yet)         |
| scene-policy/applied.json    | observation | the last applied state, what got stopped, to hand back (no schema yet)         |
| hyprfocus-held.json          | observation | windows a mode parked, with their recorded origins — an open-history           |
| dofus/team.json              | declaration | the declared team rotation                                                     |
| nvim/tools.json              | observation | tool presence per host, probe results with a generated_at                      |
| obsidian/ui.json + tags.json | observation | editor state and tags derived from use (owned by the scripts repo's stores)    |
| hypr/monitor-profile.json    | declaration | host monitor data                                                              |
| geometry.json                | declaration | per-monitor base left/right outer gap, published by conf/host.lua's `build()` (LEO-340); the bar mirrors it as its side inset, falling back to `Theme.barInset*2` when a monitor has no entry. Base gap only — never the transient solo widen from `hypr/events/solo_gaps.lua`. |

Schemas without a row here, or a row without a schema, are a defect of
the registry, not of the store: the gate test pins the schemas and the
table against each other. The scene-policy workspace's rows/applied/last
are named in schemas/scene-policy.schema.json (LEO-241); veto.json and
hyprfocus-held.json still carry their kind from this table only.

## Re-seeding a declaration (LEO-337)

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
(workspace names, mode deltas, presentation) has drifted enough that a store
seeded from an older file no longer matches what the host configs expect —
which is what happened when the workspace names changed but
`assets/hyprfocus.default.json`'s `version` did not, and the CLI had no
comparison to catch it. See `hyprfocus.md`'s "The one idea" for what the
declaration governs, and the quickshell sibling's `schemas/hyprfocus.schema.json`
for the `version` field itself.

`,hyprfocus seed` has no way to _locate_ the shipped default at runtime —
every known call site passes the source path explicitly (see
`hyprfocus-handoff.md`), and there is no installed or packaged path this
store re-seeds itself from. Calling the reseed check automatically on every
`hyprfocus` invocation, with no explicit source, therefore stays undone
until a discoverable shipped-default path exists; see the LEO-337 progress
comment on the issue for the record of that gap.
