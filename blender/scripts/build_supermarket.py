"""Regenerate the VERDANT MARKET hero scene alongside the original research rig.

Run: blender -b blender/q3_project.blend --python blender/scripts/build_supermarket.py
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import bpy

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path: sys.path.insert(0,str(SCRIPTS))

from hero_context import HeroBuilder
import build_architecture, build_shelving, build_labels, build_products, setup_lighting, setup_cameras


def main():
    # Preserve and explicitly name the controlled scene in this coordinated
    # project copy. q3_project.blend itself is the immutable baseline input.
    original=bpy.context.scene
    if original and original.name=="Scene": original.name="RESEARCH_LABEL_MEASUREMENT"
    prior=bpy.data.scenes.get("HERO_SUPERMARKET")
    if prior:
        bpy.data.scenes.remove(prior,do_unlink=True)
    scene=bpy.data.scenes.new("HERO_SUPERMARKET")
    if bpy.context.window: bpy.context.window.scene=scene
    config=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
    b=HeroBuilder(scene,config)
    build_architecture.build(b)
    build_shelving.build(b)
    build_labels.build(b)
    build_products.build(b)
    setup_lighting.build(b,"L1")
    setup_cameras.build(b)
    scene.camera=b.cameras["01_supermarket_hero"]

    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=24
    scene.cycles.preview_samples=8
    scene.cycles.use_denoising=True
    scene.render.threads_mode="AUTO"
    scene.render.resolution_x=2560; scene.render.resolution_y=1440; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGB"; scene.render.image_settings.color_depth="8"
    scene.render.image_settings.compression=18
    scene.render.film_transparent=False
    scene.render.use_file_extension=True
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=0; scene.view_settings.gamma=1
    scene.render.filepath=str(ROOT/"blender"/"renders"/"supermarket"/"previews"/"01_supermarket_hero.png")
    scene["render_engine_note"]="Cycles CPU render. AgX is used for cinematic presentation; the research measurement scene retains Standard. No rendered RGB value is a spectral measurement."
    scene["configured_source"]="config.json (initial colour and illumination parameters unchanged)"
    scene["blender_scene_role"]="presentation digital twin; separate from the authoritative controlled measurement scene"
    (ROOT/"blender"/"renders"/"supermarket"/"previews").mkdir(parents=True,exist_ok=True)
    (ROOT/"blender"/"renders"/"supermarket"/"final").mkdir(parents=True,exist_ok=True)
    out=ROOT/"blender"/"q3_supermarket.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
    print(f"VERDANT MARKET scene saved: {out}")
    print(f"Objects: {len(scene.objects)} | products: {scene.get('product_instance_count')} | camera rig: {len(b.cameras)}")


if __name__=="__main__": main()
