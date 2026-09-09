# obsidian_linear

One-way mirror of Linear issues into the Obsidian vault, on a `systemd --user`
timer. Linear is the source of truth: the sync never deletes and never writes
back.

- **Vars** `obsidian_linear_vault`, `obsidian_linear_interval`,
  `obsidian_linear_pass_*` (defaults).
- **Tag** `obsidian`, `obsidian_linear`

The API key is read from Proton Pass at run time and never written to disk; a
locked vault makes the sync notify and exit rather than run stale.
