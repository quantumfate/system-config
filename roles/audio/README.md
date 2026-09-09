# audio

WirePlumber policy: make a connecting Bluetooth sink the default one, fall back
on disconnect, and notify on sink changes.

- **Touches** `~/.local/share/wireplumber/scripts/`,
  `~/.config/wireplumber/wireplumber.conf.d/`, the `audio-notify` user unit.
- **Vars** `audio_deploy_wireplumber_hooks`, `audio_deploy_notification_service`,
  `audio_deploy_bluetooth_policy` (defaults).
- **Tag** `audio`

The Bluetooth policy exposes the headset mic by switching A2DP → HSP/HFP while
recording; HFP is 16 kHz mono, so playback quality drops while the mic is live.
