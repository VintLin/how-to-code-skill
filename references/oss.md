# OSS Protocol

## Candidate Filters

Prioritize repositories with:

- Stars roughly in the 1k–20k range
- Recent activity (recent push/update)
- Healthy merge flow (avoid PR graveyards)

## Issue Priority

- P0: clearly reproducible bugs
- P1: docs/logic corrections, migration support
- P2: feature work with prior maintainer alignment

## Conflict Audit (Before Picking an Issue)

- **48h rule**: If the issue has had frequent interaction in the last 48 hours or is already **Assigned**, approach with caution—prefer issues where you are not competing for maintainer attention.

## Maintainer Confirmation (Before Implementing)

- Post root-cause analysis and design in the issue first.
- Ask explicitly for invitation before opening a PR, e.g.: *"I've reproduced this locally and have a concrete approach. Would you welcome a PR?"*
- Start implementation only after maintainer confirms.

## Contribution Sequence

1. Scout and rank candidates.
2. Reproduce issue locally.
3. Post root-cause and design direction in issue.
4. Ask for maintainer confirmation (see above); wait before implementing.
5. Implement atomic PR with validation evidence.

## Automation Coverage

| Protocol requirement | Script output (oss_scout.py) | Manual / agent |
|----------------------|------------------------------|----------------|
| Stars 1k–20k, recent activity | Score uses `stargazerCount`, `updatedAt`; 1k–20k and recency weighted | — |
| Healthy merge flow (avoid PR graveyards) | Not in script | Check repo PR merge rate / open PR age separately |
| Issue priority (P0/P1/P2) | Not in script | Classify after selecting repo/issue |
| 48h rule, Assigned caution | Not in script | When picking issue: check last 48h activity and assignees |
| Maintainer confirmation | Not in script | Must post in issue and wait before implementing |
