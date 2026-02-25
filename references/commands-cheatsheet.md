# Commands Cheatsheet

All commands below are cross-platform assuming `gh` and `python3` are installed.

## Issue

```bash
gh issue view <id> --repo <owner/repo> --json number,title,state,author,labels,assignees,milestone,projectItems,createdAt,updatedAt,closedAt,comments,url
gh issue view <id> --repo <owner/repo> --comments
gh search issues --repo <owner/repo> --state all --limit 30 --json number,title,state,url --search "<keywords>"
```

## PR

```bash
gh pr view <id> --repo <owner/repo> --json number,title,state,isDraft,mergeable,reviewDecision,author,labels,assignees,commits,files,additions,deletions,changedFiles,statusCheckRollup,reviews,comments,updatedAt,url
gh pr checks <id> --repo <owner/repo>
gh pr diff <id> --repo <owner/repo>
```

### PR create (file-based; required)

Do **not** use `gh pr create --body "..."` (inline strings cause escaping issues). Write title and body to local Markdown files, then:

```bash
gh pr create --repo <owner/repo> --title-file <path-to-title.md> --body-file <path-to-body.md>
```

Optionally: `--base <branch>` if not default. Ensure user has explicitly authorized the write (e.g. "Proceed", "Submit") before running.

## Repo Health / OSS

```bash
gh repo view <owner/repo> --json nameWithOwner,description,stargazerCount,forkCount,pushedAt,updatedAt,url
gh search repos --limit 50 --json nameWithOwner,description,stargazerCount,forkCount,updatedAt,url -- <query>
gh issue list --repo <owner/repo> --state open --limit 50 --json number,title,labels,createdAt,updatedAt,comments,assignees,url
```

## Search (semantic impact)

For constant/global audits (check protocol), search the repo by literal value:

```bash
rg --type-add 'code:*.{ts,js,py,go,rs}' -t code '<literal-value>'
```

Prefer `rg` over `grep` for consistent behavior; use `grep -r` if `rg` is not available.

## Safety

- Use `--repo` explicitly when outside target repository.
- Use `--json` output for scripts; avoid fragile text parsing.
