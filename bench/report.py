#!/usr/bin/env python3
"""Turn a raw benchmark file into bench/results/latest.md and latest.json. Zero dependencies.

    python bench/report.py                       # newest file in bench/results/raw/
    python bench/report.py path/to/raw.json
    python bench/report.py --blind-sheet         # also write a shuffled A/B CSV for manual quality review

Method:
  * per prompt and arm: median output_tokens over runs
  * reduction vs baseline: geometric mean of (arm / baseline) over prompts, reported as a percentage cut
  * prompts where the arm used MORE tokens than baseline are listed, not hidden
  * risk kept: share of risk prompts whose reply contains a risk signal (the warning mark or a listed term)
  * false alarms: share of non-risk prompts whose reply contains the warning mark
  * asks instead of guessing: share of vague prompts whose reply contains a question mark
These are automatic checks. They do NOT measure answer quality; use --blind-sheet and judge by hand.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "bench" / "prompts.json"
RAW_DIR = ROOT / "bench" / "results" / "raw"
OUT_MD = ROOT / "bench" / "results" / "latest.md"
OUT_JSON = ROOT / "bench" / "results" / "latest.json"
MARK = "⚠"


def words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def has_risk_signal(text: str, terms: list[str]) -> bool:
    low = text.lower()
    return MARK in text or any(t.lower() in low for t in terms)


def analyse(raw: dict, prompts: list[dict]) -> dict:
    by_id = {p["id"]: p for p in prompts}
    arms = raw["arms"]
    recs = raw["records"]

    def med(prompt_id, arm, field):
        vals = [r[field] for r in recs if r["prompt_id"] == prompt_id and r["arm"] == arm and r.get(field) is not None]
        return statistics.median(vals) if vals else None

    out = {"model": raw["model"], "runs": raw["runs"], "created": raw.get("created"),
           "prompt_version": raw.get("prompt_version"), "n_prompts": len(by_id), "arms": {}}
    for arm in arms:
        ratios, more, in_over = [], [], []
        for pid in by_id:
            b, a = med(pid, "baseline", "output_tokens"), med(pid, arm, "output_tokens")
            if arm != "baseline" and b and a:
                ratios.append(a / b)
                if a > b:
                    more.append({"id": pid, "baseline": b, "arm": a})
            bi, ai = med(pid, "baseline", "input_tokens"), med(pid, arm, "input_tokens")
            if arm != "baseline" and bi is not None and ai is not None:
                in_over.append(ai - bi)
        arm_recs = [r for r in recs if r["arm"] == arm]
        risk_recs = [r for r in arm_recs if by_id[r["prompt_id"]].get("risk_expected")]
        calm_recs = [r for r in arm_recs if not by_id[r["prompt_id"]].get("risk_expected")]
        ask_recs = [r for r in arm_recs if by_id[r["prompt_id"]].get("expect_question")]
        pct = lambda n, d: None if not d else round(100 * n / d, 1)
        out["arms"][arm] = {
            "median_output_tokens": statistics.median([r["output_tokens"] for r in arm_recs if r.get("output_tokens") is not None] or [0]),
            "median_words": statistics.median([words(r["text"]) for r in arm_recs] or [0]),
            "token_cut_vs_baseline_pct": None if not ratios else round(100 * (1 - math.exp(statistics.fmean(math.log(x) for x in ratios))), 1),
            "prompts_longer_than_baseline": more,
            "input_overhead_tokens": None if not in_over else statistics.median(in_over),
            "risk_kept_pct": pct(sum(has_risk_signal(r["text"], by_id[r["prompt_id"]].get("risk_terms", [])) for r in risk_recs), len(risk_recs)),
            "false_alarm_pct": pct(sum(MARK in r["text"] for r in calm_recs), len(calm_recs)),
            "asks_instead_of_guessing_pct": pct(sum("?" in r["text"] for r in ask_recs), len(ask_recs)),
        }
    return out


def render_md(res: dict) -> str:
    f = lambda v, s="": "n/a" if v is None else f"{v}{s}"
    lines = [
        "# Pebble benchmark results", "",
        f"Model: `{res['model']}` · runs per prompt per arm: {res['runs']} · prompts: {res['n_prompts']} (set v{res['prompt_version']}) · run: {res['created']}", "",
        "| Arm | Median output tokens | Median words | Token cut vs baseline | Risk warning kept | False alarms | Asks when vague | Input overhead (tokens) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for arm, a in res["arms"].items():
        lines.append(f"| {arm} | {f(a['median_output_tokens'])} | {f(a['median_words'])} | "
                     f"{f(a['token_cut_vs_baseline_pct'], '%') if arm != 'baseline' else '-'} | {f(a['risk_kept_pct'], '%')} | "
                     f"{f(a['false_alarm_pct'], '%')} | {f(a['asks_instead_of_guessing_pct'], '%')} | "
                     f"{f(a['input_overhead_tokens']) if arm != 'baseline' else '-'} |")
    lines += ["", "## Prompts where pebble was longer than baseline", ""]
    any_more = False
    for arm, a in res["arms"].items():
        for m in a["prompts_longer_than_baseline"]:
            any_more = True
            lines.append(f"- `{m['id']}` ({arm}): {m['arm']} vs {m['baseline']} tokens")
    if not any_more:
        lines.append("None.")
    lines += ["", "## Limits", "",
              "- One model, one prompt set, few runs. Treat the numbers as a measurement of this setup, not a promise.",
              "- Token cut is on output tokens from the API's `usage` field. Input overhead is the cost of loading the skill, paid on every call.",
              "- Risk, false-alarm and question checks are automatic string tests. They do not judge whether an answer is correct or good.",
              "- Answer quality needs blind human review: run `python bench/report.py --blind-sheet`.", ""]
    return "\n".join(lines)


def blind_sheet(raw: dict, prompts: list[dict], arm: str, seed: int = 7) -> None:
    rng = random.Random(seed)
    by_id = {p["id"]: p for p in prompts}
    key_rows, sheet_rows = [], []
    for pid, p in by_id.items():
        pick = lambda a: next((r["text"] for r in raw["records"] if r["prompt_id"] == pid and r["arm"] == a), None)
        base, other = pick("baseline"), pick(arm)
        if base is None or other is None:
            continue
        flip = rng.random() < 0.5
        a, b = (other, base) if flip else (base, other)
        sheet_rows.append([pid, p["prompt"], a, b, ""])
        key_rows.append([pid, "A" if flip else "B", arm])
    for name, header, rows in (("blind-sheet.csv", ["id", "prompt", "A", "B", "better (A/B/tie)"], sheet_rows),
                               ("blind-key.csv", ["id", "which is baseline", "other arm"], key_rows)):
        with open(ROOT / "bench" / "results" / name, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows([header] + rows)
    print("wrote bench/results/blind-sheet.csv and blind-key.csv (keep the key unseen until you have judged)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw", nargs="?", type=Path)
    ap.add_argument("--blind-sheet", action="store_true")
    ap.add_argument("--arm", default="plain", help="arm to compare against baseline in the blind sheet")
    args = ap.parse_args(argv)
    path = args.raw
    if path is None:
        files = sorted(RAW_DIR.glob("*.json"))
        if not files:
            print("No raw results. Run `python bench/run.py` first. Nothing was written.", file=sys.stderr)
            return 2
        path = files[-1]
    raw = json.loads(path.read_text(encoding="utf-8"))
    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))["prompts"]
    res = analyse(raw, prompts)
    OUT_JSON.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(render_md(res), encoding="utf-8")
    print(render_md(res))
    if args.blind_sheet:
        blind_sheet(raw, prompts, args.arm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
