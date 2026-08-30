# Channel routing

**Default rule (everyone):**

1. **Member** of the room → the gateway may listen (`watch_joined: true`, `channels list --member`).
2. **`@Name`** in the text → they may reply. Bare name or a p-tag without `@` is not a ping.

Not a member → do not watch, do not speak. Invited + no `@` → stay silent.

Do **not** hand-edit `config.yaml`. `watch_joined` should be `true` unless you are intentionally DM-only.

Optional extra (not the default): `channel_name_prefixes` (e.g. `build`, `PKM`) further limits which **member** rooms they subscribe to. Leave it empty so `@Name` works in every room they are seated in.

After config or adapter changes: `hermes -p SLUG gateway restart` (default: `hermes gateway restart`). Never `gateway stop --all`.

Harness chrome (⏱️ / ⚠️ / `Redirected current run`) is not posted to Buzz.
