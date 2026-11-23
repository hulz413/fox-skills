"""Checks that run-vitest.sh caps workers and passes the caller's arguments through, using a fake npx."""

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run-vitest.sh"


class RunVitestTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        fake_npx = Path(directory.name) / "npx"
        fake_npx.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@"\n')
        fake_npx.chmod(fake_npx.stat().st_mode | stat.S_IEXEC)
        self.bin = directory.name

    def run_script(self, *args: str, **env: str) -> list[str]:
        base_env = {key: value for key, value in os.environ.items() if key != "RUN_VITEST_MAX_WORKERS"}
        full_env = {**base_env, "PATH": f"{self.bin}:{os.environ['PATH']}", **env}
        result = subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=full_env, check=True)
        return result.stdout.splitlines()

    def test_defaults_to_half_the_cores_and_passes_arguments_through(self) -> None:
        self.assertEqual(
            self.run_script("tests/stores", "-t", "login fails"),
            ["--no-install", "vitest", "run", "--maxWorkers=50%", "tests/stores", "-t", "login fails"],
        )

    def test_environment_variable_overrides_the_cap(self) -> None:
        self.assertIn("--maxWorkers=33%", self.run_script(RUN_VITEST_MAX_WORKERS="33%"))

    def test_empty_environment_variable_falls_back_to_the_default(self) -> None:
        self.assertIn("--maxWorkers=50%", self.run_script(RUN_VITEST_MAX_WORKERS=""))


if __name__ == "__main__":
    unittest.main()
