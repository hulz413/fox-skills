#!/usr/bin/env python3
"""Coordinator finish step for one dispatched Projex bug.

Checks the landing first and writes to Projex only when it passes:

  repair         every commit on <fix-branch> must be on <acceptance-branch>, either
                 patch-equivalent (git cherry "-") or as a commit with the same subject
                 and the same changed lines (cherry-picks that git merged automatically
                 change the patch id); then post the comment and set 开发完成.
  already-fixed  --fix-commit must be an ancestor of origin/master; then post and set 开发完成.
  conclusion     post the comment only; the status is not changed.

Run it from the target repository through a login shell so ALIYUN_YUNXIAO_TOKEN is set,
with Python 3.10+. --dry-run checks and prints the planned writes without writing.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJEX = Path(__file__).resolve().parents[2] / "fox-fix-issue" / "scripts" / "projex.py"
DONE = "开发完成"
LATER_THAN_DONE = {"已修复", "已关闭", "暂不修复", "无法重现"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def changed_lines(commit: str) -> list[str]:
    lines = git("show", "--format=", commit).splitlines()
    return [line for line in lines if line[:1] in "+-" and line[:3] not in ("+++", "---")]


def subject(commit: str) -> str:
    return git("log", "-1", "--format=%s", commit).strip()


def unlanded_commits(fix_branch: str, acceptance_branch: str) -> list[str]:
    pending = [line.split()[1] for line in git("cherry", acceptance_branch, fix_branch).splitlines() if line.startswith("+ ")]
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


def projex(*args: str) -> object:
    out = subprocess.run([sys.executable, str(PROJEX), *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out)["body"]


def status_id(workitem_id: str, name: str) -> str:
    matches = [s["id"] for s in projex("workflow", workitem_id)["statuses"] if s.get("name") == name]
    if len(matches) != 1:
        raise SystemExit(f"expected one status named {name}, found {len(matches)}")
    return matches[0]


def check_landing(args: argparse.Namespace) -> None:
    if args.mode == "repair":
        missing = unlanded_commits(args.fix_branch, args.acceptance_branch)
        if missing:
            raise SystemExit("not landed on " + args.acceptance_branch + ":\n  " + "\n  ".join(missing))
    elif args.mode == "already-fixed":
        if subprocess.run(["git", "merge-base", "--is-ancestor", args.fix_commit, "origin/master"]).returncode != 0:
            raise SystemExit(f"{args.fix_commit} is not an ancestor of origin/master")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workitem_id")
    parser.add_argument("comment_file", type=Path)
    parser.add_argument("--mode", choices=("repair", "already-fixed", "conclusion"), default="repair")
    parser.add_argument("--fix-branch", help="required for repair")
    parser.add_argument("--fix-commit", help="required for already-fixed")
    parser.add_argument("--acceptance-branch", default="bugfix/projex")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.mode == "repair" and not args.fix_branch:
        parser.error("--fix-branch is required for repair")
    if args.mode == "already-fixed" and not args.fix_commit:
        parser.error("--fix-commit is required for already-fixed")

    body = args.comment_file.read_text(encoding="utf-8").strip()
    if not body:
        raise SystemExit("comment file is empty")
    check_landing(args)

    item = projex("get", args.workitem_id)
    key, current = item["serialNumber"], item["status"]["name"]
    existing = [c.get("content", "").strip() for c in projex("comments", args.workitem_id)]
    post = body not in existing
    set_done = args.mode != "conclusion" and current != DONE and current not in LATER_THAN_DONE
    print(f"{key}: landing ok; status {current}; post comment: {post}; set {DONE}: {set_done}")
    if args.dry_run:
        return

    if post:
        projex("comment", args.workitem_id, "--body-file", str(args.comment_file))
    if set_done:
        projex("status", args.workitem_id, "--status-id", status_id(args.workitem_id, DONE))
    after = projex("get", args.workitem_id)["status"]["name"]
    count = len(projex("comments", args.workitem_id))
    print(f"{key}: status {after}; comments {count}")


if __name__ == "__main__":
    main()
