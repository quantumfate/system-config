# zsh

The terminal surface, templated end to end: shell config, plugin set, the
lessfilter dispatcher, kitty, both tmux servers and the logging workspace.
Supersedes chezmoi for `.zshrc`, `.zshenv`, `.lessfilter`, `.tmux.conf` and
`kitty.conf` — edit the templates here, never the rendered files.

- **Vars** `roles/zsh/defaults/main.yml`; `PATH` and scalar env vars come from
  `group_vars/all/environment.yml`, shared with `roles/session_env`.
- **Depends on** `packages` (for `zsh-antidote`).
- **Tag** `dotfiles`, `zsh`, `shell`

`files/cheatsheet.md` is a deployed asset, not documentation: it is copied to
`~/.config/zsh/cheatsheet.md` and every table row in it becomes one row of the
`Alt-h` picker. It is the only source, so a binding cannot exist in the popup
and not in the docs.

![Neovim in tmux](../../assets/rice/neovim-tmux.png)
![Interactive shell](../../assets/rice/interactive-shell.png)

## Logging workspace

A structured logging centre in its own tmux server, so killing it never touches
the coding server.

![Log workspace](../../assets/rice/log-workspace.png)

```text
source ──▶ logstream ──▶ tspin ──▶ less -RS
           columns       colour     no wrap
```

Every journal source renders as the same fixed-width table:

```text
YYYY-MM-DD HH:MM:SS  LEVEL   source                message…
└─ 19 ─────────────┘ └─ 5 ─┘ └─ 20 ───────────────┘
```

### Commands

| Command               | Source                                                      |
| --------------------- | ----------------------------------------------------------- |
| `log`                 | fzf picker: presets, uwsm apps, live units, workspace files |
| `log <spec>`          | open one source directly                                    |
| `logh <spec>`         | same, in the current terminal (no window)                   |
| `logu <unit>`         | one system unit, following                                  |
| `loguu <unit>`        | one `--user` unit, following                                |
| `logf <file>`         | a plain file, following                                     |
| `logerr` / `logwarn`  | this boot, by priority                                      |
| `logk`                | kernel ring buffer                                          |
| `logboot` / `logprev` | this boot / previous boot, from the top                     |
| `logaudit`            | audit and access denials                                    |
| `logwhy <unit>`       | state + last 50 lines, one screen                           |
| `loggrep <pat>`       | search this boot, same columns                              |
| `logsince <when>`     | a bounded window (`'15 min ago'`, `today`)                  |

### Tuning

All in `defaults/main.yml`: `zsh_kitty_log_class`, `zsh_tmux_log_socket`,
`zsh_log_workdir`, `zsh_log_dir`, `zsh_log_font_size`, `zsh_log_padding`,
`zsh_log_line_height` (extra leading between rows), `zsh_log_accent` (chrome
only — severity colours stay semantic), `zsh_tailspin_theme`, `zsh_bat_theme`.

Severity colours live in `templates/tailspin_theme.toml.j2`, written in the 16
ANSI names, because the terminal palette already _is_ Macchiato.
