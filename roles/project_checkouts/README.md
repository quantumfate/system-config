# project_checkouts

Keeps the git checkouts under `~/Projects` in sync — cloned if missing, then
pulled `--ff-only`, and skipped entirely while dirty.

- **Vars** `projects_repos`, `projects_repos_gaming`, `projects_repos_desktop`,
  `projects_with_roles` in `group_vars/all/projects.yml`.
- **Tag** `dotfiles`, `projects`

Nothing here configures an app. Three of these checkouts ship their own ansible
role (`hypr`, `quickshell`, `nvim`); `site.yml` converges those _after_ this
role has updated them, resolving them through `ansible.cfg`'s `roles_path`.

The flag-gated repo sets are conditional inside the role rather than in
`site.yml`, because the role always runs — only parts of its list are optional.
