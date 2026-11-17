"""Build and render the twelve Blender RGB visualization scenarios.

Run:
  blender --background --python blender/scripts/render_batch.py -- --output-dir renders --samples 16

Cycles is RGB-based here. Spectral calculations in colour_engine are authoritative
for colorimetric results; Blender images are controlled scene visualizations.
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
with (ROOT / "config.json").open(encoding="utf-8") as stream:
    CONFIG = json.load(stream)

def args_after_separator():
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "renders"))
    parser.add_argument("--samples", type=int, default=16)
    parser.add_argument("--blend-output", default=str(ROOT/"blender"/"q3_project.blend"))
    parser.add_argument("--colour-id", choices=list(CONFIG["colours"]), help="Optional single-color preview")
    parser.add_argument("--illumination-id", choices=list(CONFIG["illuminations"]), help="Optional single-illumination preview")
    return parser.parse_args(values)

def srgb_byte_to_linear(value):
    v = value / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

def hex_rgba(value):
    h = value.lstrip("#")
    return tuple(srgb_byte_to_linear(int(h[i:i+2], 16)) for i in (0,2,4)) + (1.0,)

def principled_material(name, rgba, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    diffuse = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse.name = "Controlled Diffuse Surface"
    diffuse.inputs["Color"].default_value = rgba
    diffuse.inputs["Roughness"].default_value = roughness
    output = nodes.new("ShaderNodeOutputMaterial")
    diffuse.location = (0, 0); output.location = (240, 0)
    mat.node_tree.links.new(diffuse.outputs["BSDF"], output.inputs["Surface"])
    return mat

def add_cube(name, location, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object; obj.name = name; obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("Soft product-safe edges", "BEVEL"); mod.width=bevel; mod.segments=3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj

def add_text(name, text, location, size, material):
    curve = bpy.data.curves.new(name, "FONT"); curve.body = text; curve.size = size
    curve.align_x = "CENTER"; curve.align_y = "CENTER"; curve.extrude = 0.001
    obj = bpy.data.objects.new(name, curve); bpy.context.collection.objects.link(obj)
    obj.location = location; obj.rotation_euler[0] = math.radians(90)
    obj.data.materials.append(material)
    return obj

def aim(obj, point):
    direction = (mathutils.Vector(point) - obj.location)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

def setup_scene(output_dir, samples):
    global mathutils
    import mathutils
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    for data in bpy.data.materials:
        if data.users == 0: bpy.data.materials.remove(data)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 960; scene.render.resolution_y = 640; scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0; scene.view_settings.gamma = 1.0
    scene.world.use_nodes = True
    background=scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value=(0.02,0.025,0.03,1)
    background.inputs["Strength"].default_value=.35
    scene.render.image_settings.color_depth = "8"

    shelfmat = principled_material("Shelf | neutral coated steel", (0.19,0.22,0.25,1))
    backingmat = principled_material("Back panel | neutral grey", (0.27,0.29,0.31,1))
    grey = principled_material("Reference card | neutral 18 percent grey", (0.18,0.18,0.18,1))
    white = principled_material("Label typography | neutral white", (0.85,0.85,0.85,1), 0.55)
    dark = principled_material("Card typography | charcoal", (0.025,0.025,0.025,1))
    add_cube("Shelf deck", (0,0.1,0.57), (5.4,1.25,0.16), shelfmat, .035)
    add_cube("Shelf front rail", (0,-0.57,0.78), (5.2,.13,.27), backingmat, .025)
    add_cube("Shelf back panel", (0,0.68,1.55), (5.4,.14,2.1), backingmat, .025)
    add_cube("Left upright", (-2.55,.0,1.47), (.15,1.25,1.95), shelfmat, .025)
    add_cube("Right upright", (2.55,.0,1.47), (.15,1.25,1.95), shelfmat, .025)
    labelmat = principled_material("Shelf label | scenario-controlled", hex_rgba("#D62828"), .36)
    label = add_cube("Expiry warning shelf label", (0,-.49,1.36), (2.75,.045,.92), labelmat, .035)
    front = add_text("Retail action", "DONATE NOW", (0,-.519,1.48), .29, white)
    sub = add_text("Warning subtitle", "EXPIRY WARNING", (0,-.521,1.20), .125, white)
    cardmat = principled_material("Grey reference swatch", (.18,.18,.18,1), .65)
    card = add_cube("Grey reference card", (-1.9,-.475,1.38), (.62,.045,.62), cardmat, .012)
    add_text("Reference card text", "18% GREY", (-1.9,-.51,1.0), .09, dark)

    camera_data=bpy.data.cameras.new("Measurement camera")
    camera=bpy.data.objects.new("Measurement camera",camera_data); bpy.context.collection.objects.link(camera)
    camera.location=(0,-6.8,2.45); aim(camera,(0,0,1.25)); camera_data.lens=45
    scene.camera=camera

    light_data=bpy.data.lights.new("Scenario illuminant panel",type="AREA")
    light_data.shape="RECTANGLE"; light_data.size=3.1; light_data.size_y=1.5; light_data.energy=200
    light=bpy.data.objects.new("Scenario illuminant panel",light_data); bpy.context.collection.objects.link(light)
    light.location=(0,-2.6,3.6); aim(light,(0,0,1.2))
    light_data.use_nodes=True
    nodes=light_data.node_tree.nodes; nodes.clear()
    blackbody=nodes.new("ShaderNodeBlackbody"); blackbody.name="Approximate LED chromaticity only"
    emission=nodes.new("ShaderNodeEmission"); emission.name="RGB area-light emission"
    output=nodes.new("ShaderNodeOutputLight")
    nodes["Approximate LED chromaticity only"].location=(-420,100)
    emission.location=(-160,100); output.location=(100,100)
    light_data.node_tree.links.new(emission.outputs["Emission"],output.inputs["Surface"])
    scene["spectral_method_note"]="Blender Cycles RGB render for visual comparison only. D65 and LED colorimetry is calculated in Python from spectra; no 6500 K blackbody is used as D65."
    scene["colour_management"]="Cycles; Standard view transform; exposure 0; gamma 1"
    scene["dataset_reference"]="CIE D65 1 nm SPD + CIE 1931 2 degree observer; see data/ and docs/spectral_sources.md"
    return scene,labelmat,light_data,emission,blackbody,output_dir

def render_all():
    args=args_after_separator()
    output=Path(args.output_dir).resolve(); output.mkdir(parents=True,exist_ok=True)
    scene,labelmat,light_data,emission,blackbody,outdir=setup_scene(output,args.samples)
    cycles_blend=Path(args.blend_output).resolve();cycles_blend.parent.mkdir(parents=True,exist_ok=True)
    first=True
    selected_colours={k:v for k,v in CONFIG["colours"].items() if not args.colour_id or k==args.colour_id}
    selected_illuminations={k:v for k,v in CONFIG["illuminations"].items() if not args.illumination_id or k==args.illumination_id}
    for colour_id, colour in selected_colours.items():
        rgba=hex_rgba(colour["hex"])
        labelmat.diffuse_color=rgba
        diffuse=next(n for n in labelmat.node_tree.nodes if n.type=="BSDF_DIFFUSE")
        diffuse.inputs["Color"].default_value=rgba
        # Text action follows the retail meaning while preserving geometry.
        text_by_action={"fresh":"FRESH","watch":"WATCH","discount":"DISCOUNT NOW","donate":"DONATE NOW"}
        action_obj=bpy.data.objects.get("Retail action"); action_obj.data.body=text_by_action[colour["action"]].upper()
        subtitle=bpy.data.objects.get("Warning subtitle")
        subtitle.data.body={"fresh":"NO ACTION","watch":"CHECK DATE","discount":"PRICE REDUCTION","donate":"EXPIRY WARNING"}[colour["action"]]
        for illumination_id,illum in selected_illuminations.items():
            if illum["kind"]=="cie_d65":
                # Neutral RGB white is an RGB visualization stand-in. The SPD is
                # handled numerically in the separate spectral integration path.
                emission.inputs["Color"].default_value=(1,1,1,1)
                light_data.node_tree.links.remove(next((link for link in light_data.node_tree.links if link.to_node==emission),None)) if any(link.to_node==emission for link in light_data.node_tree.links) else None
                emission.inputs["Strength"].default_value=1.0
                scene["illuminant_note"]="CIE D65 visualization uses neutral RGB white. Its 1 nm SPD is evaluated outside Blender; this is not a blackbody substitute."
            else:
                if not any(link.to_node==emission for link in light_data.node_tree.links):
                    light_data.node_tree.links.new(blackbody.outputs["Color"],emission.inputs["Color"])
                blackbody.inputs["Temperature"].default_value=float(illum["cct_kelvin"])
                emission.inputs["Strength"].default_value=1.0
                scene["illuminant_note"]="Approximate Blackbody chromaticity for scene visualization only; research LED spectrum is parameterized in Python."
            scene["current_colour_id"]=colour_id; scene["current_illumination_id"]=illumination_id
            filepath=output/f"{colour_id}_{illumination_id}.png"
            scene.render.filepath=str(filepath)
            if first:
                bpy.ops.wm.save_as_mainfile(filepath=str(cycles_blend)); first=False
            bpy.ops.render.render(write_still=True)
            print("Q3_RENDER",colour_id,illumination_id,filepath,flush=True)
    print("Q3_DONE",len(list(output.glob("*.png"))),str(cycles_blend),flush=True)

if __name__=="__main__":
    render_all()
