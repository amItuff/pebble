import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PortTests(unittest.TestCase):
    def test_generated_ports_are_fresh(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/build_ports.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_chatgpt_text_fits_limit(self):
        self.assertLessEqual(len((ROOT / "ports/compact.md").read_text(encoding="utf-8").strip()), 1500)

    def test_core_and_compact_agree_on_the_safety_floor(self):
        for f in ("skills/pebble/SKILL.md", "ports/compact.md"):
            t = (ROOT / f).read_text(encoding="utf-8")
            self.assertIn("⚠", t, f)
            self.assertIn("one question", t, f)

    def test_manifests_are_valid_json(self):
        import json
        for f in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "bench/prompts.json"):
            json.loads((ROOT / f).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
