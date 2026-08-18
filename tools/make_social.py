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


# ── layouts ────────────────────────────────────────────────────────────────

def horizontal(w=1200, h=630, photo="opt/harav-portrait.jpg", out="og-share.jpg"):
    """Link/share card: portrait on the right, copy on the left."""
    base = Image.new("RGB", (w, h), INK)
    pw = int(w * 0.46)
    p = cover(photo, pw, h, focus=0.35)
    base.paste(p, (w - pw, 0))
    # fade the photo's inner edge into the navy
    edge = Image.new("RGB", (pw, h), INK)
    base.paste(Image.composite(edge, base.crop((w - pw, 0, w, h)),
                               hmask(pw, h, [(0, 255), (0.45, 90), (1, 0)])), (w - pw, 0))

    d = ImageDraw.Draw(base)
    right = int(w * 0.545)
    f_head = font("Rubik-900.ttf", 78)
    f_sub  = font("Rubik-700.ttf", 34)
    f_sm   = font("Assistant-600.ttf", 24)
    f_url  = font("Assistant-600.ttf", 22)

    y = int(h * 0.20)
    d.text((right, y), rtl(HEAD), font=f_head, fill=TEXT, anchor="ra")
    y += 104
    d.text((right, y), rtl(SUB), font=f_sub, fill=GOLD_SOFT, anchor="ra")
    y += 68
    rule(d, right, y, 130)
    y += 34
    d.text((right, y), rtl(BRAND), font=f_sm, fill=FAINT, anchor="ra")
    y += 38
    d.text((right, y), rtl(DATES), font=f_sm, fill=GOLD, anchor="ra")
    d.text((right, h - 56), URL, font=f_url, fill=FAINT, anchor="ra")
    return save(base, out)


def vertical(w=1080, h=1920, photo="opt/harav-portrait.jpg", out="story.jpg",
             focus=0.32, tag=None):
    """Story / TikTok: full-bleed photo, copy held in the lower third."""
    base = cover(photo, w, h, focus=focus)
    base = scrim(base, vmask(w, h, [(0, 120), (0.22, 40), (0.46, 110),
                                    (0.60, 205), (0.78, 242), (1, 252)]))
    d = ImageDraw.Draw(base)
    right = w - 90
    f_head = font("Rubik-900.ttf", 118)
    f_sub  = font("Rubik-700.ttf", 50)
    f_sm   = font("Assistant-600.ttf", 34)
    f_tag  = font("Assistant-600.ttf", 30)

    y = int(h * 0.575)
    if tag:
        d.text((right, y), rtl(tag), font=f_tag, fill=GOLD, anchor="ra")
        y += 62
    d.text((right, y), rtl(HEAD), font=f_head, fill=TEXT, anchor="ra")
    y += 158
    d.text((right, y), rtl(SUB), font=f_sub, fill=GOLD_SOFT, anchor="ra")
    y += 96
    rule(d, right, y, 180, thick=4)
    y += 52
    d.text((right, y), rtl(BRAND), font=f_sm, fill=FAINT, anchor="ra")
    y += 52
    d.text((right, y), rtl(DATES), font=f_sm, fill=GOLD, anchor="ra")
    d.text((right, h - 110), URL, font=f_sm, fill=FAINT, anchor="ra")
    return save(base, out)


def square(w=1080, h=1080, photo="opt/beit-midrash.jpg", out="instagram-post.jpg",
           focus=0.5):
    """Feed post: photo behind, copy centred low."""
    base = cover(photo, w, h, focus=focus)
    # the beit-midrash frame is bright: at the lighter ramp the gold sub-line
    # measured 2.99 against the backdrop, under the 3.0 large-text floor.
    base = scrim(base, vmask(w, h, [(0, 140), (0.18, 70), (0.40, 185),
                                    (0.55, 232), (0.72, 248), (1, 252)]))
    d = ImageDraw.Draw(base)
    right = w - 80
    f_head = font("Rubik-900.ttf", 96)
    f_sub  = font("Rubik-700.ttf", 40)
    f_sm   = font("Assistant-600.ttf", 30)

    y = int(h * 0.48)
    d.text((right, y), rtl(HEAD), font=f_head, fill=TEXT, anchor="ra")
    y += 128
    d.text((right, y), rtl(SUB), font=f_sub, fill=GOLD_SOFT, anchor="ra")
    y += 80
    rule(d, right, y, 150, thick=4)
    y += 44
    d.text((right, y), rtl(BRAND), font=f_sm, fill=FAINT, anchor="ra")
    y += 46
    d.text((right, y), rtl(DATES), font=f_sm, fill=GOLD, anchor="ra")
    d.text((right, h - 74), URL, font=f_sm, fill=FAINT, anchor="ra")
    return save(base, out)


if __name__ == "__main__":
    print(f"{'file':<26} {'size':<12} weight")
    print("-" * 50)
    horizontal(out="og-share.jpg")
    horizontal(photo="opt/yeshiva-building.jpg", out="facebook-post.jpg")
    square(out="instagram-post.jpg")
    vertical(out="instagram-story.jpg", tag="ההרשמה נפתחה")
    vertical(photo="opt/yeshiva-building.jpg", out="tiktok.jpg",
             focus=0.42, tag="נתניה · לבוגרי צבא")
