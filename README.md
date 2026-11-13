# Dream-Project · AgentReady

**AgentReady** helps small Indian shops and D2C brands get found and bought by AI shopping agents (ChatGPT, Gemini, UPI agent payments, ONDC).

This repo starts with the **AgentReady Content Studio**, a tool that turns one simple script into:

| Output | Size | Use it for |
|---|---|---|
| `reel.mp4` | 1080×1920 (9:16) | Instagram Reels, YouTube Shorts |
| `youtube.mp4` | 1920×1080 (16:9) | YouTube videos |
| `reel-cover.png`, `youtube-cover.png` | same | Cover / thumbnail |
| `linkedin/carousel.pdf` + `slide-XX.png` | 1080×1350 | LinkedIn carousel post |
| `publish.md` | text | YouTube title + description, Instagram caption, LinkedIn post, hashtags |

You write the words once. The studio animates them in your brand colours.

---

## 1. Set up (one time)

You need **Python 3.10+** and **ffmpeg**.

```bash
# Windows:  winget install Python.Python.3.12  and  winget install ffmpeg
# Mac:      brew install python ffmpeg
git clone https://github.com/mihirpilojpara/Dream-Project.git
cd Dream-Project
pip install -r requirements.txt
```

**Don't want to install anything?** Push a script to `content/` and GitHub renders it for you.
Go to the **Actions** tab, open the latest **Render content** run, and download **rendered-content** under Artifacts.
You can also click **Run workflow** there to render on demand.

## 2. Make content

```bash
# render the sample episode (videos + carousel + captions), about 30 seconds
python -m studio render content/ep01-is-your-shop-ai-ready.yaml

# start a new episode from a template
python -m studio new "Why COD matters for AI shopping"

# quick still previews of every scene, without rendering video
python -m studio preview content/ep02-why-cod-matters-for-ai-shopping.yaml --format reel

# render only one format
python -m studio render content/ep01-is-your-shop-ai-ready.yaml --only reel
```

Everything lands in `output/<episode-slug>/`.

## 3. Daily content on autopilot

You don't write a new script every day. Ideas live in a **content bank** and a **calendar** decides what goes out each day:

| File | What it is |
|---|---|
| `content/bank/topics.yaml` | 31 ready topics (news, myths, tips, AI demos, stats, building-in-public). Add more any time. |
| `content/schedule.yaml` | Start date, days to skip, topics pinned to a date (for breaking news), and the weekly YouTube day |
| `studio/compose.py` | Turns a topic into a full Reel/Short, LinkedIn carousel and captions, rotating formats and CTAs |

```bash
python -m studio plan                         # what posts on which day (next 14 days)
python -m studio plan --all                   # every topic in the bank
python -m studio daily                        # render today's post
python -m studio daily --date 2026-11-16 --days 7   # render a whole week ahead
python -m studio topic stat-92-percent --youtube    # render any topic on demand
```

Every day you get `output/daily/<date>-<topic>/` with `reel.mp4`, `reel-cover.png`, `linkedin/carousel.pdf`, `publish.md` (ready-to-paste captions)
and `script.yaml` (the generated script, if you want to tweak and re-render it).
On **Sundays** you also get a ~2-minute 16:9 **YouTube** video stitching the week's lessons together.

**Fully automatic:** `.github/workflows/daily.yml` renders today's content on GitHub every morning at 05:30 IST.
Open **Actions → Daily content → latest run**: the captions are on the summary page and the videos are under **Artifacts**.
Your only daily job is to post them (about 5 minutes).

To add a topic, append it to `content/bank/topics.yaml`. Only `id`, `title` and `hook` are required. The comments at the top of the file list every optional field.

## 4. Writing a script by hand

A script is a YAML file in `content/`. Each scene is one animated "slide". Words in `**double stars**` get the accent colour and a highlighter.

```yaml
title: Is your shop visible to AI?
formats: [reel, youtube]
scenes:
  - type: hook
    text: Aapki shop **ChatGPT** ko dikhti hai?
    duration: 3
```

### Scene types

| Type | What it shows | Fields |
|---|---|---|
| `hook` | Huge words, revealed one by one. Use it for the first 3 seconds. | `text`, `sub` |
| `title` / `statement` | A key idea. `size: xl / l / m` | `text`, `kicker`, `sub` |
| `stat` | A number that counts up | `value` (e.g. `92%`, `₹500 Cr`), `label`, `source`, `kicker` |
| `chat` | A fake AI-assistant chat: question typed, AI replies with a list | `app`, `user`, `reply`, `items` (`name`, `note`, `bad: true`), `missing` |
| `bullets` | Items on cards, one by one | `heading`, `items`, `icon: check / cross / arrow / number` |
| `steps` | Same as bullets, numbered | `heading`, `items` |
| `compare` | Before vs after cards (side by side on YouTube, stacked on Reels) | `heading`, `left`/`right` → `title`, `items` |
| `cta` | Closing line + pulsing button | `text`, `button`, `sub` |

Every scene also accepts:
- `duration`: seconds on screen.
- `only: youtube` or `only: reel`: show the scene in one format only. This lets the YouTube version go deeper while the Reel stays short.

### Audio (optional)

```yaml
music: assets/music/background.mp3        # loops, fades out at the end
voiceover:
  reel: assets/voice/ep01-reel.mp3
  youtube: assets/voice/ep01-youtube.mp3
```

For Reels, you can also export silent and add trending audio inside Instagram.

### LinkedIn

Add a `linkedin:` section with your `post` text and a `carousel` list of slides (`cover`, `point`, `checklist`, `cta`).
If you leave out `carousel`, slides are built automatically from your scenes.
Upload `carousel.pdf` to LinkedIn as a **document** so it becomes a swipeable carousel.

## 5. Your brand

Edit `brand.yaml` to change the name, handle, colours and fonts. Every video and slide updates automatically.

## 6. Content rule: no links (yet)

Nothing is live yet, so our content builds attention and never sends people anywhere.
With `rules: no_links: true` in `brand.yaml`, the studio refuses to render a script that contains a website, "visit",
"link in bio", "sign up", "waitlist" or "buy now". Use **Follow**, **Comment** and **Save this** instead.
Social handles like `@agentready.in` are fine. Switch the rule off only when something is actually live.

## 7. Branches & how we work

We never commit to `main` or directly to the long-lived branches. See [CONTRIBUTING.md](CONTRIBUTING.md).

```
production   <- live / final code (default branch)
   ^
qa           <- quality testing & demos
   ^
development  <- integration ("stage"): every feature merges here first
   ^
feature/*    <- one branch per piece of work, opened as a PR into development
```

## Project layout

```
brand.yaml               your colours, fonts, handle
content/bank/            topic bank: the ideas behind every daily post
content/schedule.yaml    posting calendar
content/                 hand-written episode scripts
studio/
  __main__.py            command line (daily / plan / topic / render / preview / new)
  compose.py             topic bank -> script, calendar, weekly YouTube compilation
  scenes.py              scene types (hook, chat, stat, compare...)
  video.py               frame-by-frame renderer -> ffmpeg -> MP4
  linkedin.py            carousel PDF + captions file
  draw.py, anim.py       drawing, text layout and easing helpers
assets/fonts             Poppins (OFL) — supports ₹ and Devanagari
assets/music, voice      your audio files
.github/workflows        renders on GitHub automatically
```

## Roadmap

- [x] Content studio: Reels, Shorts, YouTube, LinkedIn from one script
- [x] Daily content from a topic bank + calendar, weekly YouTube compilation
- [ ] Auto-posting to Instagram, YouTube and LinkedIn (needs each platform's API access)
- [ ] More scene types: product-card, phone mockup, timeline, quote
- [ ] Auto-captions from a voiceover
- [ ] **AgentReady checker**: scan a store and score how readable it is to AI agents
- [ ] Landing page (only when we're ready to launch)
- [ ] CI/CD: automatic checks on PRs, promotion development -> qa -> production
