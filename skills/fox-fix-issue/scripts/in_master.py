#!/usr/bin/env python3
"""Decide whether a fix commit's change is in origin/master, squash merges included.

A missing hash proves nothing: squash merges, rebases, and cherry-picks give the change a new
hash. The change counts as merged when any of these holds, tried in order:

  ancestor           the commit is an ancestor of master
  patch-equivalent   master has a commit with the same patch (git cherry)
  content-present    merging the commit onto master changes nothing, which covers squash merges

A change found by hash (ancestor, patch-equivalent) may since have been reverted or reworked, so
its current effect is probed with two merges that touch no files: merging the commit onto master
changes nothing when its change is still there, and merging its reverse changes nothing when the
change is gone. Only when later edits of the same lines make both merges conflict is the effect
unknown; then a master commit after the fix branched off, titled `Revert "..."` or saying
`This reverts commit`, that touches the fix's files turns the result into undetermined.

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


def merge_tree(base: str, ours: str, theirs: str) -> str | None:
    """The tree of a clean three-way merge, or None when it conflicts."""
    merge = git("merge-tree", "--write-tree", "--merge-base", base, ours, theirs, ok=(0, 1))
    return merge.stdout.split("\n", 1)[0] if merge.returncode == 0 else None


def merged_in_master(commit: str, master: str = "origin/master") -> str | None:
    """Return the method that shows the change is in master, or None when undetermined."""
    if git("merge-base", "--is-ancestor", commit, master, ok=(0, 1)).returncode == 0:
        return "ancestor"
    if git("rev-parse", "--verify", "-q", f"{commit}^", ok=(0, 1)).returncode != 0:
        return None
    if git("cherry", master, commit, f"{commit}^").stdout.startswith("- "):
        return "patch-equivalent"
    if merge_tree(f"{commit}^", master, commit) == git("rev-parse", f"{master}^{{tree}}").stdout.strip():
        return "content-present"
    return None


def effect_in_master(commit: str, master: str = "origin/master") -> str:
    """Whether the change is currently in master: present, absent, or unknown."""
    if git("rev-parse", "--verify", "-q", f"{commit}^", ok=(0, 1)).returncode != 0:
        return "unknown"
    tree = git("rev-parse", f"{master}^{{tree}}").stdout.strip()
    if merge_tree(f"{commit}^", master, commit) == tree:
        return "present"
    if merge_tree(commit, master, f"{commit}^") == tree:
        return "absent"
    return "unknown"


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


def assess(commit: str, master: str = "origin/master") -> tuple[bool, list[str]]:
    """Return (merged, lines describing the result); not merged means undetermined."""
    method = merged_in_master(commit, master)
    if method is None:
        return False, [f"undetermined: {commit} is not shown to be in {master}; this does not prove it is missing"]
    if method == "content-present":
        return True, [f"merged: {method}"]
    effect = effect_in_master(commit, master)
    if effect == "absent":
        return False, [f"undetermined: {commit} is in {master} ({method}) but its change is no longer there: reverted or reworked"]
    reverts = possible_reverts(commit, master) if effect == "unknown" else []
    if reverts:
        return False, [f"undetermined: {commit} is in {master} ({method}), later edits hide whether a revert undid it:", *(f"  {line}" for line in reverts)]
    return True, [f"merged: {method}"]


def trailer_hints(key: str, master: str = "origin/master") -> list[str]:
    return git("log", master, "--grep", f"^Bug: {key}$", "--format=%h %s").stdout.splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("commit")
    parser.add_argument("--key", help="issue key whose Bug trailer locates candidate commits in master")
    parser.add_argument("--master", default="origin/master")
    args = parser.parse_args()
    merged, lines = assess(args.commit, args.master)
    print("\n".join(lines))
    if merged:
        return 0
    if args.key:
        hints = trailer_hints(args.key, args.master)
        print("\n".join(f"  {args.master} has Bug: {args.key}: {line}" for line in hints) or f"  no {args.master} commit has Bug: {args.key}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
