# docker

Container runtime: group membership and the services enabled.

- **Runs when** `vms`.
- **Touches** the `docker` group, `docker.service`, `containerd.service`.
- **Tag** `system`, `docker`

The package itself comes from `vm_packages`. Group changes need a re-login.
