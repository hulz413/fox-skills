#!/usr/bin/env python3
"""Coordinator finish step for one dispatched issue.

Checks the landing first and writes to Projex only when it passes:

  repair         <fix-branch> must have at least one commit beyond <acceptance-branch>,
                 and every one must be on <acceptance-branch>, either patch-equivalent
                 (git cherry "-") or as a commit with the same subject and the same
                 changed lines (cherry-picks that git merged automatically change the
                 patch id), and a commit landed on <acceptance-branch> since <fix-branch> was
                 created must carry the bug's `Bug: <key>` trailer, which the merge sync reads
                 from that branch; then post the comment and set 开发完成.
  already-fixed  --fix-commit's change must be in origin/master by in_master.py's checks
                 (ancestor, patch-equivalent, or content already present, so squash merges
                 count) and no revert may have undone it; then post, set 开发完成,
                 and set 已修复, because the fix is already merged and carries no Bug:
                 trailer for a later merge sync to find.
  conclusion     post the comment only; the status is not changed.
  landing        check a repair's landing only, for issues from other sources; no Projex
                 arguments, no writes.

Run it from the target repository through a login shell so ALIYUN_YUNXIAO_TOKEN is set,
with Python 3.10+. --dry-run checks and prints the planned writes without writing. After writing,
it reads the comment and status back and exits nonzero when either is not what it wrote.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

FIX_SCRIPTS = Path(__file__).resolve().parents[2] / "fox-fix-issue" / "scripts"
PROJEX = FIX_SCRIPTS / "projex.py"
sys.path.insert(0, str(FIX_SCRIPTS))

from in_master import assess  # noqa: E402
DONE = "开发完成"
FIXED = "已修复"
LATER_THAN_DONE = {FIXED, "已关闭", "暂不修复", "无法重现"}


def run(*command: str) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"{' '.join(command)} failed with exit {result.returncode}:\n{result.stderr.strip()}")
    return result.stdout


def git(*args: str) -> str:
    return run("git", *args)


def changed_lines(commit: str) -> list[str]:
    """Each file's `diff --git` line and its added and removed lines, without the `---`/`+++` headers."""
    kept, in_hunk = [], False
    for line in git("show", "--format=", commit).splitlines():
        if line.startswith("diff --git "):
            kept.append(line)
            in_hunk = False
        elif line.startswith("@@"):
            in_hunk = True
        elif in_hunk and line[:1] in "+-":
            kept.append(line)
    return kept


def subject(commit: str) -> str:
    return git("log", "-1", "--format=%s", commit).strip()


def unlanded_commits(fix_branch: str, acceptance_branch: str) -> list[str]:
    commits = git("cherry", acceptance_branch, fix_branch).splitlines()
    if not commits:
        raise SystemExit(
            f"{fix_branch} has no commit beyond {acceptance_branch}, so there is no repair to check; "
            "use --mode conclusion or --mode already-fixed when the issue has no repair commit"
        )
    pending = [line.split()[1] for line in commits if line.startswith("+ ")]
    if not pending:
        return []
    by_subject: dict[str, list[str]] = {}
    for commit in git("log", "--format=%H", f"{fix_branch}..{acceptance_branch}").split():
        by_subject.setdefault(subject(commit), []).append(commit)
    missing = []
    for commit in pending:
        lines = changed_lines(commit)
        if not any(changed_lines(match) == lines for match in by_subject.get(subject(commit), [])):
            missing.append(f"{commit[:10]} {subject(commit)}")
    return missing


def check_trailer(fix_branch: str, acceptance_branch: str, key: str) -> None:
    if not git("log", "--format=%H", "--grep", f"^Bug: {key}$", f"{fix_branch}..{acceptance_branch}").split():
        raise SystemExit(
            f"no commit landed on {acceptance_branch} since {fix_branch} was created carries 'Bug: {key}', so the "
            f"merge sync could never mark it {FIXED}; adding it means rewriting {acceptance_branch}, so ask the user"
        )


def projex(*args: str) -> object:
    return json.loads(run(sys.executable, str(PROJEX), *args))["body"]


def status_id(workitem_id: str, name: str) -> str:
    matches = [s["id"] for s in projex("workflow", workitem_id)["statuses"] if s.get("name") == name]
    if len(matches) != 1:
        raise SystemExit(f"expected one status named {name}, found {len(matches)}")
    return matches[0]


def comment_bodies(workitem_id: str) -> list[str]:
    return [(c.get("content") or "").strip() for c in projex("comments", workitem_id)]


def check_landing(args: argparse.Namespace) -> None:
    if args.mode in ("repair", "landing"):
        missing = unlanded_commits(args.fix_branch, args.acceptance_branch)
        if missing:
            raise SystemExit("not landed on " + args.acceptance_branch + ":\n  " + "\n  ".join(missing))
    elif args.mode == "already-fixed":
        if not assess(args.fix_commit)[0]:
            raise SystemExit(
                f"{args.fix_commit} is not shown to be in origin/master, or a revert may have undone it; "
                "this does not prove it is missing. Run in_master.py for the details and read master's code "
                "before concluding either way"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workitem_id", nargs="?", help="required except for landing")
    parser.add_argument("comment_file", type=Path, nargs="?", help="required except for landing")
    parser.add_argument("--mode", choices=("repair", "already-fixed", "conclusion", "landing"), default="repair")
    parser.add_argument("--fix-branch", help="required for repair and landing")
    parser.add_argument("--fix-commit", help="required for already-fixed")
    parser.add_argument("--acceptance-branch", default="bugfix/verification")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.mode in ("repair", "landing") and not args.fix_branch:
        parser.error(f"--fix-branch is required for {args.mode}")
    if args.mode == "landing":
        check_landing(args)
        print(f"{args.fix_branch}: landed on {args.acceptance_branch}")
        return
    if not args.workitem_id or not args.comment_file:
        parser.error("workitem_id and comment_file are required")
    if args.mode == "already-fixed" and not args.fix_commit:
        parser.error("--fix-commit is required for already-fixed")

    body = args.comment_file.read_text(encoding="utf-8").strip()
    if not body:
        raise SystemExit("comment file is empty")
    check_landing(args)

    item = projex("get", args.workitem_id)
    key, current = item["serialNumber"], item["status"]["name"]
    if args.mode == "repair":
        check_trailer(args.fix_branch, args.acceptance_branch, key)
    existing = comment_bodies(args.workitem_id)
    post = body not in existing
    earlier = current not in LATER_THAN_DONE
    set_done = args.mode != "conclusion" and current != DONE and earlier
    set_fixed = args.mode == "already-fixed" and earlier
    print(f"{key}: landing ok; status {current}; post comment: {post}; set {DONE}: {set_done}; set {FIXED}: {set_fixed}")
    if args.dry_run:
        return

    if post:
        projex("comment", args.workitem_id, "--body-file", str(args.comment_file))
    if set_done:
        projex("status", args.workitem_id, "--status-id", status_id(args.workitem_id, DONE))
    if set_fixed:
        projex("status", args.workitem_id, "--status-id", status_id(args.workitem_id, FIXED))
    expected = FIXED if set_fixed else DONE if set_done else current
    after = projex("get", args.workitem_id)["status"]["name"]
    commented = body in comment_bodies(args.workitem_id)
    print(f"{key}: status {after}; comment present: {commented}")
    if after != expected or not commented:
        raise SystemExit(f"{key}: read-back mismatch, expected status {expected} and the comment present")


if __name__ == "__main__":
    main()
