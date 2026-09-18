<!-- The attention engine: what may exist on the desk at a given moment, and
     how the system converges on it. Lives here because no single repo owns it
     — it spans the compositor, the shell, the scripts and the unit files. -->

# hyprfocus

A desk that takes things away.

The name is the point: ADHD hyperfocus is not a shortage of attention but an
inability to choose where it lands. So the system's job is not to present more,
it is to **make the wrong thing unavailable** — precisely, reversibly, and
without asking for willpower at the moment willpower is least available.

## The one idea

A **mode** declares a desk. The system converges on that declaration.

This is a materialisation model, not a permission model. The difference
matters: a permission model asks "may I open Obsidian?" and needs a gate in
front of every action. A materialisation model does not load the Dofus submap
outside game mode, so there is no key to press and nothing to ask. Gates remain
only for the few things that escape declaration — a launcher spawned from a
terminal — and are a backstop, not the mechanism.

```text
declaration                     reconciliation
─────────────                   ──────────────
mode "game"                     reconcile(running, resolved)
  workspaces  gaming, comms       ├─ workspace rules   enable/disable
  scenes      gaming              ├─ layout provider   reads the scene
  bindings    global, nav, dofus  ├─ keybinds          enable/disable
  services    −obsidian −sync     ├─ systemd (uwsm)    stop/start, with grace
  notify      none                └─ shell             route/queue/digest
  projects    —
```

Everything the desk can show or run is a **resource**. A mode is a set of
resources. A transition is a diff.

## Why this is one system and not four

Today the same intent is spread across four mechanisms that each emulate part
of it and race each other: workspace rules hold gaps, an event layer rewrites
those gaps by tile count, another rewrites global layout options around the
moment a layout reads them, and a scene engine measures the result and
dispatches corrections. They race because each writes shared state at event
time and then reads what the others left behind.

One declaration and one reconciler removes the race by construction: there is a
single writer per resource, and it is asked to produce a whole desk rather than
to nudge a running one.

## Vocabulary

| Term          | Means                                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------------ |
| **hyprfocus** | the engine as a whole                                                                                        |
| **mode**      | a named declaration of what may exist (`neutral`, `deep`, `game`, `llm`, …)                                  |
| **resource**  | anything a mode admits or withholds: a workspace, scene, binding tree, service, notification source, project |
| **scene**     | how windows are arranged on one named workspace — geometry only                                              |
| **resolve**   | fold base + mode into one complete declaration                                                               |
| **reconcile** | diff the resolved declaration against reality and act on the difference                                      |
| **hold**      | park a revoked window out of sight, alive, restorable                                                        |
| **retire**    | stop a revoked resource gracefully, with a veto and a deadline                                               |

`mode` is the word, everywhere. The engine is `hyprfocus`; a mode is one of its
states.

## What a mode declares

| Resource    | Admitted by                                 | Withheld by                                                           |
| ----------- | ------------------------------------------- | --------------------------------------------------------------------- |
| `workspace` | enabling its workspace rule                 | disabling it; windows on it are held                                  |
| `scene`     | the layout provider reading its declaration | the workspace going away                                              |
| `bindings`  | enabling that tree's keybinds               | disabling them — the key does nothing, and which-key stops listing it |
| `service`   | `systemctl --user start` under uwsm         | stop, with grace and a veto                                           |
| `notify`    | a routing rule per source                   | dropping or digesting, never silently losing                          |
| `project`   | opening it on its scene                     | not opening it; already-open ones are held                            |

Every one of these is mechanically supported at runtime. The Hyprland Lua API
returns a handle from `hl.bind`, `hl.window_rule`, `hl.workspace_rule` and
`hl.layer_rule`, and **all four carry `set_enabled`** — so a mode change
materialises a desk without a config reload.

## Base plus delta, scene sets outright

One `base` declares the whole desk: the scene catalog plus every binding tree,
service and project. Each mode names its **scene set** outright, each scene on a
monitor role, and states everything else as a difference from the base
(declaration version 3).

`base.scenes` is the desk's only scene table: the hypr scene layout, rule
compiler and companions read it, and so do scene bindings and the resolver.
The old `scenes.json` store is retired and folded in once on load.

```text
base
  scenes      code proton obsidian-linear logs dofus pokemon media …
  bindings    global nav window layout dofus shelf-ankama shelf-steam shelf-lutris
  services    theme-auto obsidian obsidian-index linear-sync state-backup

mode gaming
  scenes      dofus@primary pokemon@primary media@secondary …
  services    − obsidian − obsidian-index − linear-sync
  notify      none

mode neutral  (hidden)
  scenes      code@primary proton@primary logs@secondary
  bindings    − dofus − shelf-ankama − shelf-steam − shelf-lutris
```

The workspaces a mode admits are derived from its scene set (a scene's name is
its workspace's name). `monitor` is a host role (`primary`, `secondary`), never
an output; the mode's role wins over the host file's workspace pin, a missing
output falls back to primary, and the scene moves back when the monitor
returns. `neutral` is `hidden`: the recovery fallback, never listed as a peer
and never a default. **Login always enters `work`**, unless the pointer
names a timed mode still running (`until` in the future), in which case that
mode resumes as itself and keeps its own `previous`; a stale/expired timed
pointer, a missing store, or a pointer naming an unknown mode all boot to
`work` too — never to `previous`, and never to `neutral`. The picker offers
`work`, `study` and `gaming`. Once the desk is running, a timed mode's
expiry (not a boot) falls back to whichever mode was active before it (the
pointer's `previous`), or to `work` when nothing was recorded — this is the
hypr repo's `hypr/hyprfocus/init.lua` `effective_mode`; the boot decision is
`hypr/hyprfocus/boot.lua`, a separate rule applied once by `hyprland.start`.

A mode is **refused whole** at resolve time when its set is malformed: an
unknown scene or monitor role, a scene listed twice, or two listed scenes
claiming the same block class string (compared textually). The refusal is an
`admit/mode_refused` record naming the mode, the class and both scenes. The
token table lives in the hypr repo's `docs/scenes.md` ("Validation").
Known gap: pokemon's browser blocks claim `slot:pokemon/*` tag strings until
launch identity stamping lands, because they share a class with dofus's.

**Deltas are a writing convenience and never a runtime concept.** The
reconciler resolves base + mode into a complete declaration _first_, then diffs
that against reality. Applying deltas incrementally would make the result
depend on the order they were applied, which is the whole class of bug this
design exists to remove.

For the delta kinds (bindings, services, projects) `only` is exclusive
(nothing else survives); `+` and `−` are additive. A mode that lists neither
keeps the base.

## Dependencies: composition here, ordering in systemd

"Obsidian" is not one thing. It is a window, an indexer and a sync timer, and
you want to say `obsidian` and get all three. Two different problems hide in
that, and only one of them is ours.

**Composition** — what admitting a resource implies — is declared once, next to
the thing it belongs to, at one of two strengths:

```text
requires   cannot function without it
  binding:dofus     ->  scene:dofus

wants      uses it, runs without it
  service:obsidian  ->  service:obsidian-index, service:linear-sync
```

The two strengths mirror systemd's `Requires=` and `Wants=` rather than
inventing a vocabulary, and the difference is load-bearing. A mode that
explicitly removes something **required** is a conflict, reported rather than
guessed at. A mode that removes something merely **wanted** wins, silently.

`wants` is the common case and the one to reach for first. Obsidian without its
indexer is degraded, not broken — which is precisely why a media mode can keep
the window on screen and stop the indexing and the sync to reclaim resources.
Modelling that as a hard requirement would make behaviour that already ships
impossible to express. "The services it uses" is usually `wants`; reserve
`requires` for the cases where the thing genuinely does not work.

The resolver takes the transitive closure, so a mode that opens Obsidian gets
its services without naming them, and every other mode that opens Obsidian does
not repeat them. References are qualified (`service:`, `project:`, `scene:`, `binding:`)
because these edges cross kinds. A `scene:` reference is checked, never added:
a mode that admits something requiring a scene it does not list is refused.

**Ordering, readiness and failure** between a capability's units are _not_
ours. `Requires=`, `Wants=`, `After=`, `BindsTo=` and `PartOf=` already express
them, and a resolver that sequenced units would be reimplementing `After=`
badly. So a capability maps to a target, the reconciler starts and stops the
target, and systemd does the rest.

The rule, in one line: **we compute a capability set; systemd computes units.**

That boundary is also the right one for editing. Which services run in study
mode is a preference, edited live in the declaration. What "obsidian" consists
of is a system fact, edited in unit files and provisioned. Those are different
kinds of change and should not live in the same file.

### Who owns a unit file

The engine starts and stops units, so the units it names have to be owned where
they can be checked against the declaration that names them. The dividing line
is the declaration, not the tool:

| Unit                          | Owner                                                    |
| ----------------------------- | -------------------------------------------------------- |
| named by a declaration        | the programme — gated and diffed against the declaration |
| named by no declaration       | the dotfile manager, unchanged                           |
| a generated capability target | the programme, always                                    |

A generated file among hand-edited templates reads as editable, and the next
apply clobbers whatever was changed — so generated targets never live in a
dotfile manager's source state.

Whatever the split, **exactly one mechanism may write each path** under
`~/.config/systemd/user`. Two tools producing the same unit means the last one
run wins, which presents as systemd behaving differently on different days
rather than as a configuration conflict. That is worth a check rather than an
assumption.

Most programs need no unit at all. A window you open is a transient `uwsm app`
scope that dies with the session; only long-running background work earns a
unit file.

### When a requirement meets a refusal

`only` and `remove` are treated differently on purpose. `only` says what to
inherit, so the closure may widen it — a narrow mode still ends up with a
working app. `remove` is an explicit statement that something should not be
there, so a requirement contradicting it is reported rather than resolved
either way: adding it ignores what the mode said, and omitting it breaks
whatever needed it. Neither is a safe default.

## Colour is part of the declaration

A mode changes what may have your attention, and colour is how the desk says
so before you have consciously read anything. That makes the palette a
declared resource rather than decoration — but it is the one resource with an
existing owner, and that is what needs settling.

Today `presentation` carries `accent_role`, `surface_alpha`, `density`,
`motion_energy` and `bar_autohide`. A mode can therefore **tint** the desk, but
`accent_role` names a role _within whatever palette is active_ — it cannot
select a palette. The palette lives in the theme store and is driven by a sun
timer through `day` and `night`.

### Themes are packs, adapted into one interchange language

There is no abstraction that accounts for every theme. Ecosystems speak their
own vocabularies — Catppuccin's `base`/`mantle`/`crust`/`surface0` is not
anyone else's — so an adapter is needed whatever we do. Accepting that up front
is what keeps the architecture small: define one internal language, adapt
everything into it, and let each ecosystem keep its own names on its own side
of the boundary.

The language is a **slot set**, not semantic names: a background ramp and the
named hues. Surfaces then reference _roles_ derived from slots rather than
colours directly, which is what gives consistency between elements — not every
combination of colours works, and a role indirection is what stops one being
assembled by accident.

**A pack is a family; a variant is one palette in it.** Every variant declares
whether it is light or dark, and the day/night cycle picks between them. A pack
that offers only one kind is not an error: the cycle takes what is there.

```text
pack  catppuccin
  frappe     dark    ─┐
  macchiato  dark    ─┼─→  light counterpart: latte
  mocha      dark    ─┘
  latte      light
```

Catppuccin is the shape that proves the model: three dark variants and one
light, so each dark names the same counterpart rather than the pack pretending
to four pairs it does not have.

Resolution never fails. Wanting a kind, take the variant's own counterpart, or
the pack's fallback for that kind, or any variant of that kind, or the variant
already in hand. A desk with a theme it cannot pair is better than a desk with
no theme.

### Sixteen slots is one too few

The obvious interchange language is base16, and it is the wrong size here for a
specific reason: this desk uses colour to signal which mode is on, and base16
has eight hues with no lavender and no pink.

`neutral` is lavender and `deep` is blue; `reflect` is mauve and `media` is
pink. Through base16 each pair collapses to one slot, so two pairs of modes
become visually identical — which defeats the entire purpose of tying colour to
attention state. The background ramp fares no better: nine Catppuccin levels
flatten to about four, and the shell distinguishes six.

**base24** is a superset that resolves both. Its extra dark slots restore the
`mantle`/`crust` depth, and its bright hue variants are where lavender and pink
land without colliding with blue and mauve. Same adapters, same ecosystem, no
collapse.

The general rule this is an instance of: an interchange format must be at least
as expressive as the distinctions the system actually relies on. Colour here is
not decoration, so losing two distinguishable modes is a functional regression,
not a cosmetic one.

### A mode leases the palette, it does not own it

The rule is the same shape as the mode pointer's, for the same reason: two
writers, one value, and the one that must not be silently destroyed is the
user's own baseline.

```text
baseline    the palette you chose, and the sun timer's day/night
lease       the palette a mode asks for, while it runs
in effect   lease if a mode holds one, otherwise baseline
```

**A mode never writes the baseline.** If it did, the next sun tick would either
fight it or bury it, and leaving the mode would restore the wrong thing — the
user would lose the palette they actually picked to a mood they were in an hour
ago. A mode's palette is held for its duration and given back, exactly as a
held window is.

The sun timer keeps running underneath. Entering a mode at noon and leaving it
after dark should land on the night palette, not on the one that was in effect
when the mode began, because the baseline moved while the lease was held.

### One fan-out, not two

`,theme.sh apply` already reaches kitty, GTK, Qt, Hyprland, Neovim and the
wallpaper. A mode-driven palette goes through it. A second path would mean the
shell following the mode while every other surface follows the store, which is
worse than not theming by mode at all — a desk that half-changes reads as
broken rather than as signalling.

### Legibility is a constraint, not a preference

Tying colour to attention state is effective precisely because it bypasses
deliberate reading, which is also why an unreadable combination is worse here
than elsewhere: the signal is trusted before it is examined. Any palette a mode
can select has to clear the same contrast floor as the rest of the palette
work, and a mode that can only be entered into an illegible desk is a bug, not
a taste question.

## Not everything belongs to a mode

Two axes, and confusing them drags transition machinery into things that should
be instant.

| Axis             | Follows            | Machinery                         |
| ---------------- | ------------------ | --------------------------------- |
| **focus-scoped** | the focused window | none — it just follows focus      |
| **mode-scoped**  | the declaration    | reconciled, with phases and grace |

A note-creation binding that only means something while the Obsidian window is
focused is focus-scoped: it needs no transition, no grace period and no
reconciler, the same way an editor's buffer-local mapping does not involve the
plugin manager.

The test for which axis something belongs on is **does it cost anything while
idle**. A keybinding costs nothing, so it can follow focus. A sync timer costs
wakeups and network, so it is declared and reconciled.

## Transitions have phases

A transition is never a single act. Stopping things abruptly is how a system
that is supposed to reduce anxiety produces it.

```text
1  announce   the shell says what is about to change, and what it will take
2  grace      revoked resources are asked to wind down, with a deadline
3  veto       anything with unfinished work may refuse, and is left alone
4  act        hold windows, stop units (SIGTERM + TimeoutStopSec, never KILL)
5  admit      start what the new mode adds; wait on readiness, not on a timer
6  log        every decision, appended, inspectable
```

A resource that vetoes is recorded, surfaced once, and left running. The mode
is still considered entered — a single stubborn unit must not wedge the desk in
a half-state.

## Revocation: hold or retire

Two behaviours, declared per resource rather than chosen globally.

- **hold** — the resource is parked, alive, with enough state recorded to put
  it back exactly as it was. Correct for cheap windows whose state lives in
  them.
- **retire** — the resource is asked to stop. Correct for anything whose cost
  is the reason it is being revoked: a sync timer, an indexer, a language-model
  runtime.

The two differ in **how a resource is given up, not in whether it returns.**
What comes back is decided entirely by the next desk: leaving game mode
re-admits Obsidian because neutral declares it, whichever way it was revoked.
The difference is what you get back — a held window returns where it was, a
retired service starts fresh.

Resource saving requires retiring. Holding a window keeps its memory and its
wakeups; it buys attention, not capacity. Both are wanted, for different
things, so the schema names which per resource instead of picking one.

## Notifications need identity before they need policy

Routing notifications by application name does not work, and it is worth being
precise about why: `app_name` in the freedesktop notification spec is
**self-reported, unauthenticated free text**. `notify-send` sets it to whatever
`-a` says, or to nothing. Two programs can claim the same name, one program can
change its name between releases, and a shell script has no name at all unless
it invents one. A routing table keyed on that string is unmaintainable, which
is exactly the symptom.

The fix is to resolve a **source id** through an ordered chain, and route on
that:

| Order | Key                       | Why it is trusted                                                      |
| ----- | ------------------------- | ---------------------------------------------------------------------- |
| 1     | `desktop-entry` hint      | the `.desktop` file id; set by the toolkit, stable across releases     |
| 2     | `x-hyprfocus-source` hint | our own convention, mandated for every script we ship                  |
| 3     | `category`                | a spec-defined vocabulary (`email.arrived`, `im.received`, `device.*`) |
| 4     | `urgency`                 | three values, always present, never identity — only severity           |
| 5     | `app_name`                | last resort, and recorded as untrusted                                 |

Both `desktopEntry` and `hints` are exposed by the shell's notification server,
so this is available today and is not being invented.

**The rule for everything we write:** every script that notifies passes a
stable source id and a category, and never relies on its own name.

```sh
notify-send -a hyprfocus \
  -h string:x-hyprfocus-source:linear-sync \
  -h string:category:x-hyprfocus.sync \
  "Sync finished" "42 issues updated"
```

A mode then routes on source id and category, not on strings that happen to
appear. Four verdicts:

- **show** — a toast, positioned per the mode
- **queue** — held back, delivered as one digest when the mode ends
- **digest** — counted only; the summary says how many
- **drop** — no toast

**History is never conditional.** Every notification is recorded with the
verdict that was applied to it, whatever the mode said. Suppression is about
what interrupts, never about what is knowable afterwards — a mode that hid
something must be able to show you what it hid.

## Scenes are the geometry half, and nothing else

A scene says how windows sit on one named workspace. It does not decide whether
that workspace exists — the mode does.

The engine is a **layout provider**, registered with `hl.layout.register`. The
compositor asks it where windows go, handing it the work area and the list of
tiled targets; it answers. That inverts today's design, which measures the
result of some other layout and dispatches corrections at it.

What the inversion removes: settle and verify timers, geometry digests, turn
budgets, the focus-dance (positioning dispatchers act on the focused window, so
every correction had to steal and restore focus), ordering via `movewindow`
(which at a monitor edge throws the window onto the next monitor), and the
separate event layers for single-tile gaps and per-workspace layout options —
both of which become branches inside the one function that already decides
every box.

Grouping stays separate and stays declarative: a group is a compositor concept,
and a group arrives at the layout as a single target.

## Bindings belong to what they act on

A binding tree is a resource, so it can be admitted by a mode or by a scene.
The Dofus submap is not globally useful; it is meaningful when a Dofus group is
on screen and meaningless otherwise. Outside game mode its keybinds are
disabled and which-key does not list them — the same model as editor-local
mappings, where a buffer brings its own bindings and takes them away again.

This also means which-key becomes accurate by construction rather than by
filtering: the tree it renders is the set of enabled binds.

## Projects are part of the declaration

A coding scene names which projects open on it. Project definitions already
live in their own store; the scene references them by name, and the reconciler
opens what is missing and holds what is no longer named. "Which projects are
actually open" stops being an accident of what survived the last session.

## Automation: the calendar drives the mode

The active mode is a pointer, and a pointer can be written by anything. A
schedule derived from a calendar is one more writer.

```text
manual  ─┐
timer   ─┼─→  active mode  ──→  reconcile
calendar ┘
```

Precedence is explicit and one rule: **a manual choice wins until it expires or
is cleared.** Otherwise the desk would silently undo a deliberate decision at
the next calendar boundary, which is precisely the kind of surprise the system
exists to prevent. Every write records its source, so the shell can say _why_
the desk is in the mode it is in.

## Special workspaces retire

Special workspaces were a manual way of keeping things nearby but out of the
way. Once the engine decides how many workspaces exist, that is what they were
for. They are replaced by ordinary workspaces admitted per mode, plus `hold`
for revoked windows — one mechanism instead of two, and no hand-management.

## What may be committed

Anything derived from observed use is personal information, and the index of
what gets opened and how often is the clearest case.

- **Declarations are committed in the open.** Schemas, base declarations and
  mode definitions describe intent and are meant to be read.
- **Observations never are.** Usage counts, open histories, project activity
  and notification logs live under the state directory and stay out of git.
- **Anything observed that must be committed is encrypted at rest**, with the
  same keyfile the state backups already use. Plaintext observation data in a
  repository is a defect, and the check for it belongs in the gate that runs on
  every commit.

The distinction to hold onto: a declaration says what the desk should be, an
observation says what was actually done. The first is configuration; the second
is a diary.

See also `docs/bindings.md` — the binding architecture (LEO-303): why
root and modes are structural, why a withheld tree takes its door and
its rendering with it, and where contextual binds get their context.

## The gap between this and what runs today

Recorded so the design is not mistaken for the implementation. Updated Sep 14,
after the store-directory move and the live admission round-trip.

### Live

| Piece                                    | State                                                                                                       |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------- | --- |
| The declaration schema and a seeded desk | shipped; the store is under `$QF_STORE` and seeds itself on first run                                       |
| Resolving a mode into a complete desk    | shipped, with dependency closure; consumed per converge                                                     |
| Planning a transition                    | shipped; the watcher drives it and the shell dispatches `converge` straight into the compositor             |
| Scene geometry as a layout provider      | live — the scene IS the layout; the correction engine's extras are gated on the workspace running the scene |
| Binding trees held by name               | admit runs per converge, door and rendering included (docs/bindings.md)                                     |     |
| Workspaces held by name                  | admit runs per converge (verified live: entering gaming withdrew five workspaces, windows held)             |
| The command-line way in                  | `resolve`, `plan`, `apply` (services), `explain`, `modes`                                                   |
| Launch/scene gates at dispatch           | resolved from the store locally (no per-press subprocess)                                                   |
| Contract shape                           | `etc/scene-managed.json` is protected + tasks only; mode service policy lives in the declaration            |

### Still true of the running desk

| Area                  | Today                                                                                                                                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Background policy     | `defer`/`prevent` task keys are live (the mood panel's cycle consumes them); the wildcard `allow` shape is inert (LEO-252)                                                                                         |
| Grace                 | live: the shell announces what a transition takes before it takes it (LEO-242), and a resource's veto window holds a stop and surfaces once (LEO-256); the deadline half of refusals is the resource's own `until` |
| Notifications         | identity resolved and recorded; routing per mode is live (LEO-273/275)                                                                                                                                             |
| Geometry engine       | scheduled correction passes still exist beside the provider; timers currently do not fire (LEO-302)                                                                                                                |
| Workspaces            | declared; the last manual strays (specials, the unpinned `1`) are LEO-265/299                                                                                                                                      |
| Services and projects | services enforce from the declaration per mode; projects still untouched                                                                                                                                           |
| Mode panel            | the shell's mode editor reads/patches the policy store; full read/explain contract is LEO-280                                                                                                                      |

## Services: why not systemd targets

Spike decision (LEO-272): **modes stay a computed plan, not a target.** A mode
is a set of units that should run together — what a target is for — so the
question was whether `hyprfocus-gaming.target` with `Wants=`/`Conflicts=`
expresses the desk better than the CLI's resolved stop/start list.

Worked example, game mode both ways:

```ini
# the target way
[Unit]
Description=hyprfocus gaming desk
Conflicts=hyprfocus-work.target
Wants=obsidian.service                 # read: NOT built from the declaration?
# ...every admitted and retired unit, edited every time the declaration moves
```

- **The target way**: entering the mode is `systemctl --user isolate
hyprfocus-gaming.target`, and systemd gives ordering, dependency resolution,
  readiness and failure handling for free; conflicting targets make modes
  mutually exclusive by construction.
- **The cost: authority moves out of the store.** Targets are static files, so
  a declaration edited at runtime must regenerate the file and `daemon-reload`
  — and every converge then ends with a state the store does not describe. The
  whole design rests on the declaration being what the desk reads; this would
  put a compiled artifact back between them, replacing an atomic store write
  with a compile step plus a reload.
- **The protected rail survives this way, and dies that way.** Today protected
  units are subtraction from a computed set — the isolated target cannot stop
  something its `Conflicts=` never named. To reach them, targets would have to
  carry the protected list _into_ every mode's file, which is rail maintenance
  duplicated per mode.
- **Partial application loses its report.** Today's plan is explicit:
  stop-after-grace, oneshot timers skipped-for-readiness, missing units named
  in the log, refusals recorded — the reconcile contract's phases
  (announce/grace/veto, LEO-253) need exactly that sequence in-process. An
  isolate transaction is all-or-nothing with a single read-unfriendly error.

The reading (not the mechanism) is what a target buys; `systemctl list-dependencies` and the mode report already answer it. **Kept: the
computed plan with the store as the only declaration.** A target may OBTAIN a
future role as a read-only status convenience, never as the enforcing path.
