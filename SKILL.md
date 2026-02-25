---
name: how-to-code
description: "Unified coding governance workflow for GitHub and OSS delivery. Use when handling issue triage, PR review, code checks, implementation planning, or OSS scouting. Includes cross-platform scripts (Python + gh) to collect complete issue/PR status, generate standardized issue drafts, and rank OSS opportunities with explicit quality gates."
---

# How to Code

Use this skill as a single operational system for: issue, pr, check, coding, and oss workflows.

## Core Rules

- Keep changes atomic and acceptance-criteria driven.
- Prefer analysis quality over diff volume.
- Never skip structured status collection for issue/PR triage.
- Never run GitHub write actions without explicit user authorization.
- Keep all paths configurable; avoid machine-specific defaults.

## Workflow Router

1. **Issue triage / investigation**
   - Read `references/issue.md`.
   - Run `scripts/preflight.py` once per environment.
   - Run `scripts/issue_snapshot.py` to capture full status.

2. **PR triage / merge readiness**
   - Read `references/pr.md`.
   - Run `scripts/pr_snapshot.py` before any recommendation.

3. **Code checks / implementation validation**
   - Read `references/check.md` and `references/coding.md`.
   - Run local validation gates before marking complete.

4. **OSS scouting / prioritization**
   - Read `references/oss.md`.
   - Run `scripts/oss_scout.py` for structured candidate ranking.

5. **Issue draft generation**
   - Use `scripts/issue_draft.py` to generate consistent markdown bodies.

## Default Output Convention

- Write outputs to `./outputs/how-to-code/` by default.
- Accept `--out-dir` to override output destination.
- Generate both `.json` (machine-readable) and `.md` (review-ready) whenever possible.

## Scripts

- `scripts/preflight.py`: check required tools and versions.
- `scripts/issue_snapshot.py`: collect complete issue status and related context.
- `scripts/pr_snapshot.py`: collect complete PR status and blockers.
- `scripts/oss_scout.py`: rank OSS opportunities with explicit filters.
- `scripts/issue_draft.py`: render standardized issue markdown from structured input.

## References

- `references/commands-cheatsheet.md`: high-signal `gh` command catalog.
- `references/issue.md`: issue triage protocol.
- `references/pr.md`: pr triage protocol.
- `references/check.md`: validation and quality gate protocol.
- `references/coding.md`: implementation behavior protocol.
- `references/oss.md`: oss scouting and contribution protocol.
