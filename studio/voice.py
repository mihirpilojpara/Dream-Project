"""Voiceover support: what to read, where recordings live, and timing scenes to the voice.

Workflow
  1. `python -m studio daily` writes voiceover.txt next to each video: one numbered line per scene.
  2. Record it (phone voice memo is fine). Pause about one second between lines.
  3. Save as audio/<date>.<ext> (e.g. audio/2026-11-16.m4a) or audio/<topic-id>.<ext>.
  4. Render again: scenes are cut at your pauses, so each line shows while you say it.

Alignment: ffmpeg's silencedetect finds pauses; the N-1 longest pauses become the scene
boundaries for N scenes. If there aren't enough pauses, time is split by word count.
"""

import re
import shutil
import subprocess
from pathlib import Path

from .brand import ROOT

AUDIO_DIR = ROOT / "audio"
AUDIO_EXTS = (".m4a", ".mp3", ".wav", ".aac", ".ogg", ".opus", ".flac", ".webm")
MIN_SCENE = 1.2
TAIL = 0.8  # seconds of picture after the last word


def find_audio(*names):
    """First recording in audio/ whose name (without extension) matches one of `names`."""
    for name in names:
        for ext in AUDIO_EXTS:
            p = AUDIO_DIR / f"{name}{ext}"
            if p.exists():
                return p
    return None


def _plain(text):
    return re.sub(r"\s+", " ", str(text or "").replace("**", "")).strip()


def spoken_line(scene):
    """A natural spoken line for a scene (Hinglish), used when the topic has no `vo` lines."""
    kind = scene.get("type")
    if scene.get("say"):
        return _plain(scene["say"])
    if kind in ("hook", "title", "statement"):
        kicker = (scene.get("kicker") or "").lower()
        text = _plain(scene.get("text"))
        if kicker == "myth":
            return f"Myth: {text}"
        if kicker == "fact":
            return f"Sach yeh hai: {text}"
        sub = _plain(scene.get("sub"))
        return f"{text}. {sub}" if sub else text
    if kind == "chat":
        n = len(scene.get("items", []))
        missing = _plain(scene.get("missing"))
        return f"Maine AI se pucha: {_plain(scene.get('user'))}. AI ne {n} options diye. {missing}".strip()
    if kind == "stat":
        return f"{_plain(scene.get('value'))} {_plain(scene.get('label'))}."
    if kind == "compare":
        left, right = scene.get("left", {}), scene.get("right", {})
        return (f"{_plain(left.get('title'))}: {', '.join(_plain(i) for i in left.get('items', []))}. "
                f"{_plain(right.get('title'))}: {', '.join(_plain(i) for i in right.get('items', []))}.")
    if kind in ("bullets", "steps"):
        nums = ["Ek", "Do", "Teen", "Chaar", "Paanch", "Chhe"]
        items = [f"{nums[i] if i < len(nums) else i + 1}, {_plain(t)}." for i, t in enumerate(scene.get("items", []))]
        head = _plain(scene.get("heading"))
        return " ".join(([head + "."] if head else []) + items)
    if kind == "cta":
        return f"{_plain(scene.get('text'))}. {_plain(scene.get('sub'))}".strip(" .") + "."
    return _plain(scene.get("text"))


def voiceover_lines(script):
    return [spoken_line(s) for s in script["scenes"]]


def write_voiceover(script, out_dir, audio_name):
    lines = voiceover_lines(script)
    words = sum(len(l.split()) for l in lines)
    secs = words / 2.4  # ~145 words per minute
    body = [
        f"# Voiceover: {script.get('title', '')}",
        f"# Save your recording as: audio/{audio_name}.m4a  (mp3/wav also fine)",
        f"# {len(lines)} lines, about {secs:.0f} seconds. Read each line, then PAUSE ~1 second before the next.",
        "# Speak like you're explaining to a seller friend. Changing words is fine; keep one line per pause.",
        "",
    ]
    body += [f"{i}. {l}" for i, l in enumerate(lines, 1)]
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    path = Path(out_dir) / "voiceover.txt"
    path.write_text("\n".join(body) + "\n", encoding="utf-8")
    return path


# ------------------------------------------------------------------ alignment

def _ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        raise SystemExit("ffmpeg is needed for voiceover alignment")
    return exe


def audio_duration(path):
    out = subprocess.run([_ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        raise SystemExit(f"Could not read audio file: {path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def find_pauses(path, noise_db=-35, min_pause=0.45):
    """[(start, end), ...] of silent stretches."""
    out = subprocess.run([_ffmpeg(), "-hide_banner", "-i", str(path), "-af",
                          f"silencedetect=noise={noise_db}dB:d={min_pause}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(starts, ends))


def speech_bounds(pauses, total):
    """Where speech begins and ends (ignoring silence at the very start/end)."""
    begin, end = 0.0, total
    for s, e in pauses:
        if s <= 0.05:
            begin = e
        if e >= total - 0.05:
            end = s
    return begin, end


def align(path, lines):
    """Scene durations (seconds) for `lines` spoken in the recording at `path`."""
    n = len(lines)
    total = audio_duration(path)
    pauses = find_pauses(path)
    begin, end = speech_bounds(pauses, total)
    inner = [(s, e) for s, e in pauses if s > begin + 0.05 and e < end - 0.05]
    if n <= 1:
        return [round(total + TAIL, 2)], total, "single scene"
    if len(inner) >= n - 1:
        cuts = sorted(sorted(inner, key=lambda p: p[1] - p[0], reverse=True)[:n - 1])
        marks = [0.0] + [(s + e) / 2 for s, e in cuts] + [total + TAIL]
        method = f"{n - 1} pauses"
    else:
        weights = [max(1, len(l.split())) for l in lines]
        span = end - begin
        marks, acc = [0.0], begin
        for w in weights[:-1]:
            acc += span * w / sum(weights)
            marks.append(acc)
        marks.append(total + TAIL)
        method = f"word-count split (found {len(inner)} pauses, needed {n - 1})"
    durs = [max(MIN_SCENE, b - a) for a, b in zip(marks, marks[1:])]
    return [round(d, 2) for d in durs], total, method


def apply_voice(script, path, fmt="reel"):
    """Time `script`'s scenes to the recording and attach it as the voiceover."""
    lines = voiceover_lines(script)
    durs, total, method = align(path, lines)
    for sc, d in zip(script["scenes"], durs):
        sc["duration"] = d
    script["voiceover"] = {fmt: str(path)}
    script["_voice"] = {"file": str(path), "seconds": round(total, 1), "method": method, "durations": durs}
    return script


def build_track(segments, out_path):
    """Concatenate [(audio_or_None, seconds), ...] into one track; None = silence."""
    if not any(a for a, _ in segments):
        return None
    cmd = [_ffmpeg(), "-y", "-loglevel", "error"]
    parts = []
    for i, (a, secs) in enumerate(segments):
        if a:
            cmd += ["-i", str(a)]
            parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{secs:.3f},"
                         f"apad=whole_dur={secs:.3f},asetpts=PTS-STARTPTS[s{i}]")
        else:
            cmd += ["-f", "lavfi", "-t", f"{secs:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
            parts.append(f"[{i}:a]asetpts=PTS-STARTPTS[s{i}]")
    labels = "".join(f"[s{i}]" for i in range(len(segments)))
    graph = ";".join(parts) + f";{labels}concat=n={len(segments)}:v=0:a=1[out]"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd += ["-filter_complex", graph, "-map", "[out]", "-c:a", "aac", "-b:a", "192k", str(out_path)]
    subprocess.run(cmd, check=True)
    return out_path
