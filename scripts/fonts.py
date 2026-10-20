"""Text measurement and subset WOFF2 embedding for the SVG generators."""
import base64
import io
from functools import lru_cache

from fontTools import subset
from fontTools.ttLib import TTFont

from scripts.theme import FONTS

_SANS = "Inter, ui-sans-serif, system-ui, sans-serif"
_MONO = "'JetBrains Mono', ui-monospace, monospace"

_NAMES = {"sans-400": "S400", "sans-800": "S800", "mono-500": "M500", "mono-600": "M600"}
FAMILY = {k: f'"{n}", {_SANS if k.startswith("sans") else _MONO}' for k, n in _NAMES.items()}

_WEIGHT = {"sans-400": 400, "sans-800": 800, "mono-500": 500, "mono-600": 600}


@lru_cache(maxsize=None)
def _font(key: str) -> TTFont:
    return TTFont(FONTS[key])


def _check(chars, key: str) -> None:
    cmap = _font(key).getBestCmap()
    missing = sorted({c for c in chars if not c.isspace() and ord(c) not in cmap})
    if missing:
        raise ValueError(f"font {key!r} has no glyph for {''.join(missing)!r}")


def text_width(text: str, font: str, size: float, letter_spacing: float = 0) -> float:
    _check(text, font)
    f = _font(font)
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    units = sum(hmtx[cmap[ord(c)]][0] for c in text)
    return units * size / f["head"].unitsPerEm + letter_spacing * (len(text) - 1)


def font_face_css(usage: dict[str, str]) -> str:
    rules = []
    for key in sorted(usage):
        chars = set(usage[key]) | {" "}
        _check(chars, key)
        opts = subset.Options(flavor="woff2", layout_features=["*"], notdef_outline=True)
        sub = subset.Subsetter(opts)
        font = TTFont(FONTS[key], recalcTimestamp=False)  # keep rebuilt assets byte-identical
        sub.populate(text="".join(sorted(chars)))
        sub.subset(font)
        font.flavor = "woff2"
        buf = io.BytesIO()
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        rules.append(
            f'@font-face{{font-family:"{_NAMES[key]}";font-weight:{_WEIGHT[key]};'
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "\n".join(rules)
