# search.py - finds the most relevant pages for a question (BM25 ranking)

import math
import re
from collections import Counter

STOPWORDS = set("""a an the and or of to in on for is are be can i my me do does
how what when where who which with at by from it this that as if you your""".split())

# Words that appear on almost every page of a space add noise, not meaning
DOMAIN_WORDS = {"erasmus", "plus"}

# Pages scoring below this are treated as "no good match" instead of a weak guess
MIN_SCORE = 0.8


def words(text):
    """Turn text into a list of simple lowercase words, without filler words."""
    return [w for w in re.findall(r"[a-z0-9+]+", text.lower()) if w not in STOPWORDS and w not in DOMAIN_WORDS]


def page_words(page):
    # Title and tags count twice: they describe what the page is about
    important = page.get("title", "") + " " + page.get("tags", "")
    return words(important) * 2 + words(page.get("body", ""))


def search(question, pages, top_k=3, k1=1.5, b=0.75):
    """Score every page against the question and return the best ones."""
    docs = [page_words(p) for p in pages]
    avg_len = sum(len(d) for d in docs) / max(len(docs), 1)
    n = len(docs)
    query = words(question)

    scores = []
    for page, doc in zip(pages, docs):
        counts = Counter(doc)
        score = 0.0
        for term in query:
            df = sum(1 for d in docs if term in d)          # how many pages use this word
            if df == 0:
                continue
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))  # rare words matter more
            tf = counts[term]                                # how often this page uses it
            score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / avg_len))
        if score >= MIN_SCORE:
            scores.append((round(score, 2), page))

    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:top_k]
