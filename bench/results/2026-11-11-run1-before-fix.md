# Pebble benchmark results

Model: `claude-sonnet-5-5` · runs per prompt per arm: 3 · prompts: 24 (set v1) · run: 2026-11-11T010952Z

| Arm | Median output tokens | Median words | Token cut vs baseline | Risk warning kept | False alarms | Asks when vague | Input overhead (tokens) |
|---|---|---|---|---|---|---|---|
| baseline | 485.5 | 203.5 | - | 100.0% | 0.0% | 66.7% | - |
| plain | 96.5 | 42.0 | 77.1% | 100.0% | 49.0% | 66.7% | 840.0 |
| brief | 103.0 | 42.5 | 75.7% | 100.0% | 45.1% | 83.3% | 848.0 |

## Prompts where pebble was longer than baseline

None.

## Limits

- One model, one prompt set, few runs. Treat the numbers as a measurement of this setup, not a promise.
- Token cut is on output tokens from the API's `usage` field. Input overhead is the cost of loading the skill, paid on every call.
- Risk, false-alarm and question checks are automatic string tests. They do not judge whether an answer is correct or good.
- Answer quality needs blind human review: run `python bench/report.py --blind-sheet`.
