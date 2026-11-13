"""Turn a topic from content/bank/topics.yaml into a full script automatically.

A topic is just ideas (hook, point, stat, chat, checklist...). The composer picks
scenes, timings, kickers and calls-to-action, rotates CTA wording so daily posts
don't feel repetitive, and writes captions for Instagram, YouTube and LinkedIn.
"""

import datetime as dt
from pathlib import Path

import yaml

from .brand import ROOT

BANK = ROOT / "content" / "bank" / "topics.yaml"
SCHEDULE = ROOT / "content" / "schedule.yaml"

PILLAR_KICKERS = {
    "news": "AI shopping news",
    "myth": "Myth vs fact",
    "tip": "Seller tip",
    "demo": "Watch the AI",
    "shift": "The shift",
    "journey": "Building in public",
    "stat": "By the numbers",
}

# Rotated by day so CTAs vary. Follow/comment/save only: nothing is live yet.
CTAS = [
    {"text": "AI shopping ki aisi aur baatein? **Follow** karo", "button": "Follow {handle}", "sub": 'Comment "READY" for part 2'},
    {"text": "Kisi seller dost ko **share** karo", "button": "Follow {handle}", "sub": "Roz ek nayi AI shopping seekh"},
    {"text": "Baad mein kaam aayega. **Save** kar lo", "button": "Follow {handle}", "sub": "Daily tips for Indian sellers"},
    {"text": "Aapka sawaal? **Comment** mein likho", "button": "Follow {handle}", "sub": "Agla video aapke sawaal par"},
]

HASHTAGS = ["AgenticCommerce", "AIShopping", "D2CIndia", "EcommerceIndia", "SmallBusinessIndia", "AgentReady"]
LI_TAGS = ["AgenticCommerce", "D2CIndia", "Ecommerce", "AI", "BuildInPublic"]


def load_bank(path=BANK):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    topics = data.get("topics", [])
    ids = [t["id"] for t in topics]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"Duplicate topic ids in {path}: {', '.join(sorted(dupes))}")
    return topics


def words(text):
    return len(str(text).replace("**", "").split())


def secs(text, base=1.6, per_word=0.30, lo=2.6, hi=6.0):
    """Reading time for on-screen text."""
    return round(max(lo, min(hi, base + per_word * words(text))), 1)


def compose(topic, brand, day_index=0, linkedin=False):
    """Topic dict -> script dict (same shape as a hand-written content/*.yaml)."""
    pillar = topic.get("pillar", "tip")
    kicker = PILLAR_KICKERS.get(pillar, pillar.title())
    sc = [{"type": "hook", "text": topic["hook"], "duration": secs(topic["hook"], base=1.4, lo=2.6, hi=3.6)}]

    if topic.get("myth"):
        sc.append({"type": "statement", "kicker": "Myth", "size": "m", "text": topic["myth"],
                   "duration": secs(topic["myth"])})
        sc.append({"type": "statement", "kicker": "Fact", "size": "m", "text": topic["fact"],
                   "duration": secs(topic["fact"], hi=6.5)})
    if topic.get("news"):
        sc.append({"type": "statement", "kicker": kicker, "size": "m", "text": topic["news"],
                   "duration": secs(topic["news"], hi=7.0)})
    if topic.get("chat"):
        c = topic["chat"]
        sc.append({"type": "chat", "app": "AI shopping assistant", "user": c["user"],
                   "reply": c.get("reply", f"Here are {len(c.get('items', []))} options:"),
                   "items": c.get("items", []), "missing": c.get("missing"),
                   "duration": round(5.2 + 0.03 * len(c["user"]) + 0.45 * len(c.get("items", [])), 1)})
    if topic.get("stat"):
        s = topic["stat"]
        sc.append({"type": "stat", "kicker": kicker if pillar == "stat" else "The number",
                   "value": s["value"], "label": s["label"], "source": s.get("source"),
                   "duration": 4.4})
    if topic.get("point"):
        d = {"type": "statement", "text": topic["point"], "duration": secs(topic["point"], hi=5.0)}
        if topic.get("point_sub"):
            d["sub"] = topic["point_sub"]
            d["duration"] = round(d["duration"] + 1.0, 1)
        if not (topic.get("myth") or topic.get("news") or topic.get("chat")):
            d["kicker"] = kicker
        sc.append(d)
    if topic.get("compare"):
        cmp_ = topic["compare"]
        n = len(cmp_["left"].get("items", [])) + len(cmp_["right"].get("items", []))
        sc.append({"type": "compare", "heading": topic.get("compare_heading"), "left": cmp_["left"],
                   "right": cmp_["right"], "duration": round(3.0 + 0.55 * n, 1)})
    if topic.get("items"):
        n = len(topic["items"])
        sc.append({"type": "steps" if pillar in ("tip", "news") else "bullets",
                   "heading": topic.get("heading"), "items": topic["items"],
                   "icon": topic.get("icon") or ("number" if pillar in ("tip", "news") else "check"),
                   "duration": round(2.2 + 1.05 * n, 1)})

    cta = CTAS[day_index % len(CTAS)]
    sc.append({"type": "cta", "text": cta["text"], "button": cta["button"].format(handle=brand.handle),
               "sub": cta["sub"], "duration": 4.0})

    script = {
        "title": topic["title"],
        "slug": topic["id"],
        "formats": ["reel"],
        "fps": 30,
        "scenes": sc,
        "publish": _publish(topic, brand),
        "linkedin": _linkedin(topic, brand, kicker) if linkedin else False,
    }
    if topic.get("vo"):
        if len(topic["vo"]) != len(sc):
            raise SystemExit(f"Topic '{topic['id']}': `vo` has {len(topic['vo'])} lines but the video has "
                             f"{len(sc)} scenes. Give one line per scene.")
        for scene, line in zip(sc, topic["vo"]):
            scene["say"] = line
    return script


def _plain(text):
    return str(text).replace("**", "")


def _publish(topic, brand):
    caption = topic.get("caption")
    if not caption:
        lines = [_plain(topic["hook"])]
        if topic.get("point"):
            lines.append(_plain(topic["point"]))
        if topic.get("items"):
            lines.append("")
            lines += [f"✅ {_plain(i)}" for i in topic["items"]]
        lines += ["", f"Follow {brand.handle} for daily AI shopping tips for Indian sellers.",
                  "Save this and share it with a seller friend."]
        caption = "\n".join(lines)
    return {
        "youtube": {
            "title": f"{_plain(topic['title'])} #Shorts",
            "description": f"{_plain(topic.get('point', topic['hook']))}\n\nDaily AI shopping tips for Indian sellers. Follow {brand.handle}.",
            "tags": ["AI shopping", "agentic commerce", "D2C India", "ecommerce India", "UPI", "seller tips"],
        },
        "instagram": {"caption": caption, "hashtags": topic.get("tags", HASHTAGS)},
    }


def _linkedin(topic, brand, kicker):
    post = topic.get("linkedin") or "\n\n".join(
        x for x in [_plain(topic["title"]) + ".", _plain(topic.get("point", "")),
                    "\n".join(f"- {_plain(i)}" for i in topic.get("items", []))] if x)
    post = post.strip() + f"\n\nI share one AI-shopping lesson for Indian sellers every day. Follow along."
    slides = [{"type": "cover", "kicker": kicker, "title": topic["title"],
               "sub": _plain(topic["hook"])}]
    if topic.get("myth"):
        slides.append({"type": "point", "title": "Myth: " + _plain(topic["myth"]), "body": _plain(topic["fact"])})
    if topic.get("news"):
        slides.append({"type": "point", "title": "What happened", "body": _plain(topic["news"])})
    if topic.get("stat"):
        s = topic["stat"]
        slides.append({"type": "point", "title": f"{s['value']} {s['label']}", "body": "Source: " + s.get("source", "")})
    if topic.get("compare"):
        c = topic["compare"]
        slides.append({"type": "checklist", "title": c["right"].get("title", "Better"), "items": c["right"]["items"]})
    if topic.get("point"):
        slides.append({"type": "point", "title": topic["point"], "body": topic.get("point_sub", "")})
    if topic.get("items"):
        slides.append({"type": "checklist", "title": topic.get("heading") or "Checklist", "items": topic["items"]})
    slides.append({"type": "cta", "title": "Want more on **AI shopping**?",
                   "body": "One lesson a day for Indian sellers.", "button": f"Follow {brand.handle}"})
    return {"post": post, "hashtags": LI_TAGS, "carousel": slides}


# ------------------------------------------------------------------ calendar

def load_schedule(path=SCHEDULE):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    start = data.get("start_date")
    if isinstance(start, str):
        start = dt.date.fromisoformat(start)
    data["start_date"] = start or dt.date.today()
    data.setdefault("overrides", {})
    data.setdefault("skip", [])
    data.setdefault("weekly_youtube_day", "sunday")
    data.setdefault("when_bank_runs_out", "repeat")
    return data


def topic_for(date, topics, schedule):
    """Which topic is posted on `date`. Returns (index_in_calendar, topic) or (None, None)."""
    key = date.isoformat()
    overrides = {str(k): v for k, v in schedule["overrides"].items()}
    by_id = {t["id"]: t for t in topics}
    n = (date - schedule["start_date"]).days
    if n < 0:
        return None, None
    if key in overrides:
        tid = overrides[key]
        if tid not in by_id:
            raise SystemExit(f"schedule.yaml override {key}: unknown topic id '{tid}'")
        return n, by_id[tid]
    skipped = {str(s) for s in schedule["skip"]}
    if key in skipped:
        return n, None
    # count only non-skipped, non-overridden days before this one
    pos = sum(1 for i in range(n)
              if (schedule["start_date"] + dt.timedelta(days=i)).isoformat() not in skipped | set(overrides))
    if pos >= len(topics):
        if schedule["when_bank_runs_out"] == "stop":
            return n, None
        pos %= len(topics)
    return n, topics[pos]


WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def is_weekly_day(date, schedule):
    return WEEKDAYS[date.weekday()] == str(schedule["weekly_youtube_day"]).lower()


def week_topics(date, topics, schedule):
    """[(date, topic), ...] posted in the 7 days ending on `date` (unique topics)."""
    out, seen = [], set()
    for i in range(6, -1, -1):
        d = date - dt.timedelta(days=i)
        _, t = topic_for(d, topics, schedule)
        if t and t["id"] not in seen:
            out.append((d, t))
            seen.add(t["id"])
    return out


def compose_weekly(date, topics, schedule, brand, voice_lookup=None):
    """A 16:9 YouTube video stitching the last 7 days' lessons into one episode.

    voice_lookup(day, topic) -> recording path or None. Lessons with a recording reuse it
    (minus its closing CTA line), so the weekly video needs no extra recording.
    Returns (script, segments) where segments = [(audio_path_or_None, seconds), ...]
    describing the soundtrack in order.
    """
    from .voice import apply_voice

    picked = week_topics(date, topics, schedule)
    if not picked:
        return None, []
    week_no = max(1, (date - schedule["start_date"]).days // 7 + 1)
    intro = {"type": "title", "kicker": f"AgentReady weekly · {week_no}",
             "text": "Is hafte ki **AI shopping** seekh", "sub": f"{len(picked)} lessons for Indian sellers",
             "duration": 4.0}
    scenes, segments = [intro], [(None, 4.0)]
    for i, (day, t) in enumerate(picked, 1):
        part = compose(t, brand, i)
        rec = voice_lookup(day, t) if voice_lookup else None
        if rec:
            apply_voice(part, rec)
        body = part["scenes"][:-1]  # drop the CTA
        body[0] = {**body[0], "type": "title", "kicker": f"Lesson {i}", "text": t["hook"], "size": "l"}
        body[0].setdefault("duration", 3.4)
        scenes += body
        segments.append((rec, round(sum(x["duration"] for x in body), 2)))
    outro = {"type": "cta", "text": "Har hafte aisi seekh? **Subscribe** karo",
             "button": f"Subscribe · {brand.handle}", "sub": "Roz ek nayi AI shopping seekh", "duration": 4.5}
    scenes.append(outro)
    segments.append((None, 4.5))
    titles = "\n".join(f"{i}. {_plain(t['title'])}" for i, (_, t) in enumerate(picked, 1))
    script = {
        "title": f"AI Shopping for Indian Sellers: Week {week_no}",
        "slug": f"weekly-{week_no:02d}",
        "formats": ["youtube"],
        "fps": 30,
        "scenes": scenes,
        "linkedin": False,
        "publish": {"youtube": {
            "title": f"AI Shopping for Indian Sellers — Week {week_no} ({len(picked)} lessons)",
            "description": f"This week's lessons:\n{titles}\n\nNew lessons every week. Subscribe and follow {brand.handle}.",
            "tags": ["AI shopping", "agentic commerce", "D2C India", "ecommerce India", "UPI", "ONDC"]}},
    }
    return script, segments
