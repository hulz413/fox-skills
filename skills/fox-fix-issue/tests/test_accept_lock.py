"""Checks of the acceptance lock's ownership rules, in a temporary directory."""

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "accept-lock.sh"


class AcceptLockTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.lock = str(Path(directory.name) / "lock")

    def run_lock(self, command: str, *args: str) -> int:
        return subprocess.run(["bash", str(SCRIPT), command, self.lock, *args], capture_output=True).returncode

    def test_only_the_owner_holds_and_releases_the_lock(self) -> None:
        self.assertEqual(self.run_lock("acquire", "FISN-1"), 0)
        self.assertEqual(self.run_lock("held", "FISN-1"), 0)
        self.assertEqual(self.run_lock("held", "FISN-2"), 5)
        self.assertEqual(self.run_lock("acquire", "FISN-2", "0"), 3)
        self.assertEqual(self.run_lock("release", "FISN-2"), 4)
        self.assertEqual(self.run_lock("held", "FISN-1"), 0)
        self.assertEqual(self.run_lock("release", "FISN-1"), 0)
        self.assertEqual(self.run_lock("acquire", "FISN-2", "0"), 0)

    def test_acquiring_a_lock_already_held_by_the_same_owner_returns_at_once(self) -> None:
        self.assertEqual(self.run_lock("acquire", "FISN-1"), 0)
        self.assertEqual(self.run_lock("acquire", "FISN-1", "0"), 0)
        self.assertEqual(self.run_lock("held", "FISN-1"), 0)


if __name__ == "__main__":
    unittest.main()
