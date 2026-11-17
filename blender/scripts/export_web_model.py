"""Build a compact linked-mesh shelf segment and export the actual GLB for R3F."""
from __future__ import annotations
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"frontend"/"public"/"assets"/"supermarket"/"verdant_market.glb"


def main():
    hero=bpy.data.scenes.get("HERO_SUPERMARKET")
    if hero is None: raise RuntimeError("HERO_SUPERMARKET scene missing")
    web_scene=bpy.data.scenes.new("TEMP · glTF shelf segment export")
    if bpy.context.window: bpy.context.window.scene=web_scene
    col=bpy.data.collections.new("WEB DIGITAL TWIN · linked hero assets"); web_scene.collection.children.link(col)
    if hasattr(bpy.ops.export_scene,"gltf") is False:
        bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
    # A cropped, performant section of the measured hero-scene shelf uses the
    # same Blender meshes, PBR materials, generated label and product artwork.
    sources=[]
    for obj in hero.objects:
        if not obj.get("web_export") or obj.type not in {"MESH","FONT","CURVE"}: continue
        if abs(obj.location.x)>4.25: continue
        if obj.dimensions.x>9.0: continue
        if obj.name.startswith(("Gondola shelf deck","Shelf front channel","Shelf ticket rail acrylic","Shelf underlight diffuser")):
            continue
        # Restrict assets to the front featured gondola (not sign/produce/racks).
        if -6.1<=obj.location.y<=-4.1:
            sources.append(obj)
    for source in sources:
        item=source.copy()
        if source.data is not None: item.data=source.data
        col.objects.link(item)
        item.location=(source.location.x,source.location.y+5.25,source.location.z)
        item["web_export"]=True
        item["source_scene_object"]=source.name
    steel=bpy.data.materials.get("Powder coat · forest graphite")
    deck=bpy.data.materials.get("Gondola shelf · warm grey powder coat")
    brass=bpy.data.materials.get("Brushed champagne brass")
    rail=bpy.data.materials.get("Clear label cover · PETG")
    floor=bpy.data.materials.get("Warm oak floor · visual only")
    if floor is None:
        floor=bpy.data.materials.new("Web model · warm neutral floor")
        floor.diffuse_color=(.19,.15,.10,1); floor.use_nodes=True; floor.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=(.19,.15,.10,1)
    def cube(name,loc,dims,mat,bevel=.015):
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
        o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
        if mat:o.data.materials.append(mat)
        if bevel:
            m=o.modifiers.new("machined edge","BEVEL"); m.width=bevel; m.segments=2
            o.modifiers.new("weighted corner normals","WEIGHTED_NORMAL")
        return o
    # Neutral floor and 4-level retail gondola frame, sized for mobile orbit.
    cube("Web shelf · illuminated presentation floor",(0,0,-.22),(9.2,2.85,.38),floor,.08)
    cube("Web shelf · rear brand panel",(0,.68,2.18),(8.95,.15,4.2),steel,.045)
    for x in (-4.34,4.34):
        cube(f"Web shelf · upright {x}",(x,0,2.10),(.14,.82,4.25),steel,.018)
        cube(f"Web shelf · oak end cheek {x}",(x, -.48,2.15),(.19,.10,4.25),bpy.data.materials.get("White oak · satin"),.025)
    levels=(.64,1.47,2.30,3.13)
    for i,z in enumerate(levels):
        cube(f"Web shelf · deck {i+1}",(0,0,z),(8.65,1.02,.078),deck,.018)
        cube(f"Web shelf · ticket channel {i+1}",(0,-.54,z+.045),(8.68,.06,.095),brass,.01)
        cube(f"Web shelf · clear ticket guard {i+1}",(0,-.579,z+.052),(8.54,.02,.06),rail,.008)
        bpy.ops.object.select_all(action="DESELECT")
    # Add lightweight aisle-side brass uprights to make the digital twin read as
    # a physical gondola rather than a stack of isolated floating products.
    for x in (-4.25,4.25):
        cube(f"Web shelf · brass edge inlay {x}",(x,-.535,2.1),(.022,.012,4.12),brass,.003)
    # Keep selected face labels readily hit-testable in the GLB hierarchy.
    for obj in col.objects:
        if obj.get("source_scene_object","").startswith("Q3_LABEL_"):
            obj.name=obj.get("source_scene_object")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in col.objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=next((o for o in col.objects if o.type=="MESH"),None)
    # Export selection only so the source research scene, templates, cameras and
    # out-of-frame product variants are excluded from the browser payload.
    result=bpy.ops.export_scene.gltf(filepath=str(OUT),export_format="GLB",use_selection=True,export_apply=True,export_lights=False,export_cameras=False)
    bpy.data.scenes.remove(web_scene,do_unlink=True)
    if bpy.context.window: bpy.context.window.scene=hero
    if "FINISHED" not in result: raise RuntimeError(f"glTF export did not finish: {result}")
    print(f"Exported {len(sources)} linked hero assets + fixture geometry: {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__=="__main__":main()
