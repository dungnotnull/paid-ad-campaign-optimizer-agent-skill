"""SECOND-KNOWLEDGE-BRAIN.md reader.

Parses the knowledge-brain markdown into a structured object the harness can
use to (a) confirm benchmark currency and (b) surface recent findings to the
report's Sources & Currency section. Accepts both em-dash and ' - ' entry
separators so entries written by tools/knowledge_updater.py (which uses ' - ')
and hand-authored entries (which use em-dash) both parse.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from datetime import date

DEFAULT_BRAIN_PATH = Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"
SEP = r"(?:\u2014|\s-\s)"
ENTRY_RE = re.compile(
    r"-\s*\[(?P<date>\d{4}-\d{2}-\d{2})\]\s*(?P<title>.+?)\s*" + SEP +
    r"\s*(?P<source>.+?)\s*" + SEP +
    r"\s*(?P<url>\S+)(?:\s*<!--h:(?P<hash>[0-9a-f]+)-->)?"
)


@dataclass
class BrainEntry:
    date: str
    title: str
    source: str
    url: str
    hash: str = ""


@dataclass
class KnowledgeBrain:
    path: Path
    entries: list[BrainEntry] = field(default_factory=list)
    raw: str = ""

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def latest_date(self) -> str:
        dates = sorted(e.date for e in self.entries if e.date)
        return dates[-1] if dates else ""

    def is_stale(self, max_age_days: int = 60, today: str | None = None) -> bool:
        if not self.latest_date:
            return True
        today = today or date.today().isoformat()
        try:
            d0 = date.fromisoformat(self.latest_date)
            d1 = date.fromisoformat(today)
        except ValueError:
            return True
        return (d1 - d0).days > max_age_days


def load_brain(path: Path | None = None) -> KnowledgeBrain:
    p = path or DEFAULT_BRAIN_PATH
    kb = KnowledgeBrain(path=p)
    if not p.exists():
        return kb
    kb.raw = p.read_text(encoding="utf-8")
    for line in kb.raw.splitlines():
        m = ENTRY_RE.search(line)
        if not m:
            continue
        kb.entries.append(BrainEntry(
            date=m.group("date"),
            title=m.group("title").strip(),
            source=m.group("source").strip(),
            url=m.group("url").strip(),
            hash=m.group("hash") or "",
        ))
    return kb
