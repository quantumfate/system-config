<!-- Where the hyprfocus build actually stands, for a session that was not
     there. Read hyprfocus.md first for the design; this is the state. -->

# hyprfocus: state of the build

Read [hyprfocus.md](hyprfocus.md) for the design. This says what exists, what is
switched on, and what to do next.

## Working today

Entering a mode is one action and drives both halves of the desk.

```sh
,hyprfocus seed ~/Projects/codeberg/quantumfate/quickshell/assets/hyprfocus.default.json
hyprctl reload
```

`SUPER+f` opens the modes tree, one key per declared mode (first free letter of
its id). Entering one withdraws workspaces, withholds binding trees, parks the
windows on withdrawn workspaces, and stops the background work the mode does
not want.

**The way out is `SUPER+CTRL+SHIFT+escape`.** It returns to neutral, is bound
at root where no mode can withhold it, and works from inside any submap. It
exists because an earlier version trapped the desk badly enough to need a
reboot.

From a TTY, with no compositor: `,hyprfocus apply neutral`.

| Verb                        | Does                                   |
| --------------------------- | -------------------------------------- |
| `,hyprfocus modes`          | every declared mode, active one marked |
| `,hyprfocus resolve <mode>` | the complete desk that mode means      |
| `,hyprfocus plan <mode>`    | what a transition would change         |
| `,hyprfocus apply <mode>`   | the background-work half               |
| `,hyprfocus explain`        | which mode is on, who set it, when     |
| `,hyprfocus seed <file>`    | install a declaration                  |

## What is switched on, and what is not

| Piece                                     | State                                                   |
| ----------------------------------------- | ------------------------------------------------------- |
| Declaration, resolver, planner            | live, 263 tests in `hypr`                               |
| Mode entry on `SUPER+f`                   | **live**                                                |
| Workspace withdrawal, window hold/restore | **live**                                                |
| Binding tree withholding                  | **live**                                                |
| Background work                           | **live**, through the CLI                               |
| Scene layout provider                     | **live on the `code` workspace only**                   |
| Notification identity                     | recorded on every notification                          |
| Notification routing                      | explicit per-source rules only; `default` not consulted |
| Mode palette lease                        | designed, not built                                     |
| Calendar schedule                         | designed, not built                                     |

## The two rules that keep it out of trouble

**A mode names what it takes, never what it keeps.** `base.bindings` lists the
trees _under mode control_; a tree outside that list can never be withheld.
This is inverted from the obvious design on purpose — a tree missing from the
declaration is far more likely to be an oversight than an intention, and the
two mistakes cost wildly different amounts. An unnamed tree left enabled means
a mode takes away less than it meant to. One wrongly removed means no terminal
and no way back.

**A workspace holding windows is never withdrawn.** It is emptied first and
withdrawn second, because disabling it with windows on it leaves them somewhere
unreachable. `apply` tracks what it emptied rather than re-reading occupancy: a
move is dispatched, not performed, so asking the compositor in the same breath
returns the desk as it was a moment ago.

## Needs a human at the machine

Three things that cannot be settled without a running compositor:

1. **Gaps on the `code` workspace.** The provider reads `general:gaps_in` /
   `gaps_out` and applies them to `ctx.area`. If Hyprland already insets that
   area, gaps will look roughly doubled. Visible immediately; fix is to stop
   applying `gaps_out` in `hypr/scene/layout.lua`.
2. **Whether a group arrives as one layout target or several.** Both are
   handled (collapse for slotting, expand for placing) but only live use says
   which happens. Symptom would be the terminal group tiling wrongly.
3. **Falling back.** Set `layout = "dwindle"` on the `code` workspace in
   `hyprland.lua` and reload. The provider stays registered; nothing else
   depends on it.

## The gate that now covers this

`tests/config_smoke_spec.lua` loads `hyprland.lua` for both hosts through the
stub. Every other spec loads one module, which is why three separate
config-load failures reached a live desk instead of the suite.

It only works because the stub carries two pieces of the runtime's own
strictness — without them the spec passes on a config that cannot start:

- **keys are validated**, because Hyprland rejects a bind it cannot parse
- **`hl` refuses assignment** (opt-in per spec), because the runtime's table is
  read-only

If you add anything to the config that the stub does not implement, the smoke
spec fails with a nil-call rather than a useful message. Add the method to the
stub; that failure is the spec doing its job.

## Lessons the hard way

Both of these cost a broken desk, so they are worth not relearning.

**`hl` is read-only in the Hyprland runtime.** Assigning to it raises at config
load and takes down every module required after — the desk comes up with no
workspace rules and no keybinds. Never wrap a runtime function; route through
your own module instead, even when that means touching ten call sites.
luacheck reports this as "setting read-only field hl". It is not a style
warning.

**Withholding defaults to off, never on.** A resource the declaration does not
mention is far more likely to be an oversight than an intention. An unnamed
thing left enabled means a mode takes away less than it meant to; one wrongly
removed can mean no terminal and no way back.

## Known-wrong, already recorded

- **`theme-auto.*` and `state-backup.*` do not exist on this machine**
  (`LoadState=not-found`). The contract has named them for as long as it has
  existed. This is the missing-owner problem and it is urgent in the tracker.
- The resolver exists **twice** — Lua for the compositor, Python for the CLI —
  because the CLI must work with no compositor. Nothing compares them. Either
  share conformance fixtures or have the CLI shell out to `lua`.
- A **timer cannot override a schedule-set mode**. Inferred while building
  precedence, never specified. If a pomodoro ends while the calendar says
  "deep", the timer cannot return you to neutral.

## Where the code is

```text
hypr/hypr/hyprfocus/     resolve · plan · binds · workspaces · hold · init
hypr/hypr/scene/         spec · compile · layout · provider · model · registry
quickshell/services/     Hyprfocus.qml · HyprfocusRead.js · NotifyRoute.js
                         ModePrecedence.js
quickshell/schemas/      hyprfocus.schema.json
quickshell/assets/       hyprfocus.default.json      the seed
scripts/bin/,hyprfocus   the command line
scripts/etc/             scene-managed.json          task → units
```

Pure and testable: `resolve`, `plan`, `layout`, and the `.js` libraries. They
take tables and return tables, with no compositor and no IO. Anything touching
`hl` or systemd is a thin shell over one of them, and new logic belongs in the
pure half.

## Next, in order

1. Confirm the `code` workspace lays out correctly, or fall back.
2. Decide where user units live — nothing owns them, and two are fiction.
3. Hold-and-restore across a shell restart, with real windows.
4. The mode panel: edit the declaration from the shell.
5. Palette lease, then theme packs.
