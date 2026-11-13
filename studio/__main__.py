"""Command line for the AgentReady content studio.

  python -m studio render content/ep01-is-your-shop-ai-ready.yaml
  python -m studio render content/ep01.yaml --only reel
  python -m studio preview content/ep01.yaml --format youtube --scene 3
  python -m studio new "Why COD matters for AI shopping"
  python -m studio daily                      # today's scheduled post (from content/bank)
  python -m studio daily --date 2026-11-16 --days 7
  python -m studio plan                       # posting calendar
  python -m studio topic stat-92-percent      # one topic by id
"""

import argparse
import datetime as dt
import re
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from .brand import ROOT, load_brand
from .linkedin import render_carousel, write_publish_notes
from .rules import enforce
from .compose import compose, compose_weekly, is_weekly_day, load_bank, load_schedule, topic_for
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
    render_all(brand, script, Path(args.out) / script["slug"], only=args.only, no_video=args.no_video)


def render_all(brand, script, out, only=None, no_video=False):
    enforce(brand, script)
    out = Path(out)
    formats = [only] if only else script.get("formats", ["reel", "youtube"])
    fps = int(script.get("fps", 30))
    t0 = time.time()
    print(f"Rendering '{script.get('title', script['slug'])}' -> {out}")
    if not no_video:
        for fmt in formats:
            if fmt not in FORMAT_NAMES:
                print(f"  ! unknown format '{fmt}', skipping")
                continue
            tl = render_video(brand, fmt, script, out / f"{fmt}.mp4", fps=fps, audio=_audio_for(script, fmt))
            cover = render_still(brand, fmt, script, out / f"{fmt}-cover.png", scene_index=0)
            print(f"  ok {FORMAT_NAMES[fmt]}: {tl.total:.1f}s video + cover {cover.name}")
    if (not only or only == "linkedin") and script.get("linkedin") is not False:
        pdf, n = render_carousel(brand, script, out / "linkedin")
        print(f"  ok LinkedIn carousel: {n} slides + {pdf.name}")
    notes = write_publish_notes(script, out)
    print(f"  ok captions & post text: {notes.name}")
    print(f"Done in {time.time() - t0:.0f}s")


def _today(schedule):
    return dt.datetime.now(ZoneInfo(schedule.get("timezone", "Asia/Kolkata"))).date()


def _save_script(script, out):
    out.mkdir(parents=True, exist_ok=True)
    (out / "script.yaml").write_text(yaml.safe_dump(script, allow_unicode=True, sort_keys=False, width=110),
                                     encoding="utf-8")


def cmd_daily(args):
    """Render the scheduled content for a date (default: today) and N following days."""
    brand = load_brand(args.brand)
    topics = load_bank()
    schedule = load_schedule()
    start = dt.date.fromisoformat(args.date) if args.date else _today(schedule)
    for k in range(args.days):
        date = start + dt.timedelta(days=k)
        n, topic = topic_for(date, topics, schedule)
        if topic is None:
            print(f"{date}: nothing scheduled" + (" (before start_date)" if n is None else ""))
        else:
            script = compose(topic, brand, n)
            out = Path(args.out) / "daily" / f"{date}-{topic['id']}"
            _save_script(script, out)
            render_all(brand, script, out, no_video=args.no_video)
        if is_weekly_day(date, schedule) and not args.no_weekly:
            weekly = compose_weekly(date, topics, schedule, brand)
            if weekly:
                out = Path(args.out) / "daily" / f"{date}-{weekly['slug']}"
                _save_script(weekly, out)
                weekly["linkedin"] = False
                render_all(brand, weekly, out, no_video=args.no_video)


def cmd_topic(args):
    """Render one topic from the bank by id (any day)."""
    brand = load_brand(args.brand)
    topics = {t["id"]: t for t in load_bank()}
    if args.id not in topics:
        sys.exit(f"Unknown topic '{args.id}'. Run: python -m studio plan --all")
    script = compose(topics[args.id], brand, 0)
    if args.youtube:
        script["formats"] = ["reel", "youtube"]
    out = Path(args.out) / "topics" / args.id
    _save_script(script, out)
    render_all(brand, script, out, no_video=args.no_video)


def cmd_plan(args):
    """Print the posting calendar."""
    topics = load_bank()
    schedule = load_schedule()
    if args.all:
        for i, t in enumerate(topics, 1):
            print(f"{i:3}. [{t.get('pillar', '-'):<8}] {t['id']:<28} {t['title']}")
        return
    start = dt.date.fromisoformat(args.date) if args.date else max(_today(schedule), schedule["start_date"])
    print(f"Bank: {len(topics)} topics · start {schedule['start_date']} · weekly YouTube on "
          f"{schedule['weekly_youtube_day']}s\n")
    for k in range(args.days):
        d = start + dt.timedelta(days=k)
        _, t = topic_for(d, topics, schedule)
        extra = "  + weekly YouTube" if is_weekly_day(d, schedule) else ""
        label = f"[{t.get('pillar', '-'):<8}] {t['title']}" if t else "-"
        print(f"{d} {d.strftime('%a')}  {label}{extra}")


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

    dl = sub.add_parser("daily", help="render today's scheduled content (from the topic bank)")
    dl.add_argument("--date", help="YYYY-MM-DD (default: today in schedule timezone)")
    dl.add_argument("--days", type=int, default=1, help="also render the following N-1 days")
    dl.add_argument("--no-video", action="store_true")
    dl.add_argument("--no-weekly", action="store_true", help="skip the weekly YouTube compilation")
    dl.add_argument("--out", default="output")
    dl.set_defaults(fn=cmd_daily)

    tp = sub.add_parser("topic", help="render one topic from the bank by id")
    tp.add_argument("id")
    tp.add_argument("--youtube", action="store_true", help="also render a 16:9 version")
    tp.add_argument("--no-video", action="store_true")
    tp.add_argument("--out", default="output")
    tp.set_defaults(fn=cmd_topic)

    pl = sub.add_parser("plan", help="show the posting calendar")
    pl.add_argument("--date")
    pl.add_argument("--days", type=int, default=14)
    pl.add_argument("--all", action="store_true", help="list every topic in the bank")
    pl.set_defaults(fn=cmd_plan)

    n = sub.add_parser("new", help="create a new episode script from a template")
    n.add_argument("title")
    n.set_defaults(fn=cmd_new)

    args = ap.parse_args()
    if args.cmd == "render" and args.only == "linkedin":
        args.no_video = True
    args.fn(args)


if __name__ == "__main__":
    main()
