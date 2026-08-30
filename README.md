# Hermes Agent in Buzz

Cardless gateway: create the helper **on the Mac**. Buzz only admits the public hex as a **People** member. They **will not** appear on **Agents**. Missing there is success.

| Track | Hermes home | Procedure |
|---|---|---|
| Named slug | `~/.hermes/profiles/<slug>/` | [`SKILL.md`](./SKILL.md) |
| Default profile | `~/.hermes/` (no `-p`) | [`references/default-profile.md`](./references/default-profile.md) |

Click-by-click steps, outline, scripts, Pass/Fail: [`SKILL.md`](./SKILL.md).

---

## What we are trying to do

You have a Buzz community and Hermes Agent on a Mac. You want a **named profile** to answer DMs and `@DISPLAY_NAME` in rooms they are seated in.

They are **not** Buzz agents. Do not Create agent / Add agents.

1. Hermes profile + unique key + `SOUL.md` on the Mac.
2. Owner pastes the **public** 64-hex in **People** as **member**.
3. Kind-0 name and photo via `buzz` CLI.
4. `hermes -p SLUG gateway install` then `start`.
5. **Done only when** a DM or `@Name` in a seated room gets a reply from that hex.

---

## Outline

See the table in [`SKILL.md`](./SKILL.md) (steps 0–9). Do not skip **Prove live**.

---

## Desired end state

| Check | Meaning |
|---|---|
| People shows the name and photo | Kind-0 landed |
| **Agents does not list them** | Correct |
| Member of the community; seated in rooms you care about | They can hear |
| Unique `BUZZ_PRIVATE_KEY` only in that profile `.env` | One name, one key |
| Gateway running; log `connected as DISPLAY_NAME` | Talk path |
| DM or `@Name` reply from that pubkey | **Done** |

---

## Placeholders

`YOURUSER`, `SLUG`, `DISPLAY_NAME`, `YOUR-RELAY`, `OWNER_HEX`, `PUBHEX`, `CHANNEL` — paper, not git. No secrets in git.

Scripts: [`scripts/`](./scripts/). Set `BUZZ_RELAY_URL=https://YOUR-RELAY` before snapshot / set-profile / avatar upload.
