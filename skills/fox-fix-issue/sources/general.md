# Other sources

Issues that do not come from Projex: a QA test case, a chat message, a screenshot, a document, a link, or something the user describes. The user names the source when invoking; it can be anywhere.

## Read-only by default

Read the source with the tool that fits it (a repository file with the file tools, a Feishu document or message with the matching `lark-*` skill, an image by viewing it). Do not edit a case, tick a checklist, change a status, or reply unless the user has explicitly authorized that write in this conversation. When the user specifies a write-back target and scope, write within that scope and read it back; otherwise draft it and ask. In dispatched mode, the worker returns drafts and the coordinator owns the writes.

If the source cannot be read, report what is missing and ask for it; do not reconstruct the report from memory or guesswork.

## Issue key

The source has no key of its own. Use the key the coordinator assigned, or in standalone mode choose a short lowercase slug when starting, such as `qa-login-03` for a test case or `fb-export-csv` for feedback, and state it in the first message. The key names the task, the fix branch and worktree, the lock owner, and local test data; it is not written into commits or into the source.

Taking the issue writes nothing.

## Commit trailer

None. Describe the problem in the commit subject and body as usual.

## QA test cases

Treat each case as the report: its preconditions, steps, and expected result. A case is an issue only once it fails.

A failure is one of these; record which, with the evidence:

| Class | Next |
|---|---|
| Code defect: the product does not do what the case expects, and the expectation matches the product's documented behavior | Fix it like any other issue |
| Case wrong: the case's steps or expectation contradict documented behavior, or the case is out of date | Do not change code; conclude with the evidence and the suggested case correction |
| Environment or data: missing local data, an unavailable service, a credential, or a setup the case assumes | Fix the local setup if it is in scope; otherwise report it as a blocker |
| Disputed expectation: no source settles what the product should do | Ask the user; do not guess |

Local acceptance for a fixed case is running that case's steps again and seeing its expected result. Before reporting a case as blocked, check whether existing data, an in-scope local environment fix, or safely constructed and restored local test data can cover it. If it remains blocked, state what is missing. While a product decision is pending, continue independent steps.

### Runner assignment

A coordinator may dispatch a worker only to run cases, with the case source, the acceptance workspace, the slot, and the lock. The runner edits no code and makes no commits. It acquires the lock as in [dispatched mode](../SKILL.md#dispatched-mode) step 2, starts the slot as in step 4, runs every case end to end following [local end-to-end acceptance](../SKILL.md#local-end-to-end-acceptance), removes the test data it created, stops the slot, and releases the lock. Its report gives each case a result: passed, failed, partially completed, or blocked. List the steps verified, steps not verified and why, and evidence for failures with the class from the table above. Identify constructed data or mocked responses, their verification limits, and cleanup. Mark a case passed only when all applicable steps match their expected results; a substitute check does not pass the original flow.

## Write-back

Write back only within the target and scope the user explicitly authorized, then read it back; otherwise include a conclusion the user can paste back to the source. Keep it short and non-technical: what was wrong, what changed or why nothing changed, and what the reader should do next, if anything. Leave out commit hashes, file paths, and internal names unless the source is a technical channel.

Without a write-back there is nothing to mark fixed after merge; the conclusion says the fix reaches users once the branch is merged and deployed.
