# Erasmus+ Help Wiki — a small LLM wiki with reviewed knowledge and source traceability

A personal prototype of an **AI-readable knowledge base**: short wiki pages with metadata, a retrieval step that finds the right pages, a context builder that lets an LLM answer **only from reviewed pages with citations**, and a quality checker that flags knowledge the AI should not trust yet.

**Why I built it:** at the International Office where I work, students repeatedly email the same Erasmus+ questions (durations, grants, applications). The rules come from an EU funding programme, national agencies and the university, and they change every year. I wanted to see how an LLM can answer such questions **without inventing facts** — and what governance that needs.

## How it works

```
question ──► 1. load ONE space ──► 2. keep reviewed pages ──► 3. BM25 search ──► 4. prompt with rules + sources ──► Claude
                (boundary)            (governance)               (retrieval)         (context engineering)
```

| Part | File | What it does |
|---|---|---|
| Pages | `spaces/<space>/*.md` | Markdown pages with front matter: `id`, `title`, `space`, `owner`, `status` (draft/reviewed), `last_reviewed`, `sources`, `related`, `tags` (template in `templates/`) |
| Loader | `engine/pages.py` | Parses the front matter; loads **one space at a time** |
| Retrieval | `engine/search.py` | BM25 ranking in plain Python (title and tags weighted double, domain words ignored, minimum score) |
| Context builder | `engine/ask.py` | Builds a prompt from reviewed pages only, with rules: use only these facts, cite page ids, say "The wiki does not cover this yet" otherwise. Prints the prompt, or calls the Claude API if `ANTHROPIC_API_KEY` is set |
| Quality checker | `engine/check.py` | Flags drafts, pages older than 180 days, missing labels, duplicate ids, broken links, and links that cross spaces |
| Tests | `engine/test_wiki.py` | 6 tests for the safety rules (space boundary, drafts excluded, weak matches rejected, checker catches broken/outdated pages) |

## Two spaces, one boundary
- `spaces/erasmus/` — public knowledge, published here.
- `spaces/career/` — my private job-search knowledge; excluded via `.gitignore` and never loaded when answering an Erasmus question (tested).

## Run it
```bash
python3 engine/check.py
python3 engine/ask.py erasmus "How long can my exchange last?"
python3 engine/test_wiki.py
```
No external libraries needed (Python 3.10+).

## What worked, what didn't (so far)
- **Conflicting sources:** official documents and secondary guides disagreed on grant amounts and on recent-graduate traineeships. Instead of letting the AI pick one, those pages stay `draft` with an "Open questions" section; only pages traceable to an official source are `reviewed`.
- **Weak matches:** the first search version returned an unrelated reviewed page for a grant question because both pages contained "Erasmus". Fixed by ignoring domain-wide words and adding a minimum score; the honest answer is now "The wiki does not cover this yet." (regression test added).
- **Grant amounts depend on the home country's national agency**, so a generic EU answer can be wrong for a specific student — the wiki says so explicitly instead of giving one number.
- **Limits:** keyword search misses synonyms that are not in tags (e.g. "internship" vs "traineeship" had to be added by hand). Next step: compare BM25 with embeddings.

## Next steps
- Confirm MRU / Lithuanian national-agency rules and move draft pages to `reviewed`.
- Embedding-based retrieval vs BM25 on the same test questions.
- A small set of evaluation questions with expected page ids, to measure retrieval quality.
- A review workflow: AI drafts a page from a source, a human approves it before `status: reviewed`.

---
Built in November 2026 by Sammar Gul Awan, using Claude as a pair programmer. Sources are listed on every page; wiki content is a prototype, not official advice — always confirm with your International Office.
