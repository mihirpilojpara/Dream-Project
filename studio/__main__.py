"""Command line for the AgentReady content studio.

  python -m studio render content/ep01-is-your-shop-ai-ready.yaml
  python -m studio render content/ep01.yaml --only reel
  python -m studio preview content/ep01.yaml --format youtube --scene 3
  python -m studio new "Why COD matters for AI shopping"
"""

import argparse
import re
import sys
import time
from pathlib import Path

import yaml

from .brand import ROOT, load_brand
from .linkedin import render_carousel, write_publish_notes
from .rules import enforce
from .video import render_still, render_video

FORMAT_NAMES = {"youtube": "YouTube (16:9)", "reel": "Reel / Short (9:16)", "square": "Square post (1:1)"}


def load_script(path):
    path = Path(path)
    if not path.exists():
        sys.exit(f"Script not found: {path}")
    script = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not script or not script.get("scenes"):
        sys.exit("The script needs a `scenes:` list.")
    script.setdefault("slug", path.stem)
    return script


def _audio_for(script, fmt):
    def pick(value):
        if isinstance(value, dict):
            value = value.get(fmt)
        if value and not (ROOT / value).exists() and not Path(value).exists():
            print(f"  ! audio file not found, skipping: {value}")
            return None
        return value and str(ROOT / value if (ROOT / value).exists() else value)

    return {"music": pick(script.get("music")), "voiceover": pick(script.get("voiceover"))}


def cmd_render(args):
    brand = load_brand(args.brand)
    script = load_script(args.script)
    enforce(brand, script)
    out = Path(args.out) / script["slug"]
    formats = [args.only] if args.only else script.get("formats", ["reel", "youtube"])
    fps = int(script.get("fps", 30))
    t0 = time.time()
    print(f"Rendering '{script.get('title', script['slug'])}' -> {out}")
    if not args.no_video:
        for fmt in formats:
            if fmt not in FORMAT_NAMES:
                print(f"  ! unknown format '{fmt}', skipping")
                continue
            tl = render_video(brand, fmt, script, out / f"{fmt}.mp4", fps=fps, audio=_audio_for(script, fmt))
            cover = render_still(brand, fmt, script, out / f"{fmt}-cover.png", scene_index=0)
            print(f"  ok {FORMAT_NAMES[fmt]}: {tl.total:.1f}s video + cover {cover.name}")
    if not args.only or args.only == "linkedin":
        pdf, n = render_carousel(brand, script, out / "linkedin")
        print(f"  ok LinkedIn carousel: {n} slides + {pdf.name}")
    notes = write_publish_notes(script, out)
    print(f"  ok captions & post text: {notes.name}")
    print(f"Done in {time.time() - t0:.0f}s")


def cmd_preview(args):
    brand = load_brand(args.brand)
    script = load_script(args.script)
    out = Path(args.out) / script["slug"] / "previews"
    fmt = args.format
    if args.scene is None:
        n = len([s for s in script["scenes"] if not s.get("only") or fmt in str(s.get("only"))])
        indexes = range(n)
    else:
        indexes = [args.scene]
    for i in indexes:
        p = render_still(brand, fmt, script, out / f"{fmt}-scene{i + 1:02d}.png", scene_index=i, at=99)
        print(f"  {p}")


TEMPLATE = """# {title}
title: {title}
slug: {slug}
formats: [reel, youtube]
fps: 30

scenes:
  - type: hook
    text: Your **hook** goes here
    duration: 3

  - type: statement
    kicker: The problem
    text: Explain the **one idea** of this video
    sub: A short supporting line
    duration: 4

  - type: stat
    value: 92%
    label: a **number** that proves your point
    source: Where the number comes from
    duration: 4

  - type: steps
    heading: 3 things to do today
    items:
      - First **action**
      - Second action
      - Third action
    duration: 6

  - type: cta
    text: Aisi aur tips ke liye **Follow** karo
    button: Follow {{handle}}
    sub: Comment "READY" for part 2
    duration: 4

publish:
  youtube:
    title: "{title}"
    description: |
      Describe the video here.
    tags: [agentic commerce, D2C India]
  instagram:
    caption: |
      Caption for the Reel / Short.
    hashtags: [AgenticCommerce, D2CIndia, AgentReady]

linkedin:
  post: |
    Write your LinkedIn post here.
  hashtags: [AgenticCommerce, BuildInPublic]
  # carousel: leave out to auto-build slides from the scenes above
"""


def cmd_new(args):
    slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")[:60]
    existing = sorted(Path(ROOT / "content").glob("ep*.yaml"))
    num = len(existing) + 1
    path = ROOT / "content" / f"ep{num:02d}-{slug}.yaml"
    handle = load_brand(args.brand).handle
    text = TEMPLATE.format(title=args.title, slug=f"ep{num:02d}-{slug}").replace("{handle}", handle)
    path.write_text(text, encoding="utf-8")
    print(f"Created {path.relative_to(ROOT)} - edit it, then run:\n  python -m studio render {path.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(prog="studio", description="AgentReady content studio")
    ap.add_argument("--brand", default=None, help="path to brand.yaml (default: ./brand.yaml)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="render videos, carousel and captions for a script")
    r.add_argument("script")
    r.add_argument("--only", choices=["youtube", "reel", "square", "linkedin"])
    r.add_argument("--no-video", action="store_true", help="skip videos (carousel + captions only)")
    r.add_argument("--out", default="output")
    r.set_defaults(fn=cmd_render)

    p = sub.add_parser("preview", help="save still PNGs of scenes (fast)")
    p.add_argument("script")
    p.add_argument("--format", default="reel", choices=list(FORMAT_NAMES))
    p.add_argument("--scene", type=int, default=None, help="0-based scene index (default: all)")
    p.add_argument("--out", default="output")
    p.set_defaults(fn=cmd_preview)

    n = sub.add_parser("new", help="create a new episode script from a template")
    n.add_argument("title")
    n.set_defaults(fn=cmd_new)

    args = ap.parse_args()
    if args.cmd == "render" and args.only == "linkedin":
        args.no_video = True
    args.fn(args)


if __name__ == "__main__":
    main()
