#!/usr/bin/env python3
"""
Build optimized derivatives into img/opt/ for the landing pages.

NON-DESTRUCTIVE: originals in img/ are never modified. Other projects in this
repo (kirya.html, yoman/, sefarim/) keep referencing the originals untouched.
"""
import os
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "img")
OUT = os.path.join(SRC, "opt")
os.makedirs(OUT, exist_ok=True)

# (source, output, max_width, quality)  — JPEG derivatives
JPEGS = [
    ("harav.jpg",       "harav-hero.jpg",  1600, 78),  # full-bleed hero (LCP)
    ("harav-field.jpg", "harav-field.jpg", 1600, 80),  # band background + gallery
    ("shiur.jpg",       "shiur.jpg",       1400, 82),  # gallery, displayed ≤832px
    ("harav-hug.jpg",   "harav-hug.jpg",   1400, 82),  # gallery
]

# (source, output, target_height) — PNG logos, displayed at 40px → 2x = 80px
PNGS = [
    ("logo-dark.png",  "logo-dark.png",  80),
    ("logo-light.png", "logo-light.png", 80),
]

def kb(p):
    return os.path.getsize(p) / 1024

print(f"{'file':<26}{'before':>10}{'after':>10}{'saved':>10}")
print("-" * 56)
total_before = total_after = 0

for src, dst, maxw, q in JPEGS:
    sp, dp = os.path.join(SRC, src), os.path.join(OUT, dst)
    im = Image.open(sp)
    im = im.convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(dp, "JPEG", quality=q, optimize=True, progressive=True)
    b, a = kb(sp), kb(dp)
    total_before += b; total_after += a
    print(f"{dst:<26}{b:>9.0f}K{a:>9.0f}K{b-a:>9.0f}K")

for src, dst, h in PNGS:
    sp, dp = os.path.join(SRC, src), os.path.join(OUT, dst)
    im = Image.open(sp)
    im = im.convert("RGBA")
    if im.height > h:
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    # quantize to a small palette while preserving transparency — logos are flat art
    im.save(dp, "PNG", optimize=True)
    b, a = kb(sp), kb(dp)
    total_before += b; total_after += a
    print(f"{dst:<26}{b:>9.0f}K{a:>9.0f}K{b-a:>9.0f}K")

print("-" * 56)
print(f"{'TOTAL':<26}{total_before:>9.0f}K{total_after:>9.0f}K{total_before-total_after:>9.0f}K")

# ── 18.08: the landing pages now use photos supplied by the client, processed
# from  Downloads\דפי נחיתה\  by a one-off script. The derivatives live in
# img/opt/ and are committed. Sources (client originals, 3-30MB each) are NOT in
# the repo. Current mapping:
#   yeshiva-building.jpg <- תמונות/רחפן כולל1  (hero, 1600px q74)
#   harav-portrait.jpg   <- תמונות/3           (Rav, hat + tie; 560px square)
#   harav-podium.jpg     <- תמונות/13          (carousel face; 300px square)
#   harav-field2.jpg     <- 4.JPG              (band, football field; 1600px)
#   hug-event.jpg        <- תמונות/7           (gallery)
#   singing.jpg          <- תמונות/2           (gallery)
#   crowd-night.jpg      <- תמונות/9           (gallery)
