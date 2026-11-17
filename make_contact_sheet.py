"""Make a labeled 4x3 contact sheet from the twelve Blender PNG renders."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import argparse
from PIL import Image, ImageDraw, ImageFont
from colour_engine.config import CONFIG, ROOT

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--samples",type=int,default=8)
    parser.add_argument("--source-dir",default=str(ROOT/"renders"))
    parser.add_argument("--output",default=None)
    parser.add_argument("--metadata",default=str(ROOT/"results"/"blender_run_metadata.json"))
    parser.add_argument("--blend-file",default=str(ROOT/"blender"/"q3_project.blend"))
    args=parser.parse_args()
    source=Path(args.source_dir).resolve(); images=[]
    if not source.is_dir():raise FileNotFoundError(f"Render directory not found: {source}")
    try:font=ImageFont.truetype("arial.ttf",20)
    except OSError:font=ImageFont.load_default()
    thumb_w,thumb_h=480,320; margin=24; header=38
    for colour_id,colour in CONFIG["colours"].items():
        for illum_id,illum in CONFIG["illuminations"].items():
            path=source/f"{colour_id}_{illum_id}.png"
            if not path.exists():raise FileNotFoundError(f"Missing Blender render {path}")
            im=Image.open(path).convert("RGB").resize((thumb_w,thumb_h),Image.Resampling.LANCZOS)
            images.append((im,f"{colour_id}  {colour['name']}  |  {illum_id} {illum['name']}"))
    sheet=Image.new("RGB",(3*(thumb_w+margin)+margin,4*(thumb_h+header+margin)+margin),(244,246,248))
    draw=ImageDraw.Draw(sheet)
    for index,(im,label) in enumerate(images):
        col,row=index%3,index//3; x=margin+col*(thumb_w+margin);y=margin+row*(thumb_h+header+margin)
        draw.text((x,y),label,fill=(20,25,32),font=font)
        sheet.paste(im,(x,y+header))
    target=Path(args.output).resolve() if args.output else source/"contact_sheet.png"
    if not target.parent.is_dir():raise FileNotFoundError(f"Contact-sheet output directory not found: {target.parent}")
    sheet.save(target)
    blender=os.getenv("BLENDER_EXECUTABLE") or shutil.which("blender")
    if blender is None:
        candidate=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
        blender=str(candidate) if candidate.is_file() else None
    version="not found"
    if blender:
        try:version=subprocess.run([blender,"--version"],capture_output=True,text=True,timeout=15,check=False).stdout.splitlines()[0]
        except (OSError,subprocess.TimeoutExpired) as exc:version=f"unavailable: {exc}"
    rendered=[]
    for path in sorted(source.glob("[GYOR]_L[123].png")):
        stored_path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        rendered.append({"path":stored_path,"bytes":path.stat().st_size,
                         "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    blend=Path(args.blend_file).resolve()
    if not blend.is_file():raise FileNotFoundError(f"Blender scene not found: {blend}")
    stored_blend=blend.relative_to(ROOT).as_posix() if blend.is_relative_to(ROOT) else str(blend)
    metadata={"generated_utc":datetime.now(timezone.utc).isoformat(),"blender_executable":blender,
              "blender_version":version,"engine":"Cycles","view_transform":"Standard","samples":args.samples,
              "render_resolution_px":[960,640],"render_count":len(rendered),"rendered_files":rendered,
              "blend_file":{"path":stored_blend,"bytes":blend.stat().st_size,
                            "sha256":hashlib.sha256(blend.read_bytes()).hexdigest()},
              "spectral_note":"Blender output is an RGB visualization; spectral colorimetry is calculated by the Python CIE dataset pipeline."}
    metadata_path=Path(args.metadata).resolve()
    metadata_path.write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    print(target)
    print(metadata_path)

if __name__=="__main__":main()
