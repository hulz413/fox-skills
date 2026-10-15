import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "cc_progress.py"
spec = importlib.util.spec_from_file_location("cc_progress", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProgressTests(unittest.TestCase):
    def test_filter_excludes_bodies_arguments_and_terminal_escapes(self):
        events = module.Events()
        secret = "PRIVATE_BODY_123\x1b[2J"
        batch = [
            {"type": "system", "subtype": "init", "model": secret, "session_id": "test-id"},
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": secret},
                {"type": "thinking", "thinking": secret},
                {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": secret}},
                {"type": "tool_use", "id": "t2", "name": secret, "input": secret}]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": secret},
                {"type": "tool_result", "tool_use_id": "t2", "is_error": True, "content": secret}]}},
            {"type": "result", "subtype": "success", "is_error": False, "result": secret},
        ]
        snapshots = []
        for event in batch:
            events.consume(json.dumps(event))
            snapshots.append(events.last)
        text = json.dumps(snapshots)
        self.assertNotIn("PRIVATE_BODY", text)
        self.assertNotIn("\x1b", text)
        self.assertEqual(events.tools["t1"], "Bash")
        self.assertEqual(events.tools["t2"], "other tool")
        self.assertIn("other tool failed", text)
        self.assertIsNone(events.model)

    def test_duplicate_tool_events_and_malformed_content(self):
        events = module.Events()
        tool = {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "a", "name": {"invalid": True}}]}}
        events.consume(json.dumps(tool))
        events.consume(json.dumps(tool))
        for line in ("not JSON", "[]", '{"type":"assistant","message":{"content":42}}'):
            events.consume(line)
        self.assertEqual(events.seen_calls, {"a"})
        self.assertEqual(events.tools, {"a": "other tool"})
        self.assertEqual(events.invalid, 2)

    def setup_run(self, temporary, body):
        root = Path(temporary)
        fake = root / "fake-claude"
        fake.write_text("#!" + sys.executable + "\n" + body)
        fake.chmod(0o700)
        prompt = root / "prompt.txt"
        prompt.write_text("literal `touch unwanted` $(touch unwanted) text")
        directory = root / "turn"
        argv = [sys.executable, str(SCRIPT), "run", "--run-dir", str(directory),
                "--cwd", temporary, "--prompt-file", str(prompt), "--model", "test-model",
                "--effort", "low", "--claude", str(fake), "--", "--tools", "Read"]
        return root, directory, argv

    def test_background_status_and_bounded_caller_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            body = '''import json, sys, time
from pathlib import Path
with Path("invocations.txt").open("a") as count: count.write("invoked\\n")
Path("received.json").write_text(json.dumps({"argv": sys.argv, "stdin": sys.stdin.read()}))
print(json.dumps({"type":"system","subtype":"init","model":"test-model","session_id":"test-session"}), flush=True)
print(json.dumps({"type":"assistant","message":{"content":[{"type":"tool_use","id":"read1","name":"Read","input":{"file_path":"PRIVATE_ARGUMENT"}}]}}), flush=True)
time.sleep(1.5)
print(json.dumps({"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"read1","content":"PRIVATE_RESULT"}]}}), flush=True)
print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"PRIVATE_FINAL","permission_denials":[]}), flush=True)
'''
            root, directory, argv = self.setup_run(temporary, body)
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    path = directory / "status.json"
                    if path.exists() and json.loads(path.read_text()).get("last_event") == "Read started":
                        break
                    time.sleep(0.02)
                else:
                    self.fail("no running status before deadline")
                self.assertIsNone(process.poll(), "status must be available before process completion")
                received_before = (root / "received.json").read_bytes()
                query = subprocess.run([sys.executable, str(SCRIPT), "status",
                                        "--run-dir", str(directory)], capture_output=True, text=True, check=True)
                display = query.stdout
                self.assertEqual(json.loads(display)["phase"], "running")
                self.assertEqual((root / "received.json").read_bytes(), received_before)
                self.assertIn("Read started", display)
                self.assertNotIn("PRIVATE", display)
                stdout, stderr = process.communicate(timeout=8)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
            self.assertEqual(process.returncode, 0, stderr)
            self.assertNotIn("PRIVATE", stdout + stderr)
            state = json.loads(stdout)
            self.assertEqual(state["phase"], "completed")
            self.assertIsNone(state["effective_effort"])
            self.assertFalse((directory / "progress.log").exists())
            self.assertEqual(json.loads((directory / "status.json").read_text()), state)
            self.assertIn("PRIVATE_RESULT", (directory / "stdout.jsonl").read_text())
            self.assertIn("PRIVATE_FINAL", (directory / "result.json").read_text())
            self.assertEqual((root / "invocations.txt").read_text().splitlines(), ["invoked"])
            received = json.loads((root / "received.json").read_text())
            self.assertIn("$(touch unwanted)", received["stdin"])
            self.assertFalse((root / "unwanted").exists())
            self.assertIn("--output-format", received["argv"])
            self.assertEqual(received["argv"][received["argv"].index("--model") + 1], "test-model")

    def test_failure_exit_and_required_attention(self):
        cases = [
            ('print("unparseable")', 65, "failed"),
            ('import sys; print("private diagnostic", file=sys.stderr); sys.exit(7)', 7, "failed"),
            ('import json; print(json.dumps({"type":"result","subtype":"success","is_error":False,"permission_denials":[{"tool":"Write"}]}))', 2, "needs_attention"),
            ('import json; print(json.dumps({"type":"result","subtype":"success","is_error":False,"permission_denials":42}))', 65, "failed"),
        ]
        for body, code, phase in cases:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as temporary:
                _, directory, argv = self.setup_run(temporary, body)
                result = subprocess.run(argv, capture_output=True, text=True)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["phase"], phase)
                self.assertNotIn("private diagnostic", result.stdout + result.stderr)
                self.assertTrue((directory / "summary.json").exists())

    def test_permission_denial_event_survives_empty_final_denial_list(self):
        body = ('import json; '
                'print(json.dumps({"type":"system","subtype":"permission_denied"})); '
                'print(json.dumps({"type":"result","subtype":"success",'
                '"is_error":False,"permission_denials":[]}))')
        with tempfile.TemporaryDirectory() as temporary:
            _, directory, argv = self.setup_run(temporary, body)
            result = subprocess.run(argv, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            state = json.loads(result.stdout)
            self.assertEqual(state["phase"], "needs_attention")
            self.assertIs(state["permission_denial_seen"], True)
            self.assertEqual(state["permission_denials"], 0)
            self.assertIs(state["incomplete"], True)
            self.assertEqual(state["cc_exit_code"], 0)
            self.assertEqual(json.loads((directory / "status.json").read_text()), state)

    def test_no_evidence_overwrite_and_no_configuration_override(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, directory, argv = self.setup_run(temporary, "pass")
            directory.mkdir()
            evidence = directory / "stdout.jsonl"
            evidence.write_text("existing evidence")
            self.assertNotEqual(subprocess.run(argv, capture_output=True).returncode, 0)
            self.assertEqual(evidence.read_text(), "existing evidence")
        with tempfile.TemporaryDirectory() as temporary:
            _, directory, argv = self.setup_run(temporary, "pass")
            result = subprocess.run(argv + ["--model=another"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(directory.exists())

    def test_invocation_tokens_ignore_cumulative_model_usage_and_keep_failed_usage(self):
        usage = {"input_tokens": 4, "output_tokens": 279,
                 "cache_read_input_tokens": 8363, "cache_creation_input_tokens": 5417,
                 "output_tokens_details": {"thinking_tokens": 10}}
        for success in (True, False):
            with self.subTest(success=success), tempfile.TemporaryDirectory() as temporary:
                event = {"type": "result", "subtype": "success" if success else "error_max_turns",
                         "is_error": not success, "usage": usage, "num_turns": 2,
                         "modelUsage": {"test-model": {"inputTokens": 999999}},
                         "result": "PRIVATE_FINAL", "total_cost_usd": 987.654}
                body = "import json; print(json.dumps(" + repr(event) + "))"
                _, directory, argv = self.setup_run(temporary, body)
                argv[argv.index("--"):argv.index("--")] = ["--resume", "saved-session"]
                result = subprocess.run(argv, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0 if success else 65, result.stderr)
                state = json.loads(result.stdout)
                self.assertEqual(state["token_usage_scope"], "main_loop_invocation")
                self.assertEqual(state["token_usage"]["total_tokens"], 14063)
                self.assertEqual(state["num_turns"], 2)
                self.assertGreater(state["elapsed_seconds"], 0)
                self.assertNotIn("987.654", result.stdout)
                self.assertNotIn("PRIVATE_FINAL", result.stdout)
                self.assertFalse((directory / "acceptance.json").exists())

    def test_missing_or_invalid_token_counts_are_unknown(self):
        counts = module.token_usage({"input_tokens": 0, "output_tokens": True,
                                     "cache_read_input_tokens": -1,
                                     "cache_creation_input_tokens": 1.5})
        self.assertEqual(counts["input_tokens"], 0)
        for key in ("output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens",
                    "total_tokens"):
            self.assertIsNone(counts[key])
        self.assertTrue(all(value is None for value in module.token_usage(None).values()))

    def execution_record(self, root, name, phase="completed", usage=None):
        directory = root / name
        directory.mkdir()
        state = {"phase": phase, "incomplete": phase != "completed",
                 "cc_exit_code": 0, "runner_exit_code": 0 if phase == "completed" else 2,
                 "token_usage_scope": "main_loop_invocation",
                 "token_usage": module.token_usage(usage)}
        for filename in ("status.json", "summary.json"):
            (directory / filename).write_text(json.dumps(state))
        return directory

    def record_decision(self, directory, outcome, evidence):
        return subprocess.run([sys.executable, str(SCRIPT), "record-acceptance",
                               "--run-dir", str(directory), "--outcome", outcome,
                               "--artifact-ref", "snapshot-1", "--evidence-file", str(evidence)],
                              capture_output=True, text=True)

    def test_summary_separates_acceptance_and_reports_unknown_subtotals(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = self.execution_record(root, "first", usage={
                "input_tokens": 10, "output_tokens": 5,
                "cache_read_input_tokens": 20, "cache_creation_input_tokens": 0})
            second = self.execution_record(root, "second", "needs_attention")
            before = module.summarize([first, second])
            self.assertEqual([row["acceptance"] for row in before["runs"]], ["pending", "pending"])
            evidence = root / "verification.json"
            evidence.write_text('{"checks":"PRIVATE_CHECK_BODY"}')
            original = (first / "status.json").read_bytes()
            decision = self.record_decision(first, "passed", evidence)
            self.assertEqual(decision.returncode, 0, decision.stderr)
            self.assertEqual((first / "status.json").read_bytes(), original)
            report = subprocess.run([sys.executable, str(SCRIPT), "summarize",
                                     "--run-dir", str(first), "--run-dir", str(second),
                                     "--run-dir", str(first / ".." / "first")],
                                    capture_output=True, text=True, check=True)
            summary = json.loads(report.stdout)
            self.assertEqual(len(summary["runs"]), 2)
            self.assertEqual(summary["runs"][0]["acceptance"], "passed")
            self.assertEqual(summary["runs"][1]["process_phase"], "needs_attention")
            self.assertEqual(summary["runs"][1]["acceptance"], "pending")
            self.assertEqual(summary["token_totals"]["total_tokens"],
                             {"reported": 35, "unknown_runs": 1})
            self.assertEqual(summary["token_totals"]["cache_creation_input_tokens"],
                             {"reported": 0, "unknown_runs": 1})
            self.assertNotIn("PRIVATE_CHECK_BODY", report.stdout + decision.stdout)
            self.assertNotEqual(self.record_decision(first, "failed", evidence).returncode, 0)
            self.assertEqual(json.loads((first / "acceptance.json").read_text())["outcome"], "passed")

    def test_acceptance_requires_finished_execution_and_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence = root / "checks.txt"
            evidence.write_text("checks failed")
            for phase in ("running", "failed", "needs_attention", "cancelled"):
                with self.subTest(phase=phase):
                    directory = self.execution_record(root, phase, phase)
                    self.assertNotEqual(self.record_decision(directory, "passed", evidence).returncode, 0)
                    self.assertFalse((directory / "acceptance.json").exists())
            directory = self.execution_record(root, "complete")
            self.assertNotEqual(self.record_decision(directory, "passed", root / "missing").returncode, 0)
            self.assertFalse((directory / "acceptance.json").exists())
            self.assertEqual(self.record_decision(directory, "failed", evidence).returncode, 0)
            self.assertEqual(module.summarize([directory])["runs"][0]["acceptance"], "failed")

    def test_invalid_records_do_not_silently_become_pending(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = self.execution_record(Path(temporary), "run", "failed")
            for record in ({"outcome": "passed", "artifact_ref": "v1", "evidence_file": "checks"},
                           {"outcome": "failed"}, [], {"outcome": "unknown"}):
                with self.subTest(record=record):
                    (directory / "acceptance.json").write_text(json.dumps(record))
                    result = subprocess.run([sys.executable, str(SCRIPT), "summarize",
                                             "--run-dir", str(directory)], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")

    @unittest.skipUnless(os.name == "posix", "process group signal forwarding")
    def test_cancellation_marks_incomplete_and_stops_child(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, directory, argv = self.setup_run(temporary, "import time; time.sleep(20)")
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    path = directory / "status.json"
                    if path.exists() and json.loads(path.read_text()).get("phase") == "running":
                        break
                    time.sleep(0.02)
                else:
                    self.fail("child not started")
                child = json.loads(path.read_text())["pid"]
                process.terminate()
                stdout, stderr = process.communicate(timeout=8)
                self.assertEqual(process.returncode, 143, stderr)
                self.assertEqual(json.loads(stdout)["phase"], "cancelled")
                self.assertIs(json.loads(stdout)["incomplete"], True)
                with self.assertRaises(ProcessLookupError):
                    os.kill(child, 0)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()

    @unittest.skipUnless(os.name == "posix", "process group signal forwarding")
    def test_cancellation_reaches_descendant_after_leader_exits(self):
        with tempfile.TemporaryDirectory() as temporary:
            body = ('import subprocess, sys; from pathlib import Path; '
                    'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(20)"]); '
                    'Path("descendant.pid").write_text(str(p.pid))')
            root, directory, argv = self.setup_run(temporary, body)
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    if (root / "descendant.pid").exists():
                        break
                    time.sleep(0.02)
                else:
                    self.fail("descendant not started")
                time.sleep(0.1)
                process.terminate()
                stdout, stderr = process.communicate(timeout=8)
                self.assertEqual(process.returncode, 143, stderr)
                state = json.loads(stdout)
                self.assertEqual(state["phase"], "cancelled")
                self.assertEqual(state["cc_exit_code"], 0)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()

    @unittest.skipUnless(os.name == "posix", "process group signal forwarding")
    def test_cancel_escalates_when_descendant_ignores_term(self):
        with tempfile.TemporaryDirectory() as temporary:
            code = ('import signal,time; from pathlib import Path; '
                    'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                    'Path("ready").write_text("ready"); time.sleep(30)')
            body = ('import subprocess,sys,time; from pathlib import Path; '
                    f'p=subprocess.Popen([sys.executable,"-c",{code!r}]); '
                    '\nwhile not Path("ready").exists(): time.sleep(0.01)\n'
                    'Path("descendant.pid").write_text(str(p.pid))')
            root, directory, argv = self.setup_run(temporary, body)
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    if (root / "descendant.pid").exists():
                        break
                    time.sleep(0.02)
                else:
                    self.fail("descendant not ready")
                process.terminate()
                stdout, stderr = process.communicate(timeout=9)
                self.assertEqual(process.returncode, 143, stderr)
                self.assertEqual(json.loads(stdout)["phase"], "cancelled")
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()


if __name__ == "__main__":
    unittest.main()
