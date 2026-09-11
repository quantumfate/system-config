# chezmoi

Clones the dotfiles source, renders `chezmoi.toml`, then applies. Installs
`chezmoi-externals.timer`, which keeps the dotfiles' externals fresh between
playbook runs.

- **Vars** `chezmoi_repo`, `chezmoi_source` in `group_vars/all/main.yml`;
  `chezmoi_externals_interval` (defaults).
- **Tag** `dotfiles`, `chezmoi`

The source dir doubles as the dotfiles dev checkout, so a dirty tree is normal:
the pull is skipped while it is dirty and the working tree applied as-is —
uncommitted work is never discarded. chezmoi no longer prompts and carries no
`.chezmoiscripts`; that lives in `roles/`.

`.chezmoiexternal.toml` holds only the catppuccin themes that chezmoi-owned
configs include. The timer applies externals and nothing else
(`--include externals`), so it never touches a dotfile you are editing. It does
apply them with `--force`: a hand-edited or deleted theme file is restored, not
prompted about. It refreshes an entry only once its `refreshPeriod` has lapsed — the
dotfiles set the cadence, the timer just checks. `systemctl --user start
chezmoi-externals` forces a check now.
