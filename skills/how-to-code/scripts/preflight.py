#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main():
    parser = argparse.ArgumentParser(description="Check runtime dependencies for how-to-code skill")
    parser.add_argument("--out-dir", default="./outputs/how-to-code", help="Output directory")
    args = parser.parse_args()

    tools = ["python3", "gh", "git"]
    report = {"ok": True, "tools": {}, "gh_auth": None}

    for tool in tools:
        path = shutil.which(tool)
        ok = path is not None
        report["tools"][tool] = {"ok": ok, "path": path}
        if not ok:
            report["ok"] = False

    if report["tools"].get("gh", {}).get("ok"):
        code, out, err = run(["gh", "auth", "status"])
        report["gh_auth"] = {"ok": code == 0, "stdout": out, "stderr": err}
        if code != 0:
            report["ok"] = False

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "preflight.json"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(str(out_json))
    if not report["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
