# user_units

Every `~/.config/systemd/user` unit the desktop session runs: the session apps,
the clipboard and display daemons, and the targets other units hang off.

- **Touches** `~/.config/systemd/user/`, `~/.config/systemd/user.conf.d/timeout.conf`.
- **Vars** `user_units_deploy`, `user_units_enabled`, `user_units_passive`,
  `user_units_packaged_enabled`, `user_units_default_timeout_stop_sec` (defaults).
- **Tag** `user_units`

These units were split between chezmoi and nothing at all: five of them existed
only on the machine they were first written on and would not have survived a
rebuild. hyprfocus starts and stops units a declaration names, so a unit it
cannot find is a mode transition that half-runs — which is why one repo owns
them all and `scripts/tests/units_gate.py` checks the set against the
declaration.

Units that back a _capability_ rather than a session app stay with the role
that owns the capability (`audio`, `obsidian_index`, `obsidian_linear`,
`state_backup`, `theming`). This role is the home for what has no other one.
