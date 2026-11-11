#!/usr/bin/env python3
"""Run the pebble benchmark against the Anthropic Messages API. Zero dependencies.

    export ANTHROPIC_API_KEY=...
    python bench/run.py --model claude-sonnet-5-5 --runs 3
    python bench/report.py

Arms:
    baseline  no system prompt
    plain     system prompt = skills/pebble/SKILL.md body (default mode)
    brief     same, plus "Mode: brief."

Every call's real `usage` numbers are stored with the reply. Nothing here estimates tokens.
Set ANTHROPIC_BASE_URL to point at a proxy or a local test server.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "bench" / "prompts.json"
SKILL = ROOT / "skills" / "pebble" / "SKILL.md"
OUT_DIR = ROOT / "bench" / "results" / "raw"
API_VERSION = "2023-06-01"


def skill_body() -> str:
    text = SKILL.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n.*?\r?\n---\r?\n?(.*)$", text, re.S)
    return (m.group(1) if m else text).strip()


def system_for(arm: str) -> str | None:
    if arm == "baseline":
        return None
    if arm == "plain":
        return skill_body()
    if arm == "brief":
        return skill_body() + "\n\nMode: brief."
    raise ValueError(f"unknown arm {arm}")


def call(base_url: str, key: str, model: str, system: str | None, user: str, max_tokens: int, retries: int = 4) -> dict:
    body = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": user}]}
    if system:
        body["system"] = system
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/messages",
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "x-api-key": key, "anthropic-version": API_VERSION},
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            u = data.get("usage", {})
            return {"text": text, "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                    "stop_reason": data.get("stop_reason")}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise SystemExit(f"API error {e.code}: {e.read().decode(errors='replace')[:300]}")
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise SystemExit(f"network error: {e}")
    raise SystemExit("unreachable")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--runs", type=int, default=3, help="runs per prompt per arm")
    ap.add_argument("--arms", default="baseline,plain,brief")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--limit", type=int, default=0, help="only the first N prompts (smoke test)")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("ANTHROPIC_API_KEY is not set. Nothing was run and no results were written.", file=sys.stderr)
        return 2
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))["prompts"]
    if args.limit:
        prompts = prompts[: args.limit]
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    total = len(prompts) * len(arms) * args.runs
    records, n = [], 0
    for p in prompts:
        for arm in arms:
            for run in range(args.runs):
                n += 1
                r = call(base, key, args.model, system_for(arm), p["prompt"], args.max_tokens)
                records.append({"prompt_id": p["id"], "arm": arm, "run": run, **r})
                print(f"[{n}/{total}] {p['id']} {arm} run{run}: {r['output_tokens']} out tokens", flush=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    out = args.out or OUT_DIR / f"{stamp}-{args.model}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"model": args.model, "runs": args.runs, "arms": arms, "created": stamp,
                               "prompt_version": json.loads(PROMPTS.read_text())["version"],
                               "records": records}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
