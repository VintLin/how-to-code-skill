# Coding Protocol

## Branch Isolation (Strict)

Each new task must start from a clean default branch. Prefer the **safe variant** unless you need a hard reset.

**Safe variant** (recommended when unsure; preserves local changes on main by requiring a clean working tree):

```bash
git checkout main && git fetch upstream && git merge --ff-only upstream/main && git checkout -b <branch-name>
```

If working tree is dirty, stash or commit first. If upstream has diverged (non-fast-forward), resolve before creating the branch.

**Hard reset variant** (destructive; use only when you intend to discard all local commits and untracked files on main):

```bash
git checkout main && git fetch upstream && git reset --hard upstream/main && git clean -fd && git checkout -b <branch-name>
```

Ensure `upstream` is correct and you have no uncommitted work you need before running.

When upstream has moved and you need to update your feature branch: **use `git merge` only**. Do **not** rebase or force-push on a branch that already has an open PR (unless the maintainer explicitly asks), so review history stays intact.

## Execution Behavior

1. Plan first for non-trivial tasks.
2. Re-plan immediately if assumptions fail.
3. Keep scope minimal and acceptance-criteria aligned.
4. Validate before declaring done.
5. Prefer elegant, maintainable fixes over patchy hacks.

## Subagent Strategy

- Use subagents to keep the main context clean.
- Offload research, exploration, and parallel analysis to subagents.
- For complex problems, use more subagents for focused execution; one tack per subagent.

## Autonomous Bug Fixing

- When given a bug report: fix it directly; avoid asking for hand-holding.
- Point at logs, errors, failing tests—then resolve them.
- Fix failing CI tests without being told how; reproduce locally first if needed.

## Safety Rules

- Never add unrelated refactor in a fix PR.
- Never claim completion without evidence.
- Escalate ambiguity instead of guessing.

## Automation Coverage

No script. Branch isolation and execution are manual. The branch reset command (`git reset --hard upstream/main`, `git clean -fd`) is destructive; ensure `upstream` is correct and uncommitted work is saved or stashed before running. Prefer a safe variant when unsure (e.g. fetch + merge instead of reset).
