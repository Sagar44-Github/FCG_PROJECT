"""Render one presentation illuminant per Blender process to bound memory.

Example:
  blender -b blender/q3_supermarket.blend --python blender/scripts/render_lighting_demo.py -- --illumination-id L3
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import setup_lighting

parser = argparse.ArgumentParser()
parser.add_argument("--illumination-id", required=True, choices=("L1", "L2", "L3"))
parser.add_argument("--samples", type=int, default=8)
parser.add_argument("--width", type=int, default=1600)
parser.add_argument("--height", type=int, default=900)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

scene = bpy.data.scenes.get("HERO_SUPERMARKET")
if scene is None:
    raise RuntimeError("HERO_SUPERMARKET is missing from the opened Blender file.")
setup_lighting.set_condition(SimpleNamespace(scene=scene), args.illumination_id)
scene.camera = next(obj for obj in scene.objects if obj.get("view_key") == "illumination_comparison")
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = max(1, min(args.samples, 64))
scene.cycles.use_denoising = True
scene.render.resolution_x = args.width
scene.render.resolution_y = args.height
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.filepath = str(ROOT / "blender" / "renders" / "supermarket" / "final" / "illumination_components" / f"{args.illumination_id}_macro.png")
Path(scene.render.filepath).parent.mkdir(parents=True, exist_ok=True)
print(f"Rendering presentation preset {args.illumination_id} at {args.width}×{args.height} ({scene.cycles.samples} samples).", flush=True)
bpy.ops.render.render(write_still=True)
print(f"Saved RGB presentation preview: {scene.render.filepath}", flush=True)
