#!/usr/bin/env python3
"""Decide whether a fix commit's change is in origin/master, squash merges included.

A missing hash proves nothing: squash merges, rebases, and cherry-picks give the change a new
hash. The change counts as merged when any of these holds, tried in order:

  ancestor           the commit is an ancestor of master
  patch-equivalent   master has a commit with the same patch (git cherry)
  content-present    merging the commit onto master changes nothing, which covers squash merges

Even then it is reported as undetermined when a revert may have undone it: a master commit after
the fix branched off, titled `Revert "..."` or saying `This reverts commit`, that touches the
fix's files. Revert hints are deliberately broad; a human decides.

Exit 0 and "merged: <method>" when merged. Exit 1 and "undetermined" otherwise, which is not
proof that the change is missing (a later edit of the same lines makes the content check fail),
so read master's code for the reported behavior before concluding either way. Exit 2 when git
itself fails, for example git older than 2.40, which lacks `merge-tree --write-tree`.
--key lists master commits carrying the same `Bug: <key>` trailer as places to look.

This reads the local origin/master; run `git fetch origin master` first, or a fix merged since
the last fetch is reported as undetermined.
"""

from __future__ import annotations

import argparse
import subprocess


def git(*args: str, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode not in ok:
        raise SystemExit(f"git {' '.join(args)} failed with exit {result.returncode}:\n{result.stderr.strip()}")
    return result


def merged_in_master(commit: str, master: str = "origin/master") -> str | None:
    """Return the method that shows the change is in master, or None when undetermined."""
    if git("merge-base", "--is-ancestor", commit, master, ok=(0, 1)).returncode == 0:
        return "ancestor"
    if git("rev-parse", "--verify", "-q", f"{commit}^", ok=(0, 1)).returncode != 0:
        return None
    if git("cherry", master, commit, f"{commit}^").stdout.startswith("- "):
        return "patch-equivalent"
    merge = git("merge-tree", "--write-tree", "--merge-base", f"{commit}^", master, commit, ok=(0, 1))
    if merge.returncode == 0 and merge.stdout.split("\n", 1)[0] == git("rev-parse", f"{master}^{{tree}}").stdout.strip():
        return "content-present"
    return None


def possible_reverts(commit: str, master: str = "origin/master") -> list[str]:
    files = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).stdout.split("\n")
    files = [name for name in files if name]
    if not files:
        return []
    log = git(
        "log", f"{commit}..{master}", "-i", "--grep", '^Revert "', "--grep", "^This reverts commit",
        "--format=%h %s", "--", *files,
    )
    return log.stdout.splitlines()


def trailer_hints(key: str, master: str = "origin/master") -> list[str]:
    return git("log", master, "--grep", f"^Bug: {key}$", "--format=%h %s").stdout.splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("commit")
    parser.add_argument("--key", help="issue key whose Bug trailer locates candidate commits in master")
    parser.add_argument("--master", default="origin/master")
    args = parser.parse_args()
    method = merged_in_master(args.commit, args.master)
    reverts = possible_reverts(args.commit, args.master) if method else []
    if method and not reverts:
        print(f"merged: {method}")
        return 0
    if reverts:
        print(f"undetermined: {args.commit} is in {args.master} ({method}), but a revert may have undone it:")
        print("\n".join(f"  {line}" for line in reverts))
    else:
        print(f"undetermined: {args.commit} is not shown to be in {args.master}; this does not prove it is missing")
    if args.key:
        hints = trailer_hints(args.key, args.master)
        print("\n".join(f"  {args.master} has Bug: {args.key}: {line}" for line in hints) or f"  no {args.master} commit has Bug: {args.key}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
