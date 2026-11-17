"""Shared geometry, material, UV, collection, and photographic helpers for the hero scene."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
TEXTURES = ROOT / "blender" / "assets" / "generated_textures"

def srgb_to_linear_byte(value: int) -> float:
    v=value/255.0
    return v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4

def hex_linear(value: str) -> tuple[float,float,float,float]:
    h=value.strip().lstrip("#")
    return tuple(srgb_to_linear_byte(int(h[i:i+2],16)) for i in (0,2,4))+(1.0,)

def ensure_collection(scene: bpy.types.Scene, name: str, *, parent: bpy.types.Collection|None=None, hidden=False) -> bpy.types.Collection:
    coll=bpy.data.collections.get(name)
    if coll is None: coll=bpy.data.collections.new(name)
    target=parent or scene.collection
    if coll.name not in target.children: target.children.link(coll)
    coll.hide_render=hidden
    return coll

def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for old in list(obj.users_collection): old.objects.unlink(obj)
    collection.objects.link(obj)

def set_input(node: bpy.types.Node, names: Iterable[str], value) -> None:
    for name in names:
        socket=node.inputs.get(name)
        if socket is not None:
            socket.default_value=value
            return

def surface(name: str, color: str|tuple, roughness=.42, metallic=0.0, *,
            transmission=0.0, ior=1.46, coat=0.0, anisotropy=0.0,
            texture: str|Path|None=None, texture_scale=1.0, bump_strength=0.0,
            bump_distance=.004, procedural: str|None=None) -> bpy.types.Material:
    color_rgba=hex_linear(color) if isinstance(color,str) else color
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color=color_rgba; mat.use_nodes=True
    nt=mat.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial"); out.location=(680,80)
    bs=nt.nodes.new("ShaderNodeBsdfPrincipled"); bs.location=(390,80)
    bs.inputs["Base Color"].default_value=color_rgba
    bs.inputs["Roughness"].default_value=roughness
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["IOR"].default_value=ior
    set_input(bs,("Transmission Weight","Transmission"),transmission)
    set_input(bs,("Coat Weight","Clearcoat"),coat)
    set_input(bs,("Anisotropic IOR Level","Anisotropic"),anisotropy)
    nt.links.new(bs.outputs["BSDF"],out.inputs["Surface"])
    texcoord=nt.nodes.new("ShaderNodeTexCoord"); texcoord.location=(-900,220)
    if texture:
        path=Path(texture)
        image=bpy.data.images.load(str(path),check_existing=True)
        # Blend files live in ROOT/blender/, so the relative asset path must
        # resolve from that directory when Blender packs the source image.
        image.filepath="//" + path.resolve().relative_to((ROOT/"blender").resolve()).as_posix()
        image.pack()
        tex=nt.nodes.new("ShaderNodeTexImage"); tex.image=image; tex.interpolation="Linear"; tex.location=(-610,240)
        nt.links.new(texcoord.outputs["UV"],tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"],bs.inputs["Base Color"])
        rough=nt.nodes.new("ShaderNodeValToRGB"); rough.location=(-180,-10)
        rough.color_ramp.elements[0].position=.08; rough.color_ramp.elements[0].color=(roughness*.73,)*3+(1,)
        rough.color_ramp.elements[1].position=.94; rough.color_ramp.elements[1].color=(min(1,roughness*1.18),)*3+(1,)
        nt.links.new(tex.outputs["Color"],rough.inputs["Fac"]); nt.links.new(rough.outputs["Color"],bs.inputs["Roughness"])
    if procedural:
        noise=nt.nodes.new("ShaderNodeTexNoise"); noise.location=(-610,-220)
        noise.inputs["Scale"].default_value=texture_scale
        noise.inputs["Detail"].default_value=3.0
        noise.inputs["Roughness"].default_value=.72
        nt.links.new(texcoord.outputs["Generated"],noise.inputs["Vector"])
        if procedural=="wood":
            wave=nt.nodes.new("ShaderNodeTexWave"); wave.location=(-610,-450)
            wave.inputs["Scale"].default_value=13.0; wave.inputs["Distortion"].default_value=1.8
            wave.inputs["Detail"].default_value=2.0
            nt.links.new(texcoord.outputs["Generated"],wave.inputs["Vector"])
            ramp=nt.nodes.new("ShaderNodeValToRGB"); ramp.location=(-350,-220)
            ramp.color_ramp.elements[0].position=.1; ramp.color_ramp.elements[0].color=(.12,.067,.033,1)
            ramp.color_ramp.elements[1].position=.88; ramp.color_ramp.elements[1].color=(.36,.23,.135,1)
            mid=ramp.color_ramp.elements.new(.56); mid.color=(.23,.13,.075,1)
            nt.links.new(wave.outputs["Color"],ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
            bump_source=wave.outputs["Color"]
        elif procedural=="stone":
            vor=nt.nodes.new("ShaderNodeTexVoronoi"); vor.location=(-600,-450)
            vor.feature="DISTANCE_TO_EDGE"; vor.inputs["Scale"].default_value=16
            nt.links.new(texcoord.outputs["Generated"],vor.inputs["Vector"])
            ramp=nt.nodes.new("ShaderNodeValToRGB"); ramp.location=(-340,-220)
            ramp.color_ramp.elements[0].position=.03; ramp.color_ramp.elements[0].color=(.05,.052,.052,1)
            ramp.color_ramp.elements[1].position=.15; ramp.color_ramp.elements[1].color=(.24,.25,.24,1)
            nt.links.new(vor.outputs["Distance"],ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"],bs.inputs["Base Color"])
            bump_source=noise.outputs["Fac"]
        else:
            bump_source=noise.outputs["Fac"]
        if bump_strength>0:
            bump=nt.nodes.new("ShaderNodeBump"); bump.location=(120,-220)
            bump.inputs["Strength"].default_value=bump_strength
            bump.inputs["Distance"].default_value=bump_distance
            nt.links.new(bump_source,bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])
        roughramp=nt.nodes.new("ShaderNodeMapRange"); roughramp.location=(-120,-450)
        roughramp.inputs["From Min"].default_value=.15; roughramp.inputs["From Max"].default_value=.85
        roughramp.inputs["To Min"].default_value=max(.03,roughness-.08); roughramp.inputs["To Max"].default_value=min(.95,roughness+.1)
        nt.links.new(noise.outputs["Fac"],roughramp.inputs["Value"]); nt.links.new(roughramp.outputs["Result"],bs.inputs["Roughness"])
    return mat

def emissive(name: str, color: str, strength=1.0) -> bpy.types.Material:
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name); mat.diffuse_color=hex_linear(color); mat.use_nodes=True
    nt=mat.node_tree; nt.nodes.clear(); out=nt.nodes.new("ShaderNodeOutputMaterial"); em=nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value=hex_linear(color); em.inputs["Strength"].default_value=strength
    nt.links.new(em.outputs["Emission"],out.inputs["Surface"])
    return mat

def texture_surface(name: str, image_path: str|Path, roughness=.42, *, metallic=0.0, bump_strength=0.0) -> bpy.types.Material:
    return surface(name,"#F5F0E5",roughness,metallic,texture=Path(image_path),bump_strength=bump_strength,procedural="noise" if bump_strength else None,texture_scale=145,bump_distance=.0012)

def object_from_mesh(name: str, vertices, faces, *, materials=(), location=(0,0,0), collection,
                     uvs=None, material_indices=None, smooth=False) -> bpy.types.Object:
    mesh=bpy.data.meshes.new(name+" · mesh"); mesh.from_pydata(vertices,[],faces); mesh.update(calc_edges=True)
    for mat in materials: mesh.materials.append(mat)
    if material_indices:
        for i,poly in enumerate(mesh.polygons): poly.material_index=material_indices[i]
    if uvs:
        layer=mesh.uv_layers.new(name="UVMap")
        for poly in mesh.polygons:
            uvface=uvs[poly.index]
            for loop_index,uv in zip(poly.loop_indices,uvface): layer.data[loop_index].uv=uv
    if smooth:
        for poly in mesh.polygons: poly.use_smooth=True
    obj=bpy.data.objects.new(name,mesh); obj.location=location; collection.objects.link(obj)
    return obj

BOX_FACES=((0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7))
BOX_UVS=(((0,0),(1,0),(1,1),(0,1)),)*6

def box(name: str, location, dimensions, material, *, collection, bevel=0.0, front_material=None, web=False):
    x,y,z=(v/2 for v in dimensions)
    verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    materials=[material]+([front_material] if front_material else [])
    indices=[0,1 if front_material else 0,0,0,0,0]
    obj=object_from_mesh(name,verts,BOX_FACES,materials=materials,location=location,collection=collection,uvs=list(BOX_UVS),material_indices=indices)
    if bevel>0:
        mod=obj.modifiers.new("Machined micro-bevel","BEVEL"); mod.width=bevel; mod.segments=3
        mod.profile=.5
        obj.modifiers.new("Corner-weighted normals","WEIGHTED_NORMAL")
    obj["web_export"]=bool(web)
    return obj

def quad(name: str, center, width, height, material, *, collection, rotation=0.0, web=False):
    w=width/2; h=height/2
    verts=[(-w,-.0002,-h),(w,-.0002,-h),(w,-.0002,h),(-w,-.0002,h)]
    obj=object_from_mesh(name,verts,[(0,1,2,3)],materials=[material],location=center,collection=collection,
                         uvs=[((0,0),(1,0),(1,1),(0,1))])
    obj.rotation_euler[2]=rotation; obj["web_export"]=bool(web)
    return obj

def cylinder(name: str, location, radius, depth, material, *, collection, vertices=24, bevel=0.0, rotation=(0,0,0), smooth=True, web=False):
    verts=[]
    for z in (-depth/2,depth/2):
        verts.extend([(radius*math.cos(2*math.pi*i/vertices),radius*math.sin(2*math.pi*i/vertices),z) for i in range(vertices)])
    faces=[tuple(reversed(tuple(range(vertices)))),tuple(range(vertices,2*vertices))]
    for i in range(vertices): faces.append((i,(i+1)%vertices,(i+1)%vertices+vertices,i+vertices))
    obj=object_from_mesh(name,verts,faces,materials=[material],location=location,collection=collection,smooth=smooth)
    obj.rotation_euler=rotation; obj["web_export"]=bool(web)
    if bevel:
        mod=obj.modifiers.new("Rolled rim edge","BEVEL"); mod.width=bevel; mod.segments=2
        obj.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return obj

def lathe(name: str, profile: list[tuple[float,float]], material, *, collection, center=(0,0,0), segments=32, smooth=True, web=False):
    verts=[]
    for z,r in profile:
        for i in range(segments):
            angle=2*math.pi*i/segments
            verts.append((r*math.cos(angle),r*math.sin(angle),z))
    faces=[]
    for ring in range(len(profile)-1):
        for i in range(segments):
            a=ring*segments+i; b=ring*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    faces.append(tuple(reversed(tuple(range(segments)))))
    faces.append(tuple((len(profile)-1)*segments+i for i in range(segments)))
    obj=object_from_mesh(name,verts,faces,materials=[material],location=center,collection=collection,smooth=smooth)
    obj["web_export"]=bool(web)
    return obj

def sphere(name: str, location, scale, material, *, collection, seed=0, segments=20, rings=12, organic=0.0, web=False):
    import random
    rng=random.Random(seed); verts=[]
    for j in range(rings+1):
        phi=math.pi*j/rings
        for i in range(segments):
            theta=2*math.pi*i/segments
            perturb=1+organic*(.55*math.sin(3*theta+seed)+.32*math.cos(5*phi+theta*2)+rng.uniform(-.08,.08))
            verts.append((.5*math.sin(phi)*math.cos(theta)*perturb,.5*math.sin(phi)*math.sin(theta)*perturb,.5*math.cos(phi)*perturb))
    faces=[]
    for j in range(rings):
        for i in range(segments):
            a=j*segments+i; b=j*segments+(i+1)%segments
            faces.append((a,b,b+segments,a+segments))
    obj=object_from_mesh(name,verts,faces,materials=[material],location=location,collection=collection,smooth=True)
    obj.scale=scale; obj["web_export"]=bool(web)
    return obj

def torus(name: str, location, major_radius, minor_radius, material, *, collection, major_segments=36, minor_segments=8, web=False):
    verts=[]; faces=[]
    for i in range(major_segments):
        u=2*math.pi*i/major_segments
        for j in range(minor_segments):
            v=2*math.pi*j/minor_segments
            radius=major_radius+minor_radius*math.cos(v)
            verts.append((radius*math.cos(u),radius*math.sin(u),minor_radius*math.sin(v)))
    for i in range(major_segments):
        for j in range(minor_segments):
            a=i*minor_segments+j; b=i*minor_segments+(j+1)%minor_segments
            faces.append((a,b,((i+1)%major_segments)*minor_segments+(j+1)%minor_segments,((i+1)%major_segments)*minor_segments+j))
    obj=object_from_mesh(name,verts,faces,materials=[material],location=location,collection=collection,smooth=True)
    obj["web_export"]=bool(web)
    return obj

def add_text(name: str, body: str, location, size, material, *, collection, rotation=(math.pi/2,0,0), align="CENTER", extrude=.0008, web=False):
    curve=bpy.data.curves.new(name+" · typography","FONT"); curve.body=body; curve.size=size; curve.align_x=align
    curve.extrude=extrude; curve.bevel_depth=.00025; curve.bevel_resolution=1; curve.resolution_u=8
    obj=bpy.data.objects.new(name,curve); collection.objects.link(obj); obj.location=location; obj.rotation_euler=rotation
    obj.data.materials.append(material); obj["web_export"]=bool(web)
    return obj

def aim(obj: bpy.types.Object, point) -> None:
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat("-Z","Y").to_euler()

def clone_assembly(parts: list[bpy.types.Object], *, collection, location, rotation=0.0, scale=1.0, label="Product", web=False) -> list[bpy.types.Object]:
    c=math.cos(rotation); s=math.sin(rotation); output=[]
    for part in parts:
        obj=part.copy()
        if part.data is not None: obj.data=part.data
        obj.name=f"{label} · {part.name.split(' · ')[-1]}"
        collection.objects.link(obj)
        px,py,pz=part.location
        obj.location=(location[0]+scale*(c*px-s*py),location[1]+scale*(s*px+c*py),location[2]+scale*pz)
        obj.rotation_euler=(part.rotation_euler.x,part.rotation_euler.y,part.rotation_euler.z+rotation)
        obj.scale=tuple(v*scale for v in part.scale)
        obj["product_instance"]=label
        obj["web_export"]=bool(web)
        output.append(obj)
    return output
