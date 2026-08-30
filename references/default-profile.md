# Default Hermes profile on Buzz

Use this file only for the Buzz person whose brain is **default** Hermes (`~/.hermes/`, no `-p`). Roster name is **Hermes**.

Named helpers (Atlas, Zeus, Achilles, Hephaestus, …) use Clio-path [`SKILL.md`](../SKILL.md) with `-p SLUG`. Do not mix the two recipes. Do not Add agents for named helpers.

## What is different from a named slug

| Item | Named slug | Default (this file) |
|---|---|---|
| Hermes home | `/Users/YOURUSER/.hermes/profiles/SLUG/` | `/Users/YOURUSER/.hermes/` |
| Secret file | `profiles/SLUG/.env` | `~/.hermes/.env` |
| Gateway command | `hermes -p SLUG gateway setup` | `hermes gateway setup` (no `-p`) |
| Launchd | `ai.hermes.gateway-SLUG` | `ai.hermes.gateway` |
| Gateway log | `profiles/SLUG/logs/gateway.log` | `~/.hermes/logs/gateway.log` |
| Buzz display name | that helper’s name | **Hermes** |
| Desktop Start after gateway | off | off (same rule) |

Two names must not share one pubkey. Default Hermes is only the person named Hermes.

## Model (same as Dashboard)

Buzz does **not** get a second model. The gateway for default reads `~/.hermes/config.yaml` (`model.default` + `model.provider` + `model.base_url`).

Hermes Dashboard → this profile’s model picker writes that same file. After you change the model there:

```bash
hermes doctor
hermes gateway restart
```

**Pass:** `hermes doctor` does not say the provider is missing a key. Gateway log still `Active profile: default` and `connected ... as Hermes`. A new `@Hermes` turn uses the model you just picked.

Do not pin a model in the Buzz wizard. Do not set `model.provider` to `xai` (API key) if the only login is xAI **OAuth** (`xai-oauth`). `model.base_url` must match the provider you actually use (do not leave Anthropic’s URL on an xAI model).

Compression (summarizer) is a **separate** slot. If `auxiliary.compression.provider` is `xai` and there is no `XAI_API_KEY`, long threads post ⚠ Compression aborted into Buzz even while Grok chat works. Set:

```bash
hermes config set auxiliary.compression.provider xai-oauth
hermes gateway restart
```

Do not use the named-slug `SKILL.md` to attach this person. That recipe never writes a model or compression provider on default, so Hermes keeps whatever this home already had (on this clubhouse: Claude Sonnet until Dashboard + restart).

## Milestones (default only)

Prerequisites: Stage 0 in `SKILL.md` except 0.3 — you do **not** create a slug. Prove the brain with:

```bash
hermes chat -q "Reply with exactly PING-A1"
```

**Pass:** reply contains `PING-A1`.

Then the same Buzz identity path as named, with these substitutions:

1. **Create the Buzz person** — Agents → + → name **Hermes**, harness **Hermes**, then **Stop**. Copy `PUBHEX`.
2. **Member** of the closed community.
3. **Seat** only in rooms this assistant should hear. Blank “channels to watch” = **all joined** rooms. The word `Hermes` in other people’s messages counts as a ping unless you later tighten mention matching. Do not seat default Hermes in work rooms (ingestion, etc.) unless you want it to speak there.
4. **Secret** from Keychain `agent:PUBHEX` into **`/Users/YOURUSER/.hermes/.env`** (bottom of file):

```text
BUZZ_RELAY_URL=https://YOUR-RELAY
BUZZ_PRIVATE_KEY=PASTE_64_CHAR_HEX_ONLY
```

`chmod 600` that file. **Pass:** `buzz users get` with that env returns display name Hermes and your `PUBHEX`. Named profile `.env` files must **not** use this same secret.

5. **Desktop Start off**, start-on-launch off, auto-restart off on the Hermes card. Claude coaches stay green. Do not **Stop running agents**.
6. **Gateway:**

```bash
hermes gateway setup
```

Leave the private-key prompt **blank** if `.env` already has `BUZZ_PRIVATE_KEY`. Allow-all `y` for household. Empty channel list = all **joined** (see milestone 3).

**Pass:** `hermes gateway status` running. Log: `Active profile: default` and `Buzz: connected ... as Hermes`.

7. **Proof:** `@Hermes ping` in a room it should hear → **one** reply. Fail if a named helper answers, or if Desktop Start is still on (two brains).

If you later change `.env` or the Dashboard model: `hermes gateway restart` only — not `gateway stop --all`.

When Buzz posts ⏱️ / ⚠️ / compression abort, or Hermes sounds like the wrong model: **Troubleshooting** at the end of [`SKILL.md`](../SKILL.md).
