# secrets

SSH keys and GPG key material into `~/.ssh` and the keyring.

- **Vars** `secrets_backend`, `ssh_key_targets` in `group_vars/all/main.yml`.
- **Tag** `secrets`, `bootstrap`

Backend is chosen by `secrets_backend`: `pass-cli` reads from Proton Pass at run
time (`pass_cli.yml`), `vault` from an encrypted `group_vars/all/vault.yml`
(`vault.yml`). Nothing secret is ever committed to this repo.
