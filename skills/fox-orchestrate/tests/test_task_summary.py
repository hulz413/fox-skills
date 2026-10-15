import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cc_progress.py"
spec = importlib.util.spec_from_file_location("task_progress", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TaskSummaryTests(unittest.TestCase):
    def record(self, root, name, outcome=None, phase="completed", usage=None, artifact=None):
        directory = root / name
        directory.mkdir(parents=True)
        state = {"phase": phase, "incomplete": phase != "completed",
                 "cc_exit_code": 0 if phase == "completed" else 1,
                 "runner_exit_code": 0 if phase == "completed" else 1,
                 "session_id": "same-session", "modelUsage": {"cumulative": 999999},
                 "token_usage_scope": "main_loop_invocation", "token_usage": usage}
        (directory / "status.json").write_text(json.dumps(state))
        if outcome is not None:
            (directory / "acceptance.json").write_text(json.dumps({
                "outcome": outcome, "artifact_ref": artifact or name + "-snapshot",
                "evidence_file": str(root / "checks.json"), "private_note": "PRIVATE_BODY"}))
        return directory

    def task(self, task_id, runs, selected=None):
        return {"task_id": task_id, "run_dirs": runs, "current_acceptance_run": selected}

    def manifest(self, root, tasks):
        path = root / "batch.json"
        path.write_text(json.dumps({"tasks": tasks}))
        return path

    def test_grouped_history_selection_and_tokens_with_cli_compatibility(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            usage = {"input_tokens": 1, "output_tokens": 2,
                     "cache_read_input_tokens": 3, "cache_creation_input_tokens": 4}
            first = self.record(root, "A/turn-1", "passed", usage=usage)
            rejected = self.record(root, "B/turn-1", "failed", usage=usage)
            repaired = self.record(root, "B/turn-2", "passed", usage=usage, artifact="repaired-v2")
            path = self.manifest(root, [self.task("A", ["A/turn-1"], "A/turn-1"),
                self.task("B", ["B/turn-1", "B/turn-2", "B/turn-1/../turn-1"], "B/turn-2")])
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            # Summary must only read records, never start a worker or invoke an external checker.
            with mock.patch.object(module.subprocess, "Popen", side_effect=AssertionError("unexpected process")):
                report = module.summarize_tasks(path)
            self.assertEqual((report["task_count"], report["invocation_count"]), (2, 3))
            self.assertEqual(report["active_invocation_count"], 0)
            self.assertEqual(report["task_acceptance_counts"], {"pending": 0, "passed": 2, "failed": 0})
            self.assertEqual(report["invocation_acceptance_counts"], {"pending": 0, "passed": 2, "failed": 1})
            b = report["tasks"][1]
            self.assertEqual(b["invocation_count"], 2)
            self.assertEqual(b["current_acceptance"], {"run_dir": str(repaired.resolve()), "outcome": "passed",
                "artifact_ref": "repaired-v2", "evidence_file": str(root / "checks.json")})
            self.assertEqual([row["acceptance"] for row in b["runs"]], ["failed", "passed"])
            self.assertEqual(b["token_totals"]["total_tokens"], {"reported": 20, "unknown_runs": 0})
            self.assertEqual(report["token_totals"]["total_tokens"], {"reported": 30, "unknown_runs": 0})
            self.assertNotIn("PRIVATE_BODY", json.dumps(report))
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()})
            old = module.summarize([first, rejected, repaired, first])
            self.assertEqual(set(old), {"token_usage_scope", "runs", "token_totals",
                                       "execution_reason_counts", "acceptance_counts"})
            self.assertEqual(old["token_totals"], report["token_totals"])
            cli = subprocess.run([sys.executable, str(SCRIPT), "summarize-tasks", "--manifest", str(path)],
                                 cwd=root.parent, capture_output=True, text=True)
            self.assertEqual(cli.returncode, 0, cli.stderr)
            self.assertEqual(json.loads(cli.stdout), report)

    def test_null_selection_and_older_selected_artifact_do_not_follow_latest_call(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.record(root, "old", "passed", artifact="accepted-v1")
            self.record(root, "new", "failed", artifact="rejected-v2")
            self.record(root, "active", phase="running")
            path = self.manifest(root, [self.task("T", ["old", "new", "active"])])
            report = module.summarize_tasks(path)
            self.assertIsNone(report["tasks"][0]["current_acceptance"])
            self.assertEqual(report["task_acceptance_counts"]["pending"], 1)
            for selected, expected, artifact in (("old", "passed", "accepted-v1"),
                                                  ("new", "failed", "rejected-v2")):
                self.manifest(root, [self.task("T", ["new", "active", "old"], selected)])
                report = module.summarize_tasks(path)
                self.assertEqual(report["task_acceptance_counts"][expected], 1)
                self.assertEqual(report["active_invocation_count"], 1)
                self.assertEqual(report["tasks"][0]["current_acceptance"]["artifact_ref"], artifact)

    def test_partial_usage_failed_attempts_and_empty_tasks_preserve_unknowns(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = self.record(root, "failed", "failed", phase="failed", usage={
                "input_tokens": 7, "output_tokens": 0, "cache_read_input_tokens": None,
                "cache_creation_input_tokens": 0})
            self.record(root, "partial", usage={"input_tokens": None, "output_tokens": 5,
                "cache_read_input_tokens": 3, "cache_creation_input_tokens": 0})
            path = self.manifest(root, [self.task("T", ["failed", "partial"], "failed"),
                                        self.task("empty", [])])
            report = module.summarize_tasks(path)
            self.assertEqual(report["token_totals"]["input_tokens"], {"reported": 7, "unknown_runs": 1})
            self.assertEqual(report["token_totals"]["cache_read_input_tokens"], {"reported": 3, "unknown_runs": 1})
            self.assertEqual(report["token_totals"]["cache_creation_input_tokens"], {"reported": 0, "unknown_runs": 0})
            self.assertEqual(report["token_totals"]["total_tokens"], {"reported": None, "unknown_runs": 2})
            self.assertEqual(report["task_acceptance_counts"], {"pending": 1, "passed": 0, "failed": 1})
            self.assertEqual(report["execution_reason_counts"]["unknown"], 1)
            empty = report["tasks"][1]
            self.assertEqual(empty["invocation_count"], 0)
            self.assertIsNone(empty["current_acceptance"])
            self.assertEqual(empty["token_totals"]["total_tokens"], {"reported": None, "unknown_runs": 0})
            self.assertEqual(module.summarize([first])["runs"][0]["failure_reasons"], ["unknown"])
            self.manifest(root, [])
            self.assertEqual(module.summarize_tasks(path)["task_count"], 0)

    def test_canonical_paths_deduplicate_within_task_and_reject_cross_task_ownership(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = self.record(root, "run", "passed")
            (root / "alias").symlink_to(run, target_is_directory=True)
            path = self.manifest(root, [self.task("T", ["run", "alias", str(run)], "alias")])
            self.assertEqual(module.summarize_tasks(path)["invocation_count"], 1)
            self.manifest(root, [self.task("T", ["run"]), self.task("U", ["alias"])])
            with self.assertRaises(ValueError):
                module.summarize_tasks(path)

    def test_invalid_manifests_selections_and_records_fail_without_partial_cli_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.record(root, "accepted", "passed")
            self.record(root, "pending")
            self.record(root, "invalid", "passed", phase="failed")
            bad_json = self.record(root, "bad-json")
            (bad_json / "status.json").write_text("PRIVATE_BROKEN_JSON")
            broken_acceptance = self.record(root, "bad-acceptance")
            (broken_acceptance / "acceptance.json").write_text('{"outcome":"passed"}')
            cases = [[], {}, {"tasks": None}, {"tasks": [None]}, {"tasks": [
                self.task("T", []), self.task("T", [])]},
                {"tasks": [self.task(" ", [])]}, {"tasks": [self.task(42, [])]},
                {"tasks": [{"task_id": "T", "run_dirs": []}]},
                {"tasks": [self.task("T", "accepted")]},
                {"tasks": [self.task("T", [None])]},
                {"tasks": [self.task("T", [], "accepted")]},
                {"tasks": [self.task("T", ["accepted"], "pending")]},
                {"tasks": [self.task("T", ["pending"], "pending")]},
                {"tasks": [self.task("T", ["accepted"], False)]},
                {"tasks": [self.task("T", ["missing"])]},
                {"tasks": [self.task("T", ["invalid"], "invalid")]},
                {"tasks": [self.task("T", ["bad-json"])]},
                {"tasks": [self.task("T", ["bad-acceptance"])]}]
            path = root / "batch.json"
            for document in cases:
                with self.subTest(document=document):
                    path.write_text(json.dumps(document))
                    result = subprocess.run([sys.executable, str(SCRIPT), "summarize-tasks",
                                             "--manifest", str(path)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stdout, "")
                    self.assertNotIn("PRIVATE_BROKEN_JSON", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
