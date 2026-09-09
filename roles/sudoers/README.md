# sudoers

The `/etc/sudoers.d/10-timeout` drop-in: a longer timestamp, made global.

- **Touches** `/etc/sudoers.d/`.
- **Tag** `system`, `sudoers`

`timestamp_type=global` is what lets `yay` and `papirus-folders` reach a warm
sudo stamp from a play with no tty — see `site.yml`'s `pre_tasks`. `validate=`
makes a bad file abort rather than lock you out.
