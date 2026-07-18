#!/usr/bin/env python3
"""
Universal fix: any article page that uses <figure class="art-inline-img">
markup (inline gallery images between paragraphs) must also carry the
matching CSS rule, or the images render at 0px height and are invisible.

This scans every page in public/articles and public/es/articles, and for
any page that has the markup but is missing the CSS, injects the exact
rule already used sitewide (copied from the pages where it works).

Idempotent: safe to re-run after adding new pages/images in the future.
Run with: python3 scripts/fix-inline-img-css.py
"""
import glob

ART_INLINE_IMG_CSS = (
    '.art-inline-img{margin:56px 0;position:relative}'
    '.art-inline-img .imgph{height:416px;border-radius:18px}'
    '.art-inline-img figcaption{position:absolute;width:1px;height:1px;'
    'padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);'
    'white-space:nowrap;border:0}'
    '@media(max-width:640px){.art-inline-img .imgph{height:300px}}'
)

def fix(path):
    html = open(path, encoding='utf-8').read()

    uses_markup = 'class="art-inline-img"' in html
    has_css = '.art-inline-img{' in html

    if not uses_markup:
        return 'skip (no inline images on this page)'
    if has_css:
        return 'ok (css already present)'

    idx = html.find('</style>')
    if idx == -1:
        return 'ERROR: no </style> tag found'

    html = html[:idx] + ART_INLINE_IMG_CSS + html[idx:]
    open(path, 'w', encoding='utf-8').write(html)
    return 'FIXED (css injected)'

def main():
    files = sorted(glob.glob('public/articles/*.html')) + sorted(glob.glob('public/es/articles/*.html'))
    fixed = 0
    for path in files:
        result = fix(path)
        if 'FIXED' in result:
            fixed += 1
        print(f"{result:35s} {path}")
    print(f"\n{fixed} file(s) fixed.")

if __name__ == '__main__':
    main()
