#!/usr/bin/env python3
import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return json.loads(p.stdout)


def run_json_optional(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except Exception:
        return None


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def fetch_open_pr_count(repo):
    """Return open PR count for repo (owner/name). Uses search API; rate-limited."""
    q = f"repo:{repo} is:pr is:open"
    out = run_json_optional([
        "gh", "api", "search/issues", "-f", f"q={q}", "--jq", ".total_count",
    ])
    if out is not None and isinstance(out, int):
        return out
    return None


def score_repo(r, now, open_pr_count=None):
    stars = r.get("stargazerCount", 0) or 0
    updated = parse_ts(r.get("updatedAt"))
    age_days = (now - updated).days if updated else 9999
    score = 0
    score_breakdown = {}

    if 1000 <= stars <= 20000:
        score += 3
        score_breakdown["stars_range"] = 3
    elif stars > 200:
        score += 1
        score_breakdown["stars_range"] = 1
    else:
        score_breakdown["stars_range"] = 0

    if age_days <= 7:
        score += 3
        score_breakdown["recency"] = 3
    elif age_days <= 30:
        score += 2
        score_breakdown["recency"] = 2
    elif age_days <= 90:
        score += 1
        score_breakdown["recency"] = 1
    else:
        score_breakdown["recency"] = 0

    score += min(stars // 5000, 3)
    score_breakdown["stars_bonus"] = min(stars // 5000, 3)

    if open_pr_count is not None:
        if open_pr_count > 100:
            score -= 2
            score_breakdown["merge_flow"] = -2
        elif open_pr_count > 50:
            score -= 1
            score_breakdown["merge_flow"] = -1
        elif open_pr_count < 20:
            score += 1
            score_breakdown["merge_flow"] = 1
        else:
            score_breakdown["merge_flow"] = 0
    else:
        score_breakdown["merge_flow"] = None

    return score, score_breakdown


def main():
    parser = argparse.ArgumentParser(description="Scout and rank OSS repository candidates")
    parser.add_argument("--query", default="language:typescript", help="GitHub search query")
    parser.add_argument("--limit", type=int, default=30, help="Max repositories")
    parser.add_argument("--out-dir", default="./outputs/how-to-code", help="Output directory")
    parser.add_argument("--no-merge-flow", action="store_true", help="Skip open PR count fetch (faster, no merge-flow score)")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    repos = run_json([
        "gh", "search", "repos", "--limit", str(args.limit),
        "--json", "nameWithOwner,description,stargazerCount,forkCount,updatedAt,url",
        "--", args.query,
    ])

    now = datetime.now(timezone.utc)
    ranked = []
    for i, r in enumerate(repos):
        open_pr_count = None
        if not args.no_merge_flow:
            open_pr_count = fetch_open_pr_count(r.get("nameWithOwner", ""))
            if i < len(repos) - 1:
                time.sleep(0.5)
        score, breakdown = score_repo(r, now, open_pr_count)
        ranked.append({
            **r,
            "score": score,
            "score_breakdown": breakdown,
            "open_pr_count": open_pr_count,
        })
    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)

    payload = {
        "query": args.query,
        "generatedAt": now.isoformat(),
        "candidates": ranked,
        "protocol_reminder": "48h rule and maintainer confirmation apply when picking an issue; merge flow is a hint only.",
    }

    json_path = out_dir / "oss_candidates.json"
    md_path = out_dir / "oss_candidates.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# OSS Candidates",
        "",
        f"- Query: `{args.query}`",
        "- Protocol: 48h rule and maintainer confirmation required before implementing.",
        "",
    ]
    for i, c in enumerate(ranked[:20], start=1):
        open_pr = c.get("open_pr_count")
        pr_str = f" open_prs={open_pr}" if open_pr is not None else ""
        lines.append(
            f"{i}. **{c.get('nameWithOwner')}** | score={c.get('score')} | stars={c.get('stargazerCount')}{pr_str} | updated={c.get('updatedAt')} | {c.get('url')}"
        )
    lines.extend([
        "",
        "## Priority and risk",
        "- P0: clearly reproducible bugs; P1: docs/logic; P2: feature (after maintainer alignment).",
        "- Before picking an issue: check last 48h activity and assignees (48h rule); post design and ask for invitation before opening PR.",
    ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
