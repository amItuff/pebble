#!/usr/bin/env python3
"""Lint SKILL.md files. Zero dependencies. Backs the /pebble-lint command.

Usage:
    python scripts/lint_skill.py skills/pebble/SKILL.md
    python scripts/lint_skill.py skills/            # a whole folder, adds overlap checks
    python scripts/lint_skill.py skills/ --json

Exit code 1 if any file has an error.
Token figures are estimates (characters / 4).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VAGUE = ("etc", "and so on", "as appropriate", "if needed", "and more", "various")
TRIGGER_HINTS = ("use when", "use on", "use for", "when ", "if the user", "manual command", "on every")
DESC_ERROR = 1024   # Agent Skills spec maximum
DESC_WARN = 300     # idle cost: auto-loaded descriptions are paid for in every chat
DESC_MIN = 40
BODY_LINES_WARN = 500
BODY_TOKENS_WARN = 1500
STOP = set("a an the of to and or in on for is it this that with as at by be from your you".split())


def est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def parse(path: Path):
    """Return (frontmatter dict, body, error or None). Handles `key: value` and `>`/`|` blocks."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text, "missing frontmatter"
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return {}, text, "unterminated frontmatter"
    fm, body = {}, m.group(2)
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if km and not line.startswith(" "):
            key, val = km.group(1), km.group(2).strip()
            fm[key] = "" if val in (">", "|", ">-", "|-") else val.strip("'\"")
        elif key and line.strip():
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm, body, None


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 2}


def contradictions(body: str):
    """Heuristic: 'always <phrase>' and 'never <phrase>' with the same first two words."""
    def grab(word):
        out = {}
        for m in re.finditer(rf"\b{word}\s+([a-z]{{3,}}(?:\s+[a-z]{{3,}})?)", body.lower()):
            out.setdefault(m.group(1), m.group(0))
        return out
    a, n = grab("always"), grab("never")
    return [(a[k], n[k]) for k in a.keys() & n.keys()]


def lint_file(path: Path) -> dict:
    findings = []  # (severity, message)
    fm, body, err = parse(path)
    if err:
        findings.append(("error", err))
    else:
        name, desc = fm.get("name", ""), fm.get("description", "")
        if not name:
            findings.append(("error", "frontmatter has no `name`"))
        else:
            if not NAME_RE.match(name) or len(name) > 64:
                findings.append(("error", f"name `{name}` must be kebab-case, max 64 chars"))
            if path.parent.name != name:
                findings.append(("warn", f"name `{name}` does not match folder `{path.parent.name}`"))
        if not desc:
            findings.append(("error", "frontmatter has no `description`"))
        else:
            if len(desc) > DESC_ERROR:
                findings.append(("error", f"description is {len(desc)} chars; max {DESC_ERROR}"))
            elif len(desc) > DESC_WARN:
                findings.append(("warn", f"description is {len(desc)} chars (> {DESC_WARN}); it is paid for in every chat"))
            if len(desc) < DESC_MIN:
                findings.append(("warn", f"description is only {len(desc)} chars; too vague to trigger reliably"))
            low = desc.lower()
            if not any(h in low for h in TRIGGER_HINTS):
                findings.append(("warn", "description never says when to use the skill"))
            for v in VAGUE:
                if re.search(rf"\b{re.escape(v)}\b", low):
                    findings.append(("warn", f"vague phrase in description: '{v}'"))
        n_lines = len(body.strip().splitlines())
        if n_lines > BODY_LINES_WARN:
            findings.append(("warn", f"body is {n_lines} lines (> {BODY_LINES_WARN}); split it"))
        if est_tokens(body) > BODY_TOKENS_WARN:
            findings.append(("warn", f"body is ~{est_tokens(body)} tokens (> {BODY_TOKENS_WARN})"))
        for a, n in contradictions(body):
            findings.append(("warn", f"possible contradiction: '{a}' vs '{n}'"))
    score = 100
    for sev, _ in findings:
        score -= 25 if sev == "error" else 8
    manual = fm.get("disable-model-invocation", "").lower() == "true"
    return {
        "path": str(path),
        "name": fm.get("name", ""),
        "score": max(0, score),
        "manual_only": manual,
        "desc_tokens": 0 if manual else est_tokens(fm.get("description", "")),
        "body_tokens": est_tokens(body),
        "findings": [{"severity": s, "message": m} for s, m in findings],
        "_desc": fm.get("description", ""),
    }


def collect(target: Path):
    if target.is_file():
        return [target]
    return sorted(target.glob("**/SKILL.md"))


def overlap(results):
    out = []
    auto = [r for r in results if not r["manual_only"] and r["_desc"]]
    for i, a in enumerate(auto):
        for b in auto[i + 1:]:
            wa, wb = words(a["_desc"]), words(b["_desc"])
            if wa and wb:
                j = len(wa & wb) / len(wa | wb)
                if j > 0.5:
                    out.append(f"{a['name']} and {b['name']} have near-identical descriptions (similarity {j:.2f}); they will fight to trigger")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    files = collect(args.path)
    if not files:
        print(f"no SKILL.md found under {args.path}", file=sys.stderr)
        return 2
    results = [lint_file(f) for f in files]
    ov = overlap(results) if len(results) > 1 else []
    for r in results:
        r.pop("_desc")
    if args.json:
        print(json.dumps({"results": results, "overlap": ov}, indent=2))
    else:
        for r in results:
            tag = "manual-only" if r["manual_only"] else f"auto-load ~{r['desc_tokens']} tok idle"
            print(f"{r['score']:>3}/100  {r['name'] or r['path']}  ({tag}, body ~{r['body_tokens']} tok)")
            for f in r["findings"]:
                print(f"        {f['severity']:<5} {f['message']}")
        for line in ov:
            print(f"warn  {line}")
        idle = sum(r["desc_tokens"] for r in results)
        print(f"\nidle cost of all auto-loading descriptions: ~{idle} tokens (estimate, chars/4)")
    return 1 if any(f["severity"] == "error" for r in results for f in r["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
