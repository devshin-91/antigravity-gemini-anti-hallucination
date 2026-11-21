"""Package and install the self-contained ref-fact-checker plugin into ~/.gemini/config/plugins/."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SRC = REPO_ROOT / "plugins" / "ref-fact-checker"
LIB_SRC = REPO_ROOT / "src" / "ref_factcheck"
DEFAULT_DEST = Path.home() / ".gemini" / "config" / "plugins" / "ref-fact-checker"


def build_and_install(dest: Path, python_exe: str | None = None) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(PLUGIN_SRC, dest)
    bundled_lib = dest / "hooks" / "ref_factcheck"
    shutil.copytree(
        LIB_SRC,
        bundled_lib,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    # Pin the resolved Python interpreter path in installed hooks.json so desktop GUI hooks
    # work reliably even when conda/venv Python is not on the default system PATH.
    exe = (python_exe or sys.executable).replace("\\", "/")
    hooks_path = dest / "hooks.json"
    if hooks_path.exists():
        raw = hooks_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        plugin_hooks = data.get("ref-fact-checker", {})
        for event_name in ("PreInvocation", "PostInvocation", "Stop", "SessionStart"):
            for handler in plugin_hooks.get(event_name, []):
                if isinstance(handler.get("command"), str):
                    handler["command"] = handler["command"].replace("python ", f'"{exe}" ', 1)
        for event_name in ("PreToolUse", "PostToolUse"):
            for group in plugin_hooks.get(event_name, []):
                for handler in group.get("hooks", []):
                    if isinstance(handler.get("command"), str):
                        handler["command"] = handler["command"].replace("python ", f'"{exe}" ', 1)
        hooks_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Installed self-contained plugin to: {dest}")
    print(f"Pinned Python interpreter: {exe}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install ref-fact-checker plugin globally")
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--python-exe", type=str, default=None)
    args = parser.parse_args()
    build_and_install(args.dest, python_exe=args.python_exe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
