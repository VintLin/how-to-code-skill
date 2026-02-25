# PR Protocol

## Required Checks

1. Collect PR snapshot via script before recommendations.
2. Verify mergeability and draft status.
3. Verify status checks and failing jobs.
4. Verify review decisions and unresolved review threads.
5. Verify change scope and atomicity (files + diff size).
6. Verify issue tracking linkage (`Fixes`/`Refs`).

## Output Standard

PR review output must include:

- Merge readiness (`ready` / `blocked`)
- Blocking reasons
- Risk notes
- Exact next action
