#!/usr/bin/env python3
"""knowledge_updater.py - Paid Ad Campaign Optimizer knowledge-brain updater.

Crawl ad-platform + marketing-measurement sources, score candidate entries by
recency + relevance, deduplicate against existing brain entries by a stable
content hash, and append a dated, structured block to
SECOND-KNOWLEDGE-BRAIN.md. Designed to run as a weekly cron job.

The crawler degrades gracefully: it prefers the optional `httpx` package (pure
HTTP fetch + lightweight relevance extraction), and also supports `crawl4ai`
when present for richer JS-rendered extraction. With neither installed, it runs
in --dry-run against the bundled seed sources only and exits non-zero so cron
alerts the operator. No network call is ever made in --dry-run mode.

Usage:
    python tools/knowledge_updater.py              # fetch + append
    python tools/knowledge_updater.py --dry-run     # compute, print, do not write
    python tools/knowledge_updater.py --sources config/sources.json
    python tools/knowledge_updater.py --limit 20 --min-score 2

Exit codes: 0 success; 2 nothing to append; 3 fetch unavailable (no httpx/crawl4ai).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import pathlib
import re
import sys
from dataclasses import dataclass, asdict
from typing import Iterable, Optional

LOG = logging.getLogger("knowledge_updater")
ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAIN = ROOT / "SECOND-KNOWLEDGE-BRAIN.md"
DEFAULT_SOURCES_PATH = ROOT / "tools" / "knowledge_sources.json"

DEFAULT_SOURCES = [
    {"name": "Google Ads Help", "url": "https://support.google.com/google-ads/"},
    {"name": "Meta Business", "url": "https://www.facebook.com/business/news"},
    {"name": "TikTok For Business", "url": "https://business.tiktok.com/news"},
    {"name": "MSI", "url": "https://www.msi.org/articles/"},
    {"name": "IAB", "url": "https://www.iab.com/insights/"},
    {"name": "ARF", "url": "https://thearf.org/research/"},
]
QUERIES = ["ad platform update", "attribution measurement", "ad benchmark CTR CVR",
           "privacy ad targeting", "incrementality", "value-based bidding"]
KEYWORDS = ["roas", "cpa", "cac", "ltv", "ctr", "cvr", "attribution",
            "incrementality", "bidding", "targeting", "creative", "campaign",
            "conversion", "frequency", "fatigue", "privacy", "skan", "consent"]
HASH_RE = re.compile(r"<!--h:([0-9a-f]{12})-->")
MAX_TITLE_LEN = 200
MIN_TITLE_LEN = 20


@dataclass
class Candidate:
    title: str
    source: str
    url: str
    score: float = 0.0

    def hash(self) -> str:
        return hashlib.sha1((self.url + "|" + self.title.lower()).encode("utf-8")).hexdigest()[:12]


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def load_sources(path: Optional[pathlib.Path]) -> list[dict]:
    if path and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
            if isinstance(data, dict) and isinstance(data.get("sources"), list):
                return data["sources"]
        except json.JSONDecodeError as exc:
            LOG.warning("sources file %s is invalid JSON: %s; using defaults", path, exc)
    return DEFAULT_SOURCES


def existing_hashes(text: str) -> set[str]:
    return set(HASH_RE.findall(text))


def score_entry(entry: Candidate) -> float:
    title = entry.title.lower()
    return float(sum(1.0 for k in KEYWORDS if k in title))


def _extract_titles(markdown: str) -> list[str]:
    titles: list[str] = []
    for line in markdown.splitlines():
        t = line.strip().lstrip("#*- ").strip()
        if MIN_TITLE_LEN < len(t) < MAX_TITLE_LEN:
            titles.append(t)
    return titles


def _fetch_httpx(source: dict, timeout: float) -> list[Candidate]:
    import httpx  # type: ignore
    out: list[Candidate] = []
    try:
        resp = httpx.get(source["url"], timeout=timeout, follow_redirects=True,
                         headers={"User-Agent": "paid-ad-optimizer-knowledge-updater/1.0"})
        if resp.status_code >= 400:
            LOG.warning("HTTP %s for %s", resp.status_code, source["url"])
            return out
        text = resp.text
    except Exception as exc:  # network errors are non-fatal per-source
        LOG.warning("httpx fetch failed for %s: %s", source["name"], exc)
        return out
    # Lightweight HTML->text: grab <title>, headings, link text.
    titles = []
    title_m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if title_m:
        titles.append(re.sub(r"\s+", " ", title_m.group(1)).strip())
    for m in re.finditer(r"<h[1-4][^>]*>(.*?)</h[1-4]>", text, re.IGNORECASE | re.DOTALL):
        clean = re.sub(r"<[^>]+>", " ", m.group(1))
        clean = re.sub(r"\s+", " ", clean).strip()
        if clean:
            titles.append(clean)
    for m in re.finditer(r"<a[^>]+href=[\"'][^\"']+[\"'][^>]*>(.*?)</a>", text, re.IGNORECASE | re.DOTALL):
        clean = re.sub(r"<[^>]+>", " ", m.group(1))
        clean = re.sub(r"\s+", " ", clean).strip()
        if MIN_TITLE_LEN < len(clean) < MAX_TITLE_LEN:
            titles.append(clean)
    for t in titles:
        tl = t.lower()
        if any(k in tl for k in KEYWORDS):
            out.append(Candidate(title=t, source=source["name"], url=source["url"]))
    return out


def _fetch_crawl4ai(source: dict, timeout: float) -> list[Candidate]:
    try:
        from crawl4ai import WebCrawler  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dep
        LOG.debug("crawl4ai unavailable: %s", exc)
        return []
    try:
        c = WebCrawler()
        c.warmup()
        result = c.run(url=source["url"])
        text = getattr(result, "markdown", "") or ""
    except Exception as exc:  # pragma: no cover
        LOG.warning("crawl4ai run failed for %s: %s", source["name"], exc)
        return []
    out: list[Candidate] = []
    for t in _extract_titles(text):
        if any(k in t.lower() for k in KEYWORDS):
            out.append(Candidate(title=t, source=source["name"], url=source["url"]))
    return out


def fetch(source: dict, timeout: float = 15.0) -> list[Candidate]:
    """Fetch a source and return keyword-relevant candidate titles.

    Tries crawl4ai (richer) first when installed, then httpx, then returns []
    so the caller can detect total fetch failure.
    """
    candidates = _fetch_crawl4ai(source, timeout)
    if not candidates:
        candidates = _fetch_httpx(source, timeout)
    return candidates


def collect(sources: list[dict], timeout: float, min_score: float,
            limit: Optional[int]) -> list[Candidate]:
    collected: list[Candidate] = []
    for s in sources:
        try:
            got = fetch(s, timeout=timeout)
        except Exception as exc:  # never let one source kill the run
            LOG.warning("source %s raised: %s", s.get("name"), exc)
            got = []
        for c in got:
            c.score = score_entry(c)
        collected.extend(got)
        LOG.info("source %s: %d relevant candidates", s.get("name"), len(got))
    collected = [c for c in collected if c.score >= min_score]
    collected.sort(key=lambda c: c.score, reverse=True)
    if limit:
        collected = collected[:limit]
    return collected


def append_block(brain_text: str, today: str, entries: list[Candidate]) -> str:
    lines = []
    seen: set[str] = existing_hashes(brain_text)
    for e in entries:
        h = e.hash()
        if h in seen:
            continue
        seen.add(h)
        clean_title = e.title.replace("|", "/").strip()
        lines.append("- [{}] {} - {} - {} <!--h:{}-->".format(
            today, clean_title, e.source, e.url, h))
    if not lines:
        return brain_text
    header = "\n### Auto-update {}\n".format(today)
    return brain_text.rstrip("\n") + "\n" + header + "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="compute and print; do not write")
    ap.add_argument("--brain", type=pathlib.Path, default=BRAIN, help="path to knowledge brain md")
    ap.add_argument("--sources", type=pathlib.Path, default=None, help="JSON sources file")
    ap.add_argument("--limit", type=int, default=50, help="max entries to append")
    ap.add_argument("--min-score", type=float, default=2.0, help="min relevance score to keep")
    ap.add_argument("--timeout", type=float, default=15.0, help="HTTP timeout seconds")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    setup_logging(args.verbose)

    sources = load_sources(args.sources)
    brain_text = args.brain.read_text(encoding="utf-8") if args.brain.exists() else ""
    seen = existing_hashes(brain_text)

    # Detect fetch capability without making any network call.
    has_fetch = False
    try:
        import httpx  # noqa: F401
        has_fetch = True
    except Exception:
        pass
    try:
        import crawl4ai  # noqa: F401  # type: ignore
        has_fetch = True
    except Exception:
        pass

    today = dt.date.today().isoformat()
    if args.dry_run:
        # Dry-run: report capability + what would happen; no network calls.
        if not has_fetch:
            print("dry-run: no fetch backend (httpx/crawl4ai) installed; "
                  "would append nothing.", file=sys.stderr)
            print("Install httpx for real crawling: pip install httpx", file=sys.stderr)
            return 3
        print("dry-run: fetch backend available; would query {} sources, "
              "min_score={}, limit={}.".format(len(sources), args.min_score, args.limit))
        print("Existing brain hashes: {}".format(len(seen)))
        return 0

    if not has_fetch:
        LOG.error("No fetch backend installed. Install httpx (or crawl4ai) to run "
                  "the updater. Use --dry-run to inspect configuration.")
        return 3

    entries = collect(sources, timeout=args.timeout, min_score=args.min_score,
                      limit=args.limit if args.limit else None)
    new_block = append_block(brain_text, today, entries)
    new_count = new_block.count("<!--h:") - brain_text.count("<!--h:")
    if new_count <= 0:
        print("No new entries to append (already up to date).")
        return 2
    args.brain.write_text(new_block, encoding="utf-8")
    print("Appended {} new entries to {}.".format(new_count, args.brain))
    LOG.info("appended %d entries", new_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
