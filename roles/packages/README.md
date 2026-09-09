# packages

Resolves the package set from the feature flags and installs it in one `yay`
transaction — repo and AUR alike.

- **Vars** `common_packages`, `desktop_packages`, `laptop_packages`,
  `dev_packages`, `gaming_packages`, `vm_packages` in
  `group_vars/all/packages.yml`.
- **Depends on** `base` (for `yay`).
- **Tag** `packages`

This role owns package installation for the whole playbook. A role installs a
package itself only when it must run _before_ this one — in practice, `base`.
