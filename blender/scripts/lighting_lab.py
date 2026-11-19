"""Register an interactive lighting panel for the VERDANT MARKET scene.

Run this script once from Blender's Scripting workspace after opening
blender/q3_supermarket.blend. The Q3 Lighting Lab panel appears in the 3D
Viewport sidebar (press N). These are intentionally distinct RGB teaching
presets; scientific spectral results remain in the Python colour engine.
"""
from __future__ import annotations

import sys
from pathlib import Path

import bpy

PROJECT_ROOT = Path(bpy.data.filepath).resolve().parent.parent
SCRIPT_DIR = PROJECT_ROOT / "blender" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import setup_lighting


def set_condition(illuminant_id: str) -> None:
    scene = bpy.data.scenes.get("HERO_SUPERMARKET")
    if scene is None:
        raise RuntimeError("Open blender/q3_supermarket.blend to use the lighting lab.")
    from types import SimpleNamespace

    setup_lighting.set_condition(SimpleNamespace(scene=scene), illuminant_id)
    if bpy.context.window:
        bpy.context.window.scene = scene
    camera_key = scene.camera.get("view_key", "current_camera") if scene.camera else "current_camera"
    preview_dir = PROJECT_ROOT / "blender" / "renders" / "supermarket" / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(preview_dir / f"live_{illuminant_id}_{camera_key}.png")
    # Material Preview normally substitutes a studio HDRI. Ask it to use this
    # scene's real lights and world so changing a preset updates the viewport.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.shading.type = "MATERIAL"
                area.spaces.active.shading.use_scene_lights = True
                area.spaces.active.shading.use_scene_world = True
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


class Q3_OT_set_illuminant(bpy.types.Operator):
    bl_idname = "q3.set_illuminant"
    bl_label = "Set Visual Illuminant"
    bl_options = {"REGISTER", "UNDO"}

    illuminant_id: bpy.props.StringProperty()

    def execute(self, context):
        set_condition(self.illuminant_id)
        self.report({"INFO"}, f"Viewport set to {setup_lighting.ILLUMINANTS[self.illuminant_id]['name']}")
        return {"FINISHED"}


class Q3_PT_lighting_lab(bpy.types.Panel):
    bl_label = "Q3 Lighting Lab"
    bl_idname = "Q3_PT_lighting_lab"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Q3 Research"

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.name == "HERO_SUPERMARKET"

    def draw(self, context):
        layout = self.layout
        scene = bpy.data.scenes.get("HERO_SUPERMARKET")
        active_id = scene.get("visual_illuminant_id", "L1") if scene else "L1"
        layout.label(text="Change store lighting", icon="LIGHT")
        for illuminant_id in ("L1", "L2", "L3"):
            spec = setup_lighting.ILLUMINANTS[illuminant_id]
            row = layout.row(align=True)
            row.operator_context = "INVOKE_DEFAULT"
            operator = row.operator("q3.set_illuminant", text=f"{illuminant_id} · {spec['name']}", depress=active_id == illuminant_id)
            operator.illuminant_id = illuminant_id
        layout.separator()
        layout.label(text="Change camera using the Camera selector.")
        layout.label(text="F12 renders the current camera and light.", icon="RENDER_STILL")
        layout.separator()
        layout.label(text="RGB visual preset; not measured SPD.", icon="INFO")
        layout.label(text="CIE calculations are in the dashboard.")


CLASSES = (Q3_OT_set_illuminant, Q3_PT_lighting_lab)


def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)
    print("Q3 Lighting Lab ready. In the 3D View, press N and choose Q3 Research.")


def unregister():
    for cls in reversed(CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()
