# Parity map (v1, modeled on DOGE v11)
| Component | Repo location |
|---|---|
| Agent profile (name, title, description, welcome message, avatar shape/color) | `profile/profile.json`, `profile/welcome_message.txt` (generic for any owner) |
| Per-agent settings | `profile/settings.json` |
| Profile picture | **TODO(Empress):** `profile/avatar.png` + `skills/elonqa-getting-started/elonqa-avatar.jpg` not supplied yet (`profile/AVATAR-TODO.md`); Step 0 still runs unconditionally |
| First-run setup flow and all setup cards | `skills/elonqa-getting-started/SKILL.md` |
| "Have you used ElonQA before?" card | setup question 2 |
| Source library (sources, verbatim quotes with locators, answer log, unknown log) | `records/eq_db.py` |
| How to answer, cite, and say "I don't know" | `skills/elon-answer/SKILL.md` |
| New-posts watch (optional) | routine 2 in `routines/v1-routine-prompts.md` |
| Dependencies and install | `UPGRADE.md` step 1b |
| Private memory (`~/memory/eq/brain.db` + `eqmem`) | `skills/private-memory-db/SKILL.md`, `memory/mem.py` |
| Backup (GitHub, default / weekly file) | setup backup card; `records/eq_db.py` auto-push; weekly file routine |
| Hive Mind (send-only client, on by default, report trigger) | `skills/hive-mind/SKILL.md`, `hive/hive.py` (DOGE v11 client, CODES line adds eq/gb), `hive/README.md` |
| Creator feedback | `skills/elonqa-getting-started/SKILL.md`, `hive/README.md` |
| Routines and exact prompts | `routines/v1-routines.md`, `routines/v1-routine-prompts.md` |
| Automatic weekly updates (mandatory, always on) | `routines/weekly-update-check.md`, `UPGRADE.md` section A, setup skill "Automatic updates", monthly check re-creates it |
| Monthly settings check | `skills/elonqa-getting-started/SKILL.md`, `routines/v1-routine-prompts.md` |
| Safety rules | `docs/safety.md`, `UPGRADE.md` guardrails |
| Upgrade procedure | `UPGRADE.md` |
| Version | `VERSION`, `CHANGELOG.md` |

Built-in platform skills it also relies on (provided by Grok Bot itself, not shipped here): x-api-mcp-guide, sign-in, vault, in-chat-forms, send-on-behalf, routines, no-connector-fallback.

Not shipped on purpose: Hive Mind intake/review/aggregation code, and any owner records, memory, or audio.
