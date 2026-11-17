"""Export factual Blender scene settings and shader links from the saved .blend."""
import json
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
label=bpy.data.materials["Shelf label | scenario-controlled"]
diffuse=next(n for n in label.node_tree.nodes if n.type=="BSDF_DIFFUSE")
light=bpy.data.lights["Scenario illuminant panel"]
links=[]
for node in light.node_tree.nodes:
    for link in light.node_tree.links:
        if link.from_node==node:
            links.append({"from_node":node.name,"from_socket":link.from_socket.name,
                          "to_node":link.to_node.name,"to_socket":link.to_socket.name})
record={"blender_version":bpy.app.version_string,"project_file":str(ROOT/"blender"/"q3_project.blend"),
        "engine":scene.render.engine,"view_transform":scene.view_settings.view_transform,
        "look":scene.view_settings.look,"exposure":scene.view_settings.exposure,"gamma":scene.view_settings.gamma,
        "resolution_px":[scene.render.resolution_x,scene.render.resolution_y],"resolution_percentage":scene.render.resolution_percentage,
        "cycles_samples":scene.cycles.samples,"denoising":scene.cycles.use_denoising,
        "label_material":label.name,"label_hex":"#2E9E4F","label_diffuse_linear_rgba":list(diffuse.inputs["Color"].default_value),
        "label_diffuse_roughness":float(diffuse.inputs["Roughness"].default_value),
        "label_shader_nodes":[n.name for n in label.node_tree.nodes],
        "label_shader_links":[{"from_node":l.from_node.name,"from_socket":l.from_socket.name,"to_node":l.to_node.name,"to_socket":l.to_socket.name} for l in label.node_tree.links],
        "light_name":light.name,"light_energy":float(light.energy),"light_shader_nodes":[n.name for n in light.node_tree.nodes],
        "light_shader_links":links,"scene_spectral_note":scene.get("spectral_method_note",""),
        "scene_illuminant_note":scene.get("illuminant_note","")}
target=ROOT/"results"/"blender_scene_inspection.json"
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(record,indent=2),encoding="utf-8")
print(target)
