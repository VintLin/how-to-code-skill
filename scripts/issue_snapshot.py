#!/usr/bin/env python3
import argparse
import json
import re
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


def run_json_optional(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return []
    try:
        return json.loads(p.stdout)
    except Exception:
        return []


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


def fetch_issue_comments(repo, issue_num):
    owner, name = repo.split("/", 1)
    cmd = [
        "gh", "api", f"/repos/{owner}/{name}/issues/{issue_num}/comments",
        "--jq", "[.[] | {body: .body, user: .user.login, createdAt: .createdAt}]",
    ]
    return run_json_optional(cmd)


def parse_body_refs(body):
    if not body:
        return []
    refs = re.findall(r"(?:Fixes?|Refs?|Related to?|Closes?)\s*#(\d+)|#(\d+)", body, re.I)
    return list({int(n) for g in refs for n in g if n})


def repro_sections_hint(body):
    if not body:
        return False
    low = body.lower()
    keywords = ["step", "reproduce", "expected", "observed", "actual", "behavior", "repro"]
    return any(k in low for k in keywords)


def suggest_action(issue, related_candidates, repro_hint):
    state = (issue.get("state") or "").upper()
    if state != "OPEN":
        return "skip", "Issue is not open."
    assignees = issue.get("assignees") or []
    if assignees:
        return "ask-maintainer", "Issue has assignees; confirm with maintainer before implementing."
    closed_dupes = [r for r in related_candidates if (r.get("state") or "").upper() == "CLOSED"]
    if closed_dupes:
        return "skip", "Closed related issue(s) may be duplicate; verify before proceeding."
    if repro_hint:
        return "implement", "Open, no assignees, repro-like sections present; implement after confirm."
    return "analyze", "Needs analysis (repro clarity, scope) before recommend implement/ask-maintainer/skip."


def md_report(data):
    lines = []
    issue = data["issue"]
    lines.append(f"# Issue Snapshot #{issue.get('number')}")
    lines.append("")
    lines.append("## Current status")
    lines.append(f"- Title: {issue.get('title')}")
    lines.append(f"- State: {issue.get('state')}")
    lines.append(f"- URL: {issue.get('url')}")
    lines.append(f"- Updated: {issue.get('updatedAt')}")
    lines.append(f"- Labels: {', '.join([x.get('name','') for x in issue.get('labels',[])]) or 'NONE'}")
    lines.append(f"- Assignees: {', '.join([x.get('login','') for x in issue.get('assignees',[])]) or 'NONE'}")
    lines.append("")
    lines.append("## Repro clarity assessment")
    lines.append(f"- Repro-like sections in body: {data.get('repro_sections_hint', False)}")
    lines.append("")
    lines.append("## Duplicate / related references")
    lines.append("- Body refs (from #n / Fixes #n etc.): " + (", ".join(f"#{n}" for n in data.get("body_refs", [])) or "NONE"))
    if not data["related_candidates"]:
        lines.append("- Search candidates: NONE")
    else:
        for item in data["related_candidates"]:
            lines.append(f"- #{item.get('number')} [{item.get('state')}] {item.get('title')} ({item.get('url')})")
    lines.append("")
    lines.append("## Action recommendation")
    rec = data.get("recommendation", {})
    lines.append(f"- Suggested action: {rec.get('action', 'analyze')}")
    lines.append(f"- Reason: {rec.get('reason', '')}")
    lines.append("- All options: analyze | ask-maintainer | implement | skip")
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
    comment_list = fetch_issue_comments(args.repo, args.issue)
    body_refs = parse_body_refs(issue.get("body"))
    repro_hint = repro_sections_hint(issue.get("body"))
    action, reason = suggest_action(issue, related, repro_hint)

    payload = {
        "repo": args.repo,
        "issue": issue,
        "related_candidates": related,
        "comment_list": comment_list,
        "body_refs": body_refs,
        "repro_sections_hint": repro_hint,
        "recommendation": {"action": action, "reason": reason},
    }

    json_path = out_dir / f"issue_{args.issue}.json"
    md_path = out_dir / f"issue_{args.issue}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(md_report(payload), encoding="utf-8")

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
