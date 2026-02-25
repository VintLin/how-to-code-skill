#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_input(path):
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    required = ["summary", "environment", "steps", "expected", "observed", "impact", "related"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return data


def render(d):
    steps = d["steps"]
    if isinstance(steps, list):
        steps_md = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
    else:
        steps_md = str(steps)

    related = d["related"]
    if isinstance(related, list):
        related_md = "\n".join([f"- {x}" for x in related]) if related else "- Related: NONE"
    else:
        related_md = str(related)

    return f"""## Summary
{d['summary']}

## Environment
{d['environment']}

## Steps to Reproduce
{steps_md}

## Expected Behavior
{d['expected']}

## Observed Behavior
{d['observed']}

## Impact
{d['impact']}

## Related
{related_md}
"""


def main():
    parser = argparse.ArgumentParser(description="Generate standardized GitHub issue markdown from JSON input")
    parser.add_argument("--input", required=True, help="JSON input path")
    parser.add_argument("--out-dir", default="./outputs/how-to-code", help="Output directory (used if --out not set)")
    parser.add_argument("--out", help="Output file path (overrides --out-dir); default: <out-dir>/issue_draft.md")
    args = parser.parse_args()

    data = load_input(args.input)
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = Path(args.out_dir) / "issue_draft.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(data), encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    main()
