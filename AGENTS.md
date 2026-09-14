# Agent notes

This repo provisions the system end to end (CachyOS/Arch) and then hands
`$HOME` over to chezmoi. The desktop repos —
[hypr](https://github.com/quantumfate/hypr) (compositor Lua),
[quickshell](https://github.com/quantumfate/quickshell) (shell),
[nvim](https://github.com/quantumfate/nvim) (editor) — each carry their own
role _inside their own checkout_; this repo orchestrates and owns everything
system-level (`/etc`, units, packages, boot).

## Read order

New to the repo, read in this order:

1. [README.md](README.md) — separation of concerns, hosts table, the
   `roles_enabled` mechanism, the bootstrap flow.
2. `roles/*/README.md` — one per role; the role is the unit of change.
3. [docs/hyprfocus.md](docs/hyprfocus.md) — the full `hyprfocus` engine
   (modes, scenes, bind trees). This repo executes part of that declaration
   (user units); hypr and quickshell execute the rest.
4. Cross-repo: hypr `AGENTS.md` (scene contract) and quickshell
   `ARCHITECTURE.md` (Store + policy stores).

## Repo map

| Path          | Owns                                                                                                      |
| ------------- | --------------------------------------------------------------------------------------------------------- |
| `site.yml`    | ordering + tags only; feature gating lives in `roles_enabled`                                             |
| `group_vars/` | `roles_default` (written in terms of feature flags)                                                       |
| `host_vars/`  | `roles_override` per machine, one file per inventory host                                                 |
| `roles/`      | one role per concern (`base`, `display_manager`, `gaming`, `obsidian_linear`, `user_units`, `theming`, …) |
| `docs/`       | `hyprfocus.md` (the cross-repo engine), `desktop-rice.md`                                                 |
| `flake.nix`   | a nix flake for the same provisioning scope                                                               |

## Contract

- **Convergence is local, per host**: every machine runs against itself
  (`bootstrap.sh` passes `--limit "$(hostname)"`). There is always an
  inventory entry + `host_vars` for the hostname, or the run must fail early.
- **`roles_enabled` is one dict, built in two layers** —
  `group_vars/all/roles.yml` (`roles_default` over feature flags) merged with
  `host_vars/<hostname>.yml` (`roles_override`). Every `when:` gates on it.
- **A repo delivers its own role**: quickshell/hypr/nvim deploy from a role
  inside their own checkouts (`roles/project_checkouts` places the checkouts).
  This repo's roles never hand-copy files owned by another repo — point at the
  consumer's role instead.
- **Hard requirements live in a role's `meta/dependencies`**, not in `site.yml`.
- Monitor names in `host_vars` stay in step with the `host_configs` table in
  the hypr checkout.

## Commands

```sh
just check        # fmt-check + lint (stylua, ruff, shfmt, shellcheck, yamllint, ansible-lint) + pytest
just fmt          # reformat in place
just lint         # static analysis
just test         # pytest
```

Run `just provision`-equivalents via `bootstrap.sh` (local connection,
`--limit $(hostname)`); never aim the playbook at another host.

## Style

- YAML passes `yamllint` + `ansible-lint`; shell passes `shellcheck` +
  shfmt (4-space); scripts pass `ruff`.
- Complete-sentence comments, no comment noise.
- Do not create role-level forks of state the shell/compositor own; if a
  consumer repo owns it, converge there.
