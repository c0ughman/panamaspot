#!/usr/bin/env bash
# Optimize every IMAGE THAT IS ACTUALLY REFERENCED on the homepage + the 12
# article pages into web-optimal WebP — same pixel dimensions (heroes capped at
# 2048w, which only affects the 4032px HEIC), visually-lossless quality (q90).
#
# Sources stay untouched on disk; this only WRITES sibling .webp files and a
# dimensions manifest (scripts/img-manifest.json) + a remap list
# (scripts/img-remap.txt: "<old-web-path> <new-web-path>").
#
# Requires: cwebp + sips (macOS). HEIC is decoded via sips first.
set -euo pipefail
cd "$(dirname "$0")/.."

MAXW=2048          # cap hero width; everything else keeps native size
# q82 + sharp_yuv is visually indistinguishable from these (already-lossy ~q78)
# source JPGs — it preserves all detail the source actually contains while
# shrinking the file. Going higher only re-encodes quality the JPG already lost.
Q=82
PUB="public"
MANIFEST="scripts/img-manifest.json"
REMAP="scripts/img-remap.txt"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Collect referenced local /images/... paths from the article HTML + the app source.
REFLIST="$TMP/refs.txt"
grep -rhoE "/images/[^'\")> ]+\.(jpg|jpeg|png|webp|HEIC|heic|JPG|JPEG|PNG)" \
  public/articles public/es/articles src/app src/components 2>/dev/null \
  | sed 's/[?#].*//' | sort -u > "$REFLIST"

echo "Optimizing $(wc -l < "$REFLIST" | tr -d ' ') referenced images → WebP (q$Q, max ${MAXW}px wide)…"
: > "$REMAP"
echo "{" > "$MANIFEST"
first=1

while IFS= read -r web; do
  [ -n "$web" ] || continue
  src="$PUB$web"
  [ -f "$src" ] || { echo "  ⚠ missing source: $src" >&2; continue; }

  dir="$(dirname "$web")"
  base="$(basename "$web")"
  stem="${base%.*}"; stem="${stem%.*}"        # strip up to two extensions (e.g. tours-boquete.jpeg.webp → tours-boquete)
  newweb="$dir/$stem.webp"
  out="$PUB$newweb"

  # Decode HEIC to a temp PNG that cwebp can read; otherwise feed cwebp directly.
  ext="$(printf '%s' "$base" | tr 'A-Z' 'a-z')"
  infile="$src"
  case "$ext" in
    *.heic) sips -s format png "$src" --out "$TMP/in.png" >/dev/null 2>&1; infile="$TMP/in.png" ;;
  esac

  # Cap width only when wider than MAXW (never upscale → no quality gain/loss).
  w="$(sips -g pixelWidth "$infile" 2>/dev/null | awk '/pixelWidth/{print $2}')"
  resize=()
  if [ -n "${w:-}" ] && [ "$w" -gt "$MAXW" ]; then resize=(-resize "$MAXW" 0); fi

  cwebp -quiet -q "$Q" -m 6 -mt -sharp_yuv ${resize[@]+"${resize[@]}"} "$infile" -o "$out"

  nw="$(sips -g pixelWidth  "$out" 2>/dev/null | awk '/pixelWidth/{print $2}')"
  nh="$(sips -g pixelHeight "$out" 2>/dev/null | awk '/pixelHeight/{print $2}')"

  [ $first -eq 1 ] && first=0 || echo "," >> "$MANIFEST"
  printf '  "%s": {"w": %s, "h": %s}' "$newweb" "${nw:-0}" "${nh:-0}" >> "$MANIFEST"
  echo "$web $newweb" >> "$REMAP"

  oldsz="$(du -k "$src" | cut -f1)"; newsz="$(du -k "$out" | cut -f1)"
  printf "  ✓ %-44s %5sKB → %5sKB  (%sx%s)\n" "$stem.webp" "$oldsz" "$newsz" "${nw:-?}" "${nh:-?}"
done < "$REFLIST"

echo "" >> "$MANIFEST"
echo "}" >> "$MANIFEST"
echo "Wrote $MANIFEST and $REMAP."
