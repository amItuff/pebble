#!/usr/bin/env python3
"""Generate ports/ files from the single source of truth: skills/pebble/SKILL.md.

    python scripts/build_ports.py          # write files
    python scripts/build_ports.py --check  # exit 1 if any generated file is stale (used in CI)

Never edit generated files by hand. Edit skills/pebble/SKILL.md (or ports/compact.md) and rebuild.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "skills" / "pebble" / "SKILL.md"
COMPACT = ROOT / "ports" / "compact.md"
CHATGPT_LIMIT = 1500  # custom-instruction fields have been capped near this; check your settings

BANNER = "<!-- Generated from skills/pebble/SKILL.md by scripts/build_ports.py. Do not edit. -->\n"


def core_body() -> str:
    text = CORE.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n.*?\r?\n---\r?\n?(.*)$", text, re.S)
    body = (m.group(1) if m else text).strip()
    return re.sub(r"^# Pebble\s*\n", "", body).strip()


def outputs() -> dict[Path, str]:
    body = core_body()
    compact = COMPACT.read_text(encoding="utf-8").strip()
    if len(compact) > CHATGPT_LIMIT:
        raise SystemExit(f"ports/compact.md is {len(compact)} chars; limit {CHATGPT_LIMIT}")
    return {
        ROOT / "ports/generic/AGENTS.md": f"{BANNER}# Pebble\n\n{body}\n",
        ROOT / "ports/gemini/GEMINI.md": f"{BANNER}# Pebble\n\n{body}\n",
        ROOT / "ports/copilot/copilot-instructions.md": f"{BANNER}# Pebble\n\n{body}\n",
        ROOT / "ports/cursor/pebble.mdc": (
            "---\ndescription: Pebble - short, honest replies. Answer first, cut filler, keep risk warnings.\n"
            f"alwaysApply: true\n---\n{BANNER}\n{body}\n"
        ),
        ROOT / "ports/chatgpt/custom-instructions.md": (
            f"{BANNER}Paste the text below into Settings > Personalization > Custom instructions "
            f"(\"How would you like ChatGPT to respond?\"). {len(compact)} characters.\n\n---\n\n{compact}\n"
        ),
        ROOT / "ports/claude-ai/project-instructions.md": (
            f"{BANNER}Paste the text below into a Claude Project's instructions, or into Settings > "
            f"Profile as a preference.\n\n---\n\n{compact}\n"
        ),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    stale = []
    for path, content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    if stale:
        print("stale generated files (run python scripts/build_ports.py):", *map(str, stale), sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
