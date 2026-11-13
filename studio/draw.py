"""Drawing helpers: animated background, rich text layout, icons, cards."""

import math
import re
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFilter

from .anim import enter

# ---------------------------------------------------------------- formats

FORMATS = {
    # name: (width, height, safe margins left, top, right, bottom)
    "youtube": (1920, 1080, (150, 130, 150, 120)),
    "reel": (1080, 1920, (90, 250, 150, 420)),
    "square": (1080, 1080, (90, 110, 90, 110)),
    "carousel": (1080, 1350, (100, 150, 100, 170)),
}


@dataclass
class Canvas:
    fmt: str
    w: int
    h: int
    left: int
    top: int
    right: int
    bottom: int

    @property
    def cw(self):
        return self.w - self.left - self.right

    @property
    def ch(self):
        return self.h - self.top - self.bottom

    @property
    def vertical(self):
        return self.h > self.w

    @property
    def u(self):
        """Size unit: 1.0 at 1080px on the short side."""
        return min(self.w, self.h) / 1080 * (1.08 if self.fmt == "youtube" else 1.0)


def make_canvas(fmt):
    w, h, (l, t, r, b) = FORMATS[fmt]
    return Canvas(fmt, w, h, l, t, r, b)


# ---------------------------------------------------------------- background

class Background:
    """Gradient + soft moving glow blobs + faint dot grid. Pre-renders sprites once."""

    def __init__(self, brand, canvas):
        self.brand = brand
        self.cv = canvas
        w, h = canvas.w, canvas.h
        top = brand.c("bg_top")[:3]
        bot = brand.c("bg_bottom")[:3]
        grad = Image.new("RGB", (1, 256))
        for y in range(256):
            k = y / 255
            grad.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)))
        self.base = grad.resize((w, h), Image.BILINEAR)
        dots = ImageDraw.Draw(self.base, "RGBA")
        step = int(54 * canvas.u)
        for y in range(step // 2, h, step):
            for x in range(step // 2, w, step):
                dots.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(255, 255, 255, 14))
        r = int(max(w, h) * 0.32)
        self.blobs = [
            (self._blob(r, brand.c("blob1")[:3], 70), 0.18, 0.22, 0.00),
            (self._blob(int(r * 1.15), brand.c("blob2")[:3], 80), 0.82, 0.75, 2.10),
            (self._blob(int(r * 0.7), brand.c("accent2")[:3], 38), 0.75, 0.15, 4.20),
        ]

    @staticmethod
    def _blob(radius, rgb, alpha):
        size = radius * 2
        im = Image.new("RGBA", (size, size), rgb + (0,))
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((size * 0.2, size * 0.2, size * 0.8, size * 0.8), fill=alpha)
        im.putalpha(mask.filter(ImageFilter.GaussianBlur(radius * 0.28)))
        return im

    def frame(self, t):
        img = self.base.copy()
        w, h = self.cv.w, self.cv.h
        for sprite, fx, fy, phase in self.blobs:
            dx = math.sin(t * 0.35 + phase) * w * 0.06
            dy = math.cos(t * 0.28 + phase) * h * 0.05
            x = int(fx * w + dx - sprite.width / 2)
            y = int(fy * h + dy - sprite.height / 2)
            img.paste(sprite, (x, y), sprite)
        return img


# ---------------------------------------------------------------- rich text

TOKEN_RE = re.compile(r"\*\*(.+?)\*\*")


def parse_rich(text):
    """'Is your **shop** ready?' -> [(word, highlighted, joined), ...]; '\n' kept as a token.

    `joined` is True when the word touches the previous one with no space (e.g. '**AI**?')."""
    out = []
    pos = 0
    for m in TOKEN_RE.finditer(text):
        out += _split(text[pos:m.start()], False, bool(out))
        out += _split(m.group(1), True, bool(out) and pos < m.start() and not text[m.start() - 1].isspace()
                      or (bool(out) and pos == m.start()))
        pos = m.end()
    out += _split(text[pos:], False, bool(out))
    return out


def _split(s, hl, may_join):
    words = []
    joined_first = may_join and s[:1] not in ("", " ", "\n", "\t")
    for i, line in enumerate(s.split("\n")):
        if i > 0:
            words.append(("\n", False, False))
        for j, wd in enumerate(line.split()):
            words.append((wd, hl, joined_first and i == 0 and j == 0))
    return words


@dataclass
class Word:
    text: str
    hl: bool
    x: float
    y: float
    w: float
    index: int


@dataclass
class TextLayout:
    words: list
    width: float
    height: float
    font: object
    line_h: float


def layout_rich(text, font, max_w, align="center", line_spacing=1.18):
    tokens = parse_rich(str(text))
    space = font.getlength(" ")
    asc, desc = font.getmetrics()
    line_h = (asc + desc) * line_spacing
    lines, cur, cur_w = [], [], 0.0
    for word, hl, joined in tokens:
        if word == "\n":
            lines.append((cur, cur_w))
            cur, cur_w = [], 0.0
            continue
        ww = font.getlength(word)
        joined = joined and bool(cur)
        add = ww if (not cur or joined) else space + ww
        if cur and not joined and cur_w + add > max_w:
            lines.append((cur, cur_w))
            cur, cur_w = [], 0.0
            add = ww
        cur.append((word, hl, ww, joined))
        cur_w += add
    if cur:
        lines.append((cur, cur_w))
    words, idx = [], 0
    width = max((lw for _, lw in lines), default=0)
    for li, (line, lw) in enumerate(lines):
        if align == "center":
            x = (max_w - lw) / 2
        elif align == "right":
            x = max_w - lw
        else:
            x = 0
        for k, (word, hl, ww, joined) in enumerate(line):
            if joined:
                x -= space
            words.append(Word(word, hl, x, li * line_h, ww, idx))
            idx += 1
            x += ww + space
    height = len(lines) * line_h - (line_h - (asc + desc)) if lines else 0
    return TextLayout(words, width if align == "left" else max_w, height, font, line_h)


def fit_text(brand, text, weight, size, max_w, max_lines=4, min_size=28, align="center"):
    """Shrink the font until the text fits in `max_lines` lines."""
    s = size
    while True:
        font = brand.font(weight, s)
        lay = layout_rich(text, font, max_w, align)
        lines = round(lay.height / lay.line_h + 0.49) if lay.words else 0
        if lines <= max_lines or s <= min_size:
            return lay
        s = int(s * 0.92)


def draw_rich(d, brand, lay, x0, y0, t, start=0.0, opacity=1.0, stagger=0.06,
              color="text", hl_color="accent", marker=True, rise=0.32):
    """Draw a TextLayout with a word-by-word reveal starting at `start` seconds."""
    font = lay.font
    size = font.size
    for wd in lay.words:
        p = enter(t, start + wd.index * stagger, 0.42) if stagger is not None else enter(t, start, 0.45)
        if p <= 0:
            continue
        a = p * opacity
        dy = (1 - p) * size * rise
        x, y = x0 + wd.x, y0 + wd.y + dy
        if wd.hl and marker:
            mp = enter(t, start + wd.index * stagger + 0.25, 0.4) if stagger is not None else p
            bar_top = y + size * 0.86
            d.rounded_rectangle(
                (x - size * 0.06, bar_top, x - size * 0.06 + (wd.w + size * 0.12) * mp, bar_top + size * 0.2),
                radius=size * 0.08, fill=brand.c(hl_color, 0.28 * a))
        d.text((x, y), wd.text, font=font, fill=brand.c(hl_color if wd.hl else color, a))


# ---------------------------------------------------------------- shapes & icons

def icon_check(d, cx, cy, r, color, bg=None):
    if bg:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    w = max(3, int(r * 0.22))
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.12, cy + r * 0.35), (cx + r * 0.48, cy - r * 0.32)],
           fill=color, width=w, joint="curve")


def icon_cross(d, cx, cy, r, color, bg=None):
    if bg:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    w = max(3, int(r * 0.22))
    k = r * 0.38
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=color, width=w)
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=color, width=w)


def icon_arrow(d, x, cy, size, color):
    w = max(3, int(size * 0.14))
    d.line([(x, cy), (x + size, cy)], fill=color, width=w)
    d.line([(x + size * 0.6, cy - size * 0.38), (x + size, cy), (x + size * 0.6, cy + size * 0.38)],
           fill=color, width=w, joint="curve")


def pill(d, brand, x, y, text, font, fg="bg_top", bg="accent", alpha=1.0, pad=None):
    pad = pad or font.size * 0.7
    tw = font.getlength(text)
    asc, desc = font.getmetrics()
    h = (asc + desc) + font.size * 0.5
    d.rounded_rectangle((x, y, x + tw + pad * 2, y + h), radius=h / 2, fill=brand.c(bg, alpha))
    d.text((x + pad, y + font.size * 0.25), text, font=font, fill=brand.c(fg, alpha))
    return tw + pad * 2, h


def card(d, brand, box, alpha=1.0, color="card", border="accent", border_alpha=0.0, radius=28):
    d.rounded_rectangle(box, radius=radius, fill=brand.c(color, 0.82 * alpha),
                        outline=brand.c(border, border_alpha * alpha) if border_alpha else None,
                        width=3 if border_alpha else 0)
