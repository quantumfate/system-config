# System Configuration

Ansible playbook that provisions my CachyOS/Arch system config end to end, then
hands `$HOME` over to chezmoi.

## Separation of concerns

| Scope                                                  | Owner                                                    |
| ------------------------------------------------------ | -------------------------------------------------------- |
| `/etc`, system units, groups, bootloader, packages     | Ansible                                                  |
| `$HOME` dotfiles                                       | chezmoi                                                  |
| Interactive shell (`.zshrc`, `.zshenv`, `.lessfilter`) | Ansible (`roles/zsh`, templated)                         |
| External checkouts, themes, downloads (`$HOME`)        | Ansible (`roles/externals`)                              |
| Quickshell desktop shell (config symlink, completions) | Ansible (`roles/quickshell`, vendored)                   |
| Prompted values (profile, monitors, feature flags)     | Ansible → rendered into `~/.config/chezmoi/chezmoi.toml` |

chezmoi no longer prompts and no longer carries `.chezmoiscripts` or
`.chezmoiexternal`. All of it lives in `roles/`.

## Bootstrap a fresh machine

```sh
sudo pacman -S --needed ansible git
git clone git@codeberg.org:quantumfate/system-config.git
cd system-config
ansible-galaxy install -r requirements.yml
./bootstrap.sh            # == ansible-playbook site.yml --ask-become-pass
```

First run is interactive once: `pass-cli login` needs a TTY. Everything after
that is idempotent — re-run any time.

## Layout

```
site.yml                 role order, feature-flag gating
group_vars/all/main.yml  profile + feature flags + identity  ← edit this
group_vars/all/externals.yml  external repos/themes/downloads (ex-chezmoi externals)
group_vars/all/packages.yml  package sets per feature
inventory/hosts.yml      localhost, local connection
roles/                   one concern each
```

## Roles

| Role               | Description                                                                                                                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `base`             | system deps                                                                                                                                                                                     |
| `password_manager` | provides all secrets                                                                                                                                                                            |
| `secrets`          | key management                                                                                                                                                                                  |
| `packages`         | system packages                                                                                                                                                                                 |
| `sudoers`          | sudo configuration                                                                                                                                                                              |
| `user_dirs`        | xdg                                                                                                                                                                                             |
| `login_shell`      | zsh primary shell                                                                                                                                                                               |
| `keyboard`         | custom-dvorak layout                                                                                                                                                                            |
| `console`          | tty theming                                                                                                                                                                                     |
| `desktop_entries`  | sway and niri                                                                                                                                                                                   |
| `display_manager`  | system configuration for display-manager                                                                                                                                                        |
| `docker`           | infra tools                                                                                                                                                                                     |
| `virtualization`   | vms                                                                                                                                                                                             |
| `power_profile`    | performance related                                                                                                                                                                             |
| `devenv`           | neovim and dev dependencies                                                                                                                                                                     |
| `chezmoi`          | dotfiles clone + apply, systemd unit-reload                                                                                                                                                     |
| `externals`        | plugins, dev checkouts, catppuccin themes                                                                                                                                                       |
| `zsh`              | terminal surface: shell config, plugins, lessfilter, kitty, both tmux servers, logging workspace (templated; supersedes chezmoi for `.zshrc`/`.zshenv`/`.lessfilter`/`.tmux.conf`/`kitty.conf`) |
| `browser_profiles` | prowser profile settings                                                                                                                                                                        |
| `theming`          | rice                                                                                                                                                                                            |
| `yazi`             | file manager                                                                                                                                                                                    |

## Logging workspace

Owned by `roles/zsh`. A log surface that is deliberately boring: one column
layout, one palette, one keystroke per source. Nothing about it moves unless
the log moves.

### The pipeline

```
source ──▶ logstream ──▶ tspin ──▶ less -RS
           columns       colour     no wrap
```

Colour is applied **exactly once**, by `tspin`, using the rendered Catppuccin
Macchiato theme. `logstream` clears `LESSOPEN` so `lesspipe` → `~/.lessfilter`
cannot re-colour an already-coloured stream and corrupt the escape codes.
Never build a pipeline that pages a coloured stream yourself — hand the query
to `logstream` instead (`… --output=json | logstream json`).

Every journal source renders as the same fixed-width table:

```
YYYY-MM-DD HH:MM:SS  LEVEL   source                message…
└─ 19 ─────────────┘ └─ 5 ─┘ └─ 20 ───────────────┘
```

`LEVEL` comes from journald's own `PRIORITY`, not from string-matching the
message, so it is present and correct even for units that log unstructured
text. Colour carries the level; **bold is reserved for fatal/panic/crit**.

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

The picker lists **uwsm apps** alongside services. Anything launched through
uwsm (every GUI program started from Hyprland) lives in the user manager as an
`app-*.scope`, not a service, so a `--type=service` listing never showed them.
They are labelled by app name, and window names are stripped of uwsm's
bookkeeping — `app-Hyprland-kitty-ecc85322.scope` opens as `kitty`.

Picking a source needs a terminal, and a Hyprland keybind has none. `logview`
detects that: with a tty it runs the picker inline, without one it opens the
picker **inside the viewer** as its own tmux window (`logpickrun`), which then
renames itself after the chosen source and becomes the stream.

### Isolation

Two levels, so reading logs can never disturb coding:

1. **Its own tmux server** — socket `logs`, config `~/.config/tmux/logs.conf`.
   Same prefix as the coding server (`C-b`): the isolation is the socket, not
   your muscle memory. Separate session list, separate history, separate
   lifetime — `tmux kill-server` on either one leaves the other running. Reach
   it with `tmux -L logs attach`.
2. **Its own kitty window** — class `logviewer`, and its own CWD on tmpfs
   (`/run/user/$UID/logview`), outside every project tree.

Hyprland owns the window placement, and the rules live in the `hypr` repo —
`hypr/services/logging/init.lua`, wired like every other service (window rules
through `hypr.lib.windowrule`, keys through `hypr.lib.submap`):

- **Workspace** `logs`, persistent, on the **primary monitor**, `monocle`
  layout — one full-width window, because a log line is long and reading it
  must not depend on how the workspace happens to be split. Declared per host
  in `hyprland.lua` (`workspace 7` on desktop, `6` on laptop).
- **Window rule** — `initial_class = logviewer` is tagged `+logs`: assigned to
  that workspace, tiled, `rounding = 0`, and `opacity = 1 override 1 override`
  so log text is never dimmed by the global inactive opacity.
- **Keys** — every entry focuses the logs workspace _before_ it opens the
  source, so an action never lands on a workspace you cannot see. `SUPER+e`
  opens the `logs` submap, one letter per source, mirroring
  the shell verbs: `l` pick · `e` errors · `w` warnings · `k` kernel · `f` live
  · `b` boot · `p` previous boot · `a` audit · `g` go to the workspace ·
  `x` kill the isolated tmux server (wipes every log window, coding untouched).
  Not `SUPER+l`: that is the hjkl focus-right bind. Duplicate root binds fail
  silently — the press does both, and you end up parked inside the submap where
  every other bind looks dead. Audit new binds with
  `hyprctl binds -j | jq -r '.[]|select(.submap=="" and .modmask==64).key' | sort | uniq -d`.

What this role guarantees to that side is the class name (`zsh_kitty_log_class`)
and the `logview`/`logstream`/`logpick` commands on `PATH`.

### Tuning

All in `roles/zsh/defaults/main.yml`: `zsh_kitty_log_class`,
`zsh_tmux_log_socket`, `zsh_log_workdir`, `zsh_log_dir`, `zsh_log_font_size`,
`zsh_log_padding`, `zsh_log_line_height` (extra leading between rows),
`zsh_log_accent` (chrome accent — mauve; severity colours stay semantic and are
never themed with it), `zsh_tailspin_theme`, `zsh_bat_theme`. Severity colours
live in `roles/zsh/templates/tailspin_theme.toml.j2`; it uses the 16 ANSI
names on purpose, because the terminal palette already _is_ Macchiato — one
palette, one source of truth.

## Terminal surface

One aesthetic across kitty, both tmux servers and neovim: Catppuccin Macchiato,
a single mauve accent (`zsh_log_accent`), flat chrome, generous space. Each
layer owns only what it alone can control:

| Layer                      | Owns                                                                                             | Why there                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `kitty.conf`               | font, font size, **line height** (`modify_font cell_height`), window padding, cursor             | cell-grid properties — neither tmux nor neovim can change how tall a text row is |
| `.tmux.conf` / `logs.conf` | the status bar: layout, palette, the blank second row                                            | tmux draws inside cells; the bar is all it owns visually                         |
| neovim                     | inside the viewport: gutters (`numberwidth`, `signcolumn=yes:2`), float borders, flat statusline | the terminal cannot reach in there                                               |

Three rules hold across all of them, which is what makes the boundary between
kitty, tmux and neovim invisible: **no filled blocks** (the active item is bold
accented _text_, never a painted chip), **borders one step off the background**
(`surface1`) rather than accent-coloured frames, and **separation by whitespace**
— tmux's blank status row, kitty's window padding, and neovim's blank
`fillchars` where a split rule would be. Mauve marks exactly one thing at a
time: the focused window, the cursor's line number, the current mode.

Leading is the highest-value change of the three: `cell_height 120%` (130% in
the log viewer) adds a fifth of a row of air between every line, everywhere,
without changing glyph size. Both tmux bars are flat and hardcoded — the
catppuccin tmux plugin is gone, along with its `externals_repos` entry.

## Common runs

```sh
ansible-playbook site.yml --ask-become-pass --check --diff   # dry run
ansible-playbook site.yml --ask-become-pass -t packages      # one concern
ansible-playbook site.yml --ask-become-pass -t dotfiles      # chezmoi + friends
ansible-playbook site.yml --ask-become-pass --skip-tags bootstrap
```

## Secrets

`secrets_backend` in `group_vars/all/main.yml`:

- `pass-cli` (default) — SSH and GPG material is read from Proton Pass at run
  time. Nothing secret is stored in this repo.
- `vault` — the same material comes from an encrypted
  `group_vars/all/vault.yml`:

  ```sh
  ansible-vault create group_vars/all/vault.yml
  ```

  ```yaml
  vault_ssh_keys:
    codeberg: { private: "-----BEGIN…", public: "ssh-ed25519 …" }
  vault_gpg: { public: "…", private: "…", fingerprint: "…" }
  ```

  With `vault`, `roles/password_manager` is skipped entirely — no Proton Pass
  dependency during provisioning.
