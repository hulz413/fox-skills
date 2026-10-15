import concurrent.futures
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cc_progress.py"
spec = importlib.util.spec_from_file_location("acceptance_progress", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AcceptancePublicationTests(unittest.TestCase):
    def fixture(self, temporary):
        root = Path(temporary).resolve()
        state = {"phase": "completed", "incomplete": False, "cc_exit_code": 0,
                 "runner_exit_code": 0, "failure_reasons": []}
        for name in ("status.json", "summary.json"):
            (root / name).write_text(json.dumps(state))
        evidence = root / "checks.json"
        evidence.write_text('{"checked": true}')
        manifest = root / "batch.json"
        manifest.write_text(json.dumps({"tasks": [{"task_id": "T", "run_dirs": ["."],
                                                   "current_acceptance_run": None}]}))
        args = SimpleNamespace(run_dir=str(root), outcome="passed", artifact_ref="snapshot-v1",
                               evidence_file=str(evidence))
        return root, args, manifest

    def assert_no_temporary_files(self, root):
        self.assertEqual(list(root.glob(".acceptance-*.tmp")), [])

    def test_concurrent_readers_see_pending_until_complete_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, args, manifest = self.fixture(temporary)
            started, release = threading.Event(), threading.Event()
            dumps = module.json.dumps

            def pause_serialization(value, *positional, **keywords):
                if isinstance(value, dict) and value.get("artifact_ref") == "snapshot-v1":
                    started.set()
                    if not release.wait(5):
                        raise TimeoutError("test reader did not release the writer")
                return dumps(value, *positional, **keywords)

            with mock.patch.object(module.json, "dumps", side_effect=pause_serialization), \
                    mock.patch("builtins.print"), concurrent.futures.ThreadPoolExecutor(1) as pool:
                writer = pool.submit(module.record_acceptance, args)
                try:
                    self.assertTrue(started.wait(5), "writer did not reach serialization")
                    self.assertEqual(module.summarize([root])["runs"][0]["acceptance"], "pending")
                    self.assertEqual(module.summarize_tasks(manifest)["task_acceptance_counts"]["pending"], 1)
                    self.assertFalse((root / "acceptance.json").exists())
                finally:
                    release.set()
                self.assertEqual(writer.result(timeout=5), 0)
            self.assertEqual(module.summarize([root])["runs"][0]["acceptance"], "passed")
            document = json.loads(manifest.read_text())
            document["tasks"][0]["current_acceptance_run"] = "."
            manifest.write_text(json.dumps(document))
            self.assertEqual(module.summarize_tasks(manifest)["tasks"][0]["current_acceptance"], {
                "run_dir": str(root), "outcome": "passed", "artifact_ref": "snapshot-v1",
                "evidence_file": args.evidence_file, "evidence_integrity": "matched"})
            self.assert_no_temporary_files(root)

    def test_competing_publishers_leave_exactly_one_complete_decision(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, first, _ = self.fixture(temporary)
            second = SimpleNamespace(**{**vars(first), "outcome": "failed", "artifact_ref": "snapshot-v2"})
            link = module.os.link
            barrier = threading.Barrier(2)
            sources = []

            def simultaneous_link(source, destination):
                # Each candidate must be complete and readable before publication.
                self.assertIn(json.loads(Path(source).read_text())["artifact_ref"],
                              ("snapshot-v1", "snapshot-v2"))
                sources.append(Path(source))
                barrier.wait(timeout=5)
                return link(source, destination)

            with mock.patch.object(module.os, "link", side_effect=simultaneous_link), \
                    mock.patch("builtins.print"), concurrent.futures.ThreadPoolExecutor(2) as pool:
                writers = {pool.submit(module.record_acceptance, args): args for args in (first, second)}
                winners, collisions = [], 0
                for future, args in writers.items():
                    try:
                        self.assertEqual(future.result(timeout=8), 0)
                        winners.append(args)
                    except FileExistsError:
                        collisions += 1
            self.assertEqual((len(winners), collisions), (1, 1))
            self.assertEqual(len(set(sources)), 2)
            self.assertEqual(json.loads((root / "acceptance.json").read_text()), {
                "outcome": winners[0].outcome, "artifact_ref": winners[0].artifact_ref,
                "evidence_file": winners[0].evidence_file,
                "evidence_sha256": hashlib.sha256(Path(winners[0].evidence_file).read_bytes()).hexdigest()})
            self.assert_no_temporary_files(root)

    def test_repeated_cli_write_preserves_original_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, args, _ = self.fixture(temporary)
            command = [sys.executable, str(SCRIPT), "record-acceptance", "--run-dir", str(root),
                       "--outcome", "passed", "--artifact-ref", args.artifact_ref,
                       "--evidence-file", args.evidence_file]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = (root / "acceptance.json").read_bytes()
            command[command.index("--outcome") + 1] = "failed"
            command[command.index("--artifact-ref") + 1] = "different-snapshot"
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(second.returncode, 1)
            self.assertIn("FileExistsError", second.stderr)
            self.assertEqual(second.stdout, "")
            self.assertEqual((root / "acceptance.json").read_bytes(), original)
            self.assertEqual(module.summarize([root])["runs"][0]["acceptance"], "passed")
            self.assert_no_temporary_files(root)

    def test_failed_partial_write_leaves_no_public_record_or_temp(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, args, _ = self.fixture(temporary)
            create = module.tempfile.NamedTemporaryFile

            @contextlib.contextmanager
            def broken_writer(**keywords):
                with create(**keywords) as output:
                    write = output.write

                    def partial_write(value):
                        write(value[:10])
                        raise OSError("injected write failure")

                    with mock.patch.object(output, "write", side_effect=partial_write):
                        yield output

            with mock.patch.object(module.tempfile, "NamedTemporaryFile", side_effect=broken_writer):
                with self.assertRaises(OSError):
                    module.record_acceptance(args)
            self.assertFalse((root / "acceptance.json").exists())
            self.assertEqual(module.summarize([root])["runs"][0]["acceptance"], "pending")
            self.assert_no_temporary_files(root)

    def test_failed_link_leaves_no_public_record_or_temp(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, args, _ = self.fixture(temporary)
            with mock.patch.object(module.os, "link", side_effect=OSError("injected link failure")):
                with self.assertRaises(OSError):
                    module.record_acceptance(args)
            self.assertFalse((root / "acceptance.json").exists())
            self.assert_no_temporary_files(root)

    def test_existing_dangling_symlink_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, args, _ = self.fixture(temporary)
            target = root / "acceptance.json"
            target.symlink_to(root / "missing-original")
            with self.assertRaises(FileExistsError):
                module.record_acceptance(args)
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.readlink(), root / "missing-original")
            self.assert_no_temporary_files(root)


if __name__ == "__main__":
    unittest.main()
