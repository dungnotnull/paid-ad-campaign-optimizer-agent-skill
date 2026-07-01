"""Tests for SECOND-KNOWLEDGE-BRAIN.md reader currency + the updater's pure logic."""
import pytest
from paid_ad_optimizer.knowledge import load_brain, KnowledgeBrain, DEFAULT_BRAIN_PATH
import tools.knowledge_updater as ku


def test_brain_loads_or_missing():
    kb = load_brain()
    assert isinstance(kb, KnowledgeBrain)
    # The bundled brain exists in this repo
    assert kb.exists


def test_stale_detection_when_no_entries(tmp_path):
    fake = tmp_path / "empty.md"
    fake.write_text("# brain\n", encoding="utf-8")
    kb = load_brain(fake)
    assert kb.is_stale() is True


def test_entry_hash_dedup():
    e = ku.Candidate(title="ROAS update", source="Google Ads Help",
                     url="https://x", score=3.0)
    assert len(e.hash()) == 12


def test_append_block_dedupes_existing(tmp_path):
    brain = tmp_path / "b.md"
    cand = ku.Candidate(title="ROAS update", source="Google Ads Help",
                         url="https://x", score=3.0)
    brain.write_text("- [2026-06-01] ROAS update - Google Ads Help - https://x <!--h:{}-->\n"
                     .format(cand.hash()), encoding="utf-8")
    out = ku.append_block(brain.read_text(encoding="utf-8"), "2026-06-02", [cand])
    # hash collision -> not appended
    assert out.count("<!--h:") == 1


def test_append_block_appends_new(tmp_path):
    brain = tmp_path / "b.md"
    brain.write_text("# brain\n", encoding="utf-8")
    cands = [ku.Candidate(title="New CTR benchmark study", source="IAB",
                          url="https://iab.com/x", score=3.0)]
    out = ku.append_block(brain.read_text(encoding="utf-8"), "2026-06-02", cands)
    assert "New CTR benchmark study" in out
    assert "### Auto-update 2026-06-02" in out


def test_dry_run_no_backend_exit_code(monkeypatch, tmp_path, capsys):
    # Force no fetch backend to exercise the dry-run path that returns 3.
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name in ("httpx", "crawl4ai"):
            raise ImportError("blocked in test")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    rc = ku.main(["--dry-run", "--brain", str(tmp_path / "nope.md")])
    assert rc == 3


def test_score_entry_keyword_count():
    e = ku.Candidate(title="ROAS and CPA attribution incrementality", source="x", url="y")
    assert ku.score_entry(e) >= 4.0
