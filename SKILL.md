---
name: hermes-agent-in-buzz
description: Wire a named Hermes profile to Buzz with no Agents card.
version: 2.0.0
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [buzz, gateway, nostr, profiles]
---

# Hermes Agent in Buzz (cardless gateway)

Create the helper **entirely outside Buzz** (Hermes profile + key + gateway on the Mac). Buzz only **admits** the public hex as a **member** in People, then you seat them in rooms. They **will not** appear on the **Agents** page. That page is Desktop bot cards. Missing there is success. Do not Create agent / Add agents.

**Done** means they are live and reply to a DM or `@DISPLAY_NAME` in a room they are seated in. Name, photo, and People add without a reply is not done.

Default-profile recipe (no `-p`): [`references/default-profile.md`](./references/default-profile.md). Do not mix.

Scripts: [`scripts/`](./scripts/). Never print `BUZZ_PRIVATE_KEY`. Never paste the owner’s secret.

Fill on paper (not git):

```text
YOURUSER=          # `whoami`
SLUG=              # Hermes profile, lowercase
DISPLAY_NAME=      # what people will @mention
YOUR-RELAY=        # host only, e.g. buzz.example.com
OWNER_HEX=         # owner’s public key, 64 hex
PUBHEX=            # helper’s public key, filled at step 3
CHANNEL=           # optional proof room
```

---

## When to Use

- Buzz community already works; the owner can post.
- A named Hermes profile should talk in Buzz as a person.
- No Desktop Agents card. No Add agents.

Don't use for: installing Buzz, Docker, DNS, or Hermes. Don't use to attach the **default** profile (other file). Don't use if the user asked to Create agent in Buzz.

---

## Outline (chart this path)

Do not skip a step. Each line is one job. Stop if its **Done when** fails.

| Step | Job | Done when |
|---|---|---|
| 0 | Prerequisites | CLI, profile, ping, buzz, owner can open **People** |
| 1 | Identity files | `SOUL.md` first line is `You are DISPLAY_NAME` |
| 2 | Unique secret (new person only) | Script prints `PUBHEX=`; no other profile shares it |
| 3 | Gateway config | Each `config get` matches the table |
| 4 | Owner admits hex in **People** as **member** | `users get` is not 403. Still absent on **Agents** |
| 5 | Kind-0 name | `users get --name DISPLAY_NAME` returns that pubkey |
| 6 | Kind-0 photo | `users get` includes `picture` |
| 7 | Gateway install + start (this slug only) | Log: `Active profile: SLUG` and `connected as DISPLAY_NAME` |
| 8 | Prove live | DM or `@DISPLAY_NAME` in a **seated** room gets one reply from `PUBHEX` |
| 9 | Later rooms | If silent after a new seat: restart **this slug only**, ping again |

Existing live helper (keep the old key): skip step 2 mint. See **Same-key migrate**.

---

## Prerequisites

Use Terminal on the Mac. Paste one command, Enter, read Pass/Fail.

1. `hermes --version` — **Done when** a version line prints.
2. `hermes profile list` — **Done when** Profile column has `SLUG`. Create if missing: `hermes profile create SLUG --description "One-line job."` Create often **clones** another profile’s `.env` and `SOUL.md`. Treat that as a clone until step 2 proves a unique key.
3. `hermes -p SLUG chat -q "Reply with exactly PING-A1"` — **Done when** reply contains `PING-A1`.
4. `hermes -p SLUG config get model` and `hermes -p SLUG config get auxiliary.compression` — **Done when** `model.provider` matches the real login (`xai-oauth` vs `lmstudio`, not mixed). Compression `provider` is `xai-oauth` if there is no `XAI_API_KEY`.
5. `command -v buzz` — **Done when** an absolute path prints (often `/usr/local/bin/buzz`).
6. Owner posts one message in Buzz Desktop. `curl -sS -o /dev/null -w "%{http_code}\n" --max-time 10 https://YOUR-RELAY` is not `000`.
7. Owner can open **People / Invites**. **Do not open Agents.** This person will never be listed there. This step does not need `hermes-acp`.

Named slug: never `hermes gateway setup` without `-p SLUG`. Never put this helper’s `BUZZ_PRIVATE_KEY` in `~/.hermes/.env`.

---

## Procedure

### 1. Identity files

Folder: `/Users/YOURUSER/.hermes/profiles/SLUG/`

- `profile.yaml` `description:` is the job line.
- `SOUL.md` first line: `You are DISPLAY_NAME, …` — **not** a copied body from another profile.

**Done when:** first line names `DISPLAY_NAME`.

### 2. Unique secret (new person only)

Two names must not share one pubkey. If `.env` already has a key, it may be a **clone**.

From this skill’s `scripts/` directory:

```bash
python3 scripts/04-mint-unique-key.py SLUG
```

**Done when:** stdout has `PUBHEX=` and 64 hex. Copy that to paper. The script must **not** print the private key. It refuses `default`. It refuses to rotate a key that is already unique. If this slug matched another profile, it mints a new key and leaves the donor unchanged.

Brand-new unused pubhex: `buzz users get` with that env is **403 `relay_membership_required`** until step 4. That is expected.

Existing live helper: do **not** run this script.

Optional snapshot (no secrets): `python3 scripts/00-snapshot-pubkeys.py`

### 3. Gateway config

```bash
python3 scripts/01-apply-gateway-config.py SLUG OWNER_HEX wss://YOUR-RELAY
```

Then confirm with `hermes -p SLUG config get KEY`.

| Key | Value |
|---|---|
| `gateway.platforms.buzz.enabled` | `true` |
| `gateway.platforms.buzz.extra.relay_url` | `wss://YOUR-RELAY` |
| `gateway.platforms.buzz.extra.cli_path` | absolute `buzz` |
| `gateway.platforms.buzz.extra.channels` | `[]` (all **joined** rooms) |
| `gateway.platforms.buzz.extra.poll_interval` | `4` |
| `gateway.platforms.buzz.extra.require_mention` | `true` |
| `gateway.platforms.buzz.extra.allow_all_users` | `false` |
| `gateway.platforms.buzz.extra.allowed_users` | `[OWNER_HEX]` |
| `display.platforms.buzz.interim_assistant_messages` | `false` |
| `display.platforms.buzz.tool_progress` | `off` |
| `gateway.platforms.buzz.gateway_restart_notification` | `false` |
| `gateway.delivery_ledger` | `false` |

Also: `model.provider` / `model.default` as this household uses; `auxiliary.compression.provider` `xai-oauth` if no `XAI_API_KEY`.

Strip cloned `platforms.buzz.home_channel` (it is another profile’s DM UUID). Keep `enabled: true`.

Script does not restart. Keeps `BUZZ_PRIVATE_KEY`. `.env` mode `600`.

**Done when:** each get matches. `.env` still has `BUZZ_PRIVATE_KEY`.

### 4. Owner admits the public hex (People, not Agents)

This does **not** create an agent in Buzz. It only admits a key that already exists on the Mac.

1. Buzz Desktop as owner.
2. **People / Invites**. Stay off **Agents**.
3. Add **member** (a person). Paste `PUBHEX` (64 hex). Role **Member**.
4. They may show as Unnamed until step 5.

Do not Add agents. Do not + Create agent. That puts a **second** identity on **Agents**.

They **will not** appear on **Agents**. Look in **People**.

**Done when:** `users get` with that env is not 403, or `buzz channels list` rc 0. Unnamed in People is OK. Absent on Agents is OK.

### 5. Kind-0 name

```bash
python3 scripts/02-set-kind0-profile.py SLUG DISPLAY_NAME
```

**Done when:** `buzz users get --name DISPLAY_NAME` returns `PUBHEX`. Reopen People if the UI still says Unnamed.

### 6. Kind-0 photo

No Agents card means no tap-to-change photo. Extra JPEG metadata → relay **422**.

```bash
# Pillow lives in the Hermes venv
"$HOME/.hermes/hermes-agent/.venv/bin/python" \
  scripts/06-clean-upload-avatar.py SLUG DISPLAY_NAME /full/path/to/photo.png
```

**Done when:** `users get --name DISPLAY_NAME` includes `picture`. Reopen DM/People if the face is cached blank.

### 7. Gateway install and start (this slug only)

Until this runs, DMs and `@Name` go nowhere.

```bash
hermes -p SLUG gateway install --force
hermes -p SLUG gateway start
hermes -p SLUG gateway status
```

Log: `/Users/YOURUSER/.hermes/profiles/SLUG/logs/gateway.log` (not default `~/.hermes/logs`).

**Done when:** status is running; log has `Active profile: SLUG` and `Buzz: connected … as DISPLAY_NAME`. `watching N` may be 0 or 1.

Never `gateway restart --all` / `stop --all`. Desktop Restart is the **default** profile only.

### 8. Prove live (not done until this)

Send a DM **after** step 7, or seat them in `CHANNEL` as a **member** (not Add agents) and `@DISPLAY_NAME ping`.

**Done when:** one reply. `buzz messages get` shows `pubkey` = `PUBHEX`. Messages sent before start never arrived — send again.

| If silent | Meaning |
|---|---|
| No `connected as DISPLAY_NAME` | Gateway not up |
| Log `Unauthorized user` | Allowlist. Set `allowed_users` to `OWNER_HEX`, then `bash scripts/05-restart-one.sh SLUG` |
| Room created after connect | Frozen watch list. Seat, then `05-restart-one.sh SLUG`, ping again |
| Two different answers | Leftover Desktop Start / `hermes-acp` on this hex. Stop that card. Do not edit `managed-agents.json` |

### 9. New rooms later

Watch list is taken at connect. Seat them. If `@DISPLAY_NAME` is silent: `bash scripts/05-restart-one.sh SLUG`, ping again. Still not done until the reply lands.

---

## Same-key migrate (existing helper)

Keep `BUZZ_PRIVATE_KEY` already in that `.env`. Do not run `04-mint-unique-key.py`.

1. `python3 scripts/00-snapshot-pubkeys.py` — write this slug’s pubkey prefix.
2. Step 3 config.
3. Steps 5–6 name/photo with **that** key.
4. Pink **Delete agent** only after the owner names that slug. Confirm the dialog is that **exact** name. Delete archives them and drops **every** channel seat. Same key does not keep seats. Notes: [`scripts/03-delete-card-IS-OWNER-ONLY.md`](./scripts/03-delete-card-IS-OWNER-ONLY.md).
5. Owner People-adds **the same PUBHEX** as member.
6. `bash scripts/05-restart-one.sh SLUG`
7. Prove `@Name` from that hex. No `hermes-acp` / `buzz-acp` for that pubkey.

---

## Scripts

| File | What | Never |
|---|---|---|
| `scripts/00-snapshot-pubkeys.py` | Read-only whoami | Print private keys |
| `scripts/01-apply-gateway-config.py` | `config set` + strip non-secret `BUZZ_*` | Restart; touch private key |
| `scripts/02-set-kind0-profile.py` | `--name` [avatar URL] | Print private key |
| `scripts/03-delete-card-IS-OWNER-ONLY.md` | Owner Delete dialog | Delete the wrong name |
| `scripts/04-mint-unique-key.py` | New person unique secp, print `PUBHEX=` | Rotate a unique live key; touch donors |
| `scripts/05-restart-one.sh` | One slug restart | `--all` |
| `scripts/06-clean-upload-avatar.py` | Clean JPEG, upload, `--avatar` | `--private-key` on argv |

---

## Pitfalls

- **Created in Buzz.** Agents / Add agents / + Create agent mints a second identity. Do not use it. Missing on Agents is success.
- **Name/photo ≠ live.** Gateway still stopped → first DM silent. Keep going through step 8.
- **Clone `.env`.** Profile create copied another secret. Mint unique; do not start two names on one key.
- **Public hex stored as private key.** 403 on a hex People already has. Not the same as 403 on a brand-new hex before People add.
- **Empty allowlist + `allow_all_users` false.** Owner DM is `Unauthorized` and **no** pairing code.
- **JPEG metadata.** Relay 422. Use `06-clean-upload-avatar.py`.
- **Watch list freeze.** New seat after connect can be silent until this slug restarts.
- **`hermes gateway restart` with no `-p`.** You restarted default, not this slug.
- **Pink Delete.** Archives + drops every seat. Same key does not skip re-add.
- **JSON-edit `managed-agents.json`.** Do not.
- **`--all` gateway.** Do not.

---

## Verification

Not done until every line is true, including a real reply.

- [ ] Created on the Mac. Never created on Agents. Agents page does not list them.
- [ ] People shows them as **member** (name/photo after kind-0; reopen if cache).
- [ ] `BUZZ_PRIVATE_KEY` only in that profile `.env`, unique vs other slugs.
- [ ] `hermes -p SLUG gateway status` running; log `connected as DISPLAY_NAME`.
- [ ] `users get --name DISPLAY_NAME` is `PUBHEX`.
- [ ] Owner DM **or** `@DISPLAY_NAME` in **any seated room** gets one reply from that hex.
- [ ] `ps` has no `hermes acp` / `buzz-acp` for that pubkey.
