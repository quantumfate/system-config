# console

Catppuccin colours for the kernel VT, plus a legible font on hidpi.

- **Touches** the bootloader config (`grub.yml` / `limine.yml`, whichever is
  present) and `/etc/vconsole.conf`.
- **Vars** `vt_color_params` (defaults), `console_font` in
  `group_vars/all/main.yml`.
- **Tag** `system`, `console`

The palette is a kernel cmdline parameter, which is why a TTY theme has to go
through the bootloader.
