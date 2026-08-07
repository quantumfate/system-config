# System Config

Ansible playbook that provisions my CachyOS/Arch system config end to end, then
hands `$HOME` over to chezmoi.

## Separation of concerns

| Scope                                   | Owner   |
| --------------------------------------- | ------- |
| `/etc`, system units, groups, bootloader, packages | Ansible |
| `$HOME` dotfiles                        | chezmoi |
| External checkouts, themes, downloads (`$HOME`) | Ansible (`roles/externals`) |
| Prompted values (profile, monitors, feature flags) | Ansible → rendered into `~/.config/chezmoi/chezmoi.toml` |

chezmoi no longer prompts and no longer carries `.chezmoiscripts` or
`.chezmoiexternal`. All of it lives in `roles/`.

## Bootstrap a fresh machine

```sh
sudo pacman -S --needed ansible git
git clone git@codeberg.org:quantumfate/workstation.git
cd workstation
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

| Role               | Replaces (former `.chezmoiscripts` entry)          |
| ------------------ | -------------------------------------------------- |
| `base`             | `05-install-yay`, `install-password-manager` deps   |
| `password_manager` | `.install-password-manager.sh`, `10-login-proton-pass` |
| `secrets`          | `01-install-ssh-keys`                               |
| `packages`         | `install-packages`                                  |
| `sudoers`          | `00-install-sudoers`                                |
| `user_dirs`        | `02-xdg`                                            |
| `login_shell`      | `09-change-login-shell`                             |
| `keyboard`         | `01-install-layout`                                 |
| `console`          | `08-configure-tty`                                  |
| `desktop_entries`  | `04-install-desktop-entries`                        |
| `display_manager`  | `12-install-sddm`                                   |
| `docker`           | `11-setup-docker`                                   |
| `virtualization`   | `07-install-cockpit-vm-kvm`                         |
| `power_profile`    | `12-install-epp-performance`                        |
| `devenv`           | `05-prepare-nvim-deps`, `06-install-dev-env-packages` |
| `chezmoi`          | dotfiles clone + apply, `03-reload-user-units`      |
| `externals`        | `.chezmoiexternal.toml.tmpl` (plugins, dev checkouts, catppuccin themes) |
| `browser_profiles` | `05-install-userjs-for-browser`                     |
| `theming`          | `00-finalise-theme`, `20-do-additional-theming`     |

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
    codeberg: {private: "-----BEGIN…", public: "ssh-ed25519 …"}
  vault_gpg: {public: "…", private: "…", fingerprint: "…"}
  ```

  With `vault`, `roles/password_manager` is skipped entirely — no Proton Pass
  dependency during provisioning.

