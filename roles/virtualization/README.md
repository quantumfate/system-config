# virtualization

libvirt/KVM with the Cockpit web console on <https://localhost:9090>.

- **Runs when** `vms`.
- **Touches** `libvirtd.service`, `cockpit.socket`, the `libvirt`/`kvm`/`wheel`
  groups, the libvirt bridge firewall rule.
- **Tag** `system`, `virtualization`

Group changes need a re-login before `virt-manager` works without sudo.
