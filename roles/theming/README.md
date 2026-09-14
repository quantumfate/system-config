# theming

GTK, Qt, cursor and browser theming — one flavour, one accent, one type scale,
published to every toolkit and to the XDG portals. Also installs the per-app
catppuccin tarballs for kitty, qt5ct/qt6ct and Kvantum (`archives.yml`) — the
themes a role-rendered config points at. Themes that chezmoi-owned configs
include are `.chezmoiexternal` entries in the dotfiles (see
[`roles/chezmoi`](../chezmoi/README.md)). Supersedes chezmoi for the GTK, Qt,
Kvantum, xsettingsd and Zen `user.js` files.

- **Vars** `theme_flavour`, `theme_accent`, `theme_packages`, `theme_archives`
  and the type scale in `defaults/main.yml`; `browser_config_src` in
  `group_vars/all/main.yml`.
- **Tag** `dotfiles`, `theming` (package installs are also tagged `privileged`)

Every toolkit needs telling separately, and the portals read none of those files:

| Layer   | File                                                             | Note                                                                                                      |
| ------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| GTK2    | `~/.gtkrc-2.0.mine`                                              | the `.mine` file, because nwg-look owns `~/.gtkrc-2.0`                                                    |
| GTK3    | `~/.config/gtk-3.0/settings.ini`                                 |                                                                                                           |
| GTK4    | `settings.ini` + **symlinked** `gtk.css`/`gtk-dark.css`/`assets` | libadwaita ignores `gtk-theme-name` entirely                                                              |
| Qt      | `qt6ct.conf` / `qt5ct.conf` + Kvantum                            | fonts are QDataStream blobs, see `templates/_qtfont.j2`                                                   |
| X11     | `xsettingsd.conf`                                                | XWayland clients                                                                                          |
| Portals | **dconf** `/org/gnome/desktop/interface/*`                       | what `xdg-desktop-portal-gtk` reports — miss this and the app is themed but its file chooser is not       |
| Session | `~/.config/environment.d/50-theming.conf`                        | palette-invariant only now — `XCURSOR_*` moved to `,theme.sh`'s live fan-out, see its `apply_cursor` step |

`templates/zen-user.js.j2` renders the shared browser prefs;
`roles/browser_profiles` links them into each profile.

`awww` (installed via `theme_extra_packages`) is `,theme.sh`'s wallpaper
backend — swww's maintained continuation under a new name, not a fork. The
package lands on converge; the daemon swap itself happens the next time
`,theme.sh` applies a wallpaper, not during the playbook run.

```sh
ansible-playbook site.yml -t theming --ask-become-pass         # repo + AUR packages
ansible-playbook site.yml -t theming --skip-tags privileged    # dotfiles only, no sudo
```
