"""Timing and easing helpers used by every scene."""

import math


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def ease_out_cubic(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ease_in_out(p):
    p = clamp(p)
    return 3 * p * p - 2 * p * p * p


def ease_out_back(p, s=1.6):
    p = clamp(p) - 1
    return p * p * ((s + 1) * p + s) + 1


def progress(t, start, dur):
    """Linear 0..1 progress of an animation that starts at `start` and lasts `dur`."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


def enter(t, start, dur=0.45):
    """Eased entrance progress (0 = hidden, 1 = fully in)."""
    return ease_out_cubic(progress(t, start, dur))


def scene_fade(t, duration, fade_in=0.25, fade_out=0.3):
    """Whole-scene opacity: quick fade in, fade out at the end."""
    a = ease_in_out(progress(t, 0, fade_in))
    b = 1 - ease_in_out(progress(t, duration - fade_out, fade_out))
    return clamp(min(a, b))


def pulse(t, speed=2.2, amount=0.04):
    return 1 + amount * math.sin(t * speed * math.pi)
