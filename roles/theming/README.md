# theming

GTK, Qt, cursor and browser theming — one flavour, one accent, one type scale,
published to every toolkit and to the XDG portals. Also installs the per-app
catppuccin tarballs for kitty, qt5ct/qt6ct and Kvantum (`archives.yml`) — the
themes a role-rendered config points at. Supersedes chezmoi for the GTK, Qt,
Kvantum, xsettingsd, Zen `user.js` and the btop/rofi/wlogout/zathura
skeleton configs: those stop at provisioning, never at login, and `,theme.sh`
owns the live palette seam.

- **Vars** `theme_flavour`, `theme_accent`, `theme_packages`, `theme_archives`
  and the type scale in `defaults/main.yml`; `browser_config_src` in
  `group_vars/all/main.yml`.
- **Tag** `dotfiles`, `theming` (package installs are also tagged `privileged`)

Every toolkit needs telling separately, and the portals read none of those files:

| Layer    | File                                                                    | Note                                                                                                      |
| -------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| GTK2     | `~/.gtkrc-2.0.mine`                                                     | the `.mine` file, because nwg-look owns `~/.gtkrc-2.0`                                                    |
| GTK3     | `~/.config/gtk-3.0/settings.ini`                                        |                                                                                                           |
| GTK4     | `settings.ini` + **symlinked** `gtk.css`/`gtk-dark.css`/`assets`        | libadwaita ignores `gtk-theme-name` entirely                                                              |
| Qt       | `qt6ct.conf` / `qt5ct.conf` + Kvantum                                   | fonts are QDataStream blobs, see `templates/_qtfont.j2`                                                   |
| X11      | `xsettingsd.conf`                                                       | XWayland clients                                                                                          |
| Portals  | **dconf** `/org/gnome/desktop/interface/*`                              | what `xdg-desktop-portal-gtk` reports — miss this and the app is themed but its file chooser is not       |
| Session  | `~/.config/environment.d/50-theming.conf`                               | palette-invariant only now — `XCURSOR_*` moved to `,theme.sh`'s live fan-out, see its `apply_cursor` step |
| btop     | `~/.config/btop/btop.conf`                                              | skeleton + runtime palette via `apply_btop`                                                               |
| launcher | `~/.config/rofi/config.rasi` + `~/.local/share/rofi/themes/custom.rasi` | skeleton (config) + user theme (custom) + palette via `apply_rofi`                                        |
| wlogout  | `~/.config/wlogout/style.css`                                           | skeleton + runtime flavour in icon paths and direct palette colours via `apply_wlogout`                   |
| zathura  | `~/.config/zathura/zathurarc`                                           | skeleton + runtime palette via `apply_zathura`                                                            |

`roles/browser` renders the shared Zen config and links it into each profile.
Zen reads `user.js` and the chrome CSS once at
launch, so a palette change needs a restart to be visible.

`,theme.sh apply_zen` writes the current accent into `zen-palette.css` and
`user.js` at runtime (the browser role owns the static CSS, so nothing
overwrites it), so the files are always correct immediately even before the
next Ansible converge.

The role's final task calls `{{ theme_apply_script }} apply`, which reads the
live `theme.json` store and re-applies the user's current palette. A playbook
run therefore does not override the active desk theme with the seed variables;
the seed only provides the fallback for a fresh account before the first
apply.

The seed's scheme follows the seed flavour, never a hardcoded preference: a
dark seed renders `gtk-application-prefer-dark-theme=1` and
`color-scheme=prefer-dark` into `settings.ini` and the nwg-look store, a
latte seed renders the light equivalents, and `,theme.sh` keeps those files
in agreement with the *live* palette on every apply — apps adapt to the
system scheme, nothing is ever forced one way. A fresh install therefore
starts in the scheme its flavour implies instead of always dark.

`awww` (installed via `theme_extra_packages`) is `,theme.sh`'s wallpaper
backend — swww's maintained continuation under a new name, not a fork. The
package lands on converge; the daemon swap itself happens the next time
`,theme.sh` applies a wallpaper, not during the playbook run.

```sh
ansible-playbook site.yml -t theming --ask-become-pass         # repo + AUR packages
ansible-playbook site.yml -t theming --skip-tags privileged    # dotfiles only, no sudo
```
