# Launch checklist

Do these in order. Items 1 to 3 matter most.

## 1. Strengthen the evidence

A first run is published (about 75% output-token cut, risk warning kept on all 7 risk prompts) with its limits. Before launching, make it harder to dismiss:

- Judge the blind sheet by hand: `python bench/report.py --blind-sheet`, then compare. Quality is the first objection you will get.
- Re-run on another model, and on a few prompts that were **not** used to tune the skill. The published run was tuned on its own prompt set.
- Decide what to do about `brief`, which currently cuts no more than `plain`: fix it or drop it.
- Keep the unflattering rows in the README. Credibility here comes from showing them.

## 2. Repo settings (cannot be set from files)

- **Description:** `Short, honest AI replies for Claude, ChatGPT, Cursor and Gemini. Answer first, cut the filler, keep the warnings.`
- **Topics:** `claude-code`, `claude-skills`, `agent-skills`, `prompt-engineering`, `llm`, `token-optimization`, `chatgpt`, `cursor`, `gemini-cli`, `ai-tools`
- **Social preview:** Settings → General → Social preview → upload `assets/social-preview.png` (1280x640).
- Turn on **Discussions**.
- Create a **release v0.1.0** from the `main` branch; attach `assets/demo.mp4`; paste the CHANGELOG entry.

## 3. Name collision

`pebble` is a crowded name on GitHub (a Go key-value store with 6k+ stars, the Pebble smartwatch OS, a Java template engine, and more). Search for "pebble" will not surface this repo. Mitigate with the description and topics above, and always write "pebble skill" or "pebble for Claude" in posts. If you want an easier-to-find name, `pebble-skills` is the obvious alternative; rename before anyone links to it.

## 4. Where to post

- Show HN: `Show HN: Pebble – AI replies that answer first and keep the warnings` with a one-paragraph first comment that includes your benchmark numbers and their limits.
- Reddit: r/ClaudeAI, r/ChatGPT, r/cursor, r/LocalLLaMA (only if you add a local-model port).
- X / Threads / LinkedIn: the GIF, one line, the install command.
- Vietnamese AI and developer communities, using the Vietnamese README.
- Awesome lists: search GitHub for `awesome claude skills` and `awesome claude code`, then open a PR to each.

Post the demo GIF natively on each platform. Lead with the question, not the project name.

## 5. After launch

- Answer issues within a day. The first ten issues set the tone.
- Turn every "pebble made this worse" report into a rule fix or a benchmark prompt.
- Ship a v0.1.1 within two weeks, so the repo looks alive.

## Honest expectations

Nothing here guarantees stars. A first repository from an account with no audience commonly ends the first month in the single digits to low tens of stars without outside promotion (an estimate from general experience, not a measurement). The niche is crowded: a GitHub search on 2026-11-11 shows the most popular related skill above 100,000 stars. What moves the needle is a measured result, a short demo that makes a stranger say "oh, that", and a clear difference from existing tools. This repo is built around those three things; the first one still needs you to run the benchmark.
