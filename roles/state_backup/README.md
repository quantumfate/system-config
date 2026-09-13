# state_backup

Encrypts `$XDG_STATE_HOME` (theme, projects, focus, sound, dofus team state,
notifications — everything deliberately kept out of git) to one age blob, on
a timer.

- **Touches** `~/.config/systemd/user/state-backup.{service,timer}`, and
  installs `age`.
- **Vars** `state_backup_dest`, `state_backup_recipients_file`,
  `state_backup_interval` (defaults).
- **Tag** `state_backup`

`state_backup_dest` is where the encrypted blob lands. **It is a plain local
directory by default — no remote is decided yet.** Once one is, this is the
variable to point at it (rsync/rclone/whatever, over the same already-encrypted
blob); nothing else about the role changes.

The age *identity* (the private key that decrypts the blob) is never referenced
here and must not live in `state_backup_recipients_file` — that file holds
public recipients only, generated once via `age-keygen` and kept safe
elsewhere (a password manager, printed, a second machine). Losing it means the
backups are unrecoverable; losing the recipients file just means regenerating
it from the identity.
