#!/usr/bin/env bash
# Runs `vitest run` with a capped worker count, so several worktrees can test at once
# without every run opening about one worker per core and exhausting memory.
#
#   run-vitest.sh [vitest run arguments...]      (run from the package that owns vitest)
#
# The cap is 50% of the logical cores unless RUN_VITEST_MAX_WORKERS says otherwise (a number
# or "N%"). Set it through the variable, not through a second --maxWorkers argument, which
# vitest rejects. The variable is not called VITEST_MAX_WORKERS because vitest 4 and 5 read
# that name themselves and parse "N%" as N workers.
# A percentage was checked on vitest 3.2.7 and 4.1; older versions may reject it, so give
# the variable a plain number there.
# The cap does nothing when the project's vitest config sets poolOptions.*.maxForks or
# maxThreads (or VITEST_MAX_FORKS / VITEST_MAX_THREADS is set): vitest uses those first.
# 50% is an estimate: 1 run uses half the cores, 2 runs use all of them, 3 runs
# oversubscribe 1.5x. Lower it when the machine slows down under 3 or more parallel runs.
# --no-install makes a directory without vitest fail instead of downloading it.
set -euo pipefail

exec npx --no-install vitest run --maxWorkers="${RUN_VITEST_MAX_WORKERS:-50%}" "$@"
