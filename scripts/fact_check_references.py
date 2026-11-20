"""Automated Fact-Checker for Antigravity GEMINI.md Reference Citations."""

from pathlib import Path
import re
import sys


def verify_rule_file(rule_path: Path) -> bool:
    if not rule_path.exists():
        print(f"[FAIL] File does not exist: {rule_path}")
        return False

    text = rule_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    size_bytes = len(text.encode("utf-8"))
    within_budget = size_bytes <= 24000
    print(
        f"=== Checking {rule_path.name} ===\n"
        f"Path: {rule_path}\n"
        f"Total lines: {len(lines)}, Size: {size_bytes}/24000 bytes "
        f"({size_bytes / 24000 * 100:.1f}% of AGY 24KB limit) -> "
        f"{'PASS' if within_budget else 'FAIL (Over 24KB)'}"
    )

    pattern = re.compile(
        r"\[([^\]]+)\]\(file:///([^#)]+)(?:#L(\d+)(?:-L(\d+))?)?\)"
    )
    matches = pattern.findall(text)
    print(f"Found {len(matches)} file:/// references:")

    all_ok = within_budget
    for idx, (label, raw_path, l_start, l_end) in enumerate(matches, 1):
        p = Path(raw_path)
        if not p.exists():
            print(f"  [{idx}] FAIL (Missing file): {label} -> {p}")
            all_ok = False
            continue
        f_lines = p.read_text(encoding="utf-8").splitlines()
        tot = len(f_lines)
        if l_start:
            s = int(l_start)
            e = int(l_end) if l_end else s
            valid = 1 <= s <= e <= tot
            if not valid:
                all_ok = False
            snippet = " | ".join(
                line.strip() for line in f_lines[s - 1 : min(s + 2, e)] if line.strip()
            )[:85]
            print(
                f'  [{idx}] {"PASS" if valid else "FAIL"}: '
                f'{p.name}#L{s}-L{e} (total={tot} lines) -> "{snippet}..."'
            )
        else:
            print(f"  [{idx}] PASS: {p.name} (total={tot} lines)")
    print()
    return all_ok


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    targets = [
        repo_root / "rules" / "GEMINI.ko.md",
        repo_root / "rules" / "GEMINI.en.md",
        Path(r"C:\Users\ckstn\.gemini\config\GEMINI.md"),
    ]
    overall = True
    for t in targets:
        if t.exists():
            if not verify_rule_file(t):
                overall = False
        else:
            print(f"[WARN] Optional target not found: {t}")
    print("OVERALL REFERENCE FACT-CHECK:", "100% PASSED" if overall else "FAILED")
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
