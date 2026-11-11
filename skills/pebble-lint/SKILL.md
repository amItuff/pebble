---
name: pebble-lint
description: Score a SKILL.md for trigger quality, size, overlap and contradictions. Manual command.
disable-model-invocation: true
---

# Pebble Lint

Lint one skill file or a whole `skills/` folder. Argument: a path.

If you can run shell commands, run the real linter and report its output unchanged:

```bash
python scripts/lint_skill.py <path>
```

If you cannot run commands, check by hand and say the result is manual:

1. Frontmatter has `name` (kebab-case, matches its folder) and `description`.
2. The description says what the skill does **and** when to use it, in under 300 characters. Every skill that auto-loads costs its description in every chat.
3. No vague filler in the description: "etc", "and so on", "as appropriate".
4. The body is under 500 lines.
5. No two skills have near-identical descriptions (they fight to trigger).
6. No rule says "always X" and "never X" about the same thing.

Report a score out of 100, then the findings, errors first. Do not fix anything unless asked.
