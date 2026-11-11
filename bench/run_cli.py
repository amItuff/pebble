#!/usr/bin/env python3
"""Run the pebble benchmark through the `claude` CLI instead of the raw API. No API key needed.

    python bench/run_cli.py --runs 3
    python bench/report.py

Same prompts, same arms, same output format as run.py, so report.py reads either.

Differences from run.py you should know about:
  * The baseline system prompt is "You are a helpful assistant.", not empty.
  * Tools, slash commands, settings and session persistence are all off.
  * Token numbers come from the CLI's JSON `usage`. input_tokens here is
    input + cache-creation + cache-read, i.e. everything sent to the model.
  * The CLI uses whatever account you are logged in with, so it spends that account's quota.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import OUT_DIR, PROMPTS, system_for  # noqa: E402

BASELINE_SYSTEM = "You are a helpful assistant."


def call_cli(claude_bin: str, model: str, system: str | None, user: str, retries: int = 3) -> dict:
    cmd = [claude_bin, "-p", user, "--output-format", "json", "--tools", "", "--no-session-persistence",
           "--disable-slash-commands", "--setting-sources", "", "--system-prompt", system or BASELINE_SYSTEM]
    if model:
        cmd += ["--model", model]
    last = ""
    for attempt in range(retries + 1):
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd="/tmp")
            data = json.loads(p.stdout)
            if data.get("is_error"):
                raise RuntimeError(str(data.get("result"))[:200])
            u = data["usage"]
            return {
                "text": data["result"],
                "input_tokens": (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0),
                "output_tokens": u.get("output_tokens"),
                "stop_reason": data.get("stop_reason"),
                "model": next(iter(data.get("modelUsage", {})), None),
            }
        except Exception as e:  # noqa: BLE001 - retry on anything, report the last error
            last = f"{type(e).__name__}: {e} {(getattr(e, 'stderr', '') or '')[:200]}"
            time.sleep(2 ** (attempt + 1))
    raise SystemExit(f"claude CLI failed after retries: {last}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="", help="model alias or id; default is the CLI's own default")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--arms", default="baseline,plain,brief")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--claude-bin", default="claude")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))["prompts"]
    if args.limit:
        prompts = prompts[: args.limit]
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    jobs = [(p, arm, run) for p in prompts for arm in arms for run in range(args.runs)]

    def work(job):
        p, arm, run = job
        r = call_cli(args.claude_bin, args.model, system_for(arm), p["prompt"])
        print(f"{p['id']} {arm} run{run}: {r['output_tokens']} out tokens", flush=True)
        return {"prompt_id": p["id"], "arm": arm, "run": run, **r}

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        records = list(ex.map(work, jobs))  # map keeps job order

    model = next((r["model"] for r in records if r.get("model")), args.model or "cli-default")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    out = args.out or OUT_DIR / f"{stamp}-{model}-cli.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"model": model, "runs": args.runs, "arms": arms, "created": stamp, "via": "claude CLI",
                               "prompt_version": json.loads(PROMPTS.read_text())["version"],
                               "records": records}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
