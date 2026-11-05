"""The whole conversion of one or more old guides, in the right order:
  1. reskin_old_guides.py   new template, refuses the page if anything is lost
  2. v2_images.py           self-host and right-size its photos
  3. evalley_cta_rollout.py new CTAs on Boquete and El Valle guides
  4. build_search_thumbs.py search thumbnail
  5. page-images.ts         sitemap image list now names the photos on the page
  6. check_share_images.py  the share image must be the hero photo, or the run fails

  python3 scripts/reskin_pipeline.py <photo_download_dir> --page=articles/x [--page=...]
"""
import re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / "public"; TS = ROOT / "src/app/page-images.ts"
dl = sys.argv[1]; pages = [a.split("=", 1)[1] for a in sys.argv[2:] if a.startswith("--page=")]
if not pages: sys.exit("no pages")
run = lambda *c: subprocess.run([sys.executable, *c], cwd=ROOT, check=True)
out = subprocess.run([sys.executable, "scripts/reskin_old_guides.py", *[f"--page={p}" for p in pages]], cwd=ROOT, capture_output=True, text=True)
print(out.stdout.strip())
done = [l.split(" ", 1)[1] for l in out.stdout.splitlines() if l.startswith("wrote ")]
if not done: sys.exit("nothing converted")
run("scripts/v2_images.py", dl, *[f"--page={p}.html" for p in done])
run("scripts/evalley_cta_rollout.py", *[f"--page={p}.html" for p in done])
run("scripts/build_search_thumbs.py", "--force")
ts = TS.read_text()
for p in done:
    h = (P / (p + ".html")).read_text()
    h = re.sub(r"<!--evx:\w+-->.*?<!--/evx-->", "", h, flags=re.S)
    tags = re.findall(r'<img\b[^>]*class="hero-img"[^>]*>', h) + re.findall(r'<figure class="fig[^"]*"><img\b[^>]*>', h) + re.findall(r'<figure><img class="ph"[^>]*>', h)
    urls = list(dict.fromkeys(re.search(r'\bsrc="([^"]+)"', t)[1] for t in tags))
    block = f'  "/{p}": [\n' + "".join(f'    "{u}",\n' for u in urls) + "  ],\n"
    ts, n = re.subn(r'  "/' + re.escape(p) + r'": \[\n.*?\n  \],\n', lambda m: block, ts, flags=re.S)
    if not n: ts = ts.replace("export const pageImages", "export const pageImages", 1); print("no sitemap image entry for", p)
TS.write_text(ts)
check = subprocess.run([sys.executable, "scripts/check_share_images.py", *[f"--page={p}" for p in done]], cwd=ROOT, capture_output=True, text=True)
print(check.stdout.strip())
if check.returncode: sys.exit("share image check failed: fix before committing")
print("converted", len(done), "of", len(pages))
