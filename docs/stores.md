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

| store                          | kind         | what it is                                                                       |
| ------------------------------ | ------------ | -------------------------------------------------------------------------------- |
| hyprfocus.json                 | declaration  | the whole desk's declaration: resources, scenes, mode policy, leases             |
| mood-policy.json               | declaration  | per-mood policy (notifications, launches, background work, scene reachability)   |
| scenes.json                    | declaration  | the scene document: window geometry per mode                                     |
| theme.json                     | declaration  | the theme pointer: palette, day/night, scale, wallpapers the user bound          |
| hyprfocus.json (packs)         | declaration  | theme packs: assets/packs/*.json, committed with the code they name              |
| sound.json                     | declaration  | sound defaults and the declared pool                                             |
| notify-prefs.json              | declaration  | the DND choice — the desk saying what it should do (LEO-281 split)               |
| focus.json                     | observation  | the pointer: the active mode, who set it, when — a diary of how the desk moved   |
| notifications.json             | observation  | message content: summaries and bodies, capped at 100 entries, erasable (Clear)   |
| theme.result.json              | observation  | what an apply actually did — the truth the shell reports                         |
| whichkey.json                  | declaration  | a cache of the binding trees the compositor declares; derived, no behaviour       |
| scene-policy/veto.json         | observation  | resources refusing to stop, in their own words (LEO-256)                          |
| scene-policy/last.json         | observation  | what the last transition held back (LEO-256)                                      |
| scene-policy/log.jsonl         | observation  | every transition decision and outcome (LEO-241 curates; no schema yet)           |
| scene-policy/applied.json      | observation  | the last applied state, what got stopped, to hand back (no schema yet)           |
| hyprfocus-held.json            | observation  | windows a mode parked, with their recorded origins — an open-history             |
| dofus/team.json                | declaration  | the declared team rotation                                                        |
| nvim/tools.json                | observation  | tool presence per host, probe results with a generated_at                         |
| obsidian/ui.json + tags.json   | observation  | editor state and tags derived from use (owned by the scripts repo's stores)       |
| hypr/monitor-profile.json      | declaration  | host monitor data                                                                 |

Schemas without a row here are a defect of the registry, not of the
store: the gate test pins them against each other, and the un-schemad
observation files (the scene-policy trio, hyprfocus-held) carry their
kind in this table until their own curation issue names them in schemas
(LEO-241 for the log workspace).
