# System Configuration

Ansible playbook that provisions my CachyOS/Arch system config end to end, then
hands `$HOME` over to chezmoi.

## Separation of concerns

| Scope                                                  | Owner                                                    |
| ------------------------------------------------------ | -------------------------------------------------------- |
| `/etc`, system units, groups, bootloader, packages     | Ansible                                                  |
| `$HOME` dotfiles                                       | chezmoi                                                  |
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

| Role               | Description                                 |
| ------------------ | ------------------------------------------- |
| `base`             | system deps                                 |
| `password_manager` | provides all secrets                        |
| `secrets`          | key management                              |
| `packages`         | system packages                             |
| `sudoers`          | sudo configuration                          |
| `user_dirs`        | xdg                                         |
| `login_shell`      | zsh primary shell                           |
| `keyboard`         | custom-dvorak layout                        |
| `console`          | tty theming                                 |
| `desktop_entries`  | sway and niri                               |
| `display_manager`  | system configuration for display-manager    |
| `docker`           | infra tools                                 |
| `virtualization`   | vms                                         |
| `power_profile`    | performance related                         |
| `devenv`           | neovim and dev dependencies                 |
| `chezmoi`          | dotfiles clone + apply, systemd unit-reload |
| `externals`        | plugins, dev checkouts, catppuccin themes   |
| `browser_profiles` | prowser profile settings                    |
| `theming`          | rice                                        |
| `yazi`             | file manager                                |

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
