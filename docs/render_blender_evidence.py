"""Create traceable scene, node-graph and render-setting evidence images."""
from pathlib import Path
import json
import shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1]

DEST=ROOT/"blender"/"evidence";DEST.mkdir(parents=True,exist_ok=True)
record=json.loads((ROOT/"results"/"blender_scene_inspection.json").read_text(encoding="utf-8"))
shutil.copy2(ROOT/"renders"/"R_L1.png",DEST/"scene_overview_render.png")
shutil.copy2(ROOT/"renders"/"contact_sheet.png",DEST/"12_condition_contact_sheet.png")

def node(ax,x,y,w,h,title,subtitle,face="#e8f1fa",edge="#38658b"):
    shape=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.04,rounding_size=.08",facecolor=face,edgecolor=edge,linewidth=1.8)
    ax.add_patch(shape);ax.text(x+w/2,y+h*.67,title,ha="center",va="center",fontsize=10,fontweight="bold",color="#24313b")
    ax.text(x+w/2,y+h*.31,subtitle,ha="center",va="center",fontsize=8,color="#34434f",wrap=True)

fig,ax=plt.subplots(figsize=(12,6));ax.set_xlim(0,12);ax.set_ylim(0,6);ax.axis("off")
ax.set_title("Blender shader-node setup recorded from q3_project.blend",fontsize=15,fontweight="bold",pad=16)
node(ax,.35,3.9,2.4,1.15,"Diffuse BSDF","label surface\nlinear RGB reflectance",face="#e5f2e7",edge="#3f7650")
node(ax,4.05,3.9,2.4,1.15,"Material Output","surface")
ax.add_patch(FancyArrowPatch((2.75,4.48),(4.05,4.48),arrowstyle="-|>",mutation_scale=14,lw=1.7,color="#536775"))
ax.text(3.4,4.73,"BSDF",ha="center",fontsize=8)
node(ax,.35,1.75,2.4,1.15,"Blackbody","L2/L3 preview CCT\n4000 K / 3000 K",face="#fff1d2",edge="#a6791d")
node(ax,4.05,1.75,2.4,1.15,"Emission","RGB light shader\nstrength 1.0",face="#fff1d2",edge="#a6791d")
node(ax,8.0,1.75,2.4,1.15,"Light Output","area-light surface")
ax.add_patch(FancyArrowPatch((2.75,2.32),(4.05,2.32),arrowstyle="-|>",mutation_scale=14,lw=1.7,color="#536775"))
ax.text(3.4,2.57,"Color (LED cases)",ha="center",fontsize=8)
ax.add_patch(FancyArrowPatch((6.45,2.32),(8.0,2.32),arrowstyle="-|>",mutation_scale=14,lw=1.7,color="#536775"))
ax.text(7.23,2.57,"Emission",ha="center",fontsize=8)
node(ax,8.0,4.1,2.4,1.15,"D65 RGB stand-in","neutral white emission\n1 nm SPD stays in Python",face="#f1f3f5",edge="#737e87")
ax.add_patch(FancyArrowPatch((9.2,4.1),(5.4,2.9),arrowstyle="-|>",mutation_scale=13,lw=1.5,color="#737e87",connectionstyle="arc3,rad=.2"))
ax.text(7.6,3.65,"D65 replaces Blackbody input",ha="center",fontsize=8,color="#58656d")
ax.text(6,.65,"Technical node graph derived from the saved scene/script; it is not a screenshot of Blender's node editor.",ha="center",fontsize=9,color="#59656d")
fig.tight_layout();fig.savefig(DEST/"shader_node_configuration.png",dpi=180,bbox_inches="tight");plt.close(fig)

fig,ax=plt.subplots(figsize=(10,6));ax.set_xlim(0,10);ax.set_ylim(0,6);ax.axis("off")
ax.set_title("Blender color-management and render record",fontsize=15,fontweight="bold",pad=18)
settings=[("Render engine",record["engine"]),("View transform",record["view_transform"]),("Look",record["look"]),
          ("Exposure",str(record["exposure"])),("Gamma",str(record["gamma"])),
          ("Resolution",f"{record['resolution_px'][0]} × {record['resolution_px'][1]} px"),
          ("Resolution scale",f"{record['resolution_percentage']}%"),("Cycles samples",str(record["cycles_samples"])),
          ("Denoising",str(record["denoising"])),("Area-light energy",f"{record['light_energy']:g}")]
for i,(key,val) in enumerate(settings):
    col=i%2;row=i//2;x=.45+col*4.75;y=4.8-row*.9
    ax.add_patch(FancyBboxPatch((x,y-.42),4.2,.62,boxstyle="round,pad=.03",facecolor="#eef3f7",edgecolor="#7890a1"))
    ax.text(x+.16,y-.1,key,ha="left",va="center",fontsize=9,color="#52616b")
    ax.text(x+4.02,y-.1,val,ha="right",va="center",fontsize=10,fontweight="bold",color="#24313b")
ax.text(5,.2,"D65 uses neutral RGB only in Blender visualization; CIE spectral computation uses the official D65 SPD in Python.",ha="center",fontsize=9,color="#59656d")
fig.tight_layout();fig.savefig(DEST/"color_management_record.png",dpi=180,bbox_inches="tight");plt.close(fig)
print(f"Evidence images written to {DEST}")
