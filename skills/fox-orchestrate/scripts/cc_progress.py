#!/usr/bin/env python3
"""Run CC with local progress records; never echo its raw output to the caller."""

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time


TOOLS = {"Read", "Write", "Edit", "Bash", "Glob", "Grep", "Agent",
         "WebFetch", "WebSearch", "TodoWrite", "TaskCreate", "TaskUpdate"}
TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens",
                "cache_creation_input_tokens")
FAILURE_REASONS = ("launch_error", "permission_denied", "limit_reached", "invalid_output",
                   "execution_error", "interrupted", "runner_error", "unknown")
LIMIT_RESULTS = {"error_max_turns", "error_max_budget_usd",
                 "error_max_structured_output_retries"}


def classify_failure(events, code, interrupted, *, launch_error=False, runner_error=False):
    # Describe observed terminal evidence, never infer causes from arbitrary text.
    reasons = set()
    if launch_error:
        reasons.add("launch_error")
    if runner_error:
        reasons.add("runner_error")
    if interrupted:
        reasons.add("interrupted")
    result = events.result
    denied = result.get("permission_denials") if result is not None else None
    if events.permission_denied or (isinstance(denied, list) and denied):
        reasons.add("permission_denied")
    if events.invalid:
        reasons.add("invalid_output")
    if result is not None:
        subtype, is_error = result.get("subtype"), result.get("is_error")
        if (not isinstance(subtype, str) or not subtype or type(is_error) is not bool
                or (subtype == "success" and is_error)):
            reasons.add("invalid_output")
        elif is_error and subtype in LIMIT_RESULTS:
            reasons.add("limit_reached")
        elif subtype != "success" or is_error:
            reasons.add("execution_error")
    # Do not add missing-result/exit symptoms when a more specific cause explains them.
    if not reasons:
        if code:
            reasons.add("execution_error")
        elif result is None:
            reasons.add("invalid_output")
    return [reason for reason in FAILURE_REASONS if reason in reasons] or ["unknown"]


def recorded_failure_reasons(state):
    active = state["phase"] in ("starting", "running")
    completed = state["phase"] == "completed"
    if "failure_reasons" not in state:
        return None if active else [] if completed else ["unknown"]
    reasons = state["failure_reasons"]
    if active:
        if reasons is not None:
            raise ValueError("active execution cannot have terminal failure reasons")
    elif (not isinstance(reasons, list)
          or any(not isinstance(reason, str) or reason not in FAILURE_REASONS for reason in reasons)
          or len(set(reasons)) != len(reasons)
          or (completed and reasons) or (not completed and not reasons)
          or ("unknown" in reasons and len(reasons) != 1)):
        raise ValueError("invalid execution failure reasons")
    return reasons


def token_usage(usage):
    # Result usage covers this invocation's main loop, not nested agents.
    usage = usage if isinstance(usage, dict) else {}
    counts = {key: value if type(value := usage.get(key)) is int and value >= 0 else None
              for key in TOKEN_FIELDS}
    counts["total_tokens"] = (sum(counts.values())
                              if all(value is not None for value in counts.values()) else None)
    return counts


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


class Events:
    def __init__(self):
        self.tools = {}
        self.session_id = None
        self.model = None
        self.result = None
        self.permission_denied = False
        self.invalid = 0
        self.count = 0
        self.seen_calls = set()
        self.seen_replies = set()
        self.last = "starting"

    def emit(self, message):
        self.last = message

    def consume(self, line):
        self.count += 1
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("not an event object")
        except ValueError:
            self.invalid += 1
            if self.invalid == 1:
                self.emit("invalid event; inspect saved diagnostics")
            return
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            # Only constrained identifiers enter status, never arbitrary event strings.
            for field in ("session_id", "model"):
                value = event.get(field)
                if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.:\[\]-]{1,160}", value):
                    setattr(self, field, value)
            self.emit("CC session started")
        elif kind == "system" and event.get("subtype") == "permission_denied":
            self.permission_denied = True
            self.emit("permission denied; coordinator attention required")
        elif kind in ("assistant", "user"):
            message = event.get("message")
            blocks = message.get("content", []) if isinstance(message, dict) else []
            if not isinstance(blocks, list):
                return
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    call = block.get("id")
                    if not isinstance(call, str) or call in self.seen_calls:
                        continue
                    self.seen_calls.add(call)
                    name = block.get("name")
                    name = name if isinstance(name, str) and name in TOOLS else "other tool"
                    self.tools[call] = name
                    self.emit(f"{name} started")
                elif block.get("type") == "tool_result":
                    call = block.get("tool_use_id")
                    if not isinstance(call, str) or call in self.seen_replies:
                        continue
                    self.seen_replies.add(call)
                    name = self.tools.get(call, "other tool")
                    state = "failed" if block.get("is_error") else "completed"
                    self.emit(f"{name} {state}")
        elif kind == "result":
            self.result = event
            denied = event.get("permission_denials")
            if denied is not None and not isinstance(denied, list):
                self.invalid += 1
            success = event.get("subtype") == "success" and event.get("is_error") is False
            self.emit("CC turn completed; acceptance pending" if success else "CC turn failed")


def run(args):
    if os.name != "posix":
        raise ValueError("the runner currently requires a POSIX host")
    directory = Path(args.run_dir).resolve()
    extra = args.cc_args
    if extra[:1] == ["--"]:
        extra = extra[1:]
    reserved = {"--model", "--effort", "--resume", "-r", "--continue", "-c",
                "--fork-session", "--output-format", "--input-format", "--verbose",
                "--print", "-p"}
    if any(item.split("=", 1)[0] in reserved for item in extra):
        raise ValueError("pass model, effort and resume through runner options; stream format is fixed")
    prompt_path = Path(args.prompt_file).resolve()
    cwd = Path(args.cwd).resolve()
    # Validate resources before creating the exclusive turn record.
    with prompt_path.open("r", encoding="utf-8"):
        pass
    if not cwd.is_dir():
        raise ValueError("working directory does not exist")
    if not 1 <= len(args.model) <= 512 or not 1 <= len(args.effort) <= 64:
        raise ValueError("model/effort identifiers exceed status limits")
    directory.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    state = {"phase": "starting", "session_id": None, "observed_model": None,
             "requested_model": args.model, "requested_effort": args.effort,
             "effective_effort": None, "events": 0, "invalid_events": 0,
             "cc_exit_code": None, "runner_exit_code": None, "incomplete": True,
             "failure_reasons": None,
             "elapsed_seconds": None, "num_turns": None,
             "token_usage_scope": "main_loop_invocation", "token_usage": token_usage(None)}
    atomic_json(directory / "status.json", state)
    argv = [args.claude, "-p", "--model", args.model, "--effort", args.effort,
            "--output-format", "stream-json", "--verbose"]
    if args.resume:
        argv += ["--resume", args.resume]
    argv += extra
    child = None
    events = Events()
    interrupted = None
    cancel_timer = None

    def force_stop():
        if child is not None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def forward(number, _frame):
        nonlocal interrupted, cancel_timer
        interrupted = number
        if child is not None:
            # The leader can exit while descendants still hold the stdout pipe.
            try:
                os.killpg(child.pid, number)
            except ProcessLookupError:
                pass
            if cancel_timer is None:
                # This must run even while stdout iteration or wait() blocks.
                cancel_timer = threading.Timer(5, force_stop)
                cancel_timer.daemon = True
                cancel_timer.start()

    previous = {s: signal.signal(s, forward) for s in (signal.SIGINT, signal.SIGTERM)}
    try:
        with (directory / "stdout.jsonl").open("w", encoding="utf-8") as raw, \
             (directory / "stderr.log").open("w", encoding="utf-8") as err, \
             prompt_path.open("r", encoding="utf-8") as prompt:
            events.emit("starting CC")
            try:
                child = subprocess.Popen(argv, cwd=cwd, stdin=prompt, stdout=subprocess.PIPE,
                                         stderr=err, text=True, encoding="utf-8",
                                         errors="replace", start_new_session=True)
            except OSError as error:
                state.update(phase="failed", runner_exit_code=127,
                             failure_reasons=classify_failure(events, None, interrupted,
                                                              launch_error=True))
                err.write(f"Could not start Claude Code executable: {error}\n")
                events.emit("CC executable unavailable")
            else:
                state.update(phase="running", pid=child.pid)
                atomic_json(directory / "status.json", state)
                if interrupted:
                    forward(interrupted, None)
                for line in child.stdout:
                    raw.write(line)
                    raw.flush()
                    events.consume(line)
                    state.update(session_id=events.session_id, observed_model=events.model,
                                 events=events.count, invalid_events=events.invalid,
                                 last_event=events.last,
                                 permission_denial_seen=events.permission_denied)
                    atomic_json(directory / "status.json", state)
                child.stdout.close()
                code = child.wait()
                code = code if code >= 0 else 128 - code
                result = events.result
                if result is not None:
                    atomic_json(directory / "result.json", result)
                    turns = result.get("num_turns")
                    state.update(token_usage=token_usage(result.get("usage")),
                                 num_turns=turns if type(turns) is int and turns >= 0 else None)
                success = (result is not None and result.get("subtype") == "success"
                           and result.get("is_error") is False)
                denied = result.get("permission_denials") if result else None
                denials = len(denied) if isinstance(denied, list) else 0
                exit_code = (128 + interrupted if interrupted else code or
                             (65 if events.invalid or not success else
                              2 if denials or events.permission_denied else 0))
                phase = ("cancelled" if interrupted else "completed" if exit_code == 0
                         else "needs_attention" if exit_code == 2 else "failed")
                state.update(phase=phase, cc_exit_code=code, runner_exit_code=exit_code,
                             permission_denials=denials,
                             permission_denial_seen=events.permission_denied,
                             incomplete=exit_code != 0,
                             failure_reasons=classify_failure(events, code, interrupted) if exit_code else [],
                             interrupted_signal=interrupted)
                events.emit(f"process {phase}; CC exit {code}")
            state["last_event"] = events.last
    except (OSError, ValueError, TypeError):
        state.update(phase="failed", runner_exit_code=1,
                     failure_reasons=classify_failure(events, state["cc_exit_code"], interrupted,
                                                      launch_error="launch_error" in (state["failure_reasons"] or []),
                                                      runner_error=True))
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        if child is not None and child.stdout is not None:
            child.stdout.close()
        if cancel_timer is not None:
            cancel_timer.cancel()
        for number, handler in previous.items():
            signal.signal(number, handler)
    state["elapsed_seconds"] = round(time.monotonic() - started, 3)
    atomic_json(directory / "status.json", state)
    atomic_json(directory / "summary.json", state)
    print(json.dumps(state, ensure_ascii=False))
    return state["runner_exit_code"]


def check_acceptance(state, outcome):
    if not isinstance(state, dict) or state.get("phase") not in (
            "completed", "failed", "needs_attention", "cancelled"):
        raise ValueError("execution must finish before acceptance is recorded")
    if outcome == "passed" and not (
            state.get("phase") == "completed" and state.get("incomplete") is False
            and state.get("runner_exit_code") == 0 and state.get("cc_exit_code") == 0):
        raise ValueError("an unsuccessful execution cannot pass acceptance")


def record_acceptance(args):
    directory = Path(args.run_dir).resolve()
    state = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    check_acceptance(state, args.outcome)
    evidence = Path(args.evidence_file).resolve()
    if not args.artifact_ref.strip() or not evidence.is_file():
        raise ValueError("artifact reference and evidence file are required")
    record = {"outcome": args.outcome, "artifact_ref": args.artifact_ref,
              "evidence_file": str(evidence)}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory,
                                         prefix=".acceptance-", suffix=".tmp", delete=False) as output:
            temporary = Path(output.name)
            output.write(json.dumps(record, ensure_ascii=False) + "\n")
        # Publish closed, complete bytes atomically; link never replaces an existing decision.
        os.link(temporary, directory / "acceptance.json")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(json.dumps({"acceptance": args.outcome}))
    return 0


def read_run(directory):
    state = json.loads((directory / "status.json").read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("phase") not in (
            "starting", "running", "completed", "failed", "needs_attention", "cancelled"):
        raise ValueError("invalid execution record")
    acceptance = "pending"
    record = None
    decision = directory / "acceptance.json"
    if decision.exists():
        record = json.loads(decision.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or record.get("outcome") not in ("passed", "failed"):
            raise ValueError("invalid acceptance record")
        acceptance = record["outcome"]
        check_acceptance(state, acceptance)
        if not all(isinstance(record.get(key), str) and record[key].strip()
                   for key in ("artifact_ref", "evidence_file")):
            raise ValueError("acceptance must reference artifact and evidence")
    if state.get("token_usage_scope") not in (None, "main_loop_invocation"):
        raise ValueError("unsupported token accounting scope")
    row = {"run_dir": str(directory), "process_phase": state["phase"],
           "failure_reasons": recorded_failure_reasons(state),
           "acceptance": acceptance, "elapsed_seconds": state.get("elapsed_seconds"),
           "num_turns": state.get("num_turns"),
           "token_usage": token_usage(state.get("token_usage"))}
    return row, record


def summarize_rows(rows):
    totals = {}
    for key in (*TOKEN_FIELDS, "total_tokens"):
        reported = [row["token_usage"][key] for row in rows if row["token_usage"][key] is not None]
        totals[key] = {"reported": sum(reported) if reported else None,
                       "unknown_runs": len(rows) - len(reported)}
    reason_counts = {reason: sum(reason in (row["failure_reasons"] or []) for row in rows)
                     for reason in FAILURE_REASONS}
    acceptance_counts = {outcome: sum(row["acceptance"] == outcome for row in rows)
                         for outcome in ("pending", "passed", "failed")}
    return {"token_usage_scope": "main_loop_invocation", "runs": rows, "token_totals": totals,
            "execution_reason_counts": reason_counts, "acceptance_counts": acceptance_counts}


def summarize(run_dirs):
    directories = dict.fromkeys(Path(run_dir).resolve() for run_dir in run_dirs)
    return summarize_rows([read_run(directory)[0] for directory in directories])


def summarize_tasks(manifest):
    manifest = Path(manifest).resolve()
    document = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("tasks"), list):
        raise ValueError("manifest requires a task list")
    tasks, all_rows = [], []
    task_ids, owners = set(), set()
    for task in document["tasks"]:
        if (not isinstance(task, dict) or not isinstance(task.get("task_id"), str)
                or not task["task_id"].strip() or task["task_id"] in task_ids
                or not isinstance(task.get("run_dirs"), list)
                or "current_acceptance_run" not in task):
            raise ValueError("invalid task mapping or duplicate task ID")
        task_id = task["task_id"]
        task_ids.add(task_id)

        def resolve_run(value):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("run directory must be a nonempty path")
            return (manifest.parent / value).resolve()

        records = {}
        for value in task["run_dirs"]:
            directory = resolve_run(value)
            if directory in records:
                continue
            if directory in owners:
                raise ValueError("an invocation cannot belong to multiple tasks")
            owners.add(directory)
            records[directory] = read_run(directory)
        rows = [row for row, _ in records.values()]
        selection = task["current_acceptance_run"]
        current = None
        if selection is not None:
            directory = resolve_run(selection)
            if directory not in records or records[directory][1] is None:
                raise ValueError("current selection requires this task's recorded acceptance")
            decision = records[directory][1]
            current = {"run_dir": str(directory),
                       **{key: decision[key] for key in ("outcome", "artifact_ref", "evidence_file")}}
        summary = summarize_rows(rows)
        summary["invocation_acceptance_counts"] = summary.pop("acceptance_counts")
        tasks.append({"task_id": task_id, "invocation_count": len(rows),
                      "active_invocation_count": sum(row["process_phase"] in ("starting", "running")
                                                     for row in rows),
                      "current_acceptance": current, **summary})
        all_rows.extend(rows)
    summary = summarize_rows(all_rows)
    summary.pop("runs")  # Detailed invocation rows already belong to their tasks.
    summary["invocation_acceptance_counts"] = summary.pop("acceptance_counts")
    task_counts = {outcome: sum((task["current_acceptance"]["outcome"]
                                if task["current_acceptance"] else "pending") == outcome
                               for task in tasks)
                   for outcome in ("pending", "passed", "failed")}
    return {"task_count": len(tasks), "invocation_count": len(all_rows),
            "active_invocation_count": sum(task["active_invocation_count"] for task in tasks),
            "task_acceptance_counts": task_counts, "tasks": tasks, **summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    launch = commands.add_parser("run")
    for name in ("run-dir", "cwd", "prompt-file", "model", "effort"):
        launch.add_argument("--" + name, required=True)
    launch.add_argument("--claude", default="claude")
    launch.add_argument("--resume")
    launch.add_argument("cc_args", nargs=argparse.REMAINDER)
    status = commands.add_parser("status")
    status.add_argument("--run-dir", required=True)
    report = commands.add_parser("summarize")
    report.add_argument("--run-dir", action="append", required=True)
    task_report = commands.add_parser("summarize-tasks")
    task_report.add_argument("--manifest", required=True)
    acceptance = commands.add_parser("record-acceptance")
    acceptance.add_argument("--run-dir", required=True)
    acceptance.add_argument("--outcome", choices=("passed", "failed"), required=True)
    acceptance.add_argument("--artifact-ref", required=True)
    acceptance.add_argument("--evidence-file", required=True)
    args = parser.parse_args()
    try:
        if args.action == "run":
            return run(args)
        if args.action == "record-acceptance":
            return record_acceptance(args)
        if args.action == "summarize-tasks":
            print(json.dumps(summarize_tasks(args.manifest), ensure_ascii=False))
            return 0
        if args.action == "summarize":
            print(json.dumps(summarize(args.run_dir), ensure_ascii=False))
            return 0
        print((Path(args.run_dir) / "status.json").read_text(encoding="utf-8"), end="")
        return 0
    except (OSError, ValueError) as error:
        # No raw CC output or prompt text is included in runner diagnostics.
        print(f"CC progress runner: {type(error).__name__}; check paths/options and saved logs", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
