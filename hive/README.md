# Hive Mind connection (for ElonQA bots)
Send-only, anonymous, ON by default for new ElonQA setups (owner can turn it off anytime). Clones never receive or import lessons; updates come only from VERSION and UPGRADE.md. Full rules: `skills/hive-mind/SKILL.md`.

Install (after private memory exists at `~/memory/eq/brain.db`):
```sh
mkdir -p ~/memory/eq ~/bin
curl -fsSL https://raw.githubusercontent.com/EmpressHeavy/ElonQAUpdates/main/hive/hive.py -o ~/memory/eq/hive.py
chmod +x ~/memory/eq/hive.py
printf '#!/bin/sh\nMEM_DB="$HOME/memory/eq/brain.db" exec python3 "$HOME/memory/eq/hive.py" "$@"\n' > ~/bin/eqhive && chmod +x ~/bin/eqhive
eqhive status
```
At setup (default on, no opt-in question): `eqhive on --bot eq`, confirm `eqhive status` shows enabled=1 bot=eq, then a weekly routine "Hive Mind weekly share" running `eqhive auto` (silent unless it fails). `eqhive off` + delete the routine only if the owner turns it off.

- `eqhive` is the standard `hive` client launched with `MEM_DB` pinned to this bot's own memory, so it can share a computer with DOGE or any other bot without touching their Hive Mind state.
- Lesson intake: `https://hive-mind-intake.empressheavy.workers.dev` (built into hive.py, one JSON POST a week, no sign-in or key). Bot code: `eq`.
- Creator feedback: POST `{"type":"feedback","bot":"eq","category":"...","text":"..."}` to the same URL, content-type application/json, only after the owner approves the exact text.
- Client in hive/hive.py is the DOGE v11 client v3.5.13, byte-for-byte identical except one line: the `CODES` table also lists `eq` (ElonQA) and `gb` (Music Mastering), so `hive on --bot eq` is accepted. No other change.
- Intake: the intake must list `eq` in its accepted bot codes; until it does, weekly sends are recorded as "not sent" in `eqhive shared` (never retried another way).
