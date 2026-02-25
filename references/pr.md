# PR Protocol

## Required Checks

1. Collect PR snapshot via script before recommendations.
2. Verify mergeability and draft status.
3. Verify status checks and failing jobs.
4. Verify review decisions and unresolved review threads.
5. Verify change scope and atomicity (files + diff size).
6. Verify issue tracking linkage (`Fixes`/`Refs`).

## PR Narrative Structure (Fixed Order)

PR description must follow this 6-section order:

1. **Summary**: One sentence stating the core change.
2. **Problem**: Pain point, bug repro steps, impact scope.
3. **Changes**: Key changes (3–7 bullets; avoid long prose).
4. **Validation**: Evidence (command output, log snippets, screenshot links).
5. **Risk & Rollback**: Potential risks and rollback plan.
6. **Tracking**: Machine-readable link: `Fixes #<id>` or `Refs #<id>`. If no linked Issue: `Related: NONE (reason: ...)`.

## Volume Control

- **Scope**: 1–3 files (max 4); submit fix + tests only.
- **No scope creep**: Do not add unrelated changes or address anything beyond review feedback.

## Output Standard

PR review output must include:

- Merge readiness (`ready` / `blocked`)
- Blocking reasons
- Risk notes
- Exact next action

## Automation Coverage

| Required check | Script output (pr_snapshot.py) | Manual / agent |
|----------------|---------------------------------|----------------|
| Mergeability, draft status | `pr.mergeable`, `pr.isDraft`; blockers in MD | — |
| Status checks, failing jobs | `checks` array; failed checks added to blockers | — |
| Review decisions | `pr.reviewDecision`; CHANGES_REQUESTED → blocker | Unresolved review threads not in script; use `pr.reviews` / comments |
| Change scope, atomicity | `pr.changedFiles`, `additions`, `deletions` | Compare to protocol (1–3 files, max 4); flag scope creep |
| Issue tracking linkage | Not in script | Parse `pr.body` for `Fixes #n` / `Refs #n` |
| Merge readiness, blocking reasons | In MD: Status + Blocker list | — |
| Risk notes, exact next action | Not in script | Derive from diff scope, checks, review threads |
