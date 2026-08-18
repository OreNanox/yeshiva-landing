#!/usr/bin/env python3
"""
Build the yeshiva's social / share assets from the real photography.

Written after Canva's generator was tried and rejected: asked for a card using
the supplied portrait, it ignored the asset and invented a stock rabbi with a
long white beard. Publishing a fabricated face as the head of a real yeshiva is
not acceptable, so the assets are composed here instead — real photo, exact
brand colours, exact pixel dimensions, and Hebrew that is verifiably correct.

    python tools/make_social.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:                                   # python-bidi moved its entry point
    from bidi import get_display
except ImportError:
    from bidi.algorithm import get_display

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG   = os.path.join(ROOT, "img")
OUT   = os.path.join(IMG, "social")
FONTS = os.environ.get("YN_FONTS", os.path.join(ROOT, "tools", "fonts"))
os.makedirs(OUT, exist_ok=True)

INK       = (10, 22, 38)
GOLD      = (228, 188, 98)
GOLD_SOFT = (240, 209, 140)
TEXT      = (241, 234, 220)
FAINT     = (156, 174, 196)

HEAD  = "תן לעצמך שנה."
SUB   = "תגלה מי אתה. תחזור הביתה."
BRAND = "ישיבת יראנו ניסים · נתניה"
URL   = "yeshiva.yarenunissim.app"
DATES = "ההרשמה נסגרת בכ׳ באלול"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def rtl(s):
    """Hebrew is stored logically; PIL draws left-to-right, so reorder first."""
    return get_display(s)


def ramp(length, stops):
    """Piecewise-linear alpha ramp along `length`. stops: [(pos0-1, alpha0-255)]"""
    out = []
    for i in range(length):
        t = i / max(length - 1, 1)
        a = stops[-1][1]
        for j in range(len(stops) - 1):
            p0, a0 = stops[j]
            p1, a1 = stops[j + 1]
            if p0 <= t <= p1:
                k = (t - p0) / max(p1 - p0, 1e-9)
                a = a0 + (a1 - a0) * k
                break
        out.append(int(max(0, min(255, a))))
    return out


def vmask(w, h, stops):
    m = Image.new("L", (1, h))
    m.putdata(ramp(h, stops))
    return m.resize((w, h))


def hmask(w, h, stops):
    m = Image.new("L", (w, 1))
    m.putdata(ramp(w, stops))
    return m.resize((w, h))


def scrim(base, mask, colour=INK):
    return Image.composite(Image.new("RGB", base.size, colour), base, mask)


def cover(name, w, h, focus=0.5):
    im = Image.open(os.path.join(IMG, name)).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = int((im.height - h) * focus)
    return im.crop((x, y, x + w, y + h))


def text_w(d, s, f):
    b = d.textbbox((0, 0), rtl(s), font=f)
    return b[2] - b[0]


def rule(d, right, y, width, colour=GOLD, thick=3):
    d.rectangle([right - width, y, right, y + thick], fill=colour)


def save(im, name, quality=88):
    p = os.path.join(OUT, name)
    im.save(p, "JPEG", quality=quality, optimize=True, progressive=True)
    print(f"  {name:<26} {im.width}x{im.height}  {os.path.getsize(p)/1024:5.0f} KB")
    return p



# ── graphic craft ──────────────────────────────────────────────────────────

def harmonize(im, shadow=INK, warm=1.04, strength=0.42):
    """Pull the photo's shadows toward the brand navy so the card reads as one
    designed object rather than a photo pasted onto a coloured box."""
    a = np.asarray(im, dtype=np.float32) / 255.0
    l = a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    k = np.clip(1.0 - l, 0, 1)[..., None] ** 1.4 * strength      # shadows only
    tint = np.array(shadow, dtype=np.float32) / 255.0
    a = a * (1 - k) + tint * k
    a[..., 0] *= warm
    a[..., 2] *= (2 - warm)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def tracked_left(d, left, y, text, fnt, fill, track=0):
    """Left-anchored tracked text — the URL is Latin, so it belongs on the left,
    clear of the right-aligned Hebrew and the bottom-right bracket."""
    vis = rtl(text)
    x = left
    for ch in vis:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + track
    return x - left


def tracked(d, right, y, text, fnt, fill, track=0):
    """Letter-spaced text, right-anchored. PIL has no tracking, so advance by
    hand — the wide gold eyebrow is what makes the card feel typeset."""
    vis = rtl(text)
    widths = [d.textlength(ch, font=fnt) for ch in vis]
    total = sum(widths) + track * max(len(vis) - 1, 0)
    x = right - total
    for ch, w in zip(vis, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += w + track
    return total


def gold_grad(w, h, c0=(214, 168, 74), c1=(247, 224, 160), c2=(198, 150, 60)):
    """Vertical metallic ramp — flat gold reads as a colour, a ramp reads as leaf."""
    top = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    a = np.asarray(c0, np.float32); b = np.asarray(c1, np.float32); c = np.asarray(c2, np.float32)
    up = a + (b - a) * np.clip(top / 0.45, 0, 1)
    dn = b + (c - b) * np.clip((top - 0.45) / 0.55, 0, 1)
    col = np.where(top < 0.45, up, dn)
    return Image.fromarray(np.repeat(col[:, None, :], w, axis=1).astype(np.uint8))


def grad_text(base, xy, text, fnt, anchor="ra", grad=None):
    """Draw text filled with a vertical gradient instead of a flat colour."""
    tmp = Image.new("L", base.size, 0)
    ImageDraw.Draw(tmp).text(xy, rtl(text), font=fnt, fill=255, anchor=anchor)
    bbox = tmp.getbbox()
    if not bbox:
        return
    g = grad if grad is not None else gold_grad(base.size[0], bbox[3] - bbox[1])
    layer = Image.new("RGB", base.size, (0, 0, 0))
    layer.paste(g.resize((base.size[0], bbox[3] - bbox[1])), (0, bbox[1]))
    base.paste(layer, (0, 0), tmp)


def bracket(d, x, y, size, thick, colour=GOLD, flip_x=False, flip_y=False):
    """An open corner bracket — the frame is implied, not drawn. Reads as a
    considered mark rather than the default rectangle a template would give."""
    sx = -1 if flip_x else 1
    sy = -1 if flip_y else 1
    d.rectangle(sorted_box(x, y, x + sx * size, y + sy * thick), fill=colour)
    d.rectangle(sorted_box(x, y, x + sx * thick, y + sy * size), fill=colour)


def sorted_box(x0, y0, x1, y1):
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def corner_set(d, w, h, inset, size, thick=3):
    """Brackets on the two diagonal corners only — asymmetry looks deliberate,
    all four looks like a border."""
    bracket(d, inset, inset, size, thick)
    bracket(d, w - inset, h - inset, size, thick, flip_x=True, flip_y=True)


def side_bar(base, x, y0, y1, width=7):
    """A vertical gold spine beside the copy — anchors the text block."""
    h = y1 - y0
    base.paste(gold_grad(width, h), (x, y0))


def vignette(im, strength=0.30):
    w, h = im.size
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    k = np.clip((r - 0.65) / 0.75, 0, 1)[..., None] * strength
    a = np.asarray(im, dtype=np.float32) / 255.0
    a = a * (1 - k) + (np.array(INK, dtype=np.float32) / 255.0) * k
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))

# ── layouts ────────────────────────────────────────────────────────────────

def horizontal(w=1200, h=630, photo="opt/harav-portrait.jpg", out="og-share.jpg",
               focus=0.35, eyebrow="לבוגרי צבא · נתניה"):
    """Link/share card: portrait right, copy left, held inside a printed frame."""
    base = Image.new("RGB", (w, h), INK)
    pw = int(w * 0.48)
    p = harmonize(cover(photo, pw, h, focus=focus))
    base.paste(p, (w - pw, 0))
    edge = Image.new("RGB", (pw, h), INK)
    base.paste(Image.composite(edge, base.crop((w - pw, 0, w, h)),
                               hmask(pw, h, [(0, 255), (0.42, 80), (1, 0)])), (w - pw, 0))
    base = vignette(base, 0.22)

    d = ImageDraw.Draw(base)
    corner_set(d, w, h, 30, 46, 3)

    right = int(w * 0.560)
    f_eye  = font("Assistant-700.ttf", 19)
    f_head = font("Rubik-900.ttf", 92)
    f_sub  = font("Rubik-300.ttf", 37)
    f_sm   = font("Assistant-600.ttf", 22)
    f_url  = font("Assistant-700.ttf", 19)

    top = int(h * 0.175)
    y = top
    tracked(d, right, y, eyebrow, f_eye, GOLD, track=6.5)
    y += 54
    d.text((right, y), rtl(HEAD), font=f_head, fill=TEXT, anchor="ra")
    y += 118
    grad_text(base, (right, y), SUB, f_sub, anchor="ra")
    d = ImageDraw.Draw(base)
    y += 78
    d.text((right, y), rtl(BRAND), font=f_sm, fill=FAINT, anchor="ra")
    y += 34
    d.text((right, y), rtl(DATES), font=f_sm, fill=GOLD, anchor="ra")
    side_bar(base, right + 22, top - 6, y + 30, 6)
    d = ImageDraw.Draw(base)
    tracked_left(d, 58, h - 58, URL, f_url, FAINT, track=1.8)
    return save(base, out)


def vertical(w=1080, h=1920, photo="opt/harav-portrait.jpg", out="story.jpg",
             focus=0.32, eyebrow="ההרשמה נפתחה"):
    """Story / TikTok: full-bleed photo, copy anchored in the lower third."""
    base = vignette(harmonize(cover(photo, w, h, focus=focus)), 0.26)
    base = scrim(base, vmask(w, h, [(0, 120), (0.22, 40), (0.44, 120),
                                    (0.58, 212), (0.76, 244), (1, 252)]))
    d = ImageDraw.Draw(base)
    corner_set(d, w, h, 48, 70, 4)

    right = w - 96
    f_eye  = font("Assistant-700.ttf", 29)
    f_head = font("Rubik-900.ttf", 132)
    f_sub  = font("Rubik-300.ttf", 52)
    f_sm   = font("Assistant-600.ttf", 33)

    top = int(h * 0.535)
    y = top
    tracked(d, right, y, eyebrow, f_eye, GOLD, track=8.5)
    y += 80
    d.text((right, y), rtl(HEAD), font=f_head, fill=TEXT, anchor="ra")
    y += 184
    grad_text(base, (right, y), SUB, f_sub, anchor="ra")
    d = ImageDraw.Draw(base)
    y += 112
    d.text((right, y), rtl(BRAND), font=f_sm, fill=FAINT, anchor="ra")
    y += 48
    d.text((right, y), rtl(DATES), font=f_sm, fill=GOLD, anchor="ra")
    side_bar(base, right + 30, top - 8, y + 44, 8)
    d = ImageDraw.Draw(base)
    tracked_left(d, 84, h - 116, URL, font("Assistant-700.ttf", 28), FAINT, track=2.6)
    return save(base, out)


def square(w=1080, h=1080, photo="opt/beit-midrash.jpg", out="instagram-post.jpg",
           focus=0.5, eyebrow="בית המדרש החדש"):
    """Feed post: photo behind, copy set low and tight."""
    base = vignette(harmonize(cover(photo, w, h, focus=focus)), 0.24)
    base = scrim(base, vmask(w, h, [(0, 140), (0.18, 70), (0.38, 180),
                                    (0.54, 232), (0.72, 248), (1, 252)]))
    d = ImageDraw.Draw(base)
    corner_set(d, w, h, 40, 58, 4)

    right = w - 86
    f_eye  = font("Assistant-700.ttf", 25)
    f_head = font("Rubik-900.ttf", 106)
    f_sub  = font("Rubik-300.ttf", 42)
    f_sm   = font("Assistant-600.ttf", 29)

    top = int(h * 0.425)
    y = top
    tracked(d, right, y, eyebrow, f_eye, GOLD, track=7)
    y += 68
    d.text((right, y), rtl(HEAD), font=f_head, fill=TEXT, anchor="ra")
    y += 148
    grad_text(base, (right, y), SUB, f_sub, anchor="ra")
    d = ImageDraw.Draw(base)
    y += 94
    d.text((right, y), rtl(BRAND), font=f_sm, fill=FAINT, anchor="ra")
    y += 44
    d.text((right, y), rtl(DATES), font=f_sm, fill=GOLD, anchor="ra")
    side_bar(base, right + 26, top - 8, y + 40, 7)
    d = ImageDraw.Draw(base)
    tracked_left(d, 74, h - 82, URL, font("Assistant-700.ttf", 24), FAINT, track=2.2)
    return save(base, out)


if __name__ == "__main__":
    print(f"{'file':<26} {'size':<12} weight")
    print("-" * 50)
    horizontal(out="og-share.jpg")
    horizontal(photo="opt/yeshiva-building.jpg", out="facebook-post.jpg",
               focus=0.45, eyebrow="בית שצומח בנתניה 20 שנה")
    square(out="instagram-post.jpg")
    vertical(out="instagram-story.jpg", eyebrow="ההרשמה נפתחה")
    vertical(photo="opt/yeshiva-building.jpg", out="tiktok.jpg",
             focus=0.42, eyebrow="נתניה · לבוגרי צבא")
