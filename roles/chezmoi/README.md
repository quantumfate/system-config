# chezmoi

Clones the dotfiles source, renders `chezmoi.toml`, then applies.

- **Vars** `chezmoi_repo`, `chezmoi_source` in `group_vars/all/main.yml`.
- **Tag** `dotfiles`, `chezmoi`

The source dir doubles as the dotfiles dev checkout, so a dirty tree is normal:
the pull is skipped while it is dirty and the working tree applied as-is —
uncommitted work is never discarded. chezmoi no longer prompts and carries no
`.chezmoiscripts` or `.chezmoiexternal`; all of that lives in `roles/`.
