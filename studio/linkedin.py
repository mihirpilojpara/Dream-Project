"""LinkedIn carousel (1080x1350 PNG slides + one PDF to upload as a document) and post text."""

from pathlib import Path

from PIL import ImageDraw

from .draw import Background, card, draw_rich, fit_text, icon_arrow, icon_check, make_canvas, pill

DONE = 999.0  # draw everything fully revealed


def _slide(brand, cv, bg, slide, index, total):
    img = bg.frame(index * 1.7)
    d = ImageDraw.Draw(img, "RGBA")
    u = cv.u
    x, w = cv.left, cv.cw
    kind = slide.get("type", "point")

    # header: logo + handle
    mark = 52 * u
    d.rounded_rectangle((x, 70 * u, x + mark, 70 * u + mark), radius=mark * 0.28, fill=brand.c("accent"))
    f = brand.font("bold", mark * 0.62)
    d.text((x + (mark - f.getlength("A")) / 2, 70 * u + mark * 0.08), "A", font=f, fill=brand.c("bg_top"))
    fh = brand.font("bold", 32 * u)
    d.text((x + mark + 18 * u, 70 * u + mark * 0.12), brand.name, font=fh, fill=brand.c("text"))
    fpage = brand.font("medium", 28 * u)
    page = f"{index + 1}/{total}"
    d.text((cv.w - cv.right - fpage.getlength(page), 70 * u + mark * 0.18), page, font=fpage, fill=brand.c("muted"))

    blocks = []  # (height, fn(y))

    def text_block(text, size, weight="bold", color="text", align="left", lines=6, gap=36):
        lay = fit_text(brand, text, weight, size * u, w, max_lines=lines, align=align)
        blocks.append((lay.height, lambda y, lay=lay: draw_rich(d, brand, lay, x, y, DONE, stagger=None,
                                                                 color=color), gap * u))

    if kind == "cover":
        if slide.get("kicker"):
            fk = brand.font("bold", 30 * u)
            hk = sum(fk.getmetrics()) + fk.size * 0.5
            blocks.append((hk, lambda y: pill(d, brand, x, y, slide["kicker"].upper(), fk), 44 * u))
        text_block(slide["title"], 96, lines=5, gap=40)
        if slide.get("sub"):
            text_block(slide["sub"], 42, weight="regular", color="muted", gap=0)
    elif kind == "checklist":
        text_block(slide["title"], 72, lines=3, gap=50)
        fs = 42 * u
        for item in slide.get("items", []):
            lay = fit_text(brand, item, "medium", fs, w - 150 * u, max_lines=3, align="left")
            hgt = max(lay.height, 60 * u) + 56 * u

            def fn(y, lay=lay, hgt=hgt):
                card(d, brand, (x, y, x + w, y + hgt))
                icon_check(d, x + 62 * u, y + hgt / 2, 30 * u, brand.c("accent"), brand.c("accent", 0.18))
                draw_rich(d, brand, lay, x + 120 * u, y + (hgt - lay.height) / 2, DONE, stagger=None)

            blocks.append((hgt, fn, 22 * u))
    elif kind == "cta":
        text_block(slide["title"], 84, lines=4, gap=44)
        if slide.get("body"):
            text_block(slide["body"], 42, weight="regular", color="muted", gap=50)
        fb = brand.font("bold", 40 * u)
        label = slide.get("button", "Follow " + brand.handle)
        hb = sum(fb.getmetrics()) + fb.size * 0.9

        def btn(y):
            bw = fb.getlength(label) + fb.size * 2.2
            d.rounded_rectangle((x, y, x + bw, y + hb), radius=hb / 2, fill=brand.c("accent"))
            d.text((x + fb.size * 1.1, y + hb / 2 - fb.size * 0.62), label, font=fb, fill=brand.c("bg_top"))

        blocks.append((hb, btn, 0))
    else:  # point
        num = slide.get("number", index)
        fn_ = brand.font("bold", 150 * u)
        hn = fn_.size * 1.05
        blocks.append((hn, lambda y: d.text((x - 6 * u, y - fn_.size * 0.18), f"{num:02d}", font=fn_,
                                              fill=brand.c("accent", 0.9)), 24 * u))
        text_block(slide["title"], 74, lines=4, gap=40)
        if slide.get("body"):
            text_block(slide["body"], 42, weight="regular", color="muted", gap=0, lines=8)

    total_h = sum(h + g for h, _, g in blocks) - (blocks[-1][2] if blocks else 0)
    y = cv.top + max(0, (cv.ch - total_h) / 2)
    for h, fn, g in blocks:
        fn(y)
        y += h + g

    # footer
    ff = brand.font("medium", 30 * u)
    fy = cv.h - 105 * u
    d.text((x, fy), brand.handle, font=ff, fill=brand.c("muted"))
    if index < total - 1:
        lbl = "Swipe"
        lw = ff.getlength(lbl)
        rx = cv.w - cv.right - 46 * u
        d.text((rx - lw - 16 * u, fy), lbl, font=ff, fill=brand.c("accent"))
        icon_arrow(d, rx, fy + ff.size * 0.72, 40 * u, brand.c("accent"))
    return img


def auto_carousel(script):
    """Build a carousel from the video scenes if the script has no `linkedin.carousel`."""
    slides = [{"type": "cover", "title": script.get("title", ""), "kicker": script.get("slug", "")}]
    for sc in script.get("scenes", []):
        if sc.get("type") in ("statement", "hook") and sc is not script["scenes"][0]:
            slides.append({"type": "point", "title": sc["text"], "body": sc.get("sub", "")})
        elif sc.get("type") in ("bullets", "steps"):
            slides.append({"type": "checklist", "title": sc.get("heading", ""), "items": sc.get("items", [])})
        elif sc.get("type") == "cta":
            slides.append({"type": "cta", "title": sc.get("text", ""), "body": sc.get("sub", "")})
    return slides


def render_carousel(brand, script, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cv = make_canvas("carousel")
    bg = Background(brand, cv)
    slides = (script.get("linkedin") or {}).get("carousel") or auto_carousel(script)
    points = 0
    images = []
    for i, s in enumerate(slides):
        if s.get("type", "point") == "point":
            points += 1
            s = {**s, "number": s.get("number", points)}
        img = _slide(brand, cv, bg, s, i, len(slides))
        img.save(out_dir / f"slide-{i + 1:02d}.png")
        images.append(img)
    pdf = out_dir / "carousel.pdf"
    images[0].save(pdf, save_all=True, append_images=images[1:], resolution=150)
    return pdf, len(images)


def write_publish_notes(script, out_dir):
    """One markdown file with everything to copy-paste when posting."""
    out = Path(out_dir) / "publish.md"
    pub = script.get("publish") or {}
    li = script.get("linkedin") or {}
    vo = Path(out_dir) / "voiceover.txt"
    if vo.exists():
        lines_vo = [l for l in vo.read_text(encoding="utf-8").splitlines() if l[:1].isdigit()]
    lines = [f"# {script.get('title', '')}", ""]
    if vo.exists():
        lines += ["## Voiceover (read this, pause ~1s between lines)", ""] + lines_vo + [""]
    yt = pub.get("youtube")
    if yt:
        lines += ["## YouTube", "", f"**Title:** {yt.get('title', '')}", "", "**Description:**", "",
                  yt.get("description", "").strip(), ""]
        if yt.get("tags"):
            lines += [f"**Tags:** {', '.join(yt['tags'])}", ""]
    ig = pub.get("instagram")
    if ig:
        tags = " ".join("#" + h for h in ig.get("hashtags", []))
        lines += ["## Instagram Reel · Facebook Reel · YouTube Short caption", "", ig.get("caption", "").strip(), "",
                  tags, ""]
    if li and li.get("post"):
        tags = " ".join("#" + h for h in li.get("hashtags", []))
        lines += ["## LinkedIn post", "", li["post"].strip(), "", tags, "",
                  "_Attach `linkedin/carousel.pdf` as a document so it shows as a swipeable carousel._", ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
