"""Commercial gondola fixtures and physical shelf-edge label rails."""
from hero_utils import box, cylinder, add_text

ROWS=(-5.25,.15,5.55,10.95)
LEVELS=(.64,1.47,2.30,3.13)


def build(b):
    c=b.collection("02 · MERCHANDISING FIXTURES")
    steel=b.materials["arch_dark"]; brass=b.materials["arch_brass"]; oak=b.materials["arch_oak"]
    deck=b.mat("Gondola shelf · warm grey powder coat","#B6B8B0",.3,.55)
    label_white=b.mat("Shelf ticket paper","#F6F3E9",.62)
    rail_glass=b.mat("Clear label cover · PETG","#DDEBE5",.16,.02,transmission=.72,ior=1.47)
    rail_high=b.mat("Shelf lip aluminium","#858B86",.25,.72)
    glow=b.emit("Warm under-shelf light","#FFE5B7",1.35)
    b.shelf_rows=ROWS; b.shelf_levels=LEVELS
    main_row=0
    for ri,y in enumerate(ROWS):
        is_main=ri==main_row
        for x in (-8.75,8.75):
            post=box(f"Gondola {ri+1} · structural upright",(x,y,2.12),(.11,.78,4.25),steel,collection=c,bevel=.018,web=is_main)
            # Repeated punched adjustment slots and concealed fixing brackets.
            for z in [0.25+i*.12 for i in range(32)]:
                box(f"Upright slot · {ri+1} · {x} · {z:.2f}",(x,y-.397,z),(.028,.008,.048),rail_high,collection=c,web=is_main)
            for z in LEVELS:
                box(f"Shelf bracket · {ri+1} · {x} · {z:.1f}",(x-math_sign(x)*.13,y-.28,z-.11),(.29,.075,.055),brass,collection=c,bevel=.008,web=is_main)
        # Continuous shelf deck, lower toe kick and high canopy shelf.
        for li,z in enumerate(LEVELS):
            box(f"Gondola shelf deck · {ri+1} · {li+1}",(0,y,z),(17.58,1.02,.075),deck,collection=c,bevel=.018,web=is_main)
            box(f"Shelf front channel · {ri+1} · {li+1}",(0,y-.54,z+.045),(17.64,.055,.095),rail_high,collection=c,bevel=.012,web=is_main)
            box(f"Shelf ticket rail acrylic · {ri+1} · {li+1}",(0,y-.575,z+.058),(17.48,.021,.066),rail_glass,collection=c,bevel=.008,web=is_main)
            box(f"Shelf underlight diffuser · {ri+1} · {li+1}",(0,y-.02,z-.055),(16.9,.055,.025),glow,collection=c,web=is_main)
            for x in (-8.45,-5.6,-2.8,0,2.8,5.6,8.45):
                box(f"Shelf divider · {ri+1} · {li+1} · {x}",(x,y,.0+z+.36),(.025,.78,.7),rail_high,collection=c,bevel=.01,web=is_main)
        # End-cap timber cheeks and narrow brass inlay lend a finished store fitout.
        for x in (-8.92,8.92):
            box(f"Gondola oak endcap · {ri+1} · {x}",(x,y,2.2),(.17,.95,4.4),oak,collection=c,bevel=.035,web=is_main)
            box(f"Gondola brass endcap reveal · {ri+1} · {x}",(x-math_sign(x)*.09,y-.49,2.2),(.018,.016,4.15),brass,collection=c,web=is_main)
        # Aisle-top header panel and restrained wayfinding.
        box(f"Aisle header · {ri+1}",(0,y,4.38),(3.4,.18,.35),b.materials["arch_sage"],collection=c,bevel=.045,web=is_main)
        add_text(f"Aisle number · {ri+1}",f"{ri+1:02d}   PANTRY & PROVISIONS",(0,y-.101,4.31),.13,b.materials["arch_wall"],collection=c,rotation=(1.5708,0,0),extrude=.0005,web=is_main)
    # Large near-expiry communication panel facing into the featured aisle.
    sign=b.materials["arch_sage"]
    box("Donation programme wayfinding plaque",(-8.65,-3.45,4.72),(2.3,.12,.62),sign,collection=c,bevel=.055,web=True)
    add_text("Donate signage","GOOD FOOD, SHARED.",(-8.65,-3.519,4.68),.12,b.materials["arch_wall"],collection=c,rotation=(1.5708,0,0),extrude=.0006,web=True)


def math_sign(value): return 1 if value>0 else -1
