# The binding architecture

One page naming how keybinds are created on this desk (LEO-303). Three
legitimate classes exist and no shape between them is legitimate:

## 1. System-level binds — never gated

Always live: submap exits, the escape hatch, the compositor controls, and
everything a withheld resource must never take with it. Two trees are
structural by definition (`hypr/hyprfocus/binds.lua`):

- **root** carries the leader key and every bind outside any submap. Invariants
  pinned by `tests/hyprfocus_binds_spec.lua`: root never wields; a mode's
  declaration names what it takes, never what it keeps.
- **modes** is the only way into another mode, so withholding it leaves the
  exit behind the door it just locked and the desk at rest has no leader.

The escape hat in every tree is also a root fact: it is _attributed_ to the
tree being entered if it were, a mode that withheld that tree could lock its
own exit — so escape binds are created at eval time in the tree every submap
has, and they are never withheld. A withheld tree may not contain anything
the user needed — including its own exit.

## 2. Contextual binds — keyed by what is focused

Class-aware binding trees (the Dofus in-group keys, media-window keys, tmux
client keys) are submaps with a window condition: Hyprland's own
`binds` handle the window-filter grammar, so a contextual tree is written
like any submap tree and _its context is a runtime fact of the focused
window_, not a desk-wide admission state.

Which-key's breadcrumb rendering describes this class; the old
tag-and-context-filter heuristic (LEO-223) is retired — the window grammar
picks the keys, not a list that could otherwise drift from them.

## 3. Mode-scoped binds — the declaration admits and withholds

A binding tree is a resource like any other: the declaration's
`bindings.remove` names the trees a mode takes away, and `binds.admit`
withholds exactly those (LEO-258-era; the guard covers the structural two).
Withholding takes the WHOLE tree: its binds, its door, and its rendering —

- the tree's binds go dead (`set_enabled(false)`),
- the LEAF THAT ENTERS THE TREE goes with it: attribution at leaf-creation
  time (`SubmapEntry.opens` → `binds.attribute`) puts the door in the room it
  opens, so withholding the room removes the key entirely (commit `cd62815`,
  pinned by `tests/submap_spec.lua`),
- the way OUT stays with the root tree: the escape binds are attributed to
  the eval-time root, not to the submap, so no mode can lock the exit away,
- and the which-key dump prunes withheld trees and their `opens` leaves
  entirely, so the overlay cannot draw a door into a submap the mode took
  away (`tests/whichkey_spec.lua` — "the door into a withheld tree was still
  rendered" is the regression pin).

The acceptance case: in `work`, the Dofus key does nothing (no menu, no
empty submap — the leaf its door carries goes dead with the room); in
`gaming` everything works as today.

## The rules these hold

- **A bind may not end up inside a submap the mode withheld** — the
  leaf-with-room attribution is the structural fix; nothing prunes binds
  after creation.
- **Which-key renders the runtime document only** (LEO-268): the registry
  narrows to the loaded set per converge. The overlay, the full cheatsheet
  and the peek all read the same document, and none of them can show a key
  the mode has not loaded (by construction rather than filtering).
- **Withholding is negative by default**: a mode names what it takes. A tree
  the declaration never mentions is a declaration gap, not an intention to
  remove.
- **No per-press IPC** (LEO-267): admission owns availability; a press
  handler never asks the shell a question the disabled bind already answered
  silently.
