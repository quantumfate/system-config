# keyboard

Custom Dvorak XKB layout, installed system-wide and mirrored to the TTY.

- **Touches** `/usr/share/X11/xkb/symbols/`, `evdev.xml`, `evdev.lst`, the
  console keymap.
- **Vars** `keyboard_layout` in `group_vars/all/main.yml`.
- **Tag** `system`, `keyboard`

The symbols file lives in this role rather than in chezmoi because it targets
`/usr/share`, not `$HOME`.
