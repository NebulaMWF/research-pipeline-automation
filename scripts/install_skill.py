#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_NAME = "research-pipeline-automation"
SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = {
    "codex": Path.home() / ".codex" / "skills",
    "claude-code": Path.home() / ".claude" / "skills",
    "openclaw": Path.home() / ".openclaw" / "skills",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", required=True, choices=sorted(DEFAULT_TARGETS))
    parser.add_argument("--target-root", default="")
    parser.add_argument("--mode", choices=["symlink", "copy"], default="symlink")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_root = Path(args.target_root).expanduser().resolve() if args.target_root else DEFAULT_TARGETS[args.platform]
    target_root.mkdir(parents=True, exist_ok=True)
    target = target_root / SKILL_NAME

    if target.exists() or target.is_symlink():
        if not args.force:
            raise SystemExit(f"target exists: {target} (use --force)")
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)

    if args.mode == "symlink":
        target.symlink_to(SKILL_DIR, target_is_directory=True)
    else:
        shutil.copytree(SKILL_DIR, target)

    print(target)


if __name__ == "__main__":
    main()
