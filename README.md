# System Configuration

Ansible playbook that provisions my CachyOS/Arch system end to end, then hands
`$HOME` over to chezmoi.

## Separation of concerns

| Scope                                                  | Owner                                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------------ |
| `/etc`, system units, groups, bootloader, packages     | Ansible                                                                  |
| `$HOME` dotfiles                                       | chezmoi                                                                  |
| Interactive shell (`.zshrc`, `.zshenv`, `.lessfilter`) | Ansible ([`roles/zsh`](roles/zsh/README.md), templated)                  |
| Login/session environment                              | Ansible ([`roles/session_env`](roles/session_env/README.md))             |
| Git checkouts under `~/Projects`                       | Ansible ([`roles/project_checkouts`](roles/project_checkouts/README.md)) |
| Quickshell desktop shell, hypr, nvim                   | Ansible, from a role inside each checkout                                |
| Prompted values (profile, monitors, feature flags)     | Ansible → rendered into `~/.config/chezmoi/chezmoi.toml`                 |

chezmoi no longer prompts and no longer carries `.chezmoiscripts`; that lives in
`roles/`. Its one `.chezmoiexternal` pulls the catppuccin themes that
chezmoi-owned configs include, kept fresh by a timer from
[`roles/chezmoi`](roles/chezmoi/README.md).

`site.yml` owns ordering and tags, nothing else. Hard requirements live in a
role's `meta/dependencies`; `roles_enabled` gates whole roles in `site.yml`, and
feature flags gate partial lists inside a role.

## Hosts

Every machine has an inventory entry named after its `hostname` and a matching
`host_vars/<hostname>.yml`. Each host converges itself over a local connection,
so a run is always limited to the current machine — `bootstrap.sh` passes
`--limit "$(hostname)"` and fails early if there is no entry for it.

| Host              | Profile | Monitors         | Off                                                            |
| ----------------- | ------- | ---------------- | -------------------------------------------------------------- |
| `quantum-desktop` | desktop | DP-1 + DP-2      | —                                                              |
| `quantum-laptop`  | laptop  | eDP-1 + HDMI-A-1 | gaming, power_profile, display_manager, docker, virtualization |

Monitor names are kept in step with the `host_configs` table in the `hypr`
checkout's `hyprland.lua`, which reads the same hostnames.

### Toggling roles per host

Which roles run is one dict, built in two layers:

- `group_vars/all/roles.yml` — `roles_default`, the answer for every machine,
  written in terms of the feature flags (`gaming`, `vms`, `devenv`, `profile`).
- `host_vars/<hostname>.yml` — `roles_override`, only the keys this host
  disagrees with.

They merge into `roles_enabled`, which is what every `when:` in `site.yml`
gates on. To turn a role off on one machine:

```yaml
# host_vars/quantum-laptop.yml
roles_override:
  display_manager: false
  power_profile: false
```

Flipping a feature flag instead (`vms: false`) turns off every role derived from
it — `docker` and `virtualization` — plus that flag's package set. Package sets
follow `roles_enabled`, not the raw flags, so a role turned off in an override
does not leave its packages installed.

Adding a host: add it to `inventory/hosts.yml` under `desktops`/`laptops`, copy
a `host_vars/` file, set the profile, monitors, and flags.

### Turning a role off removes it

A disabled role stops converging, but nothing it already installed goes away on
its own. [`cleanup`](roles/cleanup/README.md) runs on every host, every time,
and for each disabled role that ships a `tasks/cleanup.yml` it runs that
teardown — so a laptop that dropped `display_manager` also gets sddm disabled,
and one that dropped `power_profile` stops pinning the CPU to `performance`.

Teardowns never touch user data: `gaming` unwires Lutris and keeps `~/Games`,
`docker` and `virtualization` stop their daemons and keep their storage.
Package removal is a separate, opt-in decision:

```sh
./bootstrap.sh -e cleanup_remove_packages=true
```

### Flushing a drifted machine

An older machine can carry orphans that no role knows to remove — units,
drop-ins and config from a layout this repo has since refactored away.
[`reset`](roles/reset/README.md) is the once-per-host answer: it archives
`~/.config` to `~/.config-pre-reset-<timestamp>` (moved, never deleted), tears
every user unit back to its vendor preset, and lets the rest of the same run
rebuild from nothing.

```sh
# from a TTY, not from inside the desktop session
./bootstrap.sh -e reset_confirm=quantum-laptop
```

It is opt-in twice: the host sets `reset_enabled: true`, _and_ the run names it.
`quantum-desktop` sets `reset_enabled: false` and cannot be flushed from the
command line at all. Afterwards a marker under `~/.local/state/system-config/`
makes it a no-op.

`~/.ssh` and `~/.gnupg` are outside `~/.config` and are never touched. Browser
profiles, Proton sessions and app logins **are** inside it — read
[`roles/reset`](roles/reset/README.md) before running this.

## Bootstrap a fresh machine

```sh
sudo pacman -S --needed ansible git
git clone git@github.com:quantumfate/system-config.git
cd system-config
ansible-galaxy install -r requirements.yml
./bootstrap.sh            # == ansible-playbook site.yml --limit "$(hostname)" --ask-become-pass
```

The machine needs an inventory entry and a `host_vars` file under its own
hostname first — see [Hosts](#hosts).

First run is interactive once: `pass-cli login` needs a TTY. Everything after
that is idempotent — re-run any time.

## Layout

```text
site.yml                        role order, tags, per-role gating
group_vars/all/main.yml         identity, secrets backend, look and feel
group_vars/all/roles.yml        roles_default → roles_enabled
group_vars/all/packages.yml     package sets per feature
group_vars/all/projects.yml     git checkouts kept in sync
group_vars/all/environment.yml  PATH + env vars shared by session_env and zsh
host_vars/<hostname>.yml        profile, monitors, flags, role overrides  ← edit this
inventory/hosts.yml             one entry per machine, local connection
roles/                          one concern each, each with its own README
```

## Roles

Each role documents itself; the tag is the role name unless noted.

**Bootstrap** — [`base`](roles/base/README.md) ·
[`password_manager`](roles/password_manager/README.md) ·
[`secrets`](roles/secrets/README.md) ·
[`packages`](roles/packages/README.md)

**System** — [`sudoers`](roles/sudoers/README.md) ·
[`user_dirs`](roles/user_dirs/README.md) ·
[`login_shell`](roles/login_shell/README.md) ·
[`keyboard`](roles/keyboard/README.md) ·
[`console`](roles/console/README.md) ·
[`desktop_entries`](roles/desktop_entries/README.md) ·
[`display_manager`](roles/display_manager/README.md) ·
[`docker`](roles/docker/README.md) ·
[`virtualization`](roles/virtualization/README.md) ·
[`power_profile`](roles/power_profile/README.md) ·
[`devenv`](roles/devenv/README.md)

**Dotfiles** — [`chezmoi`](roles/chezmoi/README.md) ·
[`yazi`](roles/yazi/README.md) ·
[`project_checkouts`](roles/project_checkouts/README.md) ·
[`session_env`](roles/session_env/README.md) ·
[`zsh`](roles/zsh/README.md) ·
[`theming`](roles/theming/README.md) ·
[`browser_profiles`](roles/browser_profiles/README.md)

**Lifecycle** — [`cleanup`](roles/cleanup/README.md) ·
[`reset`](roles/reset/README.md)

**Services** — [`audio`](roles/audio/README.md) ·
[`obsidian_index`](roles/obsidian_index/README.md) ·
[`obsidian_linear`](roles/obsidian_linear/README.md)

## Common runs

```sh
L="--limit $(hostname)"
ansible-playbook site.yml $L --ask-become-pass --check --diff   # dry run
ansible-playbook site.yml $L --ask-become-pass -t packages      # one concern
ansible-playbook site.yml $L --ask-become-pass -t dotfiles      # chezmoi + friends
ansible-playbook site.yml $L --ask-become-pass --skip-tags bootstrap
./bootstrap.sh -r "theming zsh"                              # same, by role name
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
    github: { private: "-----BEGIN…", public: "ssh-ed25519 …" }
  vault_gpg: { public: "…", private: "…", fingerprint: "…" }
  ```

  With `vault`, [`roles/password_manager`](roles/password_manager/README.md) is
  skipped entirely — no Proton Pass dependency during provisioning.
