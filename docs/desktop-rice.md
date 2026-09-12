<!-- The desktop programme: what the four repos are being taken toward, and in
     what order. Written here because no single repo owns it. -->

# The desktop programme

Four repos make one desk. This is the shape it is being taken toward, the order
the work happens in, and the tests that keep each step from undoing the last.

| Repo            | Owns                                               | Where work lands             |
| --------------- | -------------------------------------------------- | ---------------------------- |
| `hypr`          | Compositor config, keybinds, submaps, window rules | `hypr/*.lua`, `hypr/events/` |
| `quickshell`    | Bar, widgets, overlays, shared-state singletons    | `modules/`, `services/`      |
| `scripts`       | Standalone CLI helpers on `$PATH`                  | `bin/,*.sh`                  |
| `system-config` | Packages, `/etc`, fonts, theme assets              | `roles/`                     |

## The goal in one sentence

A desk with generous physical spacing, a single palette switch that reaches
every surface, a shell that scales from one number, and a focus mode that takes
options away — all deterministic enough that the same keystroke does the same
thing every morning.

## What is already right

The architecture does not need replacing. Three mechanisms already exist and are
under-used rather than missing:

- **`Store`** — one JSON file under `$XDG_STATE_HOME`, watched reactively by
  Quickshell and mtime-cached by the Lua side. Both runtimes already share state
  through it. Today it carries two fields.
- **`Theme.qml`** — four Catppuccin palettes, semantic roles, an IPC `cycle`.
  Everything needed for a theme switcher except the fan-out to non-QML surfaces.
- **`submap.tree`** — a which-key tree with descriptions, a passive peek
  overlay, and live follow-along as you traverse. The model is right; the timing
  and the depth of the common path are not.

## What is actually wrong

Every complaint traces to a hardcoded value, not a design flaw.

| Symptom                  | Cause                                                                       | Where                       | Today         |
| ------------------------ | --------------------------------------------------------------------------- | --------------------------- | ------------- |
| Shell text too small     | 75 literal `pixelSize:` values; `Theme` exposes no scale                    | `quickshell/modules/**`     | 10–17px       |
| No space between things  | Gaps tuned for a laptop, applied to a 5120×1440 panel                       | `hypr/hypr/conf.lua`        | in 2 / out 5  |
| Cheatsheet vanishes      | A fade timer that runs while you are still navigating the tree              | `hypr/hypr/events/peek.lua` | 2000 / 6000ms |
| Theme switch is partial  | `theme.json` drives the shell only; GTK/Qt/kitty/nvim are pinned in Ansible | `roles/theming/defaults`    | `macchiato`   |
| Bar is noisy             | 14 always-on modules on an opaque ground                                    | `modules/bar/Bar.qml`       | h 30, α 1.0   |
| Nothing is transparent   | Opacity globally disabled, though the event hook to drive it exists         | `hypr/events/opacity.lua`   | 1.0 / 1.0     |
| Regressions go unnoticed | `just check` is `fmt-check`; no tests in either desktop repo                | `hypr/`, `quickshell/`      | 0 tests       |

## Spacing is the headline

Not negative space in the compositional sense — physical distance between
elements, on the order of centimetres on the ultrawide. Two levers:

**Compositor gaps.** `gaps_in 2 / gaps_out 5` is the single most visible wrong
number in the tree. Target `gaps_in 12 / gaps_out 40` on the 5120×1440 panel
(≈ 1 cm inner, ≈ 3.5 cm outer at ~110 DPI), tighter on the laptop. These are
dials, not constants: set them per monitor through workspace rules and tune by
eye over a week.

**Column width.** A tiling layout cannot leave a lone window at half width
unless the layout is built for it. `hyprscrolling` is — it is installed and
already configured with `column_width = 0.5` and
`fullscreen_on_one_column = false`. A single window occupies half the panel and
the rest stays wallpaper. It is simply not the default on the primary
workspaces, which are `monocle` and `dwindle`. This is a configuration change.

**Shell spacing.** `Theme.gap` is 12 and `Theme.pad` is 16, but modules mostly
ignore them in favour of literals. The scale work in phase 1 is what makes shell
spacing adjustable at all.

## The one idea

`theme.json` widens from two fields to seven, and every surface becomes a reader
of it:

```json
{ palette, mode, day, night, scale, opacity, wallpaper }
```

Written by: the sun timer, the `SUPER+q t` bind, and a switcher UI.
Read by: Quickshell and Hyprland natively (both already watch the store), and by
everything else through one new script.

```text
sun timer  ─┐                          ┌─→ quickshell   (native watch)
SUPER+q t  ─┼─→  theme.json  ──────────┼─→ hyprland     (native watch)
switcher   ─┘         │                └─→ ,theme.sh apply
                      │                        │
                      └────────────────────────┴─→ kitty · nvim · gtk · qt · hyprpaper
```

`,theme.sh apply` is the only component that does not exist yet. It exists
because kitty, Qt and GTK need a process to poke them, and because the theme
must apply even while the shell is restarting — and because a script on `$PATH`
is runnable from tmux without a compositor.

## Phases

Ordered so daily irritations go first, and nothing later depends on anything not
already lived with for a week. Each phase ships on its own.

### P0 · Make it breathe

Value changes only, no new code.

| File                             | Setting                      | Change          |
| -------------------------------- | ---------------------------- | --------------- |
| `hypr/hypr/conf.lua`             | `general.gaps_in / gaps_out` | 2 / 5 → 12 / 40 |
| `hypr/hypr/conf.lua`             | `decoration.rounding`        | 4 → 6           |
| `hypr/hyprland.lua`              | `config.peek_delay_ms`       | 2000 → 350      |
| `hypr/hypr/events/peek.lua`      | `arm_fade` on navigation     | remove          |
| `quickshell/modules/bar/Bar.qml` | bar `Rectangle.color`        | opaque → α 0    |
| `quickshell/modules/bar/Bar.qml` | `implicitHeight`             | 30 → 38         |

The peek change matters most. The cheatsheet currently fades on a timer that
does not care whether you are still deciding. Replace it with: appear after
350 ms of dwell, **stay for as long as you are in the submap**, fade 400 ms
after leaving. That is which-key's contract, and it fixes "doesn't stay long
enough" by deleting the timer rather than lengthening it.

### P1 · One scale knob

Add a type and space scale to `Theme.qml`, then replace all 75 literals.

- `Theme.scale` — store-backed, default `1.25`. Lifts 12px labels to 15px.
- `Theme.fs` — `xs sm md lg xl`, derived from `scale`. Widgets stop naming pixels.
- `Theme.space` — same five steps; `gap` and `pad` become `md` and `lg`.
- `Theme.radius` — `2` → `6`. Low on purpose; only `radiusPill` carries a real curve.
- `qs -c quantumfate ipc call theme scale 1.35` for live tuning.

After this the shell resizes from one number, and a future 4K panel is a config
line rather than a rewrite.

### P2 · The one-button theme

Widen `theme.json`, write `,theme.sh apply`, unpin the Ansible role.

| Surface   | Mechanism                                                                   |
| --------- | --------------------------------------------------------------------------- |
| kitty     | `kitty @ set-colors -a` on every socket — live, no restart                  |
| GTK       | `gsettings` for `gtk-theme` and `color-scheme`                              |
| Qt        | rewrite qt5ct/qt6ct `color_scheme_path`, Kvantum `theme`, poke `xsettingsd` |
| Hyprland  | `hyprctl keyword general:col.active_border`                                 |
| Neovim    | `lua/theme/` gains a store reader and a watcher                             |
| Wallpaper | one per palette, swapped over `hyprpaper` IPC                               |

`roles/theming` stops pinning `theme_flavour: macchiato` and instead installs
every flavour plus the fan-out. Ansible provisions the capability; the store
picks at runtime. Day/night is a systemd user timer calling `,theme.sh auto`,
which honours a manual override until it is cleared.

### P3 · Space on the ultrawide

- Flip the primary-monitor workspace specs in `hyprland.lua` to
  `layout = "scrolling"`; keep `monocle` on the cycle key.
- Per-monitor gaps through workspace rules — no branching logic.
- For non-scrolling layouts, an event handler that widens `gaps_out` when a
  workspace holds exactly one window. Same shape as `events/opacity.lua`.
- Promote the five most-used actions out of their submaps into direct `SUPER`
  chords, leaving the tree as the discoverable path. The tree is not the
  problem; the depth of the common case is.

### P4 · Transparency, done as a table

One Lua map from window class to _role_, with opacity per role, all scaled by
`theme.json.opacity` — one dial, and a hard `0` for presentation mode.

The rule that keeps it from looking cheap: **nothing that renders images or
video gets transparency.** Terminals and the editor at 0.92–0.95; browser,
media and games fully opaque. The blur is already well tuned (size 6, 3 passes,
`noise 0.02`), which is the other half of why most transparency looks bad.

Wallpapers get flattened rather than re-hunted: a blur-and-desaturate pass at
theme-apply time into `~/.cache/wallpapers/<palette>/`, tinted toward the
palette's base. Keeps the anime vibe, kills the local contrast that makes a
transparent bar unreadable, costs nothing at runtime.

### P5 · Stores: projects, focus, sound

Three new state files, same `Store` pattern, none of them in git.

- **`projects.json`** — name, path, kind, tmux template, `study`, priority.
  Becomes the source for `,proj.sh` (which scrapes the tms config today), for
  the dashboard, and for the morning layout.
- **Project dashboard** — branch, dirty count, ahead/behind, age of last commit,
  per directory. Collected by a `,proj-health` timer writing
  `projects-health.json`; the widget only reads. Git status across eleven repos
  including a kernel tree must never run on the UI thread.
- **`focus.json`** — `{ mode, until }`. Focus mode takes things away: media
  browser and game launchers refuse to start and say why, DND on, the bar drops
  to clock, workspace and submap, the media workspace stops being reachable.
  Enforced at dispatch time, not build time, so leaving focus needs no reload.
- **`sound.json`** — rain and lofi through a long-lived `mpv` over local files,
  driven by IPC, shown as one bar pill. Local files, not streams: offline, no
  telemetry, instant.
- **Morning** — `events/start.lua` reads `projects.json` and `focus.json` and
  puts the study project on workspace 1 with its nvim window already up.

State lives in `$XDG_STATE_HOME` and stays out of git. Backups are an `age`
-encrypted tarball behind a `just state-backup` recipe: one keyfile to guard,
one blob that can be pushed anywhere.

### P6 · The bar, rebuilt

With the bar transparent and scale tokens in, rebuild it as floating pills on
wallpaper rather than a strip of fourteen things.

- Collapse SysMonitor, Weather, Brightness, PowerProfile, IdleInhibit and
  Language into one status pill that expands on hover. `Cluster`, `HoverTip`
  and `SysPanel` already exist to build it from.
- New: calendar pill (local first, CalDAV later), focus indicator, sound pill,
  projects pill opening the dashboard.
- Keep: workspaces, submap indicator, window strip, tray, clock, wlogout —
  the ones that answer "where am I".

## Visual direction

Catppuccin stays. Latte by day, Macchiato by night. The look to aim for is calm
and spacious with a technical edge — pastel surfaces, generous gaps, a
transparent bar floating over a low-contrast wallpaper, monospace throughout,
and restraint on radius. Corners stay near `6`; nothing becomes a lozenge except
the pills that are meant to read as pills.

The nerdy catch is content, not chrome: real numbers on display where they earn
their place — kernel version, load, temperature, git state across the project
set, session uptime. Information density in the widgets, emptiness in the
layout.

## Preventing regressions

Neither desktop repo has tests. `just check` is `fmt-check` in both, `luacheck`
is advisory in `hypr`, and there is no QML linting at all. Meanwhile the nvim
repo gates 202 tests. That gap is why a phase can silently undo an earlier one.

The pipeline grows with the phases, each check earning its place by guarding a
change that was just made:

| Check                                 | Guards                                                                                   | Lands with |
| ------------------------------------- | ---------------------------------------------------------------------------------------- | ---------- |
| `qmllint` over `modules/` `services/` | Unqualified property access, bad imports, typos in a language with no compiler           | P0         |
| No-literal grep gate                  | `! grep -rn 'pixelSize: [0-9]' modules/` — the scale work cannot rot                     | P1         |
| Palette contract test                 | Every palette has identical key sets; every semantic role resolves                       | P1         |
| `CheatParse.js` unit tests            | Cheatsheet parsing and column splitting, in plain node                                   | P1         |
| Store schema validation               | `theme.json`, `projects.json`, `focus.json` against JSON Schema                          | P2         |
| `luacheck` gated, not advisory        | Typos in the Lua that builds every bind                                                  | P3         |
| Lua unit tests for `hypr/lib/`        | `store`, `bind`, `submap`, `layout` — pure Lua, no compositor needed                     | P3         |
| Bind collision test                   | No duplicate `lhs` within a submap — the failure mode that hides until you press the key | P3         |
| `shellcheck` gated                    | The theme fan-out script, which touches five subsystems                                  | P2         |

Two shapes to copy from the nvim repo, which already solved this: a
`tests/run.lua` that drives each spec in its own process, and a `just check`
that is the CI gate and the pre-commit hook at once.

Screenshot-diffing the bar under a headless compositor is possible and is
deliberately not on this list — high effort, reliably flaky, and the checks
above catch more for less.

## Out of scope

The Dofus workspace stays exactly as it is. The eight-client setup, the swap
detector, `DofusTaskbar`, the `DP-1` taskbar mapping, its gaps and its opacity
are excluded from every rule above; the per-monitor and per-workspace conditions
already exist to do that cleanly. Focus mode blocks _launching_ games and never
touches a running session.

## Open decisions

1. **Where the theme fan-out lives** — a script in `scripts` (headless, works
   from tmux) or a Quickshell `Process` service (one runtime, dead while the
   shell restarts). The script is the recommendation.
2. **Whether `projects.json` replaces the tms config or mirrors it** — replacing
   gives one source of truth and means editing `,proj.sh`; mirroring is safer
   and means two files that can disagree, which is the failure mode `,proj.sh`
   already warns about in its own comments.
3. **How aggressive focus mode is** — soft (notify, let through), firm (refuse,
   with an override key), or hard (refuse until the timer expires).
4. **Where encrypted state backups go** — the recipe is easy, the remote is a
   preference.
