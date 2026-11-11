# Examples

> **These outputs are written by hand to show each command's format.** They were not captured from a model run and are not benchmark results. Real replies vary by model and prompt.

## Core: `pebble`

**You:** How do I delete everything in a folder from the terminal?

**Reply:**
```
rm -r ./folder/*
⚠ This is permanent: there is no trash. Run `ls ./folder` first to check the path.
```

**You:** Why does `0.1 + 0.2` give `0.30000000000000004` in JavaScript?

**Reply:**
> Floating-point numbers are binary, and 0.1 and 0.2 have no exact binary form. Compare with a tolerance, or use integers (cents) for money.

## `/pebble-intent`

**You:** How do I make it faster?

**Reply:**
> Q: How to speed up *what*? · Assuming: nothing, you did not say.
> What is slow, and how do you measure it?

(Asks one question, because the readings lead to different answers and a guess would waste your time.)

**You:** `/pebble-intent` Is Python good for backend?

**Reply:**
> Q: Is Python a sound choice for a web API? · Assuming: a typical CRUD service; no hard latency limits.
> Yes. Django or FastAPI will carry most services; reach for Go or Rust only if you have measured a CPU bottleneck.

## `/pebble-verify`

**You:** `/pebble-verify` What's the maximum size of a Lambda deployment package?

**Reply:**
> Zip upload is limited to about 50 MB direct and 250 MB unzipped `[guess]`. Container images go much higher `[guess]`.
> Check yourself:
> - The current limits on the AWS Lambda quotas page.

## `/pebble-audit`

**You:** `/pebble-audit`

**Reply:**
```
Audit (estimates)
1. 400-line log pasted at message 3, still in context ~3,000 tok -> keep the 10 relevant lines
2. Project background explained twice (messages 1 and 8) ~600 tok -> state once in a handoff note
3. Three replies over 500 words you did not use ~2,400 tok -> ask for /pebble brief
Biggest win: drop the pasted log.
Best next step: run /pebble-handoff and continue in a new chat.
```

## `/pebble-handoff`

```
Continue from this note.
Goal: ship the signup form by Friday
Decided: React Hook Form (already in repo); server-side validation only for email uniqueness
State: form renders, submit not wired
Open: should the password rules match the mobile app? [unresolved]
Verbatim: POST /api/signup  {email, password}  -> 201 | 409
Prefs: reply in Vietnamese, code in TypeScript
```
Paste this into a new chat.

## `/pebble-rewrite`

**You:** `/pebble-rewrite` can u help me with my resume its for a job

**Reply:**
```
Rewritten: Improve my resume for a [?] role. Keep it to one page. Suggest the 3 changes that matter most.
Changed: stated the goal and the output; removed filler.
Missing: the job title, and the resume text.
```

## `/pebble-lint`

```text
$ python scripts/lint_skill.py skills/
100/100  pebble  (auto-load ~48 tok idle, body ~599 tok)
100/100  pebble-audit  (manual-only, body ~240 tok)
...
idle cost of all auto-loading descriptions: ~48 tokens (estimate, chars/4)
```
(This one is real: run it yourself.)

## `/pebble-gain`

With no measured results:
> No measured results yet. Run `python bench/run.py`, then `python bench/report.py`.
