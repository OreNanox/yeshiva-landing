#!/usr/bin/env python3
"""
Pull the sharpest frames out of S-Log3 footage and grade them for the web.

The camera shoots a flat log profile: mean saturation ~12 and a compressed luma
range. Dropping those frames straight onto the page looks washed out and grey,
so every frame goes through a real display transform rather than a contrast
slider:

    8-bit S-Log3  ->  scene linear  ->  white balance  ->  filmic tone curve
                  ->  saturation    ->  Rec.709 gamma  ->  unsharp mask

Sharpness is measured AFTER grading: log footage has crushed micro-contrast, so
a Laplacian on the raw frame ranks every frame as equally soft.
"""
import os, cv2, numpy as np

# ── S-Log3 electro-optical transfer function (Sony's published curve) ────────
_BREAK = 171.2102946929


def slog3_to_linear(x):
    """x: 0..1 float (8-bit code /255). Returns scene-linear reflectance."""
    c = x * 1023.0
    hi = (np.power(10.0, (c - 420.0) / 261.5) * (0.18 + 0.01)) - 0.01
    lo = (c - 95.0) * 0.01125000 / (_BREAK - 95.0)
    return np.where(c >= _BREAK, hi, lo)


def white_balance(lin, strength=0.85):
    """Grey-world on the linear signal — log footage often carries a green cast."""
    m = lin.reshape(-1, 3).mean(axis=0)
    m = np.maximum(m, 1e-6)
    gain = m.mean() / m
    gain = 1.0 + (gain - 1.0) * strength
    return lin * gain


def filmic(x, shoulder=0.92):
    """Gentle S-curve: lifts the flat midtones without clipping highlights."""
    x = np.maximum(x, 0.0)
    y = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)   # ACES-ish
    return np.clip(y / shoulder, 0.0, 1.0)


def saturate(rgb, amount=1.28):
    lumw = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    l = (rgb * lumw).sum(axis=2, keepdims=True)
    return np.clip(l + (rgb - l) * amount, 0.0, 1.0)


def unsharp(img8, radius=1.6, amount=0.75, threshold=2):
    blur = cv2.GaussianBlur(img8, (0, 0), radius)
    sharp = cv2.addWeighted(img8, 1 + amount, blur, -amount, 0)
    if threshold > 0:                      # leave flat areas alone (less noise)
        low = np.abs(img8.astype(np.int16) - blur.astype(np.int16)) < threshold
        sharp = np.where(low, img8, sharp)
    return sharp.astype(np.uint8)


def auto_exposure(lin, target_mean=140.0, lo=0.10, hi=4.0, iters=14):
    """Solve for the exposure scale that lands the graded mean on target.

    A fixed exposure cannot serve 26 clips shot from a bright corridor to a dim
    stairwell — at a constant scale the bright ones clip and the dim ones stay
    muddy. Bisection on the actual graded result is cheap and always in range.
    """
    probe = lin[::8, ::8]                       # 1/64 of the pixels is plenty
    lumw = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        tone = filmic(np.maximum(probe, 0.0) * mid)
        mean = (np.power(np.clip(tone, 0, 1), 1 / 2.2) * 255.0)[..., ::-1]
        mean = float((mean * lumw).sum(axis=2).mean())
        if mean < target_mean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def grade(bgr, exposure=None, sat=1.28, target_mean=140.0):
    """Full S-Log3 -> display transform. Input/output are BGR uint8.

    exposure=None (default) auto-solves per frame.
    """
    x = bgr.astype(np.float32) / 255.0
    lin = slog3_to_linear(x)
    lin = white_balance(lin)
    if exposure is None:
        exposure = auto_exposure(lin, target_mean)
    lin = np.maximum(lin, 0.0) * exposure
    tone = filmic(lin)
    tone = saturate(tone, sat)
    out = np.power(np.clip(tone, 0, 1), 1 / 2.2)          # Rec.709-ish gamma
    return (out * 255.0).astype(np.uint8)


def frame_score(graded_bgr):
    """Sharpness x subject interest, measured on the graded frame."""
    g = cv2.cvtColor(graded_bgr, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(g, (960, 540))
    sharp = cv2.Laplacian(small, cv2.CV_64F).var()
    # penalise frames that are nearly empty (a blank wall scores high on nothing)
    detail = float(np.mean(cv2.Canny(small, 40, 120) > 0))
    return sharp * (0.35 + detail)


def best_frames(path, want=3, samples=26, min_gap=0.12):
    """Sample the clip, grade each sample, keep the top `want` spread apart."""
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if n <= 0:
        cap.release()
        return []
    picks = []
    for i in range(samples):
        frac = (i + 0.5) / samples
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * frac))
        ok, fr = cap.read()
        if not ok:
            continue
        g = grade(fr)
        picks.append((frame_score(g), frac, g))
    cap.release()

    picks.sort(key=lambda t: -t[0])
    chosen = []
    for score, frac, img in picks:
        if all(abs(frac - f) >= min_gap for _, f, _ in chosen):
            chosen.append((score, frac, img))
        if len(chosen) >= want:
            break
    return chosen
