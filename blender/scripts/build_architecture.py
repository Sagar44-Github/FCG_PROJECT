"""Architectural shell and branded visual language for VERDANT MARKET."""
import math
from hero_utils import box, cylinder, quad, add_text, torus


def build(b):
    c = b.collection("01 · ARCHITECTURE")
    mats = {
        "floor": b.mat("Porcelain · warm limestone", "#BEB6A7", .24, procedural="stone", texture_scale=38, bump_strength=.12),
        "wall": b.mat("Warm ivory plaster", "#E3DED1", .78, procedural="noise", texture_scale=88, bump_strength=.035),
        "sage": b.mat("Verdant · painted timber", "#173A32", .3, procedural="noise", texture_scale=48, bump_strength=.025),
        "oak": b.mat("White oak · satin", "#98683D", .3, procedural="wood", texture_scale=6, bump_strength=.05),
        "dark": b.mat("Powder coat · forest graphite", "#17221F", .27, .68),
        "brass": b.mat("Brushed champagne brass", "#AA8650", .23, .78, anisotropy=.45),
        "glass": b.mat("Low-iron architectural glass", "#B8D6D0", .12, .05, transmission=.86, ior=1.46),
        "ceiling": b.mat("Acoustic ceiling · warm white", "#D7D3C8", .86),
        "glow": b.emit("Warm concealed strip", "#FFE0A0", 2.6),
        "sign": b.mat("Deep green sign enamel", "#0B211D", .2, .35),
    }
    b.materials.update({f"arch_{k}":v for k,v in mats.items()})
    # Large stone floor, grout joints, timber perimeter and terrazzo entrance.
    box("Continuous limestone floor", (0, 2, -.17), (25.6, 30, .32), mats["floor"], collection=c, bevel=.035)
    grout=b.mat("Fine warm grout", "#918B80", .82)
    for x in range(-12,13,2): box(f"Floor grout · X{x}",(x,2,-.002),(.009,29.5,.004),grout,collection=c)
    for y in range(-12,17,2): box(f"Floor grout · Y{y}",(0,y,-.002),(25.3,.009,.004),grout,collection=c)
    box("West feature wall",(-12.65,2,3.7),(.42,29.5,7.4),mats["wall"],collection=c)
    box("East feature wall",(12.65,2,3.7),(.42,29.5,7.4),mats["wall"],collection=c)
    box("Rear brand wall",(0,16.65,3.7),(25.7,.42,7.4),mats["sage"],collection=c)
    # Tall oak portal framing an airy glazed shopfront at the south entrance.
    for x in (-10.6,10.6):
        box(f"Entrance oak portal · {x}",(x,-12.68,3.5),(.38,.42,7),mats["oak"],collection=c,bevel=.035)
    box("Entrance oak header",(0,-12.68,6.96),(21.6,.42,.38),mats["oak"],collection=c,bevel=.035)
    mullion=b.mat("Bronze window framing", "#5B5548", .24, .72)
    for x in (-10.15,-5.2,0,5.2,10.15):
        box(f"Shopfront bronze mullion · {x}",(x,-12.43,3.35),(.055,.09,6.55),mullion,collection=c)
    for x in (-7.65,7.65):
        pane=box(f"Shopfront low-iron glazing · {x}",(x,-12.49,3.34),(4.82,.035,6.35),mats["glass"],collection=c)
    # Ceiling is articulated as acoustic rafts so luminaires remain visible.
    box("Acoustic ceiling plane",(0,2,7.15),(25.2,29.5,.32),mats["ceiling"],collection=c)
    for x in range(-11,12,2):
        box(f"Ceiling oak slat · {x}",(x,2,6.94),(.045,28,.055),mats["oak"],collection=c)
    for y in (-9,-2,5,12):
        box(f"Ceiling raft crossbeam · {y}",(0,y,6.78),(24.7,.16,.16),mats["oak"],collection=c,bevel=.025)
    # Restrained perimeter joinery and brass reveal details.
    for z in (.18,.32):
        box(f"Rear wall brass reveal · {z}",(0,16.40,z),(24.8,.06,.035),mats["brass"],collection=c)
    # Main shop sign, lettering is actual scene geometry.
    box("VERDANT MARKET sign backplate",(0,16.37,6.03),(9.6,.2,1.18),mats["sign"],collection=c,bevel=.08)
    add_text("VERDANT MARKET · logotype","VERDANT MARKET",(0,16.25,6.21),.48,mats["brass"],collection=c,rotation=(math.pi/2,0,0),extrude=.002)
    add_text("Freshness promise","GOOD FOOD. GOOD PURPOSE.",(0,16.245,5.91),.15,mats["wall"],collection=c,rotation=(math.pi/2,0,0),extrude=.0006)
    # Oak wall bays, framed poster planes and brass edge profiles create scale cues.
    for side in (-1,1):
        for y in (-8,-3,2,7,12):
            x=side*12.38
            box(f"Wall oak pilaster · {side} · {y}",(x,y,3.6),(.13,.18,7),mats["oak"],collection=c,bevel=.018)
            box(f"Wall brass pilaster cap · {side} · {y}",(x-side*.075,y,3.65),(.025,.2,6.9),mats["brass"],collection=c)
    # Produce feature island along the front-left edge.
    box("Produce island oak plinth",(-8.5,-8.45,.51),(5.4,2.1,.96),mats["oak"],collection=c,bevel=.09)
    box("Produce island dark inset",(-8.5,-8.45,1.04),(5.25,1.96,.12),mats["dark"],collection=c,bevel=.06)
    box("Produce island brass toe kick",(-8.5,-8.45,.12),(5.28,1.98,.07),mats["brass"],collection=c,bevel=.025)
    # Refrigerated cases at the right wall; interior blue-white and glass-fronted.
    fridge=b.mat("Refrigerated case porcelain", "#DCE4DF", .2, .18)
    for i,x in enumerate((9.85,7.9,5.95)):
        box(f"Chilled case carcass · {i}",(x,8.35,1.85),(1.72,10.2,3.7),fridge,collection=c,bevel=.11)
        box(f"Chilled case dark interior · {i}",(x,3.18,2.0),(1.43,.045,3.1),mats["dark"],collection=c)
        box(f"Chilled case canopy · {i}",(x,3.04,3.63),(1.68,.2,.16),mats["glow"],collection=c,bevel=.04)
        for z in (.8,1.55,2.3,3.0):
            box(f"Chilled case glass shelf · {i} · {z}",(x,3.55,z),(1.47,.82,.035),mats["glass"],collection=c)
        # Door frame and reflective vertical dividers.
        for dx in (-.79,.79): box(f"Chiller door frame · {i} · {dx}",(x+dx,2.95,1.98),(.045,.07,3.28),mullion,collection=c)
    # Cashwrap in far left background, with brass transaction rail.
    box("Checkout oak counter",(-10.15,11.0,1.12),(3.3,1.15,.42),mats["oak"],collection=c,bevel=.12)
    box("Checkout forest-green base",(-10.15,11.12,.55),(3.0,.9,.76),mats["sage"],collection=c,bevel=.08)
    box("Checkout brass transaction rail",(-10.15,10.35,1.36),(3.1,.055,.035),mats["brass"],collection=c)
    # Tiny luminous brass accent dots on the architectural sign rails.
    b.scene["brand"]="VERDANT MARKET"
    b.scene["visual_style"]="Luxury neighbourhood grocer · warm oak · limestone · forest green · champagne brass"
