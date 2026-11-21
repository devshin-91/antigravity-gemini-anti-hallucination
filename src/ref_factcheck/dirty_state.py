"""SHA-256 dirty-state tracker so unchanged files are skipped in <1 ms."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any


def compute_sha256(path: Path) -> str:
    """Return full SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class DirtyStateStore:
    """Persist per-session and per-file verification hashes in JSON."""

    def __init__(self, state_path: Path) -> None:
        self.state_path = state_path
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"files": {}, "dirty_queue": []}
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                raw.setdefault("files", {})
                raw.setdefault("dirty_queue", [])
                return raw
        except Exception:
            pass
        return {"files": {}, "dirty_queue": []}

    def save(self) -> None:
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.state_path)

    def mark_dirty(self, file_path: Path, tool_name: str = "") -> None:
        key = str(file_path.resolve())
        queue: list[str] = self._data.setdefault("dirty_queue", [])
        if key not in queue:
            queue.append(key)
        entry = self._data["files"].setdefault(key, {})
        entry["last_modified_by_tool"] = tool_name
        entry["marked_dirty_at"] = time.time()
        entry["last_verified_sha256"] = None
        self.save()

    def pop_dirty_queue(self) -> list[Path]:
        queue = self._data.get("dirty_queue", [])
        paths = [Path(p) for p in queue if Path(p).exists()]
        self._data["dirty_queue"] = []
        self.save()
        return paths

    def is_clean_and_passed(self, file_path: Path, tier: int) -> tuple[bool, str]:
        resolved = str(file_path.resolve())
        current_sha = compute_sha256(file_path)
        rec = self._data.get("files", {}).get(resolved)
        if not rec:
            return False, current_sha
        if (
            rec.get("last_verified_sha256") == current_sha
            and rec.get("last_verified_tier", -1) >= tier
            and rec.get("last_status") == "PASS"
        ):
            return True, current_sha
        return False, current_sha

    def record_result(self, file_path: Path, sha256: str, tier: int, status: str) -> None:
        resolved = str(file_path.resolve())
        self._data.setdefault("files", {})[resolved] = {
            "last_verified_sha256": sha256,
            "last_verified_tier": tier,
            "last_status": status,
            "verified_at": time.time(),
        }
        self.save()
