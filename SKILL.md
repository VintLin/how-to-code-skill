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

## Script vs Manual Boundary

- **Scripts** produce structured evidence (JSON + MD) for issue/PR/OSS snapshots and issue drafts; they do not make final triage decisions or perform write actions.
- **You** (agent) must: interpret snapshot output, apply protocol rules, produce risk notes and exact next action, and run local validation (check protocol). Never run `gh pr create` / `gh issue create` or destructive git commands without explicit user authorization.
- Each reference (issue, pr, check, oss, coding) includes an **Automation coverage** table: script fields vs manual checks.

## Workflow Router

Route by scenario; each node lists **when** to use it and **what** to read/run.

1. **Issue triage / investigation**
   - **When**: User asks to triage an issue, investigate repro, assess duplicates, or recommend next action (`analyze` / `ask-maintainer` / `implement` / `skip`).
   - Read `references/issue.md`.
   - Run `scripts/preflight.py` once per environment.
   - Run `scripts/issue_snapshot.py` to capture full status.

2. **PR triage / merge readiness**
   - **When**: User asks whether a PR is ready to merge, what’s blocking it, or for review/risk notes.
   - Read `references/pr.md`.
   - Run `scripts/pr_snapshot.py` before any recommendation.

3. **Code checks / implementation validation**
   - **When**: Implementing a fix or feature, or validating before marking a task complete (lint/build/test, semantic impact, task handover checklist).
   - Read `references/check.md` and `references/coding.md`.
   - Run local validation gates before marking complete.

4. **OSS scouting / prioritization**
   - **When**: User asks to find OSS contribution opportunities, rank repos, or filter issues by impact/activity.
   - Read `references/oss.md`.
   - Run `scripts/oss_scout.py` for structured candidate ranking.

5. **Issue draft generation**
   - **When**: User needs a new issue body in standard format (Summary, Steps, Expected, Observed); align with `references/issue.md` style mimicry.
   - Use `scripts/issue_draft.py` to generate consistent markdown bodies.

## Default Output Convention

- Write outputs to `./outputs/how-to-code/` by default.
- Scripts accept `--out-dir` to override output destination; `issue_draft.py` also accepts `--out` to set the output file path directly.
- Generate both `.json` (machine-readable) and `.md` (review-ready) whenever possible (snapshot and OSS scripts; issue_draft produces `.md` only).

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
