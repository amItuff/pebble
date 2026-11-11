---
name: pebble-audit
description: Audit this chat for token waste and rank fixes. Estimates only. Manual command.
disable-model-invocation: true
---

# Pebble Audit

Review the conversation so far and find where tokens were wasted.

You can see only the conversation text, not billing or the real tokenizer. Estimate tokens as `characters / 4` for English; Vietnamese, Chinese, Japanese and code usually cost more. Label every figure `~` and say it is an estimate.

Remember that every new message re-sends the whole history, so early waste is paid for again each turn.

Look for, in this order:

1. Long pasted files, logs or documents still in context.
2. The same context pasted or explained more than once.
3. Long replies the user did not need.
4. Detours that no longer matter to the goal.
5. Many small corrections that one clearer prompt would have avoided.

Output, at most 12 lines:

```
Audit (estimates)
1. <what> ~<tokens> -> <concrete cut>
2. ...
Biggest win: <one sentence>
Best next step: <e.g. run /pebble-handoff and start a new chat>
```

Never advise removing context the task still needs.
