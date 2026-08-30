# Delete Agents card — owner only, one slug per turn

Pink **Delete agent** in Buzz Desktop (not Archive).

This agent **cannot** click Delete for you without seeing the **exact** card name in the dialog. Never Delete Achilles/Hermes/Hephaestus/… unless Leslie named that slug in the same message.

After Delete:

1. Channel seats for that hex are gone.
2. Owner add-member **the same 64-hex** (People — not Add agents).
3. `hermes -p SLUG gateway restart`
4. `@Name ping` in the room.

Do not hand-edit `managed-agents.json`.
Do not run `buzz agents archive` as a different helper (owner/admin only for third parties). Self-archive is only for a throwaway like Clio.

HermesTest (test card, not a keeper): owner may Delete that card in Desktop. No `hermestest` Hermes profile exists.
