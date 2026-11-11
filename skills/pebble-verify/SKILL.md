---
name: pebble-verify
description: Tag load-bearing claims [sure], [guess] or [unchecked] and list what the user must check. Manual command.
disable-model-invocation: true
---

# Pebble Verify

Answer as usual, then add honesty tags to the claims the answer depends on. Not every sentence.

| Tag | Use only when |
|---|---|
| `[sure]` | Stable, widely established fact, or something that follows directly from text in this conversation. |
| `[guess]` | Recalled from memory and could be outdated or wrong: versions, prices, dates, limits, statistics, API behaviour. |
| `[unchecked]` | Would need running code, opening a file, or looking something up to confirm. |

Rules:

1. Never invent a source, URL, citation, quote, version number or statistic. If you do not have it, say so.
2. A recalled number is `[guess]` or a range, never `[sure]`.
3. End with `Check yourself:` and at most 3 bullets, ordered by cost of being wrong. Skip the section if everything is `[sure]`.
4. Keep the answer itself as short as `pebble` plain mode.
