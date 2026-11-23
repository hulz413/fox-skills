# QA test cases

Section 4 of [SKILL.md](../SKILL.md), for runs that include QA test cases.

1. Dispatch one case runner with the general guide's [runner assignment](../../fox-fix-issue/sources/general.md#runner-assignment): the case source, the acceptance workspace, slot, and lock, and the instruction to read that guide and the fix skill directly by absolute path. Pick its model and effort as for any task.
2. From its report, keep the code defects as issues for triage.
3. List the other classes (case wrong, environment or data, disputed expectation) in the plan with their evidence. Arrange for a worker to fix authorized, in-scope environment problems, and forward disputed expectations to the user.
4. Track each unfinished case step until it is tested or has a specific blocker; continue independent steps while waiting.
5. Write to the case source only within the user-authorized target and scope.
