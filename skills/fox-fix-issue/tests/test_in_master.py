"""Checks of the merged-in-master decision against real squash, cherry-pick, and later-edit histories."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import in_master


class InMasterTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.repo)
        self.git("init", "-q", "-b", "master")
        self.commit("a.txt", "one\ntwo\nthree\n", "chore: base")
        self.git("checkout", "-q", "-b", "feature")
        self.commit("a.txt", "one\nTWO\nthree\n", "fix: first", "Bug: FISN-1")
        self.first = self.head()
        self.commit("b.txt", "new\n", "fix: second", "Bug: FISN-1")
        self.second = self.head()
        self.git("checkout", "-q", "master")

    def git(self, *args: str) -> str:
        identity = ["-c", "user.name=test", "-c", "user.email=test@example.invalid"]
        return subprocess.run(["git", *identity, *args], check=True, capture_output=True, text=True).stdout

    def head(self) -> str:
        return self.git("rev-parse", "HEAD").strip()

    def commit(self, name: str, content: str, subject: str, trailer: str = "") -> None:
        (self.repo / name).write_text(content, encoding="utf-8")
        self.git("add", name)
        self.git("commit", "-q", "-m", subject + (f"\n\n{trailer}" if trailer else ""))

    def squash(self) -> None:
        self.git("-c", "merge.ff=true", "merge", "--squash", "feature")
        self.git("commit", "-q", "-m", "feat: squashed\n\nBug: FISN-1")

    def test_unmerged_change_is_undetermined(self) -> None:
        self.assertIsNone(in_master.merged_in_master(self.second, "master"))

    def test_squash_merge_is_recognized_although_no_hash_matches(self) -> None:
        self.squash()
        self.assertNotEqual(self.git("branch", "--contains", self.second, "--list", "master").strip(), "master")
        self.assertEqual(in_master.merged_in_master(self.second, "master"), "content-present")

    def test_cherry_pick_and_plain_merge(self) -> None:
        self.git("cherry-pick", self.second)
        self.assertEqual(in_master.merged_in_master(self.second, "master"), "patch-equivalent")
        self.git("merge", "-q", "--no-ff", "-m", "merge", "feature")
        self.assertEqual(in_master.merged_in_master(self.first, "master"), "ancestor")

    def test_a_later_edit_of_the_same_lines_is_undetermined_but_the_trailer_locates_the_squash(self) -> None:
        self.squash()
        self.commit("a.txt", "one\nTWO changed again\nthree\n", "fix: someone else edits it")
        self.assertIsNone(in_master.merged_in_master(self.first, "master"))
        self.assertTrue(any("feat: squashed" in line for line in in_master.trailer_hints("FISN-1", "master")))

    def merge_feature(self) -> None:
        self.git("merge", "-q", "--no-ff", "-m", "merge feature", "feature")

    def append_and_revert(self) -> None:
        self.commit("a.txt", "one\nTWO\nthree\nfour\n", "chore: unrelated append")
        self.git("revert", "--no-edit", "HEAD")

    def cli(self, commit: str) -> tuple[int, str]:
        argv = ["in_master.py", commit, "--master", "master"]
        with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()) as out:
            return in_master.main(), out.getvalue()

    def test_reverting_the_merge_makes_the_change_absent_and_undetermined(self) -> None:
        self.merge_feature()
        self.assertEqual(in_master.effect_in_master(self.first, "master"), "present")
        self.git("revert", "-m", "1", "--no-edit", "HEAD")
        self.assertEqual(in_master.merged_in_master(self.first, "master"), "ancestor")
        self.assertEqual(in_master.effect_in_master(self.first, "master"), "absent")
        code, output = self.cli(self.first)
        self.assertEqual(code, 1)
        self.assertIn("no longer there", output)

    def test_an_unrelated_revert_on_the_same_file_does_not_block_a_merged_change(self) -> None:
        self.merge_feature()
        self.append_and_revert()
        self.assertEqual(len(in_master.possible_reverts(self.first, "master")), 1)
        self.assertEqual(self.cli(self.first)[0], 0)

    def test_later_edits_hide_the_effect_so_only_a_revert_hint_blocks(self) -> None:
        self.merge_feature()
        self.commit("a.txt", "one\nTWO changed again\nthree\n", "fix: someone else edits it")
        self.assertEqual(in_master.effect_in_master(self.first, "master"), "unknown")
        self.assertEqual(self.cli(self.first)[0], 0)
        self.commit("a.txt", "one\nTWO changed again\nthree\nfour\n", "chore: unrelated append")
        self.git("revert", "--no-edit", "HEAD")
        self.assertEqual(in_master.effect_in_master(self.first, "master"), "unknown")
        code, output = self.cli(self.first)
        self.assertEqual(code, 1)
        self.assertIn("later edits hide", output)

    def test_git_failure_is_an_error_not_an_undetermined_result(self) -> None:
        with self.assertRaisesRegex(SystemExit, "failed with exit"):
            in_master.merged_in_master(self.first, "no-such-ref")


if __name__ == "__main__":
    unittest.main()
