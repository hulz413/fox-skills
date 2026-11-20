"""Offline checks of the landing gate and the status decisions; temporary repositories, no API calls."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import finish_bug

ACCEPTANCE = "bugfix/verification"
FIX = "bugfix/fisn-1"


class LandingTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.repo)
        self.git("init", "-q", "-b", ACCEPTANCE)
        self.commit("base.txt", "chore: base")
        self.git("branch", FIX)

    def git(self, *args: str) -> None:
        identity = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]
        subprocess.run(["git", *identity, *args], check=True, capture_output=True)

    def commit(self, name: str, subject: str) -> None:
        (self.repo / name).write_text(subject, encoding="utf-8")
        self.git("add", name)
        self.git("commit", "-q", "-m", subject)

    def fix_commit(self) -> None:
        self.git("checkout", "-q", FIX)
        self.commit("fix.txt", "fix: repair")
        self.git("checkout", "-q", ACCEPTANCE)

    def test_fix_branch_without_commits_is_not_a_landed_repair(self) -> None:
        with self.assertRaisesRegex(SystemExit, "no commit beyond"):
            finish_bug.unlanded_commits(FIX, ACCEPTANCE)

    def test_cherry_picked_fix_is_landed_and_an_unpicked_one_is_not(self) -> None:
        self.fix_commit()
        self.commit("other.txt", "fix: another worker")
        self.assertEqual(len(finish_bug.unlanded_commits(FIX, ACCEPTANCE)), 1)
        self.git("cherry-pick", FIX)
        self.assertEqual(finish_bug.unlanded_commits(FIX, ACCEPTANCE), [])

    def test_a_failed_command_reports_its_own_error(self) -> None:
        with self.assertRaisesRegex(SystemExit, "bugfix/missing"):
            finish_bug.unlanded_commits("bugfix/missing", ACCEPTANCE)


class StatusTests(unittest.TestCase):
    def finish(self, mode: str, current: str) -> list[str]:
        """Run main against a fake Projex and return the status names it set, in order."""
        statuses = [{"id": name, "name": name} for name in (finish_bug.DONE, finish_bug.FIXED)]
        writes: list[str] = []

        def projex(command: str, *args: str) -> object:
            if command == "get":
                return {"serialNumber": "FISN-1", "status": {"name": current}}
            if command == "comments":
                return []
            if command == "workflow":
                return {"statuses": statuses}
            if command == "status":
                writes.append(args[-1])
            return None

        with tempfile.TemporaryDirectory() as directory:
            comment = Path(directory) / "comment.md"
            comment.write_text("结论", encoding="utf-8")
            argv = ["finish_bug.py", "bug-1", str(comment), "--mode", mode, "--fix-commit", "abc"]
            with (
                patch.object(sys, "argv", argv),
                patch.object(finish_bug, "projex", projex),
                patch.object(finish_bug, "check_landing"),
                redirect_stdout(io.StringIO()),
            ):
                finish_bug.main()
        return writes

    def test_already_fixed_goes_through_done_to_fixed(self) -> None:
        self.assertEqual(self.finish("already-fixed", "已选择"), [finish_bug.DONE, finish_bug.FIXED])
        self.assertEqual(self.finish("already-fixed", finish_bug.DONE), [finish_bug.FIXED])

    def test_a_later_status_is_never_moved_and_a_conclusion_changes_nothing(self) -> None:
        self.assertEqual(self.finish("already-fixed", "已关闭"), [])
        self.assertEqual(self.finish("already-fixed", finish_bug.FIXED), [])
        self.assertEqual(self.finish("conclusion", "已选择"), [])


if __name__ == "__main__":
    unittest.main()
