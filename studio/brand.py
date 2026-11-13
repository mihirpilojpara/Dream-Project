"""Brand theme (colors, fonts, handle) loaded from brand.yaml."""

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml
from PIL import ImageFont

ROOT = Path(__file__).resolve().parent.parent

DEFAULTS = {
    "name": "AgentReady",
    "handle": "@agentready.in",
    "website": "",
    "rules": {"no_links": True},
    "highlight": "color",
    "colors": {
        "bg_top": "#0B1020",
        "bg_bottom": "#141B3A",
        "text": "#F5F7FF",
        "muted": "#A9B1D6",
        "accent": "#22D3A6",
        "accent2": "#FFB547",
        "danger": "#FF5C7A",
        "card": "#1C2550",
        "blob1": "#22D3A6",
        "blob2": "#7C5CFF",
    },
    "fonts": {
        "regular": "assets/fonts/Poppins-Regular.ttf",
        "medium": "assets/fonts/Poppins-Medium.ttf",
        "bold": "assets/fonts/Poppins-Bold.ttf",
    },
}


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


@dataclass
class Brand:
    name: str
    handle: str
    website: str
    colors: dict = field(default_factory=dict)
    fonts: dict = field(default_factory=dict)
    rules: dict = field(default_factory=dict)
    highlight: str = "color"

    def c(self, key, alpha=1.0):
        """Color as an RGBA tuple with the given opacity (0..1)."""
        r, g, b = hex_to_rgb(self.colors[key])
        return (r, g, b, int(255 * max(0.0, min(1.0, alpha))))

    def font(self, weight, size):
        return _load_font(str(ROOT / self.fonts[weight]), int(round(size)))


@lru_cache(maxsize=512)
def _load_font(path, size):
    return ImageFont.truetype(path, max(8, size))


def load_brand(path=None):
    data = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    path = Path(path) if path else ROOT / "brand.yaml"
    if path.exists():
        user = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for key, value in user.items():
            if isinstance(value, dict) and isinstance(data.get(key), dict):
                data[key].update(value)
            else:
                data[key] = value
    return Brand(**data)
