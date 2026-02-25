#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


ISSUE_FIELDS = [
    "number", "title", "state", "author", "labels", "assignees", "milestone",
    "projectItems", "createdAt", "updatedAt", "closedAt", "comments", "url", "body"
]


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return json.loads(p.stdout)


def safe_search(repo, title):
    query = title.split("\n", 1)[0][:80]
    cmd = [
        "gh", "search", "issues", "--repo", repo, "--state", "all", "--limit", "20",
        "--json", "number,title,state,url", "--search", query,
    ]
    try:
        return run_json(cmd)
    except Exception:
        return []


def md_report(data):
    lines = []
    issue = data["issue"]
    lines.append(f"# Issue Snapshot #{issue.get('number')}")
    lines.append("")
    lines.append(f"- Title: {issue.get('title')}")
    lines.append(f"- State: {issue.get('state')}")
    lines.append(f"- URL: {issue.get('url')}")
    lines.append(f"- Updated: {issue.get('updatedAt')}")
    lines.append(f"- Labels: {', '.join([x.get('name','') for x in issue.get('labels',[])]) or 'NONE'}")
    lines.append(f"- Assignees: {', '.join([x.get('login','') for x in issue.get('assignees',[])]) or 'NONE'}")
    lines.append("")
    lines.append("## Related Candidates (search)")
    if not data["related_candidates"]:
        lines.append("- NONE")
    else:
        for item in data["related_candidates"]:
            lines.append(f"- #{item.get('number')} [{item.get('state')}] {item.get('title')} ({item.get('url')})")
    lines.append("")
    lines.append("## Recommendation")
    action = "ask-maintainer" if issue.get("assignees") else "analyze"
    lines.append(f"- Suggested action: {action}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Collect complete GitHub issue triage snapshot")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--issue", required=True, type=int, help="Issue number")
    parser.add_argument("--out-dir", default="./outputs/how-to-code", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    issue = run_json([
        "gh", "issue", "view", str(args.issue), "--repo", args.repo,
        "--json", ",".join(ISSUE_FIELDS),
    ])
    related = safe_search(args.repo, issue.get("title", ""))

    payload = {
        "repo": args.repo,
        "issue": issue,
        "related_candidates": related,
    }

    json_path = out_dir / f"issue_{args.issue}.json"
    md_path = out_dir / f"issue_{args.issue}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(md_report(payload), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
