# Optional live cooperation checks

Use these scenarios when a handoff or coordination change needs actual execution evidence. Select only affected scenarios; this is not a fixed pipeline, agent count, or per-invocation requirement. Preview decisions alone do not satisfy these checks.

## Isolated setup

Use a temporary directory and synthetic inputs. Assign each mutable artifact one owner; permit writes only inside that directory. Use current runtime limits and the skill's normal routing rules. Keep expected outcomes with the coordinator, and give participants only the task, contract and raw evidence needed for their work. No external messages, production resources or deployments are needed.

### Missing upstream evidence

Task: combine two supplied item records with upstream unit prices to produce a total, record count and total quantity. The records have fields sku and quantity: (A, 2) and (B, 1). The price evidence has fields sku and unit_price and initially contains only (A, 10). An upstream participant must report the missing B price rather than invent it. The downstream participant may produce the count summary while the total remains pending. After the blocker is reported, supply the unit price (B, 7) to the upstream owner and resume the dependent work.

Check actual artifacts and messages: the blocker names the missing input, attempts/results, reusable partial output and needed decision; no repeated lookup against unchanged evidence occurs. The final record count is 2, total quantity is 3, and total amount is 27, supported by the supplied unit prices. Completion and verification are distinguished at handoff.

### Individually valid, incompatible outputs

Task: two workers independently summarize supplied synthetic invoices. One source states an amount of 10 in USD and the other 20 in EUR; each worker must preserve the source currency in its owned output. Ask the coordinator to integrate the summaries without providing an exchange rate.

Check that both artifacts are retained and the coordinator delivers separate currency subtotals, or reports the rate/date required if a single converted total is explicitly required. A bare combined total of 30 fails. No worker edits another owner's artifact to hide the inconsistency.

### Repair and independent recheck

Task: prepare an isolated synthetic draft summary stating that three supplied amounts (10, 20, 30) total 50. Assign its repairs to a worker, and first ask an independent reviewer to assess the draft against those raw amounts. Let the coordinator route any confirmed finding to the worker, then return the repaired artifact to the reviewer.

Check that a real finding identifies the arithmetic defect and impact, the assigned owner repairs it, and the independent reviewer checks the updated artifact against the raw inputs. The coordinator accepts only after closure. Report the seeded defect as a test fixture, never as a spontaneous worker failure.

### Acceptance already satisfied

Task: provide a completed two-row summary (10 + 20 = 30), its raw inputs and a valid check record for that exact unchanged artifact. Request delivery; specify that the acceptance criteria are correct rows and total and that the existing verification is sufficient.

Check that the coordinator delivers using the existing evidence without new agents or repeated tests. Changed inputs or a genuine evidence gap justify renewed checks and must be recorded explicitly.

## Evidence and cleanup

For each executed scenario, report the input/acceptance contract, actual artifacts and relevant trace, observed outcome, and pass/fail/not exercised. A written plan or claimed outcome is not an execution pass. Record model/effort only as supported by the runtime; report usage or timing only if measured. These cases do not establish general reliability or cost superiority.

Remove task-created temporary inputs and passing-run artifacts after review. Retain concise failure evidence only when needed for diagnosis, without changing user files. No extra agents or repeated runs are needed once the selected acceptance criteria are satisfied.
