# Projex API guide

## Configuration and credentials

| Setting | Default or source |
|---|---|
| Project ID | `ab491d6f94800aaeb9ef68e915` for key-only input; an explicit project in the URL takes precedence |
| Organization ID | `659b8196e29648ed55c8f571`; override with the script's `--organization-id` option |
| Credential | Environment variable `ALIYUN_YUNXIAO_TOKEN`, sent as the `x-yunxiao-token` header |
| API origin | Central edition: `https://openapi-rdc.aliyuncs.com` |

The default organization is initial configuration, not proof of project ownership. On first use, verify the target project and work item through read-only requests. Report an organization mismatch or insufficient permissions instead of changing identity or guessing other organizations. The script implements the configured central edition only; confirm the official endpoint separately for a Region edition instance.

This environment has the token exported in `~/.zprofile`. Ordinary command tools may not inherit a login shell. If the variable is missing, run the script through `/bin/zsh -lc` while preserving the caller's working directory. Check only whether the value is nonempty. Never print the value, request headers, or shell tracing, and do not place credentials in arguments, this skill, temporary comment files, or commits.

Core permissions under Projex (`项目协作`) are work items (`工作项`): read/write; work item comments (`工作项评论`): read/write; work item workflows (`工作项工作流`): read-only; projects (`项目`): read-only. Add attachment or field read permissions only as required by the actual endpoint. Successful Codeup access does not establish Projex permissions. Do not depend on the `pr` skill or its scripts.

## Script

Use the bundled `scripts/projex.py`, which requires only the Python 3.10+ standard library. On macOS a login shell's `python3` can resolve to `/usr/bin/python3` (3.9), which fails at import; set `PY` to a 3.10+ interpreter such as `/opt/homebrew/bin/python3` and confirm it with `"$PY" --version`. Replace `SKILL_DIR` below with this skill's actual absolute path, then run commands from the target code repository:

```bash
SKILL_DIR='/Users/hulz/Developer/side-projects/fox-skills/skills/fox-fix-projex-bug'
PY='/opt/homebrew/bin/python3'
"$PY" "$SKILL_DIR/scripts/projex.py" --help
```

If the credential was not inherited, use an explicit login shell. Apply the same method to subsequent commands; loading a variable in one child process does not make later tool calls inherit it:

```bash
/bin/zsh -lc '/opt/homebrew/bin/python3 /Users/hulz/Developer/side-projects/fox-skills/skills/fox-fix-projex-bug/scripts/projex.py project ab491d6f94800aaeb9ef68e915'
```

Successful commands emit a JSON object with the original response in `body` and pagination headers in `pagination`. Redirect large responses to the task's temporary directory and parse them locally to avoid tool truncation. Errors go to stderr with a nonzero exit code. The script does not retry or load shell configuration automatically.

### URLs and issue keys

The project ID appears in `/projex/project/<project-id>/bug`; the work item ID appears in `#...&openWorkitemIdentifier=<workitem-id>`. Parse the URL path, query, and fragment with a URL parser. Do not mistake `viewIdentifier` for the work item ID.

Read-only commands:

```bash
"$PY" "$SKILL_DIR/scripts/projex.py" project ab491d6f94800aaeb9ef68e915
"$PY" "$SKILL_DIR/scripts/projex.py" get '<workitem-id>'
"$PY" "$SKILL_DIR/scripts/projex.py" search --project-id ab491d6f94800aaeb9ef68e915 --page 1
"$PY" "$SKILL_DIR/scripts/projex.py" comments '<workitem-id>'
"$PY" "$SKILL_DIR/scripts/projex.py" workflow '<workitem-id>'
"$PY" "$SKILL_DIR/scripts/projex.py" me
"$PY" "$SKILL_DIR/scripts/projex.py" search --status-id '<status-id>' --assigned-to '<user-id>' --sort asc --page 1
```

`me` returns the user that owns the token (`body.id`, `body.name`); it needs the token's organization user read permission, and a 403 means that permission is missing. `--status-id` (repeatable) and `--assigned-to` become exact `conditions` filters on the server; values are IDs, never display names. Status IDs come from an item's `status.id` or the workflow's `body.statuses`. The search response's `pagination` keeps `X-Total`, `X-Total-Pages`, and `X-Next-Page`.

`search` is read-only despite using HTTP POST. It queries the `Bug` category with 200 items per page by default. Match the input key against `serialNumber` exactly across pages, then fetch the matching work item's details. Do not guess an undocumented issue-key filter. Use pagination headers to determine when to stop; without them, continue until a page contains fewer items than requested. Keep `page * perPage <= 10000`. If that window prevents a complete search, report the limit and request a work item URL or use a verified official filter; do not claim the bug is definitely absent.

Important detail fields are `id`, `serialNumber`, `subject`, `description`, `formatType`, `space.id`, `categoryId`, `status`, and `workitemType`. Preserve each comment's `id`, `user`, `gmtCreate`, `gmtModified`, `content`, `contentFormat`, and `parentId`, including reply relationships. The current comments endpoint has no documented pagination parameters. If response headers indicate additional pages, verify the official pagination mechanism before continuing; do not claim all comments have been read.

### Status updates and comments

The workflow response's `body.statuses` contains status `id`, `name`, and `displayName`. Use an ID only after an exact name match identifies one unique status and the current issue state allows the operation. Do not hardcode IDs, match similar names, or try transitions one by one. The update command changes only `status`.

```bash
"$PY" "$SKILL_DIR/scripts/projex.py" status '<workitem-id>' --status-id '<verified-status-id>'
"$PY" "$SKILL_DIR/scripts/projex.py" get '<workitem-id>'
```

Read the completion comment from a local UTF-8 file. The script sends it as `MARKDOWN`. Include only the confirmed cause, repair details, and actual validation results. Omit commit hashes because rebases change them:

```bash
"$PY" "$SKILL_DIR/scripts/projex.py" comment '<workitem-id>' --body-file '/absolute/path/to/comment.md'
"$PY" "$SKILL_DIR/scripts/projex.py" comments '<workitem-id>'
```

A successful write command does not replace read-back verification. Follow the main workflow after HTTP errors, permission errors, or timeouts; do not resend automatically. Retain status and comment IDs in the task context for recovery.

## Images and attachments

Identify relevant material in the description, comments, and attachment list. Use these read-only commands when needed. Returned download URLs are temporary and may expire. Read large files and images with the appropriate tools; do not forward the Yunxiao token to attachment download hosts. Explain any evidence gap caused by an inaccessible critical attachment.

```bash
"$PY" "$SKILL_DIR/scripts/projex.py" attachments '<workitem-id>'
"$PY" "$SKILL_DIR/scripts/projex.py" file '<workitem-id>' --file-id '<file-id>'
```

- [ListWorkitemAttachments: request syntax and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemattachments)
- [GetWorkitemFile: request parameters and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemfile)

Prefer APIs and background reads. If browser interaction is necessary, follow the workspace's browser and account rules. In a BrandPal workspace, verify the unique Chrome profile named `brandpal.ai`; desktop input and clipboard access require permission under the workspace rules. Do not silently use another profile.

## Official references

Checked on 2026-10-30. If an interface changes, consult the relevant official documentation section rather than guessing write operations from internal web endpoints.

- [Service endpoint: endpoint domain](https://help.aliyun.com/zh/yunxiao/developer-reference/service-access-point-domain)
- [Personal access tokens: creation and permissions](https://help.aliyun.com/zh/yunxiao/user-guide/personal-access-token)
- [GetProject: request syntax and authorization](https://help.aliyun.com/zh/yunxiao/developer-reference/getproject)
- [GetWorkitem: request syntax and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitem)
- [SearchWorkitems: request parameters and pagination window](https://help.aliyun.com/zh/yunxiao/developer-reference/searchworkitems)
- [ListWorkitemComments: request syntax and response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/listworkitemcomments)
- [GetWorkitemWorkflowInfo: response fields](https://help.aliyun.com/zh/yunxiao/developer-reference/getworkitemworkflowinfo-get-work-item-workflow-information)
- [UpdateWorkitem: request syntax and status update format](https://help.aliyun.com/zh/yunxiao/developer-reference/updateworkitem)
- [CreateWorkitemComment: request parameters and formatType](https://help.aliyun.com/zh/yunxiao/developer-reference/createworkitemcomment)
