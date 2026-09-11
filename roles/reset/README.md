# reset

One-shot clean slate for a host whose `$HOME` has drifted from this repo.

Archives `~/.config` wholesale, tears every user unit back down to its vendor
preset, and lets the rest of the same run rebuild from nothing — so no unit,
drop-in or config file that this repo no longer installs can linger.

**Nothing is deleted.** `~/.config` is _moved_ to
`~/.config-pre-reset-<timestamp>`, and the dotfiles source clone goes in with it.
Delete that by hand once the rebuilt session looks right.

## What it does

1. Records the enabled user units into the marker file (the archive should say
   what the machine looked like).
2. `systemctl --user disable --now` on each of them.
3. Moves `~/.config` aside and recreates it empty.
4. Moves `~/.local/share/chezmoi` — the dotfiles source clone, the one chezmoi
   leftover that lives outside `~/.config` and would survive the flush — into
   the archive as `.chezmoi-source`. The chezmoi role re-clones it later in the
   same run. Moved rather than deleted because the clone doubles as the dotfiles
   dev checkout: uncommitted or unpushed work there exists nowhere else. Anything
   you had not pushed is in the archive's `.chezmoi-source`.
5. Copies `reset_config_keep` back out of the archive.
6. `daemon-reload`, `reset-failed`, then `preset-all` — which puts the
   _packaged_ user units back exactly where a fresh install would have them.
   Roles re-enable their own units later in the same run.
7. Writes `~/.local/state/system-config/reset-<hostname>.done`.

## What is not covered

`~/.ssh` and `~/.gnupg` are outside `~/.config` and are never touched.

`~/.config` holds a lot that neither Ansible nor chezmoi can regenerate, and a
flush sends all of it to the archive:

| Path                             | What you lose until you restore or re-login            |
| -------------------------------- | ------------------------------------------------------ |
| `zen`, `mozilla/firefox`         | browser profiles: history, cookies, logins, extensions |
| `Proton Pass`, `Proton Mail`, …  | Proton sessions                                        |
| `vesktop`, `spotify`, `obsidian` | app logins and local settings                          |

`roles/browser_profiles` only symlinks prefs _into_ profiles — it does not
create their contents. Put anything you want kept into `reset_config_keep`
before the run, or copy it out of the archive after.

## Running it

Opt-in twice over. The host must allow it:

```yaml
# host_vars/quantum-laptop.yml
reset_enabled: true
```

and the run must name it:

```sh
ansible-playbook site.yml --limit quantum-laptop --ask-become-pass \
  -e reset_confirm=quantum-laptop
```

Naming a host that has not set `reset_enabled` does nothing —
`quantum-desktop` sets it to `false` and cannot be flushed from the command
line at all.

**From a TTY, not from inside the desktop session.** A live
Hyprland/quickshell/portal writes its state back out on exit, straight into the
`~/.config` this role just emptied — which is the orphan problem it exists to
fix. The role refuses to run under a graphical session;
`-e reset_allow_graphical=true` overrides that if you know the session is idle.

Afterwards the marker makes it a no-op. To flush the same host again, delete
the marker.

## Variables

| Variable                | Default                                          | Meaning                                           |
| ----------------------- | ------------------------------------------------ | ------------------------------------------------- |
| `reset_config_keep`     | `[]`                                             | paths under `~/.config` restored from the archive |
| `reset_allow_graphical` | `false`                                          | run despite a live graphical session              |
| `reset_archive`         | `~/.config-pre-reset-<timestamp>`                | where `~/.config` and the dotfiles clone go       |
| `reset_marker`          | `~/.local/state/system-config/reset-<host>.done` | proof it already ran                              |

See also [`cleanup`](../cleanup/README.md), which is the recurring counterpart:
`reset` is a once-per-host flush, `cleanup` runs every time and removes only the
roles this host has switched off.
