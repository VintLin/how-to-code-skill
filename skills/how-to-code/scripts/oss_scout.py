#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    return json.loads(p.stdout)


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def score_repo(r, now):
    stars = r.get("stargazerCount", 0) or 0
    updated = parse_ts(r.get("updatedAt"))
    age_days = (now - updated).days if updated else 9999
    score = 0
    if 1000 <= stars <= 20000:
        score += 3
    elif stars > 200:
        score += 1
    if age_days <= 7:
        score += 3
    elif age_days <= 30:
        score += 2
    elif age_days <= 90:
        score += 1
    score += min(stars // 5000, 3)
    return score


def main():
    parser = argparse.ArgumentParser(description="Scout and rank OSS repository candidates")
    parser.add_argument("--query", default="language:typescript", help="GitHub search query")
    parser.add_argument("--limit", type=int, default=30, help="Max repositories")
    parser.add_argument("--out-dir", default="./outputs/how-to-code", help="Output directory")
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
    for r in repos:
        ranked.append({
            **r,
            "score": score_repo(r, now),
        })
    ranked.sort(key=lambda x: x.get("score", 0), reverse=True)

    payload = {
        "query": args.query,
        "generatedAt": now.isoformat(),
        "candidates": ranked,
    }

    json_path = out_dir / "oss_candidates.json"
    md_path = out_dir / "oss_candidates.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = ["# OSS Candidates", "", f"- Query: `{args.query}`", ""]
    for i, c in enumerate(ranked[:20], start=1):
        lines.append(
            f"{i}. **{c.get('nameWithOwner')}** | score={c.get('score')} | stars={c.get('stargazerCount')} | updated={c.get('updatedAt')} | {c.get('url')}"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(str(json_path))
    print(str(md_path))


if __name__ == "__main__":
    main()
