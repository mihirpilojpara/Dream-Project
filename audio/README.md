# Your voiceovers

1. Open today's `voiceover.txt` (it's also at the top of `publish.md`, and on the GitHub Actions run summary).
2. Record it on your phone (Voice Memos / Recorder app). **Pause about 1 second between lines.**
   Quiet room, phone 15–20 cm from your mouth. Reading slightly faster than normal works best for Reels.
3. Name the file by its posting date, e.g. `2026-11-16.m4a`, and put it in this folder.
   (Naming it by topic id, e.g. `stat-92-percent.m4a`, also works.)
4. Commit and push it to a `feature/*` branch. GitHub re-renders that day's video timed to your voice
   (Actions → **Daily content**). Or run locally: `python -m studio daily --date 2026-11-16`.

The studio cuts scenes at your pauses: line 1 shows while you say line 1, and so on.
Missed a pause? It still works: time is then shared out by how many words each line has.
The Sunday YouTube video reuses the week's recordings automatically, so there's nothing extra to record.
