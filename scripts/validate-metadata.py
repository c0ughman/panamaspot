#!/usr/bin/env python3
"""
Validate article metadata: ensure titles, tags, hreflang, og:* match actual page content.
"""
import re
import os
import json
from pathlib import Path

def extract_metadata(html):
    """Extract all metadata from page."""
    meta = {
        'file': None,
        'lang': None,
        'canonical': None,
        'title': None,
        'og_title': None,
        'og_url': None,
        'twitter_title': None,
        'description': None,
        'og_description': None,
        'og_image': None,
        'h1': None,
        'hero_image': None,
        'hreflang_en': None,
        'hreflang_es': None,
        'lang_switcher_en': None,
        'lang_switcher_es': None,
        'hero_tags': [],
        'issues': []
    }
    
    # Language
    meta['lang'] = 'es' if '/es/' in html else 'en'
    
    # Title
    m = re.search(r'<title>([^<]+)</title>', html)
    meta['title'] = m.group(1).strip() if m else None
    
    # H1
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    meta['h1'] = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else None
    
    # Canonical
    m = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]+)"', html)
    meta['canonical'] = m.group(1) if m else None
    
    # OG tags
    m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', html)
    meta['og_title'] = m.group(1) if m else None
    
    m = re.search(r'<meta[^>]*property="og:url"[^>]*content="([^"]*)"', html)
    meta['og_url'] = m.group(1) if m else None
    
    m = re.search(r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"', html)
    meta['og_description'] = m.group(1) if m else None
    
    m = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]*)"', html)
    meta['og_image'] = m.group(1) if m else None
    
    # Twitter
    m = re.search(r'<meta[^>]*name="twitter:title"[^>]*content="([^"]*)"', html)
    meta['twitter_title'] = m.group(1) if m else None
    
    # Description
    m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html)
    meta['description'] = m.group(1) if m else None
    
    # Hero image
    m = re.search(r'art-hero-img-full[^>]*style="background-image:url\(\'([^\']+)\'\)', html)
    meta['hero_image'] = m.group(1) if m else None
    
    # Hreflang
    m = re.search(r'<link[^>]*hreflang="en"[^>]*href="([^"]*)"', html)
    meta['hreflang_en'] = m.group(1) if m else None
    
    m = re.search(r'<link[^>]*hreflang="es"[^>]*href="([^"]*)"', html)
    meta['hreflang_es'] = m.group(1) if m else None
    
    # Language switcher
    m = re.search(r'lang-opt active[^>]*href="([^"]*)"[^>]*hreflang="en"', html)
    meta['lang_switcher_en'] = m.group(1) if m else None
    
    m = re.search(r'lang-opt[^>]*href="([^"]*)"[^>]*hreflang="es"', html)
    meta['lang_switcher_es'] = m.group(1) if m else None
    
    # Hero tags
    for m in re.finditer(r'<span class="art-hero-tag">([^<]+)</span>', html):
        meta['hero_tags'].append(m.group(1).strip())
    
    return meta

def validate_metadata(meta, filepath):
    """Validate metadata consistency."""
    issues = []
    filename = os.path.basename(filepath)
    slug = filename.replace('.html', '')
    
    # Extract page subject from slug/content
    meta['file'] = filename
    
    # Check 1: Title consistency
    if meta['title'] and meta['og_title'] and meta['title'] != meta['og_title']:
        issues.append(f"Title mismatch: <title> vs og:title")
    
    if meta['title'] and meta['twitter_title'] and meta['title'] != meta['twitter_title']:
        issues.append(f"Title mismatch: <title> vs twitter:title")
    
    # Check 2: Canonical matches file
    if meta['canonical']:
        if slug not in meta['canonical']:
            issues.append(f"Canonical doesn't match slug: {meta['canonical']}")
    
    # Check 3: OG URL matches canonical
    if meta['og_url'] and meta['canonical'] and meta['og_url'] != meta['canonical']:
        issues.append(f"og:url doesn't match canonical")
    
    # Check 4: Hero tags are relevant
    page_keywords = set(re.findall(r'\w+', slug.lower()))
    tag_keywords = set(' '.join(meta['hero_tags']).lower().split())
    if page_keywords and tag_keywords:
        overlap = page_keywords & tag_keywords
        if not overlap and len(tag_keywords) > 0:
            issues.append(f"Hero tags don't match page: tags={', '.join(meta['hero_tags'])}")
    
    # Check 5: Hreflang consistency
    if meta['lang'] == 'en':
        if meta['hreflang_en'] and slug not in meta['hreflang_en']:
            issues.append(f"hreflang en doesn't match page")
        if meta['lang_switcher_en'] and slug not in meta['lang_switcher_en']:
            issues.append(f"Language switcher en doesn't match page")
    
    # Check 6: No stray images
    if meta['hero_image'] and 'pexels.com' not in meta['hero_image'] and 'things-to-do' in meta['hero_image']:
        issues.append(f"Hero image suspicious: {meta['hero_image']}")
    
    # Check 7: Description exists and is reasonable
    if not meta['description'] or len(meta['description']) < 50:
        issues.append(f"Missing or short description")
    
    # Check 8: H1 exists
    if not meta['h1']:
        issues.append(f"Missing H1 tag")
    
    return issues, meta

def process_files():
    """Process all HTML files."""
    base = Path('/Users/coughman/Desktop/clients/panamaspot/public')
    
    all_files = list(base.glob('articles/*.html')) + list(base.glob('es/articles/*.html'))
    
    issues_by_file = {}
    all_meta = []
    
    print("Validating article metadata…\n")
    
    for filepath in sorted(all_files):
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        
        issues, meta = validate_metadata(extract_metadata(html), str(filepath))
        all_meta.append(meta)
        
        if issues:
            issues_by_file[meta['file']] = issues
    
    # Report issues
    if issues_by_file:
        print(f"⚠️  Found issues in {len(issues_by_file)} files:\n")
        for filename in sorted(issues_by_file.keys()):
            print(f"  {filename}")
            for issue in issues_by_file[filename]:
                print(f"    - {issue}")
            print()
    else:
        print("✅ No metadata issues found!\n")
    
    return all_meta, issues_by_file

if __name__ == '__main__':
    all_meta, issues = process_files()
    print(f"\nProcessed {len(all_meta)} files.")
    print(f"Issues found: {sum(len(v) for v in issues.values())}")
