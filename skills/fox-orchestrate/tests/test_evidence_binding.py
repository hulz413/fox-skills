import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cc_progress.py"
spec = importlib.util.spec_from_file_location("evidence_progress", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EvidenceBindingTests(unittest.TestCase):
    def fixture(self, root, name="run", outcome="passed", legacy=False):
        directory = root / name
        directory.mkdir()
        state = {"phase": "completed", "incomplete": False, "cc_exit_code": 0,
                 "runner_exit_code": 0, "token_usage_scope": "main_loop_invocation",
                 "token_usage": {"input_tokens": 1, "output_tokens": 2,
                                 "cache_read_input_tokens": 3, "cache_creation_input_tokens": 4}}
        for filename in ("status.json", "summary.json"):
            (directory / filename).write_text(json.dumps(state))
        evidence = directory / "checks.bin"
        # Multiple blocks, non-UTF-8 bytes and CRLF must be hashed without normalization.
        evidence.write_bytes(b"PRIVATE_CHECK_BODY\xff\r\n" * 10000)
        args = SimpleNamespace(run_dir=str(directory), outcome=outcome,
                               artifact_ref=name + "-snapshot", evidence_file=str(evidence))
        if legacy:
            (directory / "acceptance.json").write_text(json.dumps({
                "outcome": outcome, "artifact_ref": args.artifact_ref,
                "evidence_file": str(evidence)}))
        elif outcome is not None:
            with contextlib.redirect_stdout(io.StringIO()):
                module.record_acceptance(args)
        return directory, evidence, args

    def manifest(self, root, directories, selection):
        path = root / "batch.json"
        path.write_text(json.dumps({"tasks": [{"task_id": "T",
            "run_dirs": [str(directory) for directory in directories],
            "current_acceptance_run": str(selection) if selection else None}]}))
        return path

    def test_writer_binds_raw_bytes_and_both_summaries_reuse_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            directory, evidence, _ = self.fixture(root)
            record = json.loads((directory / "acceptance.json").read_text())
            self.assertEqual(record["evidence_sha256"], hashlib.sha256(evidence.read_bytes()).hexdigest())
            path = self.manifest(root, [directory], directory)
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            with mock.patch.object(module.subprocess, "Popen", side_effect=AssertionError("unexpected process")), \
                    mock.patch.object(module, "evidence_digest", wraps=module.evidence_digest) as digest:
                report = module.summarize_tasks(path)
                self.assertEqual(digest.call_count, 1)
            task = report["tasks"][0]
            self.assertEqual(task["current_acceptance"]["evidence_integrity"], "matched")
            self.assertEqual(task["runs"][0]["evidence_integrity"], "matched")
            self.assertEqual(module.summarize([directory])["runs"][0]["evidence_integrity"], "matched")
            self.assertNotIn("PRIVATE_CHECK_BODY", json.dumps(report))
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_integrity_changes_preserve_decisions_selection_counts_and_tokens(self):
        for outcome in ("passed", "failed"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                directory, evidence, _ = self.fixture(root, outcome=outcome)
                path = self.manifest(root, [directory], directory)
                protected = {p: p.read_bytes() for p in (directory / "acceptance.json",
                    directory / "status.json", directory / "summary.json", path)}
                original = evidence.read_bytes()
                expected_tokens = module.summarize([directory])["token_totals"]
                for expected in ("matched", "mismatch", "missing", "unreadable"):
                    if expected == "mismatch":
                        evidence.write_bytes(original.replace(b"\r\n", b"\n"))
                    elif expected == "missing":
                        evidence.unlink()
                    elif expected == "unreadable":
                        evidence.mkdir()
                    invocation = module.summarize([directory])
                    report = module.summarize_tasks(path)
                    current = report["tasks"][0]["current_acceptance"]
                    self.assertEqual(invocation["runs"][0]["evidence_integrity"], expected)
                    self.assertEqual((current["outcome"], current["evidence_integrity"]), (outcome, expected))
                    self.assertEqual(current["run_dir"], str(directory))
                    self.assertEqual(invocation["acceptance_counts"][outcome], 1)
                    self.assertEqual(report["task_acceptance_counts"][outcome], 1)
                    self.assertEqual(invocation["execution_reason_counts"], report["execution_reason_counts"])
                    self.assertEqual(sum(report["execution_reason_counts"].values()), 0)
                    self.assertEqual(report["token_totals"], expected_tokens)
                    self.assertEqual(invocation["token_totals"], expected_tokens)
                evidence.rmdir()
                evidence.write_bytes(original)
                with mock.patch.object(module, "evidence_digest", side_effect=PermissionError("PRIVATE_ERROR")):
                    self.assertEqual(module.summarize([directory])["runs"][0]["evidence_integrity"], "unreadable")
                self.assertTrue(all(p.read_bytes() == value for p, value in protected.items()))

    def test_legacy_records_are_unbound_without_reading_or_backfilling_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            directory, evidence, _ = self.fixture(root, legacy=True)
            evidence.unlink()
            original = (directory / "acceptance.json").read_bytes()
            path = self.manifest(root, [directory], directory)
            with mock.patch.object(module, "evidence_digest", side_effect=AssertionError("legacy evidence read")):
                self.assertEqual(module.summarize([directory])["runs"][0]["evidence_integrity"], "unbound")
                report = module.summarize_tasks(path)
            self.assertEqual(report["tasks"][0]["current_acceptance"]["evidence_integrity"], "unbound")
            self.assertEqual(report["task_acceptance_counts"]["passed"], 1)
            self.assertEqual((directory / "acceptance.json").read_bytes(), original)

    def test_pending_and_mixed_history_do_not_change_current_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            legacy, _, _ = self.fixture(root, "legacy", legacy=True)
            rejected, evidence, _ = self.fixture(root, "rejected", outcome="failed")
            pending, _, _ = self.fixture(root, "pending", outcome=None)
            evidence.write_bytes(b"changed")
            runs = [legacy, rejected, pending]
            for selection, expected in ((None, None), (legacy, "unbound"), (rejected, "mismatch")):
                path = self.manifest(root, runs, selection)
                report = module.summarize_tasks(path)
                current = report["tasks"][0]["current_acceptance"]
                if selection is None:
                    self.assertIsNone(current)
                else:
                    self.assertEqual(current["run_dir"], str(selection))
                    self.assertEqual(current["evidence_integrity"], expected)
                self.assertIsNone(report["tasks"][0]["runs"][2]["evidence_integrity"])
                self.assertEqual(report["invocation_acceptance_counts"], {"pending": 1, "passed": 1, "failed": 1})
                self.assertEqual(report["token_totals"]["total_tokens"], {"reported": 30, "unknown_runs": 0})

    def test_malformed_digest_fails_both_clis_without_partial_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            directory, _, _ = self.fixture(root)
            acceptance = directory / "acceptance.json"
            record = json.loads(acceptance.read_text())
            path = self.manifest(root, [directory], directory)
            for value in (None, False, 42, [], "", "a" * 63, "A" * 64, "g" * 64, "a" * 64 + "\n"):
                with self.subTest(value=value):
                    acceptance.write_text(json.dumps({**record, "evidence_sha256": value}))
                    for command in (("summarize", "--run-dir", str(directory)),
                                    ("summarize-tasks", "--manifest", str(path))):
                        result = subprocess.run([sys.executable, str(SCRIPT), *command], capture_output=True, text=True)
                        self.assertEqual(result.returncode, 1)
                        self.assertEqual(result.stdout, "")
                        self.assertNotIn("Traceback", result.stderr)
                        self.assertNotIn("PRIVATE_CHECK_BODY", result.stderr)

    def test_failed_hashing_never_publishes_or_leaves_temporary_files(self):
        for failure in ("missing", "directory", "read_error"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                directory, evidence, args = self.fixture(root, outcome=None)
                args.outcome = "passed"
                if failure != "read_error":
                    evidence.unlink()
                    if failure == "directory":
                        evidence.mkdir()
                patch = (mock.patch.object(module, "evidence_digest", side_effect=PermissionError("PRIVATE_ERROR"))
                         if failure == "read_error" else contextlib.nullcontext())
                with patch, self.assertRaises((OSError, ValueError)):
                    module.record_acceptance(args)
                self.assertFalse((directory / "acceptance.json").exists())
                self.assertEqual(list(directory.glob(".acceptance-*.tmp")), [])
                self.assertEqual(module.summarize([directory])["runs"][0]["acceptance"], "pending")

    def test_cli_reports_integrity_problems_without_failing_or_exposing_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            directory, evidence, _ = self.fixture(root)
            path = self.manifest(root, [directory], directory)
            for expected in ("matched", "mismatch", "missing"):
                if expected == "mismatch":
                    evidence.write_bytes(b"PRIVATE_CHANGED_BODY")
                if expected == "missing":
                    evidence.unlink()
                for command in (("summarize", "--run-dir", str(directory)),
                                ("summarize-tasks", "--manifest", str(path))):
                    result = subprocess.run([sys.executable, str(SCRIPT), *command], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    report = json.loads(result.stdout)
                    row = report["tasks"][0]["current_acceptance"] if "tasks" in report else report["runs"][0]
                    self.assertEqual(row["evidence_integrity"], expected)
                    self.assertNotIn("PRIVATE", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
