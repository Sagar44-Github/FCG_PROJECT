"""Original fictional grocery package library and linked shelf-stock instances."""
from __future__ import annotations
import math
from hero_utils import box, cylinder, lathe, quad, sphere, object_from_mesh, clone_assembly

FAMILIES=("milk_carton","juice_carton","glass_bottle","pet_bottle","aluminium_can","cereal_box","snack_pouch","glass_jar","yogurt_tub","refill_pouch","pasta_pack","produce_crate")


def _gable(b, collection, material, width, depth, base_z, peak_z, name):
    x=width/2; y=depth/2
    vertices=[(-x,-y,base_z),(x,-y,base_z),(0,-y,peak_z),(-x,y,base_z),(x,y,base_z),(0,y,peak_z)]
    faces=[(0,1,2),(3,5,4),(0,2,5,3),(1,4,5,2),(0,3,4,1)]
    return object_from_mesh(name,vertices,faces,materials=[material],location=(0,0,0),collection=collection,smooth=False)


def _prototype(b, family, variant, collection):
    mat=b.image_mat(f"Package ink · {family} · {variant+1}",family,variant,roughness=.57,bump_strength=.045)
    kraft=b.mat(f"Package edges · {family}","#E7DDC4",.48)
    cap=b.mat(f"Closures · {family}",("#D9E0C6" if variant==0 else "#C7A168"),.26,.04)
    parts=[]
    if family in ("milk_carton","juice_carton"):
        w,d,h=.33,.245,.49
        body=box(f"{family} · folding board",(0,0,h/2),(w,d,h),kraft,collection=collection,bevel=.012,front_material=mat)
        front=quad(f"{family} · printed face",(0,-d/2-.001,h*.52),w*.82,h*.68,mat,collection=collection)
        roof=_gable(b,collection,kraft,w,d,h,h+.105,f"{family} · folded gable")
        roof.location.z=0
        cap_obj=cylinder(f"{family} · screw cap",(0,0,h+.115),.037,.055,cap,collection=collection,vertices=20,bevel=.005)
        parts.extend((body,front,roof,cap_obj))
    elif family in ("cereal_box","pasta_pack"):
        w,d,h=(.37,.205,.63) if family=="cereal_box" else (.31,.15,.53)
        body=box(f"{family} · carton",(0,0,h/2),(w,d,h),kraft,collection=collection,bevel=.018,front_material=mat)
        front=quad(f"{family} · illustrated panel",(0,-d/2-.001,h*.52),w*.86,h*.76,mat,collection=collection)
        top=box(f"{family} · folded top",(0,0,h+.008),(w*.92,d*.96,.022),cap,collection=collection,bevel=.006)
        parts.extend((body,front,top))
    elif family in ("snack_pouch","refill_pouch"):
        w,d,h=(.31,.155,.48) if family=="snack_pouch" else (.29,.17,.52)
        body=box(f"{family} · flexible pouch",(0,0,h/2),(w,d,h),mat,collection=collection,bevel=.055)
        seam=box(f"{family} · sealed top fin",(0,0,h+.008),(w*.78,d*.82,.035),cap,collection=collection,bevel=.012)
        front=quad(f"{family} · front artwork",(0,-d/2-.002,h*.51),w*.82,h*.74,mat,collection=collection)
        parts.extend((body,seam,front))
        if family=="refill_pouch":
            spout=cylinder("Refill pouch · cap",(.075,0,h+.045),.035,.045,cap,collection=collection,vertices=18,bevel=.004)
            parts.append(spout)
    elif family in ("glass_bottle","pet_bottle"):
        h=.56; r=.112 if family=="glass_bottle" else .105
        bodymat=(b.mat("Green tinted reusable glass","#52786A",.14,.04,transmission=.22,ior=1.47,coat=.3) if family=="glass_bottle" else b.mat("Clear PET resin","#D9E5DD",.19,.02,transmission=.1,ior=1.47,coat=.26))
        body=lathe(f"{family} · moulded bottle",[(.02,r*.82),(.05,r),(.31,r),(.39,r*.82),(.45,r*.46),(.52,r*.42),(.54,r*.35)],bodymat,collection=collection,center=(0,0,0),segments=20,smooth=True)
        label=quad(f"{family} · wrap label",(0,-r*.94,.255),.175,.205,mat,collection=collection)
        neck=cylinder(f"{family} · neck ring",(0,0,.526),r*.39,.04,bodymat,collection=collection,vertices=20,bevel=.004)
        closure=cylinder(f"{family} · closure",(0,0,.565),r*.42,.048,cap,collection=collection,vertices=20,bevel=.005)
        parts.extend((body,label,neck,closure))
    elif family=="aluminium_can":
        bodymat=b.mat("Brushed beverage aluminium","#C5C7C2",.2,.82,anisotropy=.78)
        body=cylinder("Aluminium can · drawn body",(0,0,.21),.12,.42,bodymat,collection=collection,vertices=32,bevel=.012)
        label=quad("Aluminium can · wrap artwork",(0,-.121,.215),.208,.25,mat,collection=collection)
        top=cylinder("Aluminium can · rolled top",(0,0,.424),.105,.018,cap,collection=collection,vertices=32,bevel=.004)
        parts.extend((body,label,top))
    elif family=="glass_jar":
        glass=b.mat("Jar glass · olive tint","#728778",.17,.03,transmission=.34,ior=1.48,coat=.25)
        body=lathe("Preserve jar · glass body",[(.02,.12),(.05,.137),(.31,.137),(.35,.125),(.37,.105)],glass,collection=collection,segments=24,smooth=True)
        label=quad("Preserve jar · paper label",(0,-.139,.195),.205,.16,mat,collection=collection)
        lid=cylinder("Preserve jar · brass lid",(0,0,.388),.112,.047,cap,collection=collection,vertices=28,bevel=.006)
        parts.extend((body,label,lid))
    elif family=="yogurt_tub":
        body=lathe("Cultured tub · tapered paper cup",[(.015,.115),(.045,.13),(.30,.17),(.33,.171)],mat,collection=collection,segments=24,smooth=True)
        foil=cylinder("Cultured tub · foil seal",(0,0,.346),.174,.025,cap,collection=collection,vertices=28,bevel=.004)
        label=quad("Cultured tub · label",(0,-.157,.19),.205,.165,mat,collection=collection)
        parts.extend((body,foil,label))
    elif family=="produce_crate":
        wood=b.materials["arch_oak"]
        crate=box("Harvest crate · wood body",(0,0,.17),(.39,.28,.34),wood,collection=collection,bevel=.025,front_material=mat)
        label=quad("Harvest crate · origin tag",(0,-.143,.175),.29,.18,mat,collection=collection)
        fruit_materials=[b.mat("Crate fruit · red apple","#A94035",.28),b.mat("Crate fruit · golden pear","#D3A64A",.3),b.mat("Crate fruit · orchard green","#6D8C4D",.32)]
        parts.extend((crate,label))
        for i in range(8):
            angle=i*2.399; px=math.cos(angle)*(.085 if i<6 else .045); py=math.sin(angle)*.075
            pz=.34+(.09 if i>=6 else .035)
            apple=sphere(f"Produce · fruit {i+1}",(px,py,pz),(.105,.098,.12),fruit_materials[(i+variant)%3],collection=collection,seed=i+variant*17,segments=12,rings=8,organic=.12)
            parts.append(apple)
    return parts


def build(b):
    library=b.collection("Product Library · linked source meshes",hidden=True)
    products=b.collection("04 · FRESHLY MERCHANDISED PRODUCTS")
    prototypes={}
    for family in FAMILIES:
        for variant in range(3):
            prototypes[(family,variant)]=_prototype(b,family,variant,library)
    for ri,y in enumerate(b.shelf_rows):
        for li,z in enumerate(b.shelf_levels):
            # Alternate twelve fictional packaged categories; each product has
            # a human-readable product family and generated brand artwork.
            count=38
            for i in range(count):
                x=-8.25+i*(16.5/(count-1))
                family=FAMILIES[(i+li*3+ri*5)%len(FAMILIES)]
                variant=(i//len(FAMILIES)+li+ri)%3
                is_web=ri==0 and abs(x)<4.2
                clone_assembly(prototypes[(family,variant)],collection=products,location=(x,y-.12,z+.07),
                               rotation=0.0,scale=1.0,label=f"{family.replace('_',' ').title()} · bay {i+1:02d}",web=is_web)
    import json
    b.scene["product_families_json"]=json.dumps(list(FAMILIES))
    b.scene["product_branding_note"]="All visible product brands and artwork are original fictional VERDANT MARKET graphics; no commercial packaging scans or photographs are used."
    b.scene["product_instance_count"]=len(b.shelf_rows)*len(b.shelf_levels)*38
