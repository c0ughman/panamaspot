#!/usr/bin/env python3
"""
restore-bento.py — one-time repair: put back the hand-authored "More to see /
Across the region" bento section that image-swap.py flattened into bare images.

The bento is editorial (structured cards: bento-body / bento-split-body /
bento-overlay, each with a tag + h3 + paragraph). The image generators no longer
touch it, but the already-generated pages need their original bento restored.
This pulls each page's bento section from the page's FIRST git commit (the clean
template output) and swaps it back in — replacing the flattened one, or
re-inserting it where it was deleted.

Idempotent: re-running restores the same original section. Run once, commit.
    python3 scripts/restore-bento.py
"""
import re, json, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEL  = json.loads((ROOT/"scripts"/"image-selections.json").read_text())["selections"]

def affected_pages():
    pages = []
    for c in SEL.values():
        pages += c["pages"]
    return list(dict.fromkeys(pages))

def bento_span(html):
    """(start, end, section_html) of the <section> wrapping the REAL
    <div class="home-bento-grid"> (not the CSS rule), or (None, None, None)."""
    m = re.search(r'<div class="home-bento-grid">', html)
    if not m:
        return None, None, None
    sec_start = html.rfind("<section", 0, m.start())
    sec_end = html.find("</section>", m.start())
    if sec_start == -1 or sec_end == -1:
        return None, None, None
    end = sec_end + len("</section>")
    return sec_start, end, html[sec_start:end]

def first_commit(page):
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", page],
        cwd=ROOT, capture_output=True, text=True).stdout.split()
    return out[-1] if out else None

def orig_html(commit, page):
    return subprocess.run(["git", "show", f"{commit}:{page}"],
                          cwd=ROOT, capture_output=True, text=True).stdout

def insert_anchor(html):
    for marker in ("<!--IMGCREDITS-->", "<!--EVB-CTA:closer-->", "</main>"):
        i = html.find(marker)
        if i != -1:
            return i
    return len(html)

def process(page):
    p = ROOT/page
    commit = first_commit(page)
    if not commit:
        print(f"  ! no first commit: {page}"); return
    _, _, orig_sec = bento_span(orig_html(commit, page))
    if not orig_sec:
        print(f"  – original had no bento: {page}"); return
    cur = p.read_text(encoding="utf-8")
    cs, ce, cur_sec = bento_span(cur)
    if cur_sec:
        new = cur[:cs] + orig_sec + cur[ce:]
        how = "replaced"
    else:
        a = insert_anchor(cur)
        new = cur[:a] + orig_sec + cur[a:]
        how = "re-inserted"
    if new != cur:
        p.write_text(new, encoding="utf-8")
    print(f"  ✓ {how}: {page}")

def main():
    for page in affected_pages():
        process(page)

if __name__ == "__main__":
    main()
