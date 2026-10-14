# Claude Code CLI dispatch from Codex App

Read this when Claude Code CLI is requested or already authorized as an execution backend. Use Codex's command tool to run the installed `claude` executable. Do not pass Claude model IDs to Codex's native subagent dispatcher. This reference adds a backend adapter; it does not relax the [coordination rules](../SKILL.md) or [model-routing rules](model-routing.md).

## Prepare one bounded assignment

- Keep the coordinator in Codex App. Record backend `claude-code-cli`, role, resource owner, working directory, inputs, deliverable, acceptance, dependencies and selected model/effort. Supply role boundaries explicitly; CC does not inherit the Codex conversation or its invoked skills.
- Check the installed `claude --version`, supported CLI flags and existing authentication. For auth checks, retain only the needed logged-in/provider fields; do not print credentials or unrelated account details. Missing CLI, authentication or permissions is a blocker, not permission to install, log in interactively, change shared settings or substitute a backend.
- Select model and effort using CC's available models, current documentation and account restrictions. Honor exact pins. Aliases can resolve through user/provider configuration; record the resolved model and use it on subsequent turns to avoid alias drift. Never infer CC availability from the Codex model catalog.
- Check effort support, environment overrides and managed/account caps before accepting a pin. CC can clamp unsupported or capped effort, including silently in JSON output. A successful process or model self-report does not establish the effective effort. If a pin cannot be verified, block the route rather than claim it applied. An unpinned unknown effective effort must be reported as unknown with its requested value and acceptance limits.
- Select tools, permissions, hooks and MCP access for the role and assignment. Preserve required project instructions and existing safeguards. CC is a separate process: Codex's tool permissions are not automatically a CC permission policy. Do not add permission-bypass flags or broaden access to overcome a denial. In unattended runs, use supported non-interactive denial behavior and narrowly allow only authorized operations. Keep dispatch with the coordinator unless bounded coordination was explicitly delegated.

## Start and collect

Start a new session for a new assignment, without `--resume`, `--continue` or `--fork-session`. Advisors receive fresh supplied context, never an App fork. Save the prompt as a UTF-8 file containing the task, constraints, necessary raw evidence and acceptance criteria; do not embed untrusted task text in shell code.

Use explicit `--model`, `--effort` and structured output. The following read-only example uses an argv array and stdin, preserving stdout, stderr and the actual process exit status. Replace paths and selected settings with the assignment's values; the example is not a model recommendation or a permission template for writing tasks.

```python
import json
import subprocess
from pathlib import Path

assignment_dir = Path("/absolute/path/to/assignment-record")
assignment_dir.mkdir(parents=True, exist_ok=False)
argv = [
    "claude", "-p",
    "--model", selected_model,
    "--effort", selected_effort,
    "--output-format", "stream-json", "--verbose",
    "--tools", "Read", "--allowedTools", "Read",
    "--permission-mode", "dontAsk",
    "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
    "--settings", '{"disableAllHooks":true}',
]
# Retain required hooks/MCP tools when the assignment needs them;
# these invocation-only restrictions do not edit shared settings.
with prompt_path.open("r", encoding="utf-8") as prompt, \
     (assignment_dir / "stdout.jsonl").open("w", encoding="utf-8") as out, \
     (assignment_dir / "stderr.log").open("w", encoding="utf-8") as err:
    process = subprocess.Popen(argv, cwd=working_directory, stdin=prompt,
                               stdout=out, stderr=err)
    # Use the host command session for bounded polling, cancellation and updates.
    exit_code = process.wait()
(assignment_dir / "exit.json").write_text(
    json.dumps({"exit_code": exit_code}), encoding="utf-8")
```

The command may run asynchronously through the host's process-session interface; return to useful coordinator work and maintain progress updates. Track each process and assignment separately. Do not cancel another assignment's process or start overlapping writers on the same resource.

Inspect structured events after completion, not just the last output line or claimed task success:

- Retain the session ID from initialization/result events, CLI version, requested configuration, observable effective configuration, exit status and diagnostics in the assignment record. Use reported fields only when actually present; output schemas vary by version. `system/init.model`, assistant message models and final `modelUsage` provide model evidence. Inspect all relevant model usage for substitutions or fallback, accounting separately for auxiliary models rather than equating every usage key with the worker model.
- Require a successful process exit and a successful final `result` (`is_error: false`, successful subtype), then check permission denials, incomplete work and the actual acceptance criteria. A final response alone does not prove files changed correctly or tests passed. Empty/malformed output, missing result, authentication/model errors, cancellation and denied required operations are failures or incomplete work; preserve their diagnostics.
- Verify effort through runtime configuration evidence, such as the session's local `/effort` report or sanitized configuration metadata, where supported. Some CC versions record `effort` and `perTurnEffort` on assistant entries in that session's persisted transcript; inspect only the assigned session and extract only needed fields. CLI acceptance, `per_turn_effort_active` and thinking-token counts do not establish a particular effort level. Do not collect raw API bodies or credentials merely for proof. Record unavailable evidence honestly; never use model prose as configuration evidence.
- If a pin differs from observed settings, stop accepting work under that route and report the mismatch. Do not silently retry with another backend/model/effort. For unpinned substitutions, apply the existing fallback and acceptance rules before further work.

## Resume without changing configuration

Save the exact session ID and verify that persistence actually worked before promising continuation. Do not use `--no-session-persistence` for resumable work. A returned session ID alone does not prove that a transcript was saved; sandbox permissions or local persistence policy may prevent it.

For a follow-up, resume the recorded ID in the same working directory using `--resume SESSION_ID`, the same resolved model and selected effort, and the same required permission/tool configuration. Save each turn's stdout, stderr and exit status separately without overwriting earlier evidence. Supply the delta, missing evidence and affected checks. Never use `--continue` to guess which session to resume, or `--fork-session` to replace the existing assignment. Do not change configurations during corrections, repairs or final checks.

If the session is missing, report the persistence failure. Restore necessary context only through an authorized fresh-context handoff with the unchanged assignment configuration; disclose the loss of retained context rather than presenting the new process as a successful resume. Resolve permission or persistence conditions before repeating a failed call. Independent reviewers use a separate fresh session from the producer and receive the artifact/version and necessary evidence.

## Finish

The coordinator checks outputs, affected callers and critical failure paths, and owns repairs/rechecks and final acceptance. Distinguish requested settings, observable effective settings, CC task completion and coordinator verification. Retain useful failure evidence and requested deliverables, remove unneeded task-created temporary data, and do not delete unrelated CC sessions or shared configuration. Actual provider/tool usage belongs to the external backend; report costs only when measured, without inferring equivalence to Codex usage.

Current interface references: [CLI flags](https://code.claude.com/docs/en/cli-reference), [programmatic execution and resume](https://code.claude.com/docs/en/headless), [model and effort configuration](https://code.claude.com/docs/en/model-config). Consult them for material interface gaps; use the installed interface and observed behavior for execution.
