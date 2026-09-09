# power_profile

Pins the CPU energy-performance preference to `performance` while the machine
is up.

- **Runs when** `gaming`, and only on an EPP-capable scaling driver
  (`amd-pstate-epp`, `intel_pstate`) — other drivers are reported and skipped.
- **Touches** `/etc/systemd/system/epp-performance.service`.
- **Tag** `system`, `power`
