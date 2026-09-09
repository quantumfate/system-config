# session_env

The login-session environment, in two layers:

| File                                    | Read by                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------ |
| `~/.config/environment.d/00-shell.conf` | `systemd --user` at login — every uwsm session and user unit inherits it |
| `~/.config/uwsm/env`, `env-niri`        | the uwsm session, Wayland compositor vars only                           |

- **Vars** `env_paths`, `env_paths_devenv`, `env_vars`, `env_session_vars` in
  `group_vars/all/environment.yml`.
- **Tag** `dotfiles`, `session_env`

Those lists are shared: `roles/zsh` renders the same ones into `~/.zshenv` for
shells started outside uwsm. Edit them in one place.
