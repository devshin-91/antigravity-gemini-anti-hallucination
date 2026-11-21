"""Core data structures for tiered reference fact-checking."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["PASS", "WARN", "FAIL"]
Track = Literal["local_ref", "academic_ref", "rule_budget", "semantic_pdf"]


@dataclass(slots=True)
class Issue:
    """Single verification finding with minimal actionable fix metadata."""

    code: str
    severity: Severity
    track: Track
    file: str
    line: int | None
    target: str
    message: str
    expected: str | None = None
    actual: str | None = None
    fix_hint: str | None = None

    def to_compact_dict(self) -> dict[str, Any]:
        """Return only non-empty fields to minimize LLM context consumption."""
        data = {
            "code": self.code,
            "sev": self.severity,
            "track": self.track,
            "file": self.file,
            "target": self.target,
            "msg": self.message,
        }
        if self.line is not None:
            data["line"] = self.line
        if self.expected is not None:
            data["expected"] = self.expected
        if self.actual is not None:
            data["actual"] = self.actual
        if self.fix_hint is not None:
            data["fix"] = self.fix_hint
        return data


@dataclass(slots=True)
class ReferenceEntry:
    """Parsed bibliography entry from a markdown document."""

    index: int
    line: int
    raw: str
    authors_raw: str
    first_author_key: str
    is_korean: bool
    is_solo: bool
    year: str
    doi: str | None = None
    url: str | None = None
    title_hint: str = ""
    journal_hint: str = ""
    volume_hint: str = ""
    pages_or_article_hint: str = ""


@dataclass(slots=True)
class CitationMention:
    """Parsed in-text or table citation occurrence."""

    line: int
    raw: str
    author_key: str
    year: str
    is_et_al: bool
    style: Literal["narrative", "parenthetical", "table"]


@dataclass(slots=True)
class FileCheckSummary:
    """Aggregated verification result for a single inspected file."""

    file: str
    sha256: str
    skipped_clean: bool = False
    local_refs_checked: int = 0
    academic_refs_checked: int = 0
    intext_citations_checked: int = 0
    network_cache_hits: int = 0
    network_live_calls: int = 0
    elapsed_ms: float = 0.0
    issues: list[Issue] = field(default_factory=list)

    @property
    def fail_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "WARN")

    @property
    def status(self) -> Severity:
        if self.fail_count > 0:
            return "FAIL"
        if self.warn_count > 0:
            return "WARN"
        return "PASS"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status
        d["fail_count"] = self.fail_count
        d["warn_count"] = self.warn_count
        return d
