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

## 3. Writing a script

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

## 4. Your brand

Edit `brand.yaml` to change the name, handle, colours and fonts. Every video and slide updates automatically.

## 5. Content rule: no links (yet)

Nothing is live yet, so our content builds attention and never sends people anywhere.
With `rules: no_links: true` in `brand.yaml`, the studio refuses to render a script that contains a website, "visit",
"link in bio", "sign up", "waitlist" or "buy now". Use **Follow**, **Comment** and **Save this** instead.
Social handles like `@agentready.in` are fine. Switch the rule off only when something is actually live.

## 6. Branches & how we work

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
content/                 one YAML script per episode
studio/
  __main__.py            command line (render / preview / new)
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
- [ ] More scene types: product-card, phone mockup, timeline, quote
- [ ] Auto-captions from a voiceover
- [ ] **AgentReady checker**: scan a store and score how readable it is to AI agents
- [ ] Landing page (only when we're ready to launch)
- [ ] CI/CD: automatic checks on PRs, promotion development -> qa -> production
