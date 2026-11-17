"""Generate original, fictional VERDANT MARKET package graphics with Pillow."""
from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "blender" / "assets" / "generated_textures"
SIZE = (768, 1024)

PALETTES = [
    {"ink": "#263D34", "leaf": "#759C6B", "cream": "#F3EEDF", "sun": "#D1A954", "accent": "#B65E42"},
    {"ink": "#30425B", "leaf": "#83A2A0", "cream": "#F2F0E8", "sun": "#D8AE56", "accent": "#C86F4F"},
    {"ink": "#4A342B", "leaf": "#8AA06B", "cream": "#F6ECDD", "sun": "#C99845", "accent": "#A9533B"},
    {"ink": "#3E3851", "leaf": "#78967C", "cream": "#F0EBE2", "sun": "#D2A44D", "accent": "#B95B55"},
]
BRANDS = ["VERDANT SELECT", "NORTHFIELD", "HARVEST & CO.", "MORNING GROVE", "PURE ORIGIN"]
PRODUCTS = {
    "milk_carton": ["WHOLE MILK", "OAT DRINK", "FARMHOUSE CREAM"],
    "juice_carton": ["APPLE & PEAR", "COLD PRESSED ORANGE", "GINGER CITRUS"],
    "glass_bottle": ["ELDERFLOWER TONIC", "BOTANICAL KOMBUCHA", "SPARKLING PEAR"],
    "pet_bottle": ["SPRING WATER", "GREEN TEA", "LEMON INFUSION"],
    "aluminium_can": ["ROASTED TOMATO SOUP", "SPARKLING YUZU", "CHICKPEA STEW"],
    "cereal_box": ["ANCIENT GRAIN MUESLI", "HONEY OAT CLUSTERS", "HEARTH GRANOLA"],
    "snack_pouch": ["SEA SALT LENTIL CRISPS", "ROSEMARY SEED BITES", "GARDEN ROOT CHIPS"],
    "glass_jar": ["WILD BERRY PRESERVE", "SMOKED TOMATO RELISH", "ALMOND BUTTER"],
    "yogurt_tub": ["GREEK STYLE YOGURT", "VANILLA BEAN SKYR", "CULTURED OAT"],
    "refill_pouch": ["COLD BREW CONCENTRATE", "ORGANIC TOMATO PASSATA", "MAPLE OAT BASE"],
    "pasta_pack": ["BRONZE CUT RIGATONI", "FARRO & HERB PILAF", "RED LENTIL PENNE"],
    "produce_crate": ["ORCHARD APPLES", "HEIRLOOM TOMATOES", "CITRUS SELECTION"],
}

def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = [
        r"C:\Windows\Fonts\georgiab.ttf" if bold else r"C:\Windows\Fonts\georgia.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for path in names:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()

def draw_plant(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, palette: dict, variant: int) -> None:
    x, y = center
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=palette["leaf"])
    # Original botanical line art varies by package while keeping a coherent family.
    draw.arc((x-radius*.7, y-radius*.7, x+radius*.7, y+radius*.7), 205, 330, fill=palette["cream"], width=5)
    for i in range(5):
        px = x + int((i-2) * radius * .22)
        py = y - int(radius * .66) + abs(i-2) * 8
        draw.ellipse((px-13, py-27, px+13, py+11), fill=palette["cream"] if (i+variant)%2 else palette["sun"])

def draw_barcode(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int, seed: int) -> None:
    rng = random.Random(seed)
    cursor = x
    while cursor < x + width:
        bar = rng.choice((2, 3, 5, 7))
        gap = rng.choice((2, 3, 4))
        draw.rectangle((cursor, y, min(cursor+bar, x+width), y+height), fill="#33342F")
        cursor += bar + gap

def render_art(kind: str, variant: int) -> Image.Image:
    p = PALETTES[(variant + sum(map(ord, kind))) % len(PALETTES)]
    rng = random.Random(2511 + variant * 67 + sum(map(ord, kind)))
    image = Image.new("RGB", SIZE, p["cream"])
    draw = ImageDraw.Draw(image)
    brand = BRANDS[(variant + len(kind)) % len(BRANDS)]
    product = PRODUCTS[kind][variant % len(PRODUCTS[kind])]
    draw.rectangle((0, 0, SIZE[0], 108), fill=p["ink"])
    draw.rectangle((0, 0, 18, SIZE[1]), fill=p["leaf"])
    draw.text((55, 24), brand, font=font(39, True), fill="#F8F5EC")
    draw.text((58, 77), "FIELD NOTES  /  EST. 2026", font=font(15), fill="#D9D6C9")
    draw.rounded_rectangle((54, 145, 714, 210), radius=18, fill=p["sun"])
    draw.text((78, 159), ["SINGLE ORIGIN", "SMALL BATCH", "GROWN WITH CARE"][variant % 3], font=font(23, True), fill=p["ink"])

    name_font = font(49 if len(product) < 19 else 41, True)
    lines = product.split()
    line = ""
    row = 249
    for word in lines:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=name_font)[2] > 625 and line:
            draw.text((58, row), line, font=name_font, fill=p["ink"])
            row += 57
            line = word
        else:
            line = candidate
    if line:
        draw.text((58, row), line, font=name_font, fill=p["ink"])

    draw_plant(draw, (385, 542), 142, p, variant)
    # Category cues are original stylized illustration, not photographs or trademarks.
    if "milk" in kind or "yogurt" in kind:
        draw.ellipse((290, 445, 480, 635), fill="#F4E3BC", outline=p["cream"], width=5)
        draw.arc((326, 464, 444, 605), 190, 345, fill="#9A7042", width=12)
    elif "cereal" in kind or "pasta" in kind or "pouch" in kind:
        for i in range(7):
            xx = 290 + i*24
            draw.line((xx, 632, xx+82, 466+rng.randint(-20, 20)), fill=p["sun"], width=6)
    elif "bottle" in kind:
        draw.rounded_rectangle((340, 424, 430, 662), radius=35, outline=p["cream"], width=12)
        draw.rectangle((365, 395, 406, 443), fill=p["cream"])
    else:
        draw.ellipse((314, 473, 465, 625), outline=p["cream"], width=12)

    draw.line((58, 719, 708, 719), fill=p["leaf"], width=4)
    descriptors = ["WHOLESOME · THOUGHTFULLY SOURCED", "PANTRY GOODS · MADE IN SMALL RUNS", "FRESH HARVEST · PACKED WITH CARE"]
    draw.text((58, 740), descriptors[(variant + 1) % 3], font=font(18, True), fill=p["ink"])
    draw.text((58, 786), "INGREDIENTS  /  ORIGIN  /  PREPARATION", font=font(15), fill="#5F665A")
    for i in range(4):
        x0, y0 = 58, 821 + i*20
        draw.line((x0, y0, x0+int(rng.randint(240, 570)), y0), fill="#9EA092", width=3)
    draw.rounded_rectangle((58, 915, 315, 978), radius=8, fill=p["ink"])
    draw.text((76, 929), ["NET 1 L", "NET 340 g", "NET 6 × 250 ml"][variant % 3], font=font(25, True), fill="#F8F5EC")
    draw_barcode(draw, 524, 912, 174, 60, variant + len(kind))
    draw.text((520, 977), f"VM-{sum(map(ord, kind))%997:03d}-{variant+1:02d}", font=font(12), fill="#40423C")
    return image

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    catalog: dict[str, list[str]] = {}
    for kind in PRODUCTS:
        paths=[]
        for variant in range(3):
            path=OUT/f"{kind}_{variant+1:02d}.png"
            render_art(kind, variant).save(path, optimize=True)
            paths.append(path.relative_to(ROOT).as_posix())
        catalog[kind]=paths
    # Controlled label graphics are separate from the exact measurement swatch.
    labels={
        "G":("#2E9E4F","FRESH","NO ACTION","BEST BEFORE 18 NOV"),
        "Y":("#F5B700","WATCH","CHECK DATE","BEST BEFORE 17 NOV"),
        "O":("#F07C1E","DISCOUNT NOW","PRICE REDUCTION","BEST BEFORE 16 NOV"),
        "R":("#D62828","DONATE NOW","NEAR-EXPIRY PRIORITY","BEST BEFORE 15 NOV"),
    }
    for identifier,(hex_color,headline,subline,date) in labels.items():
        image=Image.new("RGB",(1536,512),"#FCFAF4")
        d=ImageDraw.Draw(image)
        d.rectangle((0,0,1536,512),fill=hex_color)
        d.rectangle((15,15,1521,497),outline="#FFFFFF",width=5)
        d.text((62,38),f"VERDANT MARKET  /  {identifier}",font=font(31,True),fill="#FFF8EF")
        d.text((62,117),headline,font=font(91 if len(headline)<12 else 72,True),fill="#FFFFFF")
        d.text((67,244),subline,font=font(38,True),fill="#FFF8EF")
        d.text((67,338),date,font=font(29),fill="#FFF8EF")
        d.rounded_rectangle((1198,176,1467,388),radius=18,fill="#FFF9EC")
        d.text((1232,196),"TODAY",font=font(25,True),fill="#485247")
        d.text((1218,244),["$4.49","$3.99","$3.49","$2.99"]["GYOR".index(identifier)],font=font(66,True),fill="#263D34")
        path=OUT/f"shelf_label_{identifier}.png"; image.save(path,optimize=True)
        catalog.setdefault("shelf_label",[]).append(path.relative_to(ROOT).as_posix())
    (OUT/"packaging_catalog.json").write_text(json.dumps(catalog,indent=2),encoding="utf-8")
    print(f"Generated {sum(map(len,catalog.values()))} original packaging/label graphics in {OUT}")

if __name__=="__main__":main()
