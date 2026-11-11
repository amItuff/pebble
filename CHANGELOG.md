# Changelog

All notable changes are listed here. Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-11-11

First release.

### Added
- Core `pebble` skill with `brief`, `plain` and `full` modes, an off switch, and a fixed safety floor (exact code, the `⚠` risk line, required steps, one question over a costly guess).
- Eight manual commands: `pebble-intent`, `pebble-verify`, `pebble-audit`, `pebble-handoff`, `pebble-rewrite`, `pebble-lint`, `pebble-gain`, `pebble-help`.
- Claude Code plugin manifest and marketplace file.
- Generated instruction files for Claude.ai, ChatGPT, Cursor, Gemini CLI, GitHub Copilot and generic `AGENTS.md`.
- `scripts/lint_skill.py`, a dependency-free `SKILL.md` linter.
- `scripts/build_ports.py`, which generates `ports/` from the single core skill and fails CI when stale.
- `bench/`: fixed 24-prompt set, an API runner, a `claude` CLI runner (no key needed) and a reporter, with one published run.
- English and Vietnamese READMEs, banner, and demo video.

### Fixed after the first benchmark run
- Rule 5 asked for a `⚠` line on "a very common mistake", so 49% of replies to non-risk prompts carried a warning. Removed that clause; the rate fell to 13.7%. Both runs are kept in `bench/results/`.
- Measured input overhead of the core skill is about 870 tokens, not the ~600 the character-count estimate suggested.
- `brief` mode still does not cut more than `plain` (known, on the roadmap).

### Changed from the original design
- Only the core skill auto-loads; the other eight are manual-only, so idle context cost is one short description.
- Added what the first draft lacked: an off switch, mode persistence rules, a precedence rule (your instructions win), a language rule, an explicit exemption for requested deliverables, and a ban on ritual disclaimers.
- `pebble-verify` tags only load-bearing claims, not every sentence.
- `pebble-gain` prints measured results only and says so when there are none, instead of showing a fixed before/after table.
- `pebble-lint` is backed by a real script instead of a prompt alone.
