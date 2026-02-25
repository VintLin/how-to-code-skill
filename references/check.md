# Check Protocol

Run the six-gate check before completion:

1. format
2. lint
3. build
4. related tests
5. regression tests
6. semantic impact check (when protocol/constants changed)

## Semantic Impact Audit

- **Constants / globals**: When changing global constants, run `rg` (or `grep`) for the literal value across the repo to avoid breaking hardcoded assertions.
- **Protocol / serialization**: For any change to protocols or message structures, include a round-trip test: API fetch → serialize → send again (closed loop).

## Rules

- Do not push fixes blindly after CI failure; reproduce locally first.
- Do not skip semantic impact checks for naming/protocol/serialization changes.
- Capture command evidence for validation sections.

## Task Handover Checklist (Must-Check Before Done)

- [ ] Duplicate check done (no duplicate Issue/PR)
- [ ] Branch cut from clean upstream/main
- [ ] Atomic scope (1–3 files, no unrelated changes)
- [ ] Local gates passed (lint/build/test)
- [ ] PR narrative matches required structure (Problem/Changes/Validation, plus Summary, Risk & Rollback, Tracking)
- [ ] Valid Fixes/Refs linkage present
- [ ] PR submitted via file-based title/body (no CLI string body)
- [ ] User explicitly authorized the write action

## Automation Coverage

No script; all items are manual. Run locally:

- **Six gates**: format / lint / build / related tests / regression tests / semantic impact (when applicable)—capture command output as evidence.
- **Semantic audit**: use `rg` for repo-wide literal constant search (or `grep` if `rg` unavailable); add round-trip tests for protocol/serialization changes.
- **Handover checklist**: tick each item before marking task done; keep evidence in PR Validation section.
