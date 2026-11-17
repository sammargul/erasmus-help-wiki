# check.py - quality checker: finds pages the AI should not trust yet
#
# Usage: python3 engine/check.py

from datetime import date, datetime

from pages import load_all

MAX_AGE_DAYS = 180
REQUIRED = ["id", "title", "space", "owner", "status", "last_reviewed", "sources"]


def check(pages, today=None):
    today = today or date.today()
    ids = [p.get("id") for p in pages]
    problems = []

    for p in pages:
        pid = p.get("id", p["file"])
        for field in REQUIRED:
            if not p.get(field):
                problems.append((pid, f"missing label '{field}'"))
        if ids.count(pid) > 1:
            problems.append((pid, "duplicate id"))
        if p.get("space") and p["space"] not in p["file"]:
            problems.append((pid, "label 'space' does not match the folder it is in"))
        if p.get("status") not in ("draft", "reviewed"):
            problems.append((pid, f"unknown status '{p.get('status')}'"))
        elif p["status"] == "draft":
            problems.append((pid, "draft - excluded from AI answers until reviewed"))
        try:
            age = (today - datetime.strptime(p["last_reviewed"], "%Y-%m-%d").date()).days
            if age > MAX_AGE_DAYS:
                problems.append((pid, f"outdated - last reviewed {age} days ago"))
        except (KeyError, ValueError):
            problems.append((pid, "last_reviewed is not a valid date (YYYY-MM-DD)"))
        for rel in p.get("related", []):
            if rel not in ids:
                problems.append((pid, f"broken link -> '{rel}' does not exist"))
            else:
                other = next(q for q in pages if q.get("id") == rel)
                if other.get("space") != p.get("space"):
                    problems.append((pid, f"link crosses spaces -> '{rel}' (boundary risk)"))
    return problems


if __name__ == "__main__":
    pages = load_all()
    problems = check(pages)
    reviewed = sum(1 for p in pages if p.get("status") == "reviewed")
    print(f"Checked {len(pages)} pages: {reviewed} reviewed, {len(pages) - reviewed} draft.\n")
    for pid, msg in problems:
        print(f"  [{pid}] {msg}")
    print(f"\n{len(problems)} issue(s) found." if problems else "\nNo issues found.")
