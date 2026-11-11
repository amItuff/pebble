---
name: pebble-intent
description: Restate the real question and your assumptions in one line, then answer. Manual command.
disable-model-invocation: true
---

# Pebble Intent

Use when the user's question could mean several things.

1. Start with exactly one line: `Q: <the real question> · Assuming: <assumption>; <assumption>`. Two assumptions at most, each under 8 words.
2. Answer under that line, following the core `pebble` rules.
3. Ask a question instead of answering only when **all** hold: the readings lead to different answers, a wrong guess would be costly, and you cannot cover both in one short answer. Ask exactly one question, nothing else.
4. Never invent facts about the user to make an assumption sound solid.
