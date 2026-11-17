"""Named editorial cameras for the six repeatable supermarket view products."""
import bpy
from mathutils import Vector
from hero_utils import aim

VIEWS={
    "01_supermarket_hero":{"lens":29,"resolution":(2560,1440),"samples":24},
    "02_shelf_detail":{"lens":42,"resolution":(2560,1440),"samples":28},
    "03_donate_now_macro":{"lens":72,"resolution":(2560,1440),"samples":32},
    "04_colour_status_system":{"lens":46,"resolution":(2560,1440),"samples":26},
    "illumination_comparison":{"lens":46,"resolution":(2560,1440),"samples":24},
    "06_supermarket_isometric":{"lens":35,"resolution":(2560,1440),"samples":24},
}


def _camera(b, name, location, target, lens, dof=False, ortho=None):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); b.collection("06 · CAMERA RIG").objects.link(obj)
    obj.location=location; aim(obj,target); data.lens=lens; data.sensor_width=36; data.clip_start=.03; data.clip_end=250
    if ortho:
        data.type="ORTHO"; data.ortho_scale=ortho
    if dof:
        data.dof.use_dof=True; data.dof.aperture_fstop=5.6; data.dof.aperture_blades=9
        focus=bpy.data.objects.get("Q3_LABEL_R_PANEL")
        if focus: data.dof.focus_object=focus
    return obj


def build(b):
    b.cameras={}
    b.cameras["01_supermarket_hero"]=_camera(b,"CAM · 01 Supermarket hero",(11,-9.5,5.2),(0,3.0,2.6),29)
    b.cameras["02_shelf_detail"]=_camera(b,"CAM · 02 Shelf detail",(3.5,-8.6,3.0),(.15,-5.55,2.15),47)
    b.cameras["03_donate_now_macro"]=_camera(b,"CAM · 03 Donate-now macro",(2.45,-8.15,1.92),(1.62,-5.91,1.525),72,dof=True)
    b.cameras["04_colour_status_system"]=_camera(b,"CAM · 04 Four-colour status system",(.0,-11.4,2.15),(0,-5.91,1.525),44,dof=True)
    status_focus=bpy.data.objects.get("Q3_LABEL_R_PANEL")
    if status_focus:
        b.cameras["04_colour_status_system"].data.dof.focus_object=status_focus
        b.cameras["04_colour_status_system"].data.dof.aperture_fstop=9.0
    b.cameras["illumination_comparison"]=_camera(b,"CAM · Illuminant comparison lockoff",(4.5,-11.4,4.25),(.1,-5.55,2.15),46)
    b.cameras["06_supermarket_isometric"]=_camera(b,"CAM · 06 Isometric plan view",(17,-20,20),(0,1.8,1.9),35,ortho=31)
    for key,camera in b.cameras.items():
        camera["view_key"]=key
    b.scene["camera_rig"]="Six locked, named views with repeatable focal lengths and camera targets."
