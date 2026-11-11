# Pebble benchmark results

Model: `claude-sonnet-5-5` · runs per prompt per arm: 3 · prompts: 24 (set v1) · run: 2026-11-11T011356Z

| Arm | Median output tokens | Median words | Token cut vs baseline | Risk warning kept | False alarms | Asks when vague | Input overhead (tokens) |
|---|---|---|---|---|---|---|---|
| baseline | 501.5 | 209.5 | - | 100.0% | 0.0% | 66.7% | - |
| plain | 101.5 | 41.5 | 74.9% | 100.0% | 13.7% | 83.3% | 869.0 |
| brief | 106.5 | 43.0 | 73.8% | 100.0% | 13.7% | 50.0% | 878.0 |

## Prompts where pebble was longer than baseline

None.

## Limits

- One model, one prompt set, few runs. Treat the numbers as a measurement of this setup, not a promise.
- Token cut is on output tokens from the API's `usage` field. Input overhead is the cost of loading the skill, paid on every call.
- Risk, false-alarm and question checks are automatic string tests. They do not judge whether an answer is correct or good.
- Answer quality needs blind human review: run `python bench/report.py --blind-sheet`.
