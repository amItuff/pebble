---
name: pebble-handoff
description: Compress this chat into a short note to paste into a fresh chat. Manual command.
disable-model-invocation: true
---

# Pebble Handoff

Write a handoff note so the user can start a new chat without losing the thread. Starting fresh is the cheapest way to cut token use in a long chat.

Output one fenced block, at most about 200 words:

```
Continue from this note.
Goal: <one line>
Decided: <decision> (<reason, max 6 words>); ...
State: <what exists or works now>
Open: <unresolved questions>
Verbatim: <code, commands, paths, numbers, names that must not change>
Prefs: <language, tone, format, constraints the user stated>
```

Rules:

1. Copy code, commands, paths and numbers exactly. Never paraphrase them.
2. Drop pleasantries, abandoned ideas, and anything the new chat does not need.
3. Mark anything uncertain `[unresolved]`; never present a guess as a decision.
4. If the verbatim material alone exceeds the budget, keep the budget and say what was left out.
5. After the block, add one line: "Paste this into a new chat."
