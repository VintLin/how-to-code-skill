#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


PR_FIELDS = [
    "number", "title", "state", "isDraft", "mergeable", "reviewDecision", "author",
    "labels", "assignees", "commits", "files", "additions", "deletions", "changedFiles",
    "statusCheckRollup", "reviews", "comments", "updatedAt", "url", "body",
]


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return json.loads(p.stdout)


def md_report(data):
    pr = data["pr"]
    blockers = []
    if pr.get("isDraft"):
        blockers.append("PR is draft")
    if str(pr.get("mergeable", "")).upper() not in ("MERGEABLE", "UNKNOWN"):
        blockers.append(f"mergeable={pr.get('mergeable')}")
    if pr.get("reviewDecision") in ("CHANGES_REQUESTED",):
        blockers.append("changes requested by reviewers")

    lines = [
        f"# PR Snapshot #{pr.get('number')}",
        "",
        f"- Title: {pr.get('title')}",
        f"- State: {pr.get('state')}",
        f"- URL: {pr.get('url')}",
        f"- Draft: {pr.get('isDraft')}",
        f"- Mergeable: {pr.get('mergeable')}",
        f"- Review Decision: {pr.get('reviewDecision')}",
        f"- Changed Files: {pr.get('changedFiles')}",
        f"- Diff Stats: +{pr.get('additions')} / -{pr.get('deletions')}",
        "",
        "## Checks",
    ]

    checks = data.get("checks", [])
    if not checks:
        lines.append("- No checks returned")
    else:
        for c in checks:
            lines.append(f"- {c.get('name','(unnamed)')}: {c.get('state')} ({c.get('link','')})")
            if str(c.get("state", "")).lower() in ("fail", "failure", "error", "cancelled"):
                blockers.append(f"failed check: {c.get('name','(unnamed)')}")

    lines.extend(["", "## Merge Readiness", f"- Status: {'blocked' if blockers else 'ready'}"])
    if blockers:
        for b in blockers:
            lines.append(f"- Blocker: {b}")
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

    payload = {"repo": args.repo, "pr": pr, "checks": checks}

    json_path = out_dir / f"pr_{args.pr}.json"
    md_path = out_dir / f"pr_{args.pr}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(md_report(payload), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
