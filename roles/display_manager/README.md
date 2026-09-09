# display_manager

SDDM as the sole display manager: install, theme, keymap and keyring — and tear
down every competing greeter.

- **Touches** `/etc/sddm.conf.d/`, the `sddm` unit, the greeter `Xsetup`.
- **Vars** `sddm_theme_package` in `group_vars/all/main.yml`.
- **Tag** `system`, `display_manager`

`teardown.yml` removes the greetd/dms-greeter era leftovers; without it two
greeters race for the seat.
