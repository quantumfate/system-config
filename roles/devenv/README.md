# devenv

The toolchain bits no package provides: the rustup channel and components, the
tree-sitter CLI, and the pip-only git tools.

- **Runs when** `devenv`.
- **Tag** `devenv`

Assumes `rustup` is already installed — it comes from `dev_packages`, and this
role fails loudly if it is missing.
