"""host-evidence: verify FEV delivery and explicit business acceptance."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from cook_runtime import write_run_bundle


class RunDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.graph = Path(self.temp.name)
        self.fev = {
            "question": "Does the target API write runtime state?",
            "outcome": "Control executed; target readback remains unavailable.",
            "observations": ["Control count: expected 1, observed 1."],
            "interpretation": "Control success does not establish target behavior.",
            "verdict": "INCONCLUSIVE",
            "limitations": ["Target readback is UNKNOWN."],
            "guidance": ["Add target instrumentation before implementation."],
            "evidence": ["evidence/control.json"],
            "reproduction": "Command: probe --control; environment: fixture v1; provenance: manifest.json.",
        }

    def test_fev_pass_checks_do_not_promote_verdict_or_request_approval(self):
        run = write_run_bundle(self.graph, pipeline_id="probe", fev=self.fev,
                               checks=[{"id": "control", "status": "pass"}])
        report = (run / "report.md").read_text(encoding="utf-8")
        self.assertFalse((run / "acceptance.md").exists())
        self.assertNotIn("Wait for user", report)
        self.assertIn("**INCONCLUSIVE**", report)
        self.assertIn("pass=1", report)
        for value in (self.fev["question"], self.fev["outcome"], self.fev["interpretation"],
                      self.fev["limitations"][0], self.fev["guidance"][0], self.fev["evidence"][0]):
            self.assertIn(value, report)
        summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["fev"], self.fev)

    def test_explicit_business_gate_and_legacy_template(self):
        for use_template in (False, True):
            with self.subTest(use_template=use_template):
                graph = self.graph / str(use_template)
                template = self.graph / "custom.md"
                template.write_text("# {{slug}}\nStatus: **pending**\n", encoding="utf-8")
                kwargs = {"acceptance_template": template} if use_template else {"human_acceptance": True}
                run = write_run_bundle(graph, pipeline_id="business", **kwargs)
                self.assertTrue((run / "acceptance.md").exists())
                self.assertIn("P3 user acceptance", (run / "report.md").read_text(encoding="utf-8"))

    def test_invalid_fev_is_rejected_before_creating_run(self):
        for change in ({"verdict": "PASS"}, {"outcome": ""},
                       {"verdict": "FEASIBLE", "evidence": []}, {"observations": "not a list"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                write_run_bundle(self.graph, pipeline_id="probe", fev={**self.fev, **change})
        self.assertFalse((self.graph / "runs").exists())

    def test_fev_cannot_enable_human_gate(self):
        with self.assertRaises(ValueError):
            write_run_bundle(self.graph, pipeline_id="probe", fev=self.fev, human_acceptance=True)
        self.assertFalse((self.graph / "runs").exists())

    def test_empty_checks_do_not_imply_success(self):
        run = write_run_bundle(self.graph, pipeline_id="probe")
        report = (run / "report.md").read_text(encoding="utf-8")
        self.assertIn("no pass inferred", report)
        self.assertFalse((run / "acceptance.md").exists())


if __name__ == "__main__":
    unittest.main()
