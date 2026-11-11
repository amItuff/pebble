---
name: pebble-gain
description: Show pebble's measured benchmark results, or say honestly that none exist yet. Manual command.
disable-model-invocation: true
---

# Pebble Gain

Show measured results only. Never estimate, extrapolate, or guess savings for the user's own chats.

1. If you can read files, read `bench/results/latest.md`. If it exists, print it unchanged, then add one line: "Measured on the fixed prompt set in `bench/prompts.json`; your chats will differ."
2. If it does not exist, or you cannot read files, say exactly: "No measured results yet. Run `python bench/run.py`, then `python bench/report.py`." Show nothing else.
3. Do not state a percentage that is not in that file.
