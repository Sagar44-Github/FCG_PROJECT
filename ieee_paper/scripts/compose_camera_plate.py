#!/usr/bin/env python3
"""Compose the paper's six-view plate from the six final Blender PNGs."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
VIEWS = (
    ("01_supermarket_hero.png", "01  SUPERMARKET HERO"),
    ("02_shelf_detail.png", "02  SHELF DETAIL"),
    ("03_donate_now_macro.png", "03  DONATE NOW MACRO"),
    ("04_colour_status_system.png", "04  COLOUR STATUS SYSTEM"),
    ("05_illuminant_comparison.png", "05  ILLUMINANT COMPARISON"),
    ("06_supermarket_isometric.png", "06  SUPERMARKET ISOMETRIC"),
)
TILE = (640, 360)
MARGIN, GAP, HEADER, LABEL_H, FOOTER = 20, 16, 44, 24, 30
SIZE = (2 * MARGIN + 3 * TILE[0] + 2 * GAP,
        HEADER + 2 * MARGIN + 2 * TILE[1] + GAP + 2 * LABEL_H + FOOTER)


def get_font(size: int, bold: bool = False):
    candidates = (
        (Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/arial.ttf"))
        if bold else
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/segoeui.ttf"))
    )
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def main() -> None:
    canvas = Image.new("RGB", SIZE, (10, 16, 24))
    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, 13), "Q3 RESEARCH  /  FINAL BLENDER CAMERA VIEWS",
              fill=(226, 234, 243), font=get_font(18, bold=True))
    y0 = HEADER + MARGIN
    for index, (filename, label) in enumerate(VIEWS):
        source = FIGURES / filename
        if not source.is_file():
            raise FileNotFoundError(f"Required Blender render is missing: {source}")
        with Image.open(source) as opened:
            tile = opened.convert("RGB")
            tile.thumbnail(TILE, Image.Resampling.LANCZOS)
            if tile.size != TILE:
                tile = tile.resize(TILE, Image.Resampling.LANCZOS)
        x = MARGIN + (index % 3) * (TILE[0] + GAP)
        y = y0 + (index // 3) * (TILE[1] + GAP + LABEL_H)
        canvas.paste(tile, (x, y))
        draw.rectangle((x, y + TILE[1], x + TILE[0], y + TILE[1] + LABEL_H),
                       fill=(19, 28, 40))
        draw.text((x + 8, y + TILE[1] + 5), label, fill=(214, 223, 234),
                  font=get_font(13, bold=True))
    draw.text((MARGIN, SIZE[1] - FOOTER + 7),
              "Presentation renders; analytical colour results are computed by the Python spectral pipeline.",
              fill=(156, 174, 192), font=get_font(12))
    output = FIGURES / "supermarket_six_views_plate.png"
    canvas.save(output, optimize=True)
    print(f"Wrote {output} ({SIZE[0]} x {SIZE[1]} px)")


if __name__ == "__main__":
    main()
