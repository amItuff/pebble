import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import lint_skill as L  # noqa: E402


def make(tmp: Path, name: str, desc: str, body: str = "Body.\n", extra: str = "") -> Path:
    d = tmp / name
    d.mkdir(parents=True, exist_ok=True)
    p = d / "SKILL.md"
    p.write_text(f"---\nname: {name}\ndescription: {desc}\n{extra}---\n{body}", encoding="utf-8")
    return p


class LintTests(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.tmp = Path(self._t.name)

    def tearDown(self):
        self._t.cleanup()

    def msgs(self, r):
        return [f["message"] for f in r["findings"]]

    def test_good_skill_scores_100(self):
        r = L.lint_file(make(self.tmp, "good-skill", "Summarise a pull request. Use when the user asks for a PR summary."))
        self.assertEqual(r["score"], 100, self.msgs(r))

    def test_missing_frontmatter_is_error(self):
        d = self.tmp / "x"; d.mkdir()
        (d / "SKILL.md").write_text("no frontmatter", encoding="utf-8")
        r = L.lint_file(d / "SKILL.md")
        self.assertTrue(any(f["severity"] == "error" for f in r["findings"]))

    def test_bad_name_and_mismatch(self):
        d = self.tmp / "folder"; d.mkdir()
        (d / "SKILL.md").write_text("---\nname: Bad_Name\ndescription: Use when testing things here ok.\n---\nb", encoding="utf-8")
        self.assertTrue(any("kebab-case" in m for m in self.msgs(L.lint_file(d / "SKILL.md"))))

    def test_long_and_vague_descriptions(self):
        r = L.lint_file(make(self.tmp, "wordy", "Does stuff etc. " + "x" * 320))
        m = " ".join(self.msgs(r))
        self.assertIn("paid for in every chat", m)
        self.assertIn("vague phrase", m)
        self.assertIn("never says when", m)

    def test_description_over_spec_limit_is_error(self):
        r = L.lint_file(make(self.tmp, "huge", "Use when " + "y" * 1100))
        self.assertTrue(any(f["severity"] == "error" for f in r["findings"]))

    def test_contradiction_detected(self):
        r = L.lint_file(make(self.tmp, "conflict", "Use when testing contradictions in rules.",
                             "Always include warnings.\nNever include warnings.\n"))
        self.assertTrue(any("contradiction" in m for m in self.msgs(r)))

    def test_placeholder_not_flagged(self):
        r = L.lint_file(make(self.tmp, "placeholder", "Use when testing placeholders in text.", 'Say "always X" and "never X".\n'))
        self.assertFalse(any("contradiction" in m for m in self.msgs(r)))

    def test_overlap_detected_and_manual_skills_excluded(self):
        a = L.lint_file(make(self.tmp, "alpha", "Use when the user wants concise short answers to questions."))
        b = L.lint_file(make(self.tmp, "beta", "Use when the user wants concise short answers to questions today."))
        self.assertTrue(L.overlap([a, b]))
        m = L.lint_file(make(self.tmp, "gamma", "Use when the user wants concise short answers to questions.",
                             extra="disable-model-invocation: true\n"))
        self.assertFalse(L.overlap([a, m]))
        self.assertEqual(m["desc_tokens"], 0)

    def test_repo_skills_have_no_errors_or_warnings(self):
        for f in L.collect(ROOT / "skills"):
            r = L.lint_file(f)
            self.assertEqual(r["findings"], [], f"{f}: {r['findings']}")

    def test_cli_exit_codes_and_json(self):
        ok = subprocess.run([sys.executable, str(ROOT / "scripts/lint_skill.py"), str(ROOT / "skills"), "--json"],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0)
        self.assertEqual(len(json.loads(ok.stdout)["results"]), 9)
        d = self.tmp / "bad"; d.mkdir()
        (d / "SKILL.md").write_text("oops", encoding="utf-8")
        bad = subprocess.run([sys.executable, str(ROOT / "scripts/lint_skill.py"), str(d / "SKILL.md")], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)


if __name__ == "__main__":
    unittest.main()
