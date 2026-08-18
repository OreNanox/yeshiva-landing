#!/usr/bin/env python3
"""
Batch: pull graded stills out of the client's S-Log3 clips.

Walks the Drive zips, extracts one MP4 at a time (never more — the set is 8.3 GB),
picks the sharpest well-composed frames, grades them with tools/grade_slog3.py,
sharpens, and writes full-resolution JPEGs to the candidates folder. Each video
is deleted as soon as it has been read.

    python tools/extract_frames.py <zip-dir> <work-dir> [frames-per-clip]
"""
import os, sys, zipfile, shutil, time
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grade_slog3 import grade, unsharp, best_frames

ZIPDIR = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\User\Downloads"
WORK   = sys.argv[2] if len(sys.argv) > 2 else "frames_work"
PER    = int(sys.argv[3]) if len(sys.argv) > 3 else 2

VID  = os.path.join(WORK, "vid")
OUT  = os.path.join(WORK, "candidates")
for d in (VID, OUT):
    os.makedirs(d, exist_ok=True)

# Only the archives for this shoot. The Downloads folder holds other unrelated
# drive-download-*.zip files (shiurim), and processing those wastes 4K decodes
# and pollutes the candidate set.
PREFIX = os.environ.get("ZIP_PREFIX", "drive-download-20260818T110938Z")
zips = sorted(
    os.path.join(ZIPDIR, f) for f in os.listdir(ZIPDIR)
    if f.startswith(PREFIX) and f.endswith(".zip")
)
print(f"{len(zips)} archives", flush=True)

t0 = time.time()
made = 0
for zp in zips:
    z = zipfile.ZipFile(zp)
    names = [n for n in z.namelist() if n.lower().endswith(".mp4")]
    print(f"\n=== {os.path.basename(zp)} : {len(names)} clips ===", flush=True)
    for name in names:
        stem = os.path.splitext(os.path.basename(name))[0]
        path = os.path.join(VID, os.path.basename(name))
        try:
            with z.open(name) as src, open(path, "wb") as dst:
                shutil.copyfileobj(src, dst, 1 << 22)

            picks = best_frames(path, want=PER, samples=18)
            for k, (score, frac, img) in enumerate(picks):
                out = os.path.join(OUT, f"{stem}_{k}.jpg")
                cv2.imwrite(out, unsharp(img), [cv2.IMWRITE_JPEG_QUALITY, 92])
                made += 1
            print(f"  {stem}: {len(picks)} frames "
                  f"(best score {picks[0][0]:.0f})" if picks else f"  {stem}: no frames",
                  flush=True)
        except Exception as e:
            print(f"  {stem}: FAILED {e}", flush=True)
        finally:
            if os.path.exists(path):
                os.remove(path)

print(f"\ndone: {made} candidate frames in {(time.time()-t0)/60:.1f} min -> {OUT}", flush=True)
