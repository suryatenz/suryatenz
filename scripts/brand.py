"""Shared palette and type for every SVG in this profile.

Colours and fonts are the same system as the portfolio (surya-prajyesh.vercel.app):
warm paper, ink, and five tones (cobalt, apricot, mint, butter, sky), each with a
light tint for surfaces and a dark shade for text on that tint.
"""
import base64
from functools import lru_cache
from pathlib import Path

FONTS = Path(__file__).resolve().parent / "fonts"

PAPER = "#f6f5f1"
SURFACE = "#ffffff"
INK = "#15171f"
INK2 = "#585e6c"
LINE = "#e4e2dc"

TONES = {
    #          base       tint       dark
    "cobalt": ("#2e4bff", "#dfe5ff", "#2e4bff"),
    "apricot": ("#ff8a5c", "#ffe4d8", "#b2410f"),
    "mint": ("#7fdcb6", "#d9f4e8", "#176548"),
    "butter": ("#ffd66b", "#fff0c2", "#8a5a00"),
    "sky": ("#8ccbf2", "#daeefb", "#13608f"),
}

# family name -> (file, weight, style)
FACES = {
    "display": ("Outfit-600", 600, "normal"),
    "display-m": ("Outfit-500", 500, "normal"),
    "body": ("WorkSans-400", 400, "normal"),
    "body-m": ("WorkSans-500", 500, "normal"),
    "body-i": ("WorkSans-400i", 400, "italic"),
}


@lru_cache(maxsize=None)
def _b64(name):
    return base64.b64encode((FONTS / f"{name}.woff2").read_bytes()).decode()


def font_css(*faces):
    """@font-face rules with the fonts inlined, since SVGs shown as images can't fetch fonts."""
    rules = []
    for face in faces:
        name, weight, style = FACES[face]
        rules.append(
            f"@font-face {{ font-family:'{face}'; font-weight:{weight}; font-style:{style}; "
            f"src:url(data:font/woff2;base64,{_b64(name)}) format('woff2'); }}"
        )
    fallbacks = {
        "display": "'display', ui-sans-serif, system-ui, sans-serif",
        "display-m": "'display-m', ui-sans-serif, system-ui, sans-serif",
        "body": "'body', ui-sans-serif, system-ui, sans-serif",
        "body-m": "'body-m', ui-sans-serif, system-ui, sans-serif",
        "body-i": "'body-i', ui-sans-serif, system-ui, sans-serif",
    }
    classes = [
        f".f-{face} {{ font-family:{fallbacks[face]};{' font-style:italic;' if face == 'body-i' else ''} }}"
        for face in faces
    ]
    return "\n    ".join(rules + classes)
