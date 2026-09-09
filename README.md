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

chezmoi no longer prompts and no longer carries `.chezmoiscripts` or
`.chezmoiexternal`. All of it lives in `roles/`.

`site.yml` owns ordering and tags, nothing else. Hard requirements live in a
role's `meta/dependencies`; feature flags gate whole roles in `site.yml` and
partial lists inside a role.

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

```text
site.yml                        role order, tags, feature-flag gating
group_vars/all/main.yml         profile + feature flags + identity  ← edit this
group_vars/all/packages.yml     package sets per feature
group_vars/all/projects.yml     git checkouts kept in sync
group_vars/all/environment.yml  PATH + env vars shared by session_env and zsh
inventory/hosts.yml             localhost, local connection
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

**Services** — [`audio`](roles/audio/README.md) ·
[`obsidian_index`](roles/obsidian_index/README.md) ·
[`obsidian_linear`](roles/obsidian_linear/README.md)

## Common runs

```sh
ansible-playbook site.yml --ask-become-pass --check --diff   # dry run
ansible-playbook site.yml --ask-become-pass -t packages      # one concern
ansible-playbook site.yml --ask-become-pass -t dotfiles      # chezmoi + friends
ansible-playbook site.yml --ask-become-pass --skip-tags bootstrap
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
    codeberg: { private: "-----BEGIN…", public: "ssh-ed25519 …" }
  vault_gpg: { public: "…", private: "…", fingerprint: "…" }
  ```

  With `vault`, [`roles/password_manager`](roles/password_manager/README.md) is
  skipped entirely — no Proton Pass dependency during provisioning.
