#!/usr/bin/env python3
"""
merge-curated.py — merge subagent-curated image sets into image-selections.json
(+ image-artists.json), verifying every new URL is HTTP 200 and free-licensed.

Inputs (from the scratchpad, produced by the curation subagents):
  boquete-images.json  {"rewrites":[{url,caption_en,caption_es}...],
                        "additions":[{url,license,artist,caption_en,caption_es}...]}
  daytrips-images.json {"<Category>":[{url,license,artist,caption_en,caption_es}...]}

Usage: python3 scripts/merge-curated.py <boquete-images.json> <daytrips-images.json>
"""
import re, json, sys, pathlib, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SELP = ROOT/"scripts"/"image-selections.json"
ARTP = ROOT/"scripts"/"image-artists.json"
OK_LIC = ("cc0", "public domain", "cc by")

def norm(u):
    return urllib.parse.unquote(u.replace("&amp;", "&"))

import time
UA = "PanamaSpot-image-tooling/1.0 (https://panamaspot.com; contact@panamaspot.com)"
def http_ok(u):
    # Wikimedia rate-limits (429) bursts under a generic UA; use a descriptive UA
    # and back off on 429 before giving up.
    for attempt in range(4):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=30).status == 200
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(4 * (attempt + 1)); continue
            return False
        except Exception:
            return False
    return False

def free(lic):
    return (lic or "").strip().lower().startswith(OK_LIC)

def verify(item):
    lic = item.get("license", "")
    if not free(lic):
        print(f"    ✗ reject (license {lic!r}): {item['url'][:70]}"); return False
    if not http_ok(item["url"]):
        print(f"    ✗ reject (not 200): {item['url'][:70]}"); return False
    print(f"    ✓ {lic}: {item['url'].split('/')[-1][:55]}")
    return True

def main():
    boq = json.loads(pathlib.Path(sys.argv[1]).read_text())
    day = json.loads(pathlib.Path(sys.argv[2]).read_text())
    doc = json.loads(SELP.read_text())
    SEL = doc["selections"]
    ART = json.loads(ARTP.read_text()) if ARTP.exists() else {}

    # index existing urls per category by normalized url
    def find(cat, url):
        for it in SEL[cat]["use"]:
            if norm(it["url"]) == norm(url):
                return it
        if SEL[cat].get("hero") and norm(SEL[cat]["hero"]["url"]) == norm(url):
            return SEL[cat]["hero"]
        return None

    BOQ_CAT = "Boquete — town, highlands, coffee"
    # 1) Boquete caption rewrites
    print("[Boquete rewrites]")
    for rw in boq.get("rewrites", []):
        it = find(BOQ_CAT, rw["url"])
        if it:
            it["caption_en"] = rw["caption_en"]; it["caption_es"] = rw["caption_es"]
            print(f"    ✓ recaption {rw['url'].split('/')[-1][:50]}")
        else:
            print(f"    ! not found: {rw['url'][:70]}")

    # 2) additions (Boquete + day-trip categories)
    add_groups = {BOQ_CAT: boq.get("additions", [])}
    for cat, items in day.items():
        add_groups.setdefault(cat, []).extend(items)

    added = 0
    for cat, items in add_groups.items():
        if cat not in SEL:
            print(f"  ! unknown category {cat!r}, skipping"); continue
        print(f"[{cat}] verifying {len(items)} additions")
        existing = {norm(it["url"]) for it in SEL[cat]["use"]}
        hero_url = norm(SEL[cat]["hero"]["url"]) if SEL[cat].get("hero") else None
        for item in items:
            if norm(item["url"]) == hero_url:
                # same as the category hero: don't add a gallery dup, but keep its
                # artist so the credits block can attribute the hero.
                if item.get("artist") and "upload.wikimedia.org" in item["url"]:
                    ART[item["url"]] = item["artist"]
                print(f"    – equals hero, artist recorded: {item['url'].split('/')[-1][:45]}"); continue
            if norm(item["url"]) in existing:
                print(f"    – dup, skip: {item['url'].split('/')[-1][:50]}"); continue
            if not verify(item):
                continue
            entry = {"url": item["url"], "license": item["license"],
                     "caption_en": item.get("caption_en", ""), "caption_es": item.get("caption_es", "")}
            SEL[cat]["use"].append(entry)
            existing.add(norm(item["url"]))
            if item.get("artist") and "upload.wikimedia.org" in item["url"]:
                ART[item["url"]] = item["artist"]
            added += 1

    SELP.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    ARTP.write_text(json.dumps(ART, ensure_ascii=False, indent=1))
    print(f"\nMerged. New images added: {added}")

if __name__ == "__main__":
    main()
