# obsidian_index

Watcher that re-pins index callouts under a note's H1, as a `systemd --user`
unit.

- **Vars** `obsidian_index_vault`, `obsidian_index_debounce`,
  `obsidian_index_deploy_watcher` (defaults).
- **Tag** `obsidian`, `obsidian_index`

The normalizer and its inotify wrapper come from the `scripts` repo, cloned by
`roles/project_checkouts`. Skipped when the vault directory is absent.
