"""Tests for bench/run.py and bench/report.py.

All numbers below are SYNTHETIC test data. They are never written to bench/results/.
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "bench"))
import report  # noqa: E402

SEEN = []


class Stub(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        SEEN.append({"path": self.path, "key": self.headers.get("x-api-key"), "body": body})
        out = 40 if "system" in body else 100
        data = json.dumps({"content": [{"type": "text", "text": "stub reply"}], "stop_reason": "end_turn",
                           "usage": {"input_tokens": 700 if "system" in body else 20, "output_tokens": out}}).encode()
        self.send_response(200); self.send_header("content-type", "application/json"); self.end_headers(); self.wfile.write(data)

    def log_message(self, *a):
        pass


class RunTests(unittest.TestCase):
    def test_refuses_without_key_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "o.json"
            env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
            r = subprocess.run([sys.executable, str(ROOT / "bench/run.py"), "--out", str(out)], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(out.exists())

    def test_run_against_stub_server(self):
        srv = HTTPServer(("127.0.0.1", 0), Stub)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "o.json"
            env = {**os.environ, "ANTHROPIC_API_KEY": "test-key", "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{srv.server_port}"}
            r = subprocess.run([sys.executable, str(ROOT / "bench/run.py"), "--runs", "2", "--limit", "2", "--out", str(out)],
                               capture_output=True, text=True, env=env)
            srv.shutdown()
            srv.server_close()
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(out.read_text())
        self.assertEqual(len(data["records"]), 2 * 3 * 2)  # prompts x arms x runs
        self.assertTrue(all(s["path"] == "/v1/messages" and s["key"] == "test-key" for s in SEEN))
        baseline = [s for s in SEEN if "system" not in s["body"]]
        pebble = [s for s in SEEN if "system" in s["body"]]
        self.assertEqual(len(baseline), 4)
        self.assertEqual(len(pebble), 8)
        self.assertIn("Find the real question", pebble[0]["body"]["system"])
        self.assertNotIn("name: pebble", pebble[0]["body"]["system"])  # frontmatter stripped
        self.assertTrue(any(s["body"]["system"].endswith("Mode: brief.") for s in pebble))


class ReportTests(unittest.TestCase):
    PROMPTS = [
        {"id": "a", "category": "x", "prompt": "q1"},
        {"id": "b", "category": "x", "prompt": "q2"},
        {"id": "r", "category": "risky", "prompt": "q3", "risk_expected": True, "risk_terms": ["backup"]},
        {"id": "v", "category": "ambiguous", "prompt": "q4", "expect_question": True},
    ]

    def rec(self, pid, arm, out, text="t", inp=10):
        return {"prompt_id": pid, "arm": arm, "run": 0, "text": text, "input_tokens": inp, "output_tokens": out}

    def raw(self, recs):
        return {"model": "m", "runs": 1, "arms": ["baseline", "plain"], "created": "t", "prompt_version": 1, "records": recs}

    def test_geometric_mean_cut_and_longer_prompts_listed(self):
        recs = [self.rec("a", "baseline", 100), self.rec("a", "plain", 50, inp=710),
                self.rec("b", "baseline", 100), self.rec("b", "plain", 200, inp=710),   # pebble longer: must be listed
                self.rec("r", "baseline", 100), self.rec("r", "plain", 25, text="Make a backup first.", inp=710),
                self.rec("v", "baseline", 100), self.rec("v", "plain", 10, text="What is it?", inp=710)]
        res = report.analyse(self.raw(recs), self.PROMPTS)["arms"]["plain"]
        # ratios 0.5, 2.0, 0.25, 0.1 -> geometric mean = (0.5*2*0.25*0.1)^(1/4)
        self.assertAlmostEqual(res["token_cut_vs_baseline_pct"], round(100 * (1 - (0.5 * 2 * 0.25 * 0.1) ** 0.25), 1))
        self.assertEqual([m["id"] for m in res["prompts_longer_than_baseline"]], ["b"])
        self.assertEqual(res["input_overhead_tokens"], 700)
        self.assertEqual(res["risk_kept_pct"], 100.0)
        self.assertEqual(res["asks_instead_of_guessing_pct"], 100.0)

    def test_risk_dropped_and_false_alarm_detected(self):
        recs = [self.rec("a", "baseline", 100), self.rec("a", "plain", 10, text="⚠ careful"),
                self.rec("r", "baseline", 100), self.rec("r", "plain", 10, text="Just do it."),
                self.rec("b", "baseline", 100), self.rec("b", "plain", 10),
                self.rec("v", "baseline", 100), self.rec("v", "plain", 10, text="Sure.")]
        res = report.analyse(self.raw(recs), self.PROMPTS)["arms"]["plain"]
        self.assertEqual(res["risk_kept_pct"], 0.0)
        self.assertAlmostEqual(res["false_alarm_pct"], 33.3, places=1)
        self.assertEqual(res["asks_instead_of_guessing_pct"], 0.0)

    def test_markdown_always_has_limits_section(self):
        recs = [self.rec("a", "baseline", 100), self.rec("a", "plain", 50)]
        md = report.render_md(report.analyse(self.raw(recs), self.PROMPTS))
        self.assertIn("## Limits", md)
        self.assertIn("None.", md)

    def test_report_refuses_when_no_raw_files(self):
        if (ROOT / "bench/results/raw").exists() and any((ROOT / "bench/results/raw").glob("*.json")):
            self.skipTest("real raw results present")
        r = subprocess.run([sys.executable, str(ROOT / "bench/report.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
