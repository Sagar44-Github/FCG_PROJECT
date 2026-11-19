"""Set the saved Blender file to a useful interactive supermarket demo view."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import bpy

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "blender" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import setup_lighting

scene = bpy.data.scenes.get("HERO_SUPERMARKET")
if scene is None:
    raise RuntimeError("HERO_SUPERMARKET is missing. Open blender/q3_supermarket.blend.")

scene.camera = next(obj for obj in scene.objects if obj.get("view_key") == "01_supermarket_hero")
scene.render.engine = "CYCLES"
scene.cycles.preview_samples = 8
scene["demo_instructions"] = (
    "The file opens on the supermarket hero camera. In the Scripting workspace run "
    "the embedded Q3 Lighting Lab.py script; then press N in the 3D viewport and "
    "select the Q3 Research tab to switch D65 / neutral LED / warm LED RGB presets. "
    "Press F12 to render the selected light and camera."
)
setup_lighting.set_condition(SimpleNamespace(scene=scene), "L1")

# Camera view and scene-lit Material Preview avoid the plan-like construction
# viewport and make the RGB light buttons visible without starting a full render.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type != "VIEW_3D":
            continue
        space = area.spaces.active
        space.region_3d.view_perspective = "CAMERA"
        space.shading.type = "MATERIAL"
        space.shading.use_scene_lights = True
        space.shading.use_scene_world = True

script_path = SCRIPTS / "lighting_lab.py"
script_text = bpy.data.texts.get("Q3 Lighting Lab.py") or bpy.data.texts.new("Q3 Lighting Lab.py")
script_text.clear()
script_text.write(script_path.read_text(encoding="utf-8"))

if bpy.context.window:
    bpy.context.window.scene = scene
bpy.ops.wm.save_mainfile()
print("Prepared Q3 supermarket demo startup and embedded the Q3 Lighting Lab script.")
