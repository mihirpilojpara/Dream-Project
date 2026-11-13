"""Turns a script into an MP4 by drawing every frame with Pillow and piping it to ffmpeg."""

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import ImageDraw

from .anim import scene_fade
from .draw import Background, make_canvas
from .scenes import make_scene


def draw_chrome(d, brand, cv, t, total, show_progress=True):
    """Brand wordmark + progress bar that sit on every frame."""
    u = cv.u
    font = brand.font("bold", 34 * u)
    mark = 46 * u
    label = brand.name
    width = mark + 16 * u + font.getlength(label)
    if cv.vertical:
        x = (cv.w - width) / 2
        y = cv.top - 150 * u
    else:
        x, y = cv.left, 56 * u
    d.rounded_rectangle((x, y, x + mark, y + mark), radius=mark * 0.28, fill=brand.c("accent"))
    f2 = brand.font("bold", mark * 0.62)
    d.text((x + (mark - f2.getlength("A")) / 2, y + mark * 0.08), "A", font=f2, fill=brand.c("bg_top"))
    d.text((x + mark + 16 * u, y + mark * 0.02), label, font=font, fill=brand.c("text", 0.92))
    if show_progress and total > 0:
        k = min(1.0, t / total)
        if cv.vertical:
            bx0, by, bx1 = cv.w * 0.3, y + mark + 34 * u, cv.w * 0.7
        else:
            bx0, by, bx1 = 0, cv.h - 8 * u, cv.w
        d.rounded_rectangle((bx0, by, bx1, by + 6 * u), radius=3 * u, fill=brand.c("text", 0.12))
        d.rounded_rectangle((bx0, by, bx0 + (bx1 - bx0) * k, by + 6 * u), radius=3 * u, fill=brand.c("accent"))


class Timeline:
    def __init__(self, brand, fmt, script):
        self.brand = brand
        self.cv = make_canvas(fmt)
        self.bg = Background(brand, self.cv)
        self.scenes = []
        t = 0.0
        for data in script["scenes"]:
            only = data.get("only")
            if only and fmt not in ([only] if isinstance(only, str) else only):
                continue
            sc = make_scene(brand, self.cv, data)
            self.scenes.append((t, sc))
            t += sc.duration
        self.total = t

    def frame(self, t):
        img = self.bg.frame(t)
        d = ImageDraw.Draw(img, "RGBA")
        for start, sc in self.scenes:
            if start <= t < start + sc.duration:
                local = t - start
                sc.draw(d, local, scene_fade(local, sc.duration))
                break
        draw_chrome(d, self.brand, self.cv, t, self.total)
        return img


def _ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        sys.exit("ffmpeg not found. Install it: https://ffmpeg.org/download.html "
                 "(Windows: winget install ffmpeg, Mac: brew install ffmpeg)")
    return exe


def render_video(brand, fmt, script, out_path, fps=30, audio=None, music_volume=0.18, quiet=False):
    tl = Timeline(brand, fmt, script)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = int(round(tl.total * fps))
    cmd = [_ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{tl.cv.w}x{tl.cv.h}", "-r", str(fps), "-i", "-"]
    voice, music = (audio or {}).get("voiceover"), (audio or {}).get("music")
    filters, maps = [], ["-map", "0:v"]
    idx = 1
    mix = []
    if voice:
        cmd += ["-i", str(voice)]
        # Clean up phone recordings: cut rumble, even out loudness for Reels/Shorts (-16 LUFS).
        mix.append(f"[{idx}:a]highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11[v{idx}]")
        idx += 1
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        fade_start = max(0.0, tl.total - 1.5)
        mix.append(f"[{idx}:a]volume={music_volume},afade=t=out:st={fade_start:.2f}:d=1.5[v{idx}]")
        idx += 1
    if mix:
        labels = "".join(f"[v{i}]" for i in range(1, idx))
        filters = mix + [f"{labels}amix=inputs={idx - 1}:duration=longest:normalize=0[aout]"]
        cmd += ["-filter_complex", ";".join(filters)]
        maps += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += maps + ["-t", f"{tl.total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                   "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(n):
            proc.stdin.write(tl.frame(i / fps).tobytes())
            if not quiet and (i % fps == 0 or i == n - 1):
                pct = (i + 1) / n * 100
                print(f"\r  {fmt:<8} {pct:5.1f}%  ({(i + 1) / fps:5.1f}s / {tl.total:.1f}s)", end="", flush=True)
    finally:
        proc.stdin.close()
        proc.wait()
    if not quiet:
        print()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {out_path}")
    return tl


def render_still(brand, fmt, script, out_path, scene_index=0, at=None):
    """Save one frame as PNG (thumbnails, cover images, quick previews)."""
    tl = Timeline(brand, fmt, script)
    scene_index = min(scene_index, len(tl.scenes) - 1)
    start, sc = tl.scenes[scene_index]
    local = at if at is not None else sc.duration * 0.62
    img = tl.frame(start + min(local, sc.duration - 0.35))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path
