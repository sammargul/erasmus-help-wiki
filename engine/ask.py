# ask.py - answers a question from ONE space, using reviewed pages only
#
# Usage:  python3 engine/ask.py erasmus "How long can an exchange last?"
#         add --include-drafts to see what drafts would add (never for real answers)
#
# Without an API key it prints a ready-to-paste prompt for Claude.
# With ANTHROPIC_API_KEY set, it sends the prompt to Claude and prints the answer.

import json
import os
import sys
import urllib.request

from pages import load_space
from search import search

INSTRUCTIONS = """You answer questions using ONLY the wiki pages below.
Rules:
1. Use only facts written in the pages. Do not add outside knowledge.
2. After every fact, cite the page id in square brackets, e.g. [erasmus-duration-rules].
3. If the pages do not answer the question, say exactly: "The wiki does not cover this yet."
4. If a page lists open questions related to the answer, mention them.
"""


def build_context(question, space, include_drafts=False):
    pages = load_space(space)                       # context boundary: one space only
    usable = [p for p in pages if p.get("status") == "reviewed" or include_drafts]
    skipped = [p["id"] for p in pages if p not in usable]
    hits = search(question, usable)

    blocks = []
    for score, p in hits:
        blocks.append(
            f"### Page id: {p['id']} (status: {p['status']}, last reviewed: {p['last_reviewed']})\n"
            f"Title: {p['title']}\nSources: {', '.join(p.get('sources', []))}\n\n{p['body']}"
        )
    prompt = INSTRUCTIONS + "\n\n" + "\n\n".join(blocks) + f"\n\nQuestion: {question}\n"
    return prompt, hits, skipped


def ask_claude(prompt):
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({
            "model": os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5"),
            "max_tokens": 600,
            "messages": [{"role": "user", "content": prompt}],
        }).encode(),
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["content"][0]["text"]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__ if __doc__ else "Usage: python3 engine/ask.py <space> \"<question>\"")
        sys.exit(1)
    space, question = sys.argv[1], sys.argv[2]
    prompt, hits, skipped = build_context(question, space, "--include-drafts" in sys.argv)

    print(f"Space: {space}")
    print(f"Skipped (not reviewed): {', '.join(skipped) or 'none'}")
    print("Pages found:", ", ".join(f"{p['id']} ({s})" for s, p in hits) or "none")
    if not hits:
        print("\nNo reviewed page matches this question -> the honest answer is: "
              "'The wiki does not cover this yet.'")
        sys.exit(0)

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("\n--- Claude's answer ---\n" + ask_claude(prompt))
    else:
        print("\n--- Prompt to paste into Claude ---\n" + prompt)
