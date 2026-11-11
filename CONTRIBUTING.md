# Contributing

Thanks for helping. The most useful contributions, in order:

1. **A prompt where pebble made things worse.** Open an issue with the prompt, the reply, and what it should have said. These improve the rules.
2. **A benchmark run.** See [`bench/README.md`](bench/README.md). Losses are as welcome as wins.
3. **A prompt set in another language** for `bench/`.
4. **Fixes and clarifications** to the skills or docs.

## Ground rules

- **No invented numbers.** A figure in the docs must come from a script in this repo or be absent. Hand-written examples must say they are hand-written.
- **Keep the safety floor.** Changes must not weaken: exact code and numbers, the `⚠` line, required steps, the one-question rule.
- **Mind the tokens.** The core skill is paid for on every load. Prefer deleting a rule to adding one. Only the core skill may auto-load; every other skill needs `disable-model-invocation: true`.

## Setup

Python 3.9+. No dependencies.

```bash
python -m unittest discover -s tests
python scripts/lint_skill.py skills/
python scripts/build_ports.py --check
```

## Editing the core rules

`skills/pebble/SKILL.md` is the single source of truth. The files in `ports/` are **generated**; never edit them by hand.

```bash
# edit skills/pebble/SKILL.md (and ports/compact.md for the ChatGPT / Claude.ai text)
python scripts/build_ports.py        # regenerate ports/
python -m unittest discover -s tests
```

CI fails if `ports/` is stale or any skill has a lint error.

## Pull requests

Small and focused. Say what changed and why, and paste the output of the three commands above.
