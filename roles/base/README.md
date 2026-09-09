# base

The minimum a fresh machine needs before any other role can run: asserts the
host is Arch-family, installs the fetch tools and `base-devel`, then `yay`.

- **Touches** system packages via `pacman`.
- **Tag** `base`, `bootstrap`

Every AUR install downstream goes through the `yay` this role puts in place.
