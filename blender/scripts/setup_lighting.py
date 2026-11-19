"""Cinematic RGB presentation lighting; spectral authority remains Python."""
import bpy
from mathutils import Vector
from hero_utils import hex_linear, box

ILLUMINANTS={
    "L1":{"name":"D65 daylight","hex":"#E6F0FF","world":"#8FAFD8","visual":"cool-neutral RGB presentation preset; CIE D65 spectrum is calculated in Python"},
    "L2":{"name":"Neutral LED · 4000 K approximation","hex":"#FFC978","world":"#D69D5E","visual":"warm-neutral RGB presentation preset; not a measured store-lamp SPD"},
    "L3":{"name":"Warm LED · 3000 K approximation","hex":"#F07832","world":"#B64E22","visual":"amber RGB presentation preset; deliberately visible in the demo and not a measured store-lamp SPD"},
}


def _emission_panel_material(name, kelvin):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial"); out.location=(420,40)
    emit=nt.nodes.new("ShaderNodeEmission"); emit.location=(190,40); emit.inputs["Strength"].default_value=1.2
    if kelvin:
        blackbody=nt.nodes.new("ShaderNodeBlackbody"); blackbody.location=(-60,40); blackbody.inputs["Temperature"].default_value=kelvin
        nt.links.new(blackbody.outputs["Color"],emit.inputs["Color"])
    else:
        emit.inputs["Color"].default_value=(1.0,.96,.89,1)
    nt.links.new(emit.outputs["Emission"],out.inputs["Surface"])
    return mat


def set_condition(b, illuminant_id):
    spec=ILLUMINANTS[illuminant_id]
    rgb=hex_linear(spec["hex"])
    for light in b.scene.objects:
        if light.type=="LIGHT" and light.get("hero_fixture"):
            light.data.color=rgb[:3]
            light.data.energy=light.get("base_energy",750.0)
    for obj in b.scene.objects:
        if obj.get("luminaire_panel"):
            kelvin=None if illuminant_id=="L1" else (4000 if illuminant_id=="L2" else 3000)
            obj.data.materials.clear(); obj.data.materials.append(_emission_panel_material(f"Luminaire emission · {illuminant_id}",kelvin))
    b.scene["visual_illuminant_id"]=illuminant_id
    b.scene["visual_illuminant_name"]=spec["name"]
    b.scene["illumination_visualization_boundary"]=spec["visual"]
    # Keep the selected mode visible in viewport previews and renders. The
    # stronger RGB separation is a teaching aid, not a claim of measured SPD.
    world=b.scene.world
    if world and world.use_nodes:
        background=world.node_tree.nodes.get("Background")
        if background:
            background.inputs["Color"].default_value=hex_linear(spec["world"])
            background.inputs["Strength"].default_value={"L1":.19,"L2":.17,"L3":.14}[illuminant_id]
    b.scene["visual_preset_note"]="RGB presentation preset for demonstration. Use results/*.csv and the Python CIE pipeline for scientific colour values; this is not a calibrated spectral render."


def build(b, initial="L1"):
    c=b.collection("05 · ILLUMINATION & ATMOSPHERE")
    softbox=b.mat("Architectural light diffuser","#F4EEDC",.24)
    brass=b.materials["arch_brass"]
    # Broad, high-mounted area sources; energy is a scene-appearance choice,
    # not a calibrated spectral irradiance measurement.
    for i,(x,y) in enumerate(((-8,-7),(0,-7),(8,-7),(-8,1),(0,1),(8,1),(-8,9),(0,9),(8,9))):
        data=bpy.data.lights.new(f"Shop softbox · {i+1:02d}",type="AREA")
        data.energy=760; data.shape="RECTANGLE"; data.size=4.7; data.size_y=1.1
        obj=bpy.data.objects.new(data.name,data); c.objects.link(obj); obj.location=(x,y,6.42); obj.rotation_euler=(0,0,0)
        obj["hero_fixture"]=True; obj["base_energy"]=760
        # Pitched warm-oak cove reflection without hot point-source highlights.
        data2=bpy.data.lights.new(f"Cove bounce · {i+1:02d}",type="AREA"); data2.energy=150; data2.shape="RECTANGLE"; data2.size=2.6; data2.size_y=.18
        obj2=bpy.data.objects.new(data2.name,data2); c.objects.link(obj2); obj2.location=(x,y,6.77); obj2.rotation_euler=(.15,0,0)
        obj2["hero_fixture"]=True; obj2["base_energy"]=150
        panel=box(f"Recessed luminous diffuser · {i+1:02d}",(x,y,6.89),(4.6,1.0,.025),softbox,collection=c,bevel=.025)
        panel["luminaire_panel"]=True
        for dx in (-2.22,2.22): box(f"Softbox champagne trim · {i+1:02d} · {dx}",(x+dx,y,6.873),(.022,1.01,.025),brass,collection=c,bevel=.008)
    # Warm under-shelf practical emitters are paired with area fixtures to
    # retain believable shelf highlights at preview samples.
    practical=b.mat("Shelf practical emission","#FFF0CF",1.0)
    for ri,y in enumerate(b.shelf_rows):
        for li,z in enumerate(b.shelf_levels):
            data=bpy.data.lights.new(f"Gondola task light · {ri+1}-{li+1}",type="AREA")
            data.energy=28; data.shape="RECTANGLE"; data.size=8.0; data.size_y=.045
            obj=bpy.data.objects.new(data.name,data); c.objects.link(obj); obj.location=(0,y-.30,z-.075); obj.rotation_euler=(0,0,0)
            obj["hero_fixture"]=True; obj["base_energy"]=28
    world=bpy.data.worlds.new("Hero scene · warm daylight atmosphere")
    world.use_nodes=True; world.node_tree.nodes["Background"].inputs["Color"].default_value=(.40,.43,.42,1); world.node_tree.nodes["Background"].inputs["Strength"].default_value=.18
    b.scene.world=world
    set_condition(b,initial)
