# AgentReady: 90-day audience plan

**16 Nov 2026 → 14 Feb 2027 · 65 Shorts + 13 YouTube videos · faceless animation + your voice**

## The strategy in one paragraph

For 90 days we build an **audience of Indian online sellers who trust us about AI shopping**. We teach the
*problem* (AI assistants are starting to choose and buy products for customers, and most small stores
are unreadable to them) and the *free fixes* sellers can do themselves. We never show, describe or hint
at the product we're building. By day 90 we want a channel that sellers follow, save and comment on.
Those comments become our research: real questions from real sellers, collected before we build anything.

## Decisions we've made (and why)

| Decision | Why |
|---|---|
| **Teach the problem, hide the solution** (stealth) | The trend itself isn't secret: Razorpay, NPCI, Google, Shopify and funded startups are already public about it. Our edge is an audience that trusts us and knowledge of what sellers struggle with. Our product plan is the one thing a faster competitor could copy, so it stays private. The studio blocks product words automatically (`no_product_reveal`). |
| **No links, no sign-ups** | Nothing is live, and sending people to an empty page burns trust. Calls to action are only follow, comment, save and share (`no_links`). |
| **Instagram Reels + Facebook Reels + YouTube Shorts** | Same 9:16 video on all three, so one recording reaches three audiences. |
| **YouTube 16:9 every Sunday** | Stitched from the week's Shorts and your recordings. No extra recording, and it builds a searchable library. |
| **LinkedIn stays separate** | LinkedIn is for your job/career profile. You tell Claude what to post there; it isn't part of this pipeline. |
| **5 Shorts a week, not 7** | Saturday is your buffer. Consistency for 13 weeks beats daily for 3 weeks and then stopping. |

## Your weekly routine (about 2 hours a week)

| When | What | Time |
|---|---|---|
| **Sunday evening** | Open next week's 5 `voiceover.txt` files and record all 5 (batching is easier). Save as `audio/<date>.m4a`, push. | 45 min |
| **Each weekday morning** | GitHub has rendered the day's video. Download it from Actions → Daily content. Post to Instagram (cross-post to Facebook) and YouTube Shorts with the caption from `publish.md`. | 10 min |
| **Each weekday evening** | Reply to comments, and note good questions in `docs/seller-questions.md`. | 10 min |
| **Sunday** | Post the weekly YouTube video. Look at the numbers (below). | 15 min |

To swap a topic for something fresh (news, a great comment), add an `overrides:` line in
`content/schedule.yaml`, or ask Claude to write a new topic.

## Phases and what "good" looks like

We don't promise follower numbers. Early on, these show whether the content works:

| Phase | Weeks | Focus | Watch these |
|---|---|---|---|
| **1 · Wake-up** | 1–4 | What AI shopping is, myths, first easy fixes | Do people watch past 3 seconds (hook)? Average % of the Short watched |
| **2 · Practical fixes** | 5–9 | Step-by-step fixes, wedding/New Year/sale moments | **Saves and shares** (useful content gets saved) |
| **3 · Trust & community** | 10–13 | Sellers' common questions, trust, routines | **Comments with questions**, follows per video |

**Checkpoints:** at day 30, day 60 and day 90, ask Claude to run `/yt-audit` on your numbers.
Find the 3 best and 3 worst Shorts and change the next month's topics to match. Swap the `qa-*`
topics for real questions from your comments as soon as you have them.

## What we never say

- Anything about a tool, app, checker, beta, launch or "what I'm building"
- Links, "visit", "link in bio", "sign up", "waitlist", "buy now"
- A number without a named source (every stat on screen shows its source)
- Promises: "guaranteed", "100%", "get rich", "AI will replace you"

## Before day 1 (by Sunday 15 Nov)

1. Create the brand accounts with the same handle everywhere (currently `@agentready.in` in `brand.yaml`;
   change it there if that handle is taken): Instagram (professional/creator account), Facebook Page
   linked to the Instagram account (so Reels can cross-post), and a YouTube channel.
2. Profile bio, no link: *"AI shopping, explained for Indian sellers. New Short every weekday."*
3. Record week 1's five voiceovers (Claude can render them so you can preview before posting).
4. Merge the open PRs so the daily automation runs from `production`.

## The calendar

### Phase 1 · Wake-up

| Week | Date | Day | Format | Topic |
|---|---|---|---|---|
| 1 | 16 Nov | Mon | Short (shift) | Customers now ask AI what to buy |
| 1 | 17 Nov | Tue | Short (stat) | 92% of shoppers in India's metros have used AI while shopping |
| 1 | 18 Nov | Wed | Short (shift) | What is an AI shopping agent? |
| 1 | 19 Nov | Thu | Short (myth) | Myth: AI shopping is only for big brands |
| 1 | 20 Nov | Fri | Short (tip) | Write product titles an AI can understand |
| 1 | 22 Nov | Sun | **YouTube 16:9** | Week 1 recap: the 5 lessons above |
| 2 | 23 Nov | Mon | Short (news) | AI agents are learning to pay with UPI |
| 2 | 24 Nov | Tue | Short (shift) | How an AI reads your store |
| 2 | 25 Nov | Wed | Short (myth) | Myth: good photos are enough |
| 2 | 26 Nov | Thu | Short (tip) | Size charts AI agents can read |
| 2 | 27 Nov | Fri | Short (stat) | COD still matters in small-town India |
| 2 | 29 Nov | Sun | **YouTube 16:9** | Week 2 recap: the 5 lessons above |
| 3 | 30 Nov | Mon | Short (demo) | Wedding season shopping, the AI way |
| 3 | 01 Dec | Tue | Short (news) | ONDC crossed 2 lakh active retail merchants |
| 3 | 02 Dec | Wed | Short (tip) | One price everywhere |
| 3 | 03 Dec | Thu | Short (myth) | Myth: AI will replace sellers |
| 3 | 04 Dec | Fri | Short (tip) | A return policy AI can explain |
| 3 | 06 Dec | Sun | **YouTube 16:9** | Week 3 recap: the 5 lessons above |
| 4 | 07 Dec | Mon | Short (demo) | How an AI picks a gift |
| 4 | 08 Dec | Tue | Short (stat) | 60% of Indian consumers are interested in a personal AI agent |
| 4 | 09 Dec | Wed | Short (tip) | An FAQ section answers the AI's questions |
| 4 | 10 Dec | Thu | Short (news) | Google brings AI agent shopping to India with Flipkart |
| 4 | 11 Dec | Fri | Short (tip) | Weekly checklist: is your store AI-ready? |
| 4 | 13 Dec | Sun | **YouTube 16:9** | Week 4 recap: the 5 lessons above |

### Phase 2 · Practical fixes

| Week | Date | Day | Format | Topic |
|---|---|---|---|---|
| 5 | 14 Dec | Mon | Short (demo) | Why AI asks for your pin code |
| 5 | 15 Dec | Tue | Short (news) | Pine Labs launched an agentic payment protocol on UPI |
| 5 | 16 Dec | Wed | Short (tip) | Out-of-stock is the fastest way to lose an AI's trust |
| 5 | 17 Dec | Thu | Short (myth) | Myth: AI only understands English listings |
| 5 | 18 Dec | Fri | Short (stat) | Most new D2C orders now come from smaller cities |
| 5 | 20 Dec | Sun | **YouTube 16:9** | Week 5 recap: the 5 lessons above |
| 6 | 21 Dec | Mon | Short (demo) | Two stores, same product. Who does the AI pick? |
| 6 | 22 Dec | Tue | Short (tip) | Reviews are data too |
| 6 | 23 Dec | Wed | Short (tip) | Product descriptions that answer questions |
| 6 | 24 Dec | Thu | Short (myth) | Myth: it's too early to prepare |
| 6 | 25 Dec | Fri | Short (tip) | Make your sale readable by AI |
| 6 | 27 Dec | Sun | **YouTube 16:9** | Week 6 recap: the 5 lessons above |
| 7 | 28 Dec | Mon | Short (news) | 2026 recap: the year AI learned to shop in India |
| 7 | 29 Dec | Tue | Short (tip) | Tell the AI what your photos show |
| 7 | 30 Dec | Wed | Short (myth) | Myth: AI shopping is only for metro cities |
| 7 | 31 Dec | Thu | Short (insight) | What I'm learning from sellers |
| 7 | 01 Jan | Fri | Short (news) | India's new rules on AI-generated content |
| 7 | 03 Jan | Sun | **YouTube 16:9** | Week 7 recap: the 5 lessons above |
| 8 | 04 Jan | Mon | Short (tip) | Sizes and colours an AI can pick from |
| 8 | 05 Jan | Tue | Short (demo) | Shopping by voice, in Hindi |
| 8 | 06 Jan | Wed | Short (tip) | Your WhatsApp catalog counts too |
| 8 | 07 Jan | Thu | Short (myth) | Myth: the cheapest price always wins |
| 8 | 08 Jan | Fri | Short (stat) | Over 1.5 million sellers on Flipkart and Amazon India |
| 8 | 10 Jan | Sun | **YouTube 16:9** | Week 8 recap: the 5 lessons above |
| 9 | 11 Jan | Mon | Short (tip) | Trust signals an AI looks for |
| 9 | 12 Jan | Tue | Short (demo) | The return question that loses orders |
| 9 | 13 Jan | Wed | Short (tip) | Write a clear delivery promise |
| 9 | 14 Jan | Thu | Short (news) | Shopify opens its catalog to AI shopping agents |
| 9 | 15 Jan | Fri | Short (myth) | Myth: getting AI-ready is expensive |
| 9 | 17 Jan | Sun | **YouTube 16:9** | Week 9 recap: the 5 lessons above |

### Phase 3 · Trust & community

| Week | Date | Day | Format | Topic |
|---|---|---|---|---|
| 10 | 18 Jan | Mon | Short (tip) | Prepare listings before the Republic Day sales |
| 10 | 19 Jan | Tue | Short (tip) | Make combos and bundles clear |
| 10 | 20 Jan | Wed | Short (demo) | How an AI compares two prices |
| 10 | 21 Jan | Thu | Short (qa) | Common question: does this matter for Meesho sellers? |
| 10 | 22 Jan | Fri | Short (tip) | Update listings for the season |
| 10 | 24 Jan | Sun | **YouTube 16:9** | Week 10 recap: the 5 lessons above |
| 11 | 25 Jan | Mon | Short (stat) | UPI processed over 23 billion transactions in one month |
| 11 | 26 Jan | Tue | Short (tip) | An "About us" that builds trust |
| 11 | 27 Jan | Wed | Short (demo) | Two similar stores, one gets trusted |
| 11 | 28 Jan | Thu | Short (qa) | Common question: I only sell on Instagram. Now what? |
| 11 | 29 Jan | Fri | Short (tip) | Turn customer DMs into FAQs |
| 11 | 31 Jan | Sun | **YouTube 16:9** | Week 11 recap: the 5 lessons above |
| 12 | 01 Feb | Mon | Short (news) | Why 2027 is about trust in AI payments |
| 12 | 02 Feb | Tue | Short (tip) | Don't fake reviews |
| 12 | 03 Feb | Wed | Short (demo) | When AI reorders for your customer |
| 12 | 04 Feb | Thu | Short (myth) | Myth: AI shopping will kill Instagram selling |
| 12 | 05 Feb | Fri | Short (tip) | A 15-minute weekly routine |
| 12 | 07 Feb | Sun | **YouTube 16:9** | Week 12 recap: the 5 lessons above |
| 13 | 08 Feb | Mon | Short (demo) | Valentine's gifting with an AI assistant |
| 13 | 09 Feb | Tue | Short (stat) | Forecast: $500 billion in AI-agent commerce by 2028 |
| 13 | 10 Feb | Wed | Short (qa) | Common question: should I write in Hindi or English? |
| 13 | 11 Feb | Thu | Short (tip) | Name colours the way customers do |
| 13 | 12 Feb | Fri | Short (tip) | 90 days of lessons: the AI-ready store in one list |
| 13 | 14 Feb | Sun | **YouTube 16:9** | Week 13 recap: the 5 lessons above |