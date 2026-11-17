# test_wiki.py - automatic tests that prove the wiki's safety rules work
#
# Usage: python3 engine/test_wiki.py

from datetime import date

from ask import build_context
from check import check
from pages import load_space


def test_boundary_erasmus_never_sees_career():
    prompt, hits, _ = build_context("automation story power query interview", "erasmus", include_drafts=True)
    assert all(p["space"] == "erasmus" for _, p in hits)
    assert "career-" not in prompt


def test_drafts_are_excluded_by_default():
    _, hits, skipped = build_context("How much is the Erasmus grant per month?", "erasmus")
    assert "erasmus-grant-basics" in skipped
    assert all(p["status"] == "reviewed" for _, p in hits)


def test_unknown_question_finds_nothing():
    _, hits, _ = build_context("What is the canteen menu on Friday?", "erasmus")
    assert hits == []


def test_weak_match_is_not_returned():
    # Only a draft page covers grants, so the reviewed duration page must NOT be returned
    _, hits, _ = build_context("How much is the Erasmus grant per month?", "erasmus")
    assert hits == []


def test_checker_catches_broken_link_and_outdated_page():
    fake = [{"id": "a", "title": "A", "space": "erasmus", "owner": "x", "status": "reviewed",
             "last_reviewed": "2025-01-01", "sources": ["s"], "related": ["missing-page"],
             "file": "spaces/erasmus/a.md"}]
    msgs = [m for _, m in check(fake, today=date(2026, 11, 18))]
    assert any("broken link" in m for m in msgs)
    assert any("outdated" in m for m in msgs)


def test_every_page_has_a_source():
    for space in ("erasmus", "career"):
        for p in load_space(space):
            assert p.get("sources"), p["id"]


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS  {t.__name__}")
    print(f"\nAll {len(tests)} tests passed.")
