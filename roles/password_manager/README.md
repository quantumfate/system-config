# password_manager

Installs Proton Pass `pass-cli` and makes sure a vault session is open, so
`secrets` can read key material at run time.

- **Runs when** `secrets_backend == 'pass-cli'`.
- **Tag** `secrets`, `bootstrap`

The login step is interactive by design — first provision needs a TTY.
