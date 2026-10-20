"""Colour tokens and font paths shared by every SVG generator."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GREEN = "#10b981"
ORANGE = "#e8913f"

THEMES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "line": "#30363d",
        "ink": "#e6edf3", "muted": "#8b949e", "green": GREEN, "orange": ORANGE,
    },
    "light": {
        "bg": "#ffffff", "panel": "#f2f3f5", "line": "#e2e4e8",
        "ink": "#15171c", "muted": "#6b7280", "green": GREEN, "orange": ORANGE,
    },
}

FONTS = {
    "sans-400": ROOT / "fonts" / "Inter-Regular.ttf",
    "sans-800": ROOT / "fonts" / "Inter-ExtraBold.ttf",
    "mono-500": ROOT / "fonts" / "JetBrainsMono-Medium.ttf",
    "mono-600": ROOT / "fonts" / "JetBrainsMono-SemiBold.ttf",
}
