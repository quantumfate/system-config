# cleanup

Tears down the roles this host has switched off.

Turning a role off in `roles_override` stops it converging, but nothing it
already installed goes away on its own — a disabled `display_manager` leaves
sddm enabled, a disabled `obsidian_linear` leaves its timer firing. This role
closes that gap.

It runs on every host, every time, right after `packages` and before the system
roles — so a disabled role is torn down before its neighbours converge on top
of it. On a host with nothing disabled it is a no-op.

## How it dispatches

For each role that is `false` in `roles_enabled`, it looks for
`roles/<name>/tasks/cleanup.yml` and includes it via `include_role` +
`tasks_from` (which is what puts the role's own defaults in scope). A role
without that file is simply skipped, so adding a teardown is opt-in per role.

Skipped entirely: `reset` and `cleanup` themselves, plus the roles that live in
their own checkout (`hypr`, `quickshell`, `nvim`) — those may not be cloned yet.

## Writing a `cleanup.yml`

Three rules:

1. **It is the inverse of `main.yml`, and nothing more.** Disable what it
   enabled, remove the files it wrote, drop the groups it added.
2. **It never touches user data.** `roles/gaming/tasks/cleanup.yml` unwires
   Lutris' libretro runner; `~/Games` — ROMs, saves, firmware — stays.
   `docker` and `virtualization` stop their daemons and leave
   `/var/lib/{docker,libvirt}` alone.
3. **It is safe on a machine where the role never ran.** Use
   `failed_when: false` on the `systemctl` calls; a unit that was never
   installed is not an error.

Roles that ship one: `display_manager`, `docker`, `virtualization`,
`power_profile`, `gaming`, `audio`, `obsidian_index`, `obsidian_linear`.

## Package removal

Off by default. Units and config come back cheaply; a pacman removal is the one
part of a teardown that can take a shared dependency with it.

```sh
ansible-playbook site.yml --limit quantum-laptop --ask-become-pass \
  -e cleanup_remove_packages=true
```

The removable set is every disabled feature's packages _minus_ everything the
enabled ones still ask for — `dev_packages` and `gaming_packages` both want
`base-devel`, and disabling one must not take it from the other.

## Variables

| Variable                  | Default                             | Meaning                                    |
| ------------------------- | ----------------------------------- | ------------------------------------------ |
| `cleanup_remove_packages` | `false`                             | also uninstall disabled features' packages |
| `cleanup_skip`            | external roles + `reset`, `cleanup` | never dispatched into                      |

See also [`reset`](../reset/README.md), the once-per-host flush of `~/.config`
and every user unit.
