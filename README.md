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
| `theming`          | GTK/Qt/cursor/browser theming — one flavour, one accent, one type scale (templated; supersedes chezmoi for the GTK, Qt, Kvantum, xsettingsd and Zen `user.js` files)                            |
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

The one deliberate exception is the coding server's **prefix indicator**: while
`C-b` is held, the session chip in `status-left` inverts to a filled mauve
block. A modifier state is the one thing that must be unmissable in peripheral
vision, and it lasts a fraction of a second — the block never competes with
anything because it is never on screen while you are reading. It replaced a
`⚑PREFIX` label, which was permanent visual weight for a transient fact.

The session list in `status-right` is built with tmux's own `#{S:fmt,cur-fmt}`
loop, not a `#()` shell hook. A hook there is wrong twice over: it polls (every
redraw is a subprocess, and a timed redraw flickers popups), and `#S` inside its
command string is expanded by tmux _before_ the shell runs — so the old bar
printed the current session's name once per open session instead of listing them.

The bar carries the session chip, the window list and that session list —
nothing else. The active pane's directory was dropped because tms names sessions
after their project directory, so it repeated the chip in a second colour, and
the clock with it: tmux sits inside a terminal, inside a compositor with a bar,
and both already answer that question.

Leading is the highest-value change of the three: `cell_height 120%` (130% in
the log viewer) adds a fifth of a row of air between every line, everywhere,
without changing glyph size. Both tmux bars are flat and hardcoded — the
catppuccin tmux plugin is gone, along with its `externals_repos` entry.

## Interactive shell

Day-to-day usage — prompt, keys, aliases — is a one-page cheatsheet in
[`roles/zsh/README.md`](roles/zsh/README.md). This section is the design.

`roles/zsh` renders `.zshrc` from one template; `zsh_plugins` in the role
defaults is the whole plugin set, and **its order is load order** (zsh-defer
first, syntax-highlighting near the end, history-substring-search after it).

Startup cost is kept off the critical path: every `eval "$(tool init)"`
(zoxide, thefuck, direnv, the `tms` completion) runs through `zsh-defer -c`,
after the first prompt paints. The `-c` is load-bearing — without it the
`$(...)` is substituted immediately and nothing is deferred.

### Prompt

Three rows — blank, context, input — and no framework behind it.

```
~/P/c/q/system-config/roles/zsh  main ⇡2 +1 !8 ?2  1&  4.2s  ✗1
❯
```

The shape is the argument. A one-line prompt with an `RPROMPT` loses exactly the
information you wanted during a long pipeline, because a long command line
overwrites it. Putting context on its own row above gives it the full width,
leaves the command a clean line starting at a fixed column, and puts the blank
row where every other surface here puts one.

Long paths are shortened by abbreviating components, never with an ellipsis:
`~/…/system-config` is shorter but it throws away which tree you are in and
hands back a character meaning "something was here". Two components are always
spelled out — the last one, and the root of the repo you are in, which is bold,
so "which project" is answerable without reading the path.

The row is dim by design: it is reference material, glanced at. Only the path
tail is at full text brightness and only the chevron is accented; everything else earns
colour by meaning something — teal divergence, green staged, yellow modified,
grey untracked, red conflicted or failed, peach for an interrupted rebase or
merge. Every segment after the cwd is conditional, so a clean directory outside
a repo prints one path and nothing else.

**Vi mode lives in the chevron**, not in a word on the far right: `❯` mauve in
insert, `❮` blue in normal, and the terminal cursor switches beam/block with it
the way it does in nvim. A mode is something you need to know _before_ the next
keystroke, so it belongs where the cursor already is.

`vcs_info` is gone. One `git status --porcelain=v2 --branch` answers branch,
ahead/behind and all four path counts in a single fork — vcs_info needed four or
five for strictly less (no divergence, no counts). The git dir is cached per
directory and flushed on `chpwd`; `--no-optional-locks` keeps the prompt from
rewriting the index behind a running editor.

Two conventions make the alias set navigable rather than merely large:

- **`f`-prefixed = interactive.** `fa`, `fdi`, `flog`, `fco`, `frb`, `fcf` are
  forgit's fzf pickers; the prefix promises the command shows you a list and a
  preview before it acts. forgit loads with `FORGIT_NO_ALIASES=1` so its own
  `ga`/`gd`/`gi` cannot shadow the plain git aliases.
- **Global aliases are pipeline punctuation.** `G L H T WC J S U X CP` expand
  anywhere on the line, so `rg TODO G test CP` reads left to right.

`du`, `df`, `ps` and `top` are aliased to `dust`, `duf`, `procs` and `btop`.
`command du` (or `\du`) still reaches the original — worth remembering when
copying an invocation out of a manpage. `zsh-you-should-use` reports the alias
you could have typed _after_ the command runs, which is the only way a set this
size enters muscle memory.

## Desktop theming

`roles/theming` owns the look outside the terminal: Catppuccin **Macchiato**,
accent **mauve**, UI at **12pt**, cursor **28** — the same palette and the same
"bigger text, more space, no filled chrome" rules as the terminal surface.

Four toolkits need telling in four dialects, and the portals read none of those
files:

| Layer   | File                                                             | Note                                                                                                |
| ------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| GTK2    | `~/.gtkrc-2.0.mine`                                              | the `.mine` file, because nwg-look owns `~/.gtkrc-2.0`                                              |
| GTK3    | `~/.config/gtk-3.0/settings.ini`                                 |                                                                                                     |
| GTK4    | `settings.ini` + **symlinked** `gtk.css`/`gtk-dark.css`/`assets` | libadwaita ignores `gtk-theme-name` entirely                                                        |
| Qt      | `qt6ct.conf` / `qt5ct.conf` + Kvantum                            | fonts are QDataStream blobs, see `templates/_qtfont.j2`                                             |
| X11     | `xsettingsd.conf`                                                | XWayland clients                                                                                    |
| Portals | **dconf** `/org/gnome/desktop/interface/*`                       | what `xdg-desktop-portal-gtk` reports — miss this and the app is themed but its file chooser is not |
| Session | `~/.config/environment.d/50-theming.conf`                        | reaches every systemd user unit, which is how portal popups spawned without a shell get `XCURSOR_*` |

`nwg-look -a` is **not** run: it re-exports `settings.ini`, `.gtkrc-2.0`,
`index.theme`, `xsettingsd` and the GTK4 symlinks from its own store, so it
would overwrite the templates. The role renders that store instead, so opening
the GUI shows the truth.

The browser follows the same rules: `templates/zen-user.js.j2` sets the mauve
accent, 4px radius, wider content separation, no dimming of unfocused windows,
and reduced motion.

```sh
ansible-playbook site.yml -t theming --ask-become-pass              # repo packages via pacman + become
sudo -v && ansible-playbook site.yml -t theming --ask-become-pass   # ...plus AUR, on a fresh machine
ansible-playbook site.yml -t theming --skip-tags privileged        # dotfiles only, no sudo at all
```

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
