# Issue Protocol

## Style Mimicry (Before Submitting)

Before submitting a new issue, inspect the target repo’s **closed or high-engagement issues** and align with their conventions:

- **Title format**: Match existing patterns (e.g. `[Bug]: ...`, `[Feature]: ...`).
- **Body structure**: Use the same sections (e.g. Summary, Steps, Expected, Observed/Log). Keep the issue self-explanatory without prior context.

## Required Checks

1. Collect issue snapshot via script before conclusions.
2. Confirm state, assignees, labels, milestone, and project item context.
3. Review full comments for maintainer direction changes.
4. Run duplicate search across open and closed issues.
5. Check for linked or mentioning PRs.
6. Summarize blockers, owner status, and next action.

## Output Standard

Issue review output must include:

- Current status
- Repro clarity assessment
- Duplicate/related references
- Action recommendation (`analyze`, `ask-maintainer`, `implement`, `skip`)

## Automation Coverage

| Required check | Script output (issue_snapshot.py) | Manual / agent |
|----------------|-----------------------------------|----------------|
| State, assignees, labels, milestone, project | `issue.state`, `assignees`, `labels`, `milestone`, `projectItems` in JSON | — |
| Full comments for maintainer direction | `issue.comments` in JSON (raw list) | Interpret direction; summarize blockers/next action |
| Duplicate search | `related_candidates` (search by title) | Confirm true duplicate vs related; run closed-issue search if needed |
| Linked or mentioning PRs | Not in script | Use `gh pr list` / issue body parsing |
| Repro clarity | Not in script | Read `issue.body`; assess Steps/Expected/Observed completeness |
| Action recommendation | `suggested action` in MD (only `analyze` / `ask-maintainer`) | Extend to `implement` / `skip` using full context |
