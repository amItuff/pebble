# Benchmark

Measures what pebble does to replies. Zero dependencies, standard library only.

> **No results are published yet.** `bench/results/` is empty on purpose. Nothing in this repo estimates or invents savings. If you run it, please share the raw file.

## Run

```bash
export ANTHROPIC_API_KEY=...
python bench/run.py --model claude-sonnet-5-5 --runs 3     # writes bench/results/raw/<time>-<model>.json
python bench/report.py                                      # writes bench/results/latest.md and latest.json
python bench/report.py --blind-sheet                        # optional: shuffled A/B CSV for manual quality review
```

A smoke test of 2 prompts: `python bench/run.py --limit 2 --runs 1`.
24 prompts x 3 arms x 3 runs = 216 API calls; keep `max_tokens` at the default 1024.

## Design

| Arm | System prompt |
|---|---|
| `baseline` | none |
| `plain` | body of `skills/pebble/SKILL.md` |
| `brief` | same, plus `Mode: brief.` |

Prompts live in [`prompts.json`](prompts.json): 5 factual, 4 how-to, 4 decision, 3 debug, 6 risky, 2 deliberately vague. Seven of them carry a `risk_expected` flag with terms a good answer should mention.

| Metric | Definition | Source |
|---|---|---|
| Token cut | geometric mean over prompts of `median(arm output tokens) / median(baseline output tokens)`, shown as a percentage cut | API `usage.output_tokens` |
| Prompts longer | prompts where the arm's median exceeds baseline's, **listed** | same |
| Input overhead | median extra `input_tokens` vs baseline (the cost of loading the skill) | API `usage.input_tokens` |
| Risk kept | share of risk-prompt replies containing `⚠` or a listed term | string match |
| False alarms | share of non-risk replies containing `⚠` | string match |
| Asks when vague | share of vague-prompt replies containing `?` | string match |

## Limits you should know

- **Quality is not measured automatically.** A shorter answer is not a better one. Use `--blind-sheet`, judge A/B without looking at the key, then compare.
- The risk check is a keyword test. It can pass a reply that mentions a term in passing and fail one that warns in other words.
- One model and one prompt set per run; English only so far. Few runs per prompt, so small differences are noise.
- Do not edit `prompts.json` after publishing results. Add a new version instead.
- Without a system prompt the baseline is the model's default style, which differs between models and versions.

## Contributing results

Open a PR adding your `bench/results/raw/*.json` and the generated `latest.md`. Include the model name. Runs where pebble loses are as welcome as runs where it wins.
