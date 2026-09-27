import copy
import json
import unittest
import subprocess
import sys
import tempfile
from pathlib import Path
from routing_eval import CASES, check, prompt, validate_output, report

class RoutingCheckerTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads(CASES.read_text())
        self.good = [dict(id=c["id"], reason="fixture", **c["expected"]) for c in self.suite["cases"]]

    def test_accepts_complete_results(self):
        self.assertEqual(check(self.suite, self.good), [])

    def test_prompt_hides_expectations(self):
        self.assertTrue(all("expected" not in c for c in prompt(self.suite)["cases"]))

    def test_rejects_missing_duplicate_unknown(self):
        for bad in ([], self.good[:-1], self.good + [self.good[0]], self.good + [dict(id="unknown")]):
            with self.subTest(bad=bad):
                self.assertTrue(check(self.suite, bad))

    def test_rejects_wrong_routing_fields(self):
        for field, value in (("model", "strong-fixture"), ("reasoning_effort", "max"), ("status", "inherited"), ("fork_turns", "all"), ("reason", "")):
            bad = copy.deepcopy(self.good)
            bad[0][field] = value
            with self.subTest(field=field):
                self.assertTrue(check(self.suite, bad))

    def test_reason_in_fork_field_regression(self):
        bad = copy.deepcopy(self.good)
        bad[0]["fork_turns"] = bad[0].pop("reason")
        errors = validate_output(bad)
        self.assertTrue(any("fork_turns" in error for error in errors))
        self.assertTrue(any("reason" in error for error in errors))
        self.assertTrue(check(self.suite, bad))

    def test_malformed_values_return_errors_without_crashing(self):
        for value in (None, 1, {}, "result", [None], [{"id": []}], [{"id": {}}]):
            with self.subTest(value=value):
                self.assertTrue(check(self.suite, value))

    def test_prompt_template_has_no_answers(self):
        for item in prompt(self.suite)["output_template"]:
            self.assertTrue(all(value is None for key, value in item.items() if key != "id"))

    def test_context_string_formats(self):
        for value, valid in (("none", True), ("all", True), ("2", True), (2, False), ("0", False), ("reason here", False)):
            items = copy.deepcopy(self.good)
            items[0]["fork_turns"] = value
            with self.subTest(value=value):
                self.assertEqual(not validate_output(items), valid)

    def test_structure_cli_does_not_need_expected_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "routing_eval.py"
            script.write_text(Path(__file__).with_name("routing_eval.py").read_text())
            result = Path(tmp) / "result.json"
            result.write_text(json.dumps(self.good))
            run = subprocess.run([sys.executable, str(script), "--validate-output", str(result)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result.write_text("not json")
            run = subprocess.run([sys.executable, str(script), "--validate-output", str(result)], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("Invalid JSON", run.stdout)

    def test_prompt_exposes_only_task_inputs(self):
        for case in prompt(self.suite)["cases"]:
            self.assertLessEqual(set(case), {"id", "task", "runtime_patch"})

    def test_group_results_are_independent(self):
        bad = copy.deepcopy(self.good)
        natural = next(c for c in self.suite["cases"] if c["group"] == "autonomous")
        next(p for p in bad if p["id"] == natural["id"])["model"] = "wrong-model"
        result = report(self.suite, bad)
        self.assertTrue(result["structure"]["passed"])
        self.assertEqual(result["groups"]["autonomous"]["passed"], result["groups"]["autonomous"]["total"] - 1)
        self.assertEqual(result["groups"]["rules"]["passed"], result["groups"]["rules"]["total"])

    def test_invalid_structure_is_not_a_routing_score(self):
        result = report(self.suite, [{"id": []}])
        self.assertFalse(result["structure"]["passed"])
        self.assertTrue(all(g["passed"] is None for g in result["groups"].values()))

    def test_rejects_silent_pin_substitution(self):
        bad = copy.deepcopy(self.good)
        item = next(p for p in bad if p["id"] == "badpin")
        item.update(model="light-fixture", reasoning_effort="low", status="requested")
        self.assertTrue(check(self.suite, bad))

if __name__ == "__main__":
    unittest.main()
