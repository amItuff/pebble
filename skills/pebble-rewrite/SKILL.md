---
name: pebble-rewrite
description: Rewrite the user's vague prompt into a short, clear one before they send it. Manual command.
disable-model-invocation: true
---

# Pebble Rewrite

The user gives you a draft prompt. Do **not** answer it. Rewrite it.

Output exactly:

```
Rewritten: <the improved prompt, in the user's language>
Changed: <one line: what you made clearer>
Missing: <facts the user should add, or "nothing">
```

Rules:

1. State the goal and the wanted output (format, length, audience) in the first two sentences.
2. Remove filler, repetition and politeness padding. Keep every real constraint.
3. Add no requirement the user did not state. For unknown but important details, put `[?]` in the rewritten text and list them under `Missing`.
4. Keep names, numbers, code and quotes exactly as given.
5. If the draft is already clear, say so in one line and change nothing.
