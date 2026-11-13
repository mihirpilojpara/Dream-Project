"""Scene types. Each scene measures its layout once, then draws itself at any time t.

Every scene is vertically centred inside the format's safe area, so the same
script looks right in 16:9 (YouTube) and 9:16 (Reels / Shorts).
"""

import re

from .anim import enter, progress, pulse, ease_out_back
from .draw import (card, draw_rich, fit_text, icon_arrow, icon_check, icon_cross,
                   layout_rich, pill)


class Scene:
    default_duration = 4.0

    def __init__(self, brand, cv, data):
        self.b, self.cv, self.data = brand, cv, data
        self.duration = float(data.get("duration", self.default_duration))
        self.u = cv.u
        # Build, and if the content is taller than the safe area, shrink and rebuild.
        for _ in range(4):
            self.blocks = []  # (height, draw_fn(d, y, t, op), gap_after)
            self.build()
            total = sum(h + g for h, _, g in self.blocks) - (self.blocks[-1][2] if self.blocks else 0)
            if total <= cv.ch:
                break
            self.u *= max(0.6, cv.ch / total * 0.97)
        self.y0 = cv.top + max(0, (cv.ch - total) / 2)

    def add(self, height, fn, gap=0):
        self.blocks.append((height, fn, gap))

    def build(self):
        raise NotImplementedError

    def draw(self, d, t, op):
        y = self.y0
        for h, fn, gap in self.blocks:
            fn(d, y, t, op)
            y += h + gap

    # shared pieces --------------------------------------------------------
    def add_kicker(self, text, start=0.0, align="center"):
        font = self.b.font("bold", 30 * self.u)
        h = (sum(font.getmetrics())) + font.size * 0.5

        def fn(d, y, t, op):
            p = enter(t, start, 0.4)
            if p <= 0:
                return
            w = font.getlength(text.upper()) + font.size * 1.4
            x = self.cv.left + (self.cv.cw - w) / 2 if align == "center" else self.cv.left
            pill(d, self.b, x, y + (1 - p) * 12, text.upper(), font, alpha=p * op)

        self.add(h, fn, gap=34 * self.u)

    def add_text(self, text, size, weight="bold", start=0.0, align="center", color="text",
                 max_lines=5, stagger=0.06, gap=30, max_w=None):
        max_w = min(self.cv.cw, max_w or self.cv.cw)
        lay = fit_text(self.b, text, weight, size * self.u, max_w, max_lines=max_lines, align=align)
        x0 = self.cv.left + (self.cv.cw - max_w) / 2 if align == "center" else self.cv.left

        def fn(d, y, t, op):
            draw_rich(d, self.b, lay, x0, y, t, start=start, opacity=op, stagger=stagger, color=color)

        self.add(lay.height, fn, gap=gap * self.u)
        return lay


# -------------------------------------------------------------------- statement

class Statement(Scene):
    """Big words that reveal one by one. Use for hooks, key ideas, punchlines."""
    default_duration = 3.5
    SIZES = {"xl": 104, "l": 82, "m": 64}

    def build(self):
        dd = self.data
        if dd.get("kicker"):
            self.add_kicker(dd["kicker"])
        size = self.SIZES.get(dd.get("size", "l"), 82)
        lay = self.add_text(dd["text"], size, start=0.15, gap=36)
        if dd.get("sub"):
            words = len(lay.words)
            self.add_text(dd["sub"], 40, weight="regular", color="muted",
                          start=0.3 + words * 0.06, stagger=None, gap=0)


class Hook(Statement):
    def build(self):
        self.data.setdefault("size", "xl")
        super().build()


class Title(Statement):
    default_duration = 4.0

    def build(self):
        self.data.setdefault("size", "xl")
        super().build()


# -------------------------------------------------------------------- bullets

class Bullets(Scene):
    """Heading + items that appear one by one on cards (icon: check | cross | number | arrow)."""
    default_duration = 6.0

    def build(self):
        dd = self.data
        items = dd.get("items", [])
        if dd.get("kicker"):
            self.add_kicker(dd["kicker"])
        if dd.get("heading"):
            self.add_text(dd["heading"], 66, start=0.1, gap=44, max_lines=3)
        icon = dd.get("icon", "check")
        n = max(1, len(items))
        gap_t = min(1.0, max(0.35, (self.duration - 1.8) / n))
        font_size = (44 if self.cv.vertical else 42) * self.u
        r = font_size * 0.62
        pad = font_size * 0.62
        max_w = min(self.cv.cw, 1200 * self.u)
        x0 = self.cv.left + (self.cv.cw - max_w) / 2
        text_w = max_w - pad * 3 - r * 2
        for i, item in enumerate(items):
            lay = fit_text(self.b, item, "medium", font_size, text_w, max_lines=3, align="left")
            hgt = max(lay.height, r * 2) + pad * 1.6
            start = 0.6 + i * gap_t

            def fn(d, y, t, op, lay=lay, hgt=hgt, start=start, i=i):
                p = enter(t, start, 0.45)
                if p <= 0:
                    return
                a = p * op
                dx = (1 - p) * 60 * self.u
                card(d, self.b, (x0 + dx, y, x0 + dx + max_w, y + hgt), alpha=a)
                cx, cy = x0 + dx + pad + r, y + hgt / 2
                color = "danger" if icon == "cross" else "accent"
                bg = self.b.c(color, 0.18 * a)
                if icon == "cross":
                    icon_cross(d, cx, cy, r, self.b.c("danger", a), bg)
                elif icon == "number":
                    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=self.b.c("accent", a))
                    f = self.b.font("bold", r * 1.1)
                    s = str(i + 1)
                    d.text((cx - f.getlength(s) / 2, cy - r * 0.68), s, font=f, fill=self.b.c("bg_top", a))
                elif icon == "arrow":
                    icon_arrow(d, cx - r * 0.6, cy, r * 1.2, self.b.c("accent", a))
                else:
                    icon_check(d, cx, cy, r, self.b.c("accent", a), bg)
                tx = cx + r + pad
                draw_rich(d, self.b, lay, tx, y + (hgt - lay.height) / 2, t, start=start,
                          opacity=op, stagger=None)

            self.add(hgt, fn, gap=22 * self.u)


# -------------------------------------------------------------------- stat

NUM_RE = re.compile(r"(\d[\d,]*\.?\d*)")


class Stat(Scene):
    """A big number that counts up, with a label and an optional source line."""
    default_duration = 4.0

    def build(self):
        dd = self.data
        value = str(dd["value"])
        m = NUM_RE.search(value)
        font = self.b.font("bold", (230 if self.cv.vertical else 210) * self.u)
        while font.getlength(value) > self.cv.cw and font.size > 60:
            font = self.b.font("bold", font.size * 0.9)
        h = sum(font.getmetrics())

        def fmt(p):
            if not m:
                return value
            raw = m.group(1)
            num = float(raw.replace(",", ""))
            decimals = len(raw.split(".")[1]) if "." in raw else 0
            cur = num * p
            s = f"{cur:,.{decimals}f}" if "," in raw else f"{cur:.{decimals}f}"
            return value[:m.start()] + s + value[m.end():]

        def fn(d, y, t, op):
            p = enter(t, 0.1, 0.4)
            count = 1 - (1 - progress(t, 0.15, 1.3)) ** 3
            txt = fmt(count)
            full_w = font.getlength(fmt(1.0))
            x = self.cv.left + (self.cv.cw - full_w) / 2
            d.text((x, y + (1 - p) * 30), txt, font=font, fill=self.b.c("accent", p * op))

        if dd.get("kicker"):
            self.add_kicker(dd["kicker"])
        self.add(h, fn, gap=10 * self.u)
        if dd.get("label"):
            self.add_text(dd["label"], 58, start=0.9, gap=30)
        if dd.get("source"):
            self.add_text("Source: " + dd["source"], 28, weight="regular", color="muted",
                          start=1.6, stagger=None)


# -------------------------------------------------------------------- chat

class Chat(Scene):
    """Fake AI-assistant chat: user types a question, the AI answers with a list."""
    default_duration = 7.0

    def build(self):
        dd = self.data
        u = self.u
        max_w = min(self.cv.cw, 1300 * u)
        self.x0 = self.cv.left + (self.cv.cw - max_w) / 2
        self.max_w = max_w
        fs = (44 if self.cv.vertical else 40) * u
        self.pad = 30 * u
        bubble_w = max_w * 0.86
        self.user_text = dd.get("user", "")
        self.user_font = self.b.font("medium", fs)
        self.user_lay = layout_rich(self.user_text, self.user_font, bubble_w - self.pad * 2, "left")
        self.user_h = self.user_lay.height + self.pad * 2
        self.type_dur = min(2.2, 0.035 * len(self.user_text))
        reply = dd.get("reply", "")
        self.reply_lay = layout_rich(reply, self.b.font("medium", fs), bubble_w - self.pad * 2, "left") if reply else None
        self.items = []
        item_font = self.b.font("medium", fs * 0.95)
        for it in dd.get("items", []):
            if isinstance(it, str):
                it = {"name": it}
            label = it["name"] + (f"  ·  {it['note']}" if it.get("note") else "")
            self.items.append((layout_rich(label, item_font, bubble_w - self.pad * 2 - 60 * u, "left"), it))
        self.reply_h = self.pad * 2 + (self.reply_lay.height + 24 * u if self.reply_lay else 0)
        self.reply_h += sum(l.height + 22 * u for l, _ in self.items)
        self.bubble_w = bubble_w
        self.t_reply = 0.4 + self.type_dur + 1.0
        if dd.get("app"):
            self.add_kicker(dd["app"], align="center")
        self.add(self.user_h, self.draw_user, gap=36 * u)
        self.add(self.reply_h, self.draw_reply, gap=40 * u)
        if dd.get("missing"):
            last = self.t_reply + 0.5 + len(self.items) * 0.45
            self.add_text(dd["missing"], 48, start=last, gap=0, max_lines=3)

    def draw_user(self, d, y, t, op):
        p = enter(t, 0.2, 0.35)
        if p <= 0:
            return
        x1 = self.x0 + self.max_w
        x0 = x1 - self.bubble_w
        d.rounded_rectangle((x0, y, x1, y + self.user_h), radius=34 * self.u,
                            fill=self.b.c("accent", 0.95 * p * op))
        shown = int(len(self.user_text) * progress(t, 0.4, self.type_dur))
        lay = layout_rich(self.user_text[:shown] or " ", self.user_font, self.bubble_w - self.pad * 2, "left")
        for wd in lay.words:
            d.text((x0 + self.pad + wd.x, y + self.pad + wd.y), wd.text, font=self.user_font,
                   fill=self.b.c("bg_top", p * op))

    def draw_reply(self, d, y, t, op):
        u = self.u
        x0 = self.x0
        if t < self.t_reply:
            p = enter(t, 0.4 + self.type_dur + 0.1, 0.3)
            if p <= 0:
                return
            d.rounded_rectangle((x0, y, x0 + 190 * u, y + 90 * u), radius=34 * u, fill=self.b.c("card", 0.9 * p * op))
            for i in range(3):
                k = (pulse(t * 1.4 + i * 0.25, 2.5, 0.5) - 0.5)
                d.ellipse((x0 + (48 + i * 46) * u - 9 * u, y + 45 * u - 9 * u - k * 8 * u,
                           x0 + (48 + i * 46) * u + 9 * u, y + 45 * u + 9 * u - k * 8 * u),
                          fill=self.b.c("muted", p * op))
            return
        p = enter(t, self.t_reply, 0.35)
        d.rounded_rectangle((x0, y, x0 + self.bubble_w, y + self.reply_h), radius=34 * u,
                            fill=self.b.c("card", 0.92 * p * op))
        cy = y + self.pad
        if self.reply_lay:
            draw_rich(d, self.b, self.reply_lay, x0 + self.pad, cy, t, start=self.t_reply, opacity=op, stagger=0.03)
            cy += self.reply_lay.height + 24 * u
        for i, (lay, it) in enumerate(self.items):
            start = self.t_reply + 0.5 + i * 0.45
            q = enter(t, start, 0.35)
            if q > 0:
                color = "danger" if it.get("bad") else "accent"
                d.ellipse((x0 + self.pad, cy + lay.font.size * 0.42, x0 + self.pad + 18 * u,
                           cy + lay.font.size * 0.42 + 18 * u), fill=self.b.c(color, q * op))
            draw_rich(d, self.b, lay, x0 + self.pad + 48 * u, cy, t, start=start, opacity=op, stagger=None)
            cy += lay.height + 22 * u


# -------------------------------------------------------------------- compare

class Compare(Scene):
    """Two cards: before (cross) vs after (check). Side by side on 16:9, stacked on 9:16."""
    default_duration = 7.0

    def build(self):
        dd = self.data
        u = self.u
        if dd.get("heading"):
            self.add_text(dd["heading"], 62, start=0.1, gap=40, max_lines=2)
        side = not self.cv.vertical
        gap = 40 * u
        cw = (self.cv.cw - gap) / 2 if side else self.cv.cw
        pad = 36 * u
        fs = 38 * u
        cols = []
        for key, good in (("left", False), ("right", True)):
            col = dd.get(key, {})
            title_lay = fit_text(self.b, col.get("title", ""), "bold", 46 * u, cw - pad * 2, 2, align="left")
            item_lays = [fit_text(self.b, it, "medium", fs, cw - pad * 2 - 64 * u, 3, align="left")
                         for it in col.get("items", [])]
            h = pad * 2 + title_lay.height + 28 * u + sum(l.height + 20 * u for l in item_lays)
            cols.append((title_lay, item_lays, h, good))
        n_left = len(cols[0][1])
        t_right = 0.6 + n_left * 0.45 + 0.4

        def draw_col(d, x, y, col, h, start, op):
            title_lay, item_lays, _, good = col
            p = enter(t_global[0], start, 0.45)
            if p <= 0:
                return
            color = "accent" if good else "danger"
            card(d, self.b, (x, y + (1 - p) * 40, x + cw, y + h + (1 - p) * 40), alpha=p * op,
                 border=color, border_alpha=0.9)
            yy = y + pad + (1 - p) * 40
            draw_rich(d, self.b, title_lay, x + pad, yy, t_global[0], start=start, opacity=op,
                      stagger=None, color=color)
            yy += title_lay.height + 28 * u
            for i, lay in enumerate(item_lays):
                s = start + 0.35 + i * 0.45
                q = enter(t_global[0], s, 0.35)
                if q > 0:
                    r = fs * 0.5
                    cx, cy = x + pad + r, yy + fs * 0.62
                    (icon_check if good else icon_cross)(d, cx, cy, r, self.b.c(color, q * op),
                                                          self.b.c(color, 0.18 * q * op))
                draw_rich(d, self.b, lay, x + pad + 64 * u, yy, t_global[0], start=s, opacity=op, stagger=None)
                yy += lay.height + 20 * u

        t_global = [0.0]
        if side:
            h = max(cols[0][2], cols[1][2])

            def fn(d, y, t, op):
                t_global[0] = t
                draw_col(d, self.cv.left, y, cols[0], h, 0.5, op)
                draw_col(d, self.cv.left + cw + gap, y, cols[1], h, t_right, op)

            self.add(h, fn)
        else:
            def fl(d, y, t, op):
                t_global[0] = t
                draw_col(d, self.cv.left, y, cols[0], cols[0][2], 0.5, op)

            def fr(d, y, t, op):
                t_global[0] = t
                draw_col(d, self.cv.left, y, cols[1], cols[1][2], t_right, op)

            self.add(cols[0][2], fl, gap=gap)
            self.add(cols[1][2], fr)


# -------------------------------------------------------------------- CTA

class CTA(Scene):
    """Closing call to action with a pulsing button and your handle."""
    default_duration = 4.5

    def build(self):
        dd = self.data
        u = self.u
        self.add_text(dd.get("text", "Follow for more"), 74, start=0.1, gap=56)
        label = dd.get("button", "Follow " + self.b.handle)
        font = self.b.font("bold", 46 * u)
        bh = sum(font.getmetrics()) + font.size * 0.9

        def fn(d, y, t, op):
            p = ease_out_back(progress(t, 0.7, 0.5))
            if p <= 0:
                return
            k = p * pulse(t, 1.6, 0.035)
            w = (font.getlength(label) + font.size * 2.2) * k
            hh = bh * k
            cx = self.cv.left + self.cv.cw / 2
            cy = y + bh / 2
            a = min(1.0, max(0.0, p)) * op
            glow = 18 * u * (0.6 + 0.4 * pulse(t, 1.6, 1))
            d.rounded_rectangle((cx - w / 2 - glow, cy - hh / 2 - glow, cx + w / 2 + glow, cy + hh / 2 + glow),
                                radius=hh, fill=self.b.c("accent", 0.12 * a))
            d.rounded_rectangle((cx - w / 2, cy - hh / 2, cx + w / 2, cy + hh / 2), radius=hh / 2,
                                fill=self.b.c("accent", a))
            f = self.b.font("bold", font.size * k)
            d.text((cx - f.getlength(label) / 2, cy - f.size * 0.62), label, font=f, fill=self.b.c("bg_top", a))

        self.add(bh, fn, gap=44 * u)
        sub = dd.get("sub", self.b.website or self.b.handle)
        if sub:
            self.add_text(sub, 36, weight="medium", color="muted", start=1.2, stagger=None)


SCENES = {
    "hook": Hook,
    "title": Title,
    "statement": Statement,
    "bullets": Bullets,
    "steps": Bullets,
    "stat": Stat,
    "chat": Chat,
    "compare": Compare,
    "cta": CTA,
}


def make_scene(brand, cv, data):
    kind = data.get("type", "statement")
    if kind not in SCENES:
        raise ValueError(f"Unknown scene type '{kind}'. Use one of: {', '.join(SCENES)}")
    if kind == "steps":
        data = {**data, "icon": data.get("icon", "number")}
    return SCENES[kind](brand, cv, dict(data))
