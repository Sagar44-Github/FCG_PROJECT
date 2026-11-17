"""Render six reproducible editorial products and the three-illuminant plate.

Usage: blender -b blender/q3_supermarket.blend --python blender/scripts/render_supermarket.py -- --preview
"""
from __future__ import annotations
import argparse, gc, sys
from pathlib import Path

import bpy

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=Path(__file__).resolve().parent
sys.path.insert(0,str(SCRIPTS))
from hero_context import HeroBuilder
import setup_lighting


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--preview",action="store_true"); ap.add_argument("--views",default="all",help="comma-separated keys or all")
    args=ap.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    scene=bpy.data.scenes.get("HERO_SUPERMARKET")
    if not scene: raise RuntimeError("HERO_SUPERMARKET scene was not found in q3_supermarket.blend")
    bpy.context.window.scene=scene
    config=__import__("json").loads((ROOT/"config.json").read_text(encoding="utf-8"))
    b=HeroBuilder(scene,config)
    preview=args.preview
    out=ROOT/"blender"/"renders"/"supermarket"/("previews" if preview else "final")
    out.mkdir(parents=True,exist_ok=True)
    scene.render.engine="CYCLES"; scene.cycles.device="CPU"; scene.cycles.use_denoising=True
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.image_settings.color_mode="RGB"; scene.render.image_settings.color_depth="8"
    scene.render.film_transparent=False
    scene.view_settings.view_transform="AgX"; scene.view_settings.look="AgX - Medium High Contrast"
    selected=set([x.strip() for x in args.views.split(",") if x.strip()])
    if "all" in selected:
        selected={"01_supermarket_hero","02_shelf_detail","03_donate_now_macro","04_colour_status_system","illumination_comparison","06_supermarket_isometric"}
    keys=("01_supermarket_hero","02_shelf_detail","03_donate_now_macro","04_colour_status_system","06_supermarket_isometric")
    # CPU-friendly proof frames are reviewed before the final resolution pass.
    for key in keys:
        if key not in selected: continue
        camera=next(o for o in scene.objects if o.get("view_key")==key)
        scene.camera=camera
        scene.render.resolution_x,scene.render.resolution_y=((960,540) if preview else (2560,1440))
        scene.cycles.samples=8 if preview else {"01_supermarket_hero":12,"02_shelf_detail":14,"03_donate_now_macro":16,"04_colour_status_system":12,"06_supermarket_isometric":12}[key]
        setup_lighting.set_condition(b,"L1")
        scene.render.filepath=str(out/f"{key}.png")
        temporary_hidden=[]
        if key=="04_colour_status_system":
            # This editorial view isolates the real central G/Y/O/R assembly;
            # all surrounding fixture and product geometry remains in the scene.
            for obj in scene.objects:
                if "label_feature" in obj:
                    temporary_hidden.append((obj,obj.hide_render))
                    obj.hide_render=not bool(obj.get("label_feature"))
        elif key=="06_supermarket_isometric":
            # Open-roof isometric cutaway exposes the store plan without changing
            # the default saved shell or the primary in-store views. Hide the
            # diffuser meshes as well: once the ceiling is cut away, showing
            # luminous panels in mid-air reads as a scene-construction artifact.
            for obj in scene.objects:
                if obj.name.startswith(("Acoustic ceiling plane","Ceiling oak slat","Ceiling raft crossbeam",
                                        "West feature wall","East feature wall","Rear brand wall",
                                        "Shopfront","Entrance oak portal","Entrance oak header",
                                        "Wall oak pilaster","Wall brass pilaster","Rear wall brass reveal",
                                        "Recessed luminous diffuser","Softbox champagne trim")):
                    temporary_hidden.append((obj,obj.hide_render)); obj.hide_render=True
        print(f"Rendering {key} at {scene.render.resolution_x}x{scene.render.resolution_y}, {scene.cycles.samples} Cycles samples",flush=True)
        bpy.ops.render.render(write_still=True)
        for obj,old_value in temporary_hidden: obj.hide_render=old_value
        gc.collect()
    if "illumination_comparison" in selected and not preview:
        frames=[]
        camera=next(o for o in scene.objects if o.get("view_key")=="illumination_comparison")
        scene.camera=camera; scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.cycles.samples=12
        diagnostics=out/"illumination_components"; diagnostics.mkdir(exist_ok=True)
        for light in ("L1","L2","L3"):
            setup_lighting.set_condition(b,light)
            scene.render.filepath=str(diagnostics/f"{light}_macro.png")
            print(f"Rendering comparison frame {light}",flush=True)
            bpy.ops.render.render(write_still=True); frames.append(Path(scene.render.filepath)); gc.collect()
        print("Illuminant frames saved; run compose_supermarket_evidence.py to create the comparison plate and contact sheet.")
    setup_lighting.set_condition(b,"L1")
    print(f"Render pass complete: {out}",flush=True)


if __name__=="__main__": main()
