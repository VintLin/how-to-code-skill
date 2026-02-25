#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path


PR_FIELDS = [
    "number", "title", "state", "isDraft", "mergeable", "reviewDecision", "author",
    "labels", "assignees", "commits", "files", "additions", "deletions", "changedFiles",
    "statusCheckRollup", "reviews", "comments", "updatedAt", "url", "body",
]
MAX_FILES_SCOPE = 4


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return json.loads(p.stdout)


def run_json_optional(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return []
    try:
        return json.loads(p.stdout)
    except Exception:
        return []


def parse_tracking_linkage(body):
    if not body:
        return {"fixes": [], "refs": [], "closes": [], "summary": "Related: NONE (reason: no linkage in body)"}
    fixes = re.findall(r"Fixes?\s*#(\d+)", body, re.I)
    closes = re.findall(r"Closes?\s*#(\d+)", body, re.I)
    refs = re.findall(r"Refs?\s*#(\d+)", body, re.I)
    ids = list({int(n) for n in fixes + closes + refs})
    parts = []
    if fixes or closes:
        parts.append("Fixes " + ", ".join(f"#{n}" for n in (fixes + closes)))
    if refs:
        parts.append("Refs " + ", ".join(f"#{n}" for n in refs))
    summary = "; ".join(parts) if parts else "Related: NONE (reason: no Fixes/Refs/Closes in body)"
    return {
        "fixes": [int(x) for x in fixes],
        "closes": [int(x) for x in closes],
        "refs": [int(x) for x in refs],
        "summary": summary,
    }


def fetch_review_comments(repo, pr_num):
    owner, name = repo.split("/", 1)
    cmd = [
        "gh", "api", f"/repos/{owner}/{name}/pulls/{pr_num}/comments",
        "--paginate", "--jq", "[.[] | {id: .id, body: .body, user: .user.login, created: .created_at}]",
    ]
    return run_json_optional(cmd)


def md_report(data):
    pr = data["pr"]
    blockers = data.get("blockers", [])
    checks = data.get("checks", [])

    tracking = data.get("tracking_linkage", {})
    review_comments = data.get("review_comments", [])

    lines = [
        f"# PR Snapshot #{pr.get('number')}",
        "",
        f"- Title: {pr.get('title')}",
        f"- State: {pr.get('state')}",
        f"- URL: {pr.get('url')}",
        f"- Draft: {pr.get('isDraft')}",
        f"- Mergeable: {pr.get('mergeable')}",
        f"- Review Decision: {pr.get('reviewDecision')}",
        f"- Changed Files: {pr.get('changedFiles')} (scope limit {MAX_FILES_SCOPE})",
        f"- Diff Stats: +{pr.get('additions')} / -{pr.get('deletions')}",
        f"- Tracking: {tracking.get('summary', '')}",
        f"- Review comments (threads): {len(review_comments)}",
        "",
        "## Checks",
    ]
    if not checks:
        lines.append("- No checks returned")
    else:
        for c in checks:
            lines.append(f"- {c.get('name','(unnamed)')}: {c.get('state')} ({c.get('link','')})")

    lines.extend([
        "",
        "## Merge Readiness",
        f"- Status: {'blocked' if blockers else 'ready'}",
    ])
    if blockers:
        for b in blockers:
            lines.append(f"- Blocker: {b}")
    lines.extend([
        "",
        "## Risk notes",
        "(Agent: fill from diff scope, dependencies, and rollback plan.)",
        "",
        "## Exact next action",
        "Address blockers above then re-run snapshot; get explicit user authorization before merge."
        if blockers
        else "Ready to merge after explicit user authorization.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Collect complete GitHub PR triage snapshot")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="PR number")
    parser.add_argument("--out-dir", default="./outputs/how-to-code", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pr = run_json([
        "gh", "pr", "view", str(args.pr), "--repo", args.repo,
        "--json", ",".join(PR_FIELDS),
    ])
    checks = run_json([
        "gh", "pr", "checks", str(args.pr), "--repo", args.repo,
        "--json", "name,state,link",
    ])
    review_comments = fetch_review_comments(args.repo, args.pr)
    tracking_linkage = parse_tracking_linkage(pr.get("body"))

    blockers = []
    if pr.get("isDraft"):
        blockers.append("PR is draft")
    if str(pr.get("mergeable", "")).upper() not in ("MERGEABLE", "UNKNOWN"):
        blockers.append(f"mergeable={pr.get('mergeable')}")
    if pr.get("reviewDecision") == "CHANGES_REQUESTED":
        blockers.append("changes requested by reviewers")
    for c in checks:
        if str(c.get("state", "")).lower() in ("fail", "failure", "error", "cancelled"):
            blockers.append(f"failed check: {c.get('name','(unnamed)')}")
    if (pr.get("changedFiles") or 0) > MAX_FILES_SCOPE:
        blockers.append(f"scope creep (changed files > {MAX_FILES_SCOPE})")

    payload = {
        "repo": args.repo,
        "pr": pr,
        "checks": checks,
        "review_comments": review_comments,
        "tracking_linkage": tracking_linkage,
        "blockers": blockers,
    }

    json_path = out_dir / f"pr_{args.pr}.json"
    md_path = out_dir / f"pr_{args.pr}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(md_report(payload), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
