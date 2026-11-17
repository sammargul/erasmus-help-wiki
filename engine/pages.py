# pages.py - reads wiki pages and their labels (front matter)

from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parent.parent
SPACES = WIKI_ROOT / "spaces"


def read_page(path):
    """Read one wiki page and return its labels and its text."""
    text = Path(path).read_text(encoding="utf-8")

    # The labels sit between the first two '---' lines
    _, header, body = text.split("---", 2)

    labels = {}
    current_list = None
    for line in header.strip().splitlines():
        if line.startswith("  - "):              # an item in a list (sources, related)
            labels[current_list].append(line[4:].strip())
        elif line.endswith(":"):                 # a label that starts a list
            current_list = line[:-1]
            labels[current_list] = []
        else:                                    # a simple label: key: value
            key, value = line.split(":", 1)
            labels[key.strip()] = value.strip()

    labels["body"] = body.strip()
    labels["file"] = str(path)
    return labels


def load_space(space):
    """Load every page of ONE knowledge space. Other spaces are never touched."""
    folder = SPACES / space
    if not folder.is_dir():
        raise ValueError(f"Unknown space: {space}")
    return [read_page(p) for p in sorted(folder.glob("*.md"))]


def load_all():
    """Load every page of every space (used only by the quality checker)."""
    pages = []
    for folder in sorted(SPACES.iterdir()):
        if folder.is_dir():
            pages += load_space(folder.name)
    return pages
