# ElonQAUpdates

The official update source for the **ElonQA** Grok Bot: it answers about Elon Musk from his own X posts, books about him, and interview transcripts, with a citation for every claim and an honest "I don't know" when there's no source.

## For owners
Updates are **automatic and always on**: once a week the bot checks this repo and, if there's a newer version, updates itself and sends you a short "ElonQA updated to vN, here's what's new" note. This is built in and can't be switched off (you can move the time it runs).

## Safety promises
- The bot only accepts updates from this exact repo.
- Update files can never make ElonQA post on X, send messages, handle passwords or SSNs, or delete your data. Those abilities are **your settings**, chosen by you during setup, and each outgoing message still needs your yes.
- Your records are never overwritten. The bot takes a snapshot before every update and rolls back if anything fails.
- New optional features start off and are offered to you as a card.

Full component map: [PARITY.md](PARITY.md). Current version: [VERSION](VERSION). Changes: [CHANGELOG.md](CHANGELOG.md).
