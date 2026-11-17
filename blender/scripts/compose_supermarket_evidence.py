"""Use system Pillow to create the final D65/LED plate and hero contact sheet."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,sys
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"blender"/"renders"/"supermarket"/"final"
OUT=ROOT/"blender"/"renders"/"supermarket"

def font(size):
    for path in (r"C:\Windows\Fonts\segoeuib.ttf",r"C:\Windows\Fonts\arialbd.ttf"):
        if Path(path).is_file(): return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def comparison():
    plate=Image.new("RGB",(2560,1440),(9,17,22)); draw=ImageDraw.Draw(plate)
    tags=(("L1 · D65 DAYLIGHT","CIE standard reference; RGB render proxy"),("L2 · NEUTRAL LED · 4000 K","Parameterized appearance; not a measured lamp"),("L3 · WARM LED · 3000 K","Parameterized appearance; not a measured lamp"))
    for i,(illuminant,(title,note)) in enumerate(zip(("L1","L2","L3"),tags)):
        frame=Image.open(BASE/"illumination_components"/f"{illuminant}_macro.png").convert("RGB")
        frame=frame.resize((2560,1440),Image.Resampling.LANCZOS)
        band=frame.crop((0,450,2560,930))
        plate.paste(band,(0,i*480))
        draw.rectangle((0,i*480,690,i*480+66),fill=(9,17,22))
        draw.text((21,i*480+7),title,font=font(26),fill=(246,244,232))
        draw.text((23,i*480+40),note,font=font(14),fill=(195,207,197))
        if i<2: draw.line((0,(i+1)*480-1,2560,(i+1)*480-1),fill=(173,148,102),width=2)
    draw.rectangle((0,1385,2560,1440),fill=(9,17,22))
    draw.text((24,1401),"RGB presentation renders · spectral calculations use the Python CIE pipeline; LED appearances are not measured store-lamp spectra.",font=font(17),fill=(205,218,213))
    path=BASE/"05_illuminant_comparison.png"; plate.save(path,optimize=True); return path

def contact_sheet():
    names=("01_supermarket_hero","02_shelf_detail","03_donate_now_macro","04_colour_status_system","05_illuminant_comparison","06_supermarket_isometric")
    canvas=Image.new("RGB",(2400,1450),(10,17,22)); draw=ImageDraw.Draw(canvas)
    for i,name in enumerate(names):
        source=BASE/f"{name}.png"
        if not source.exists(): continue
        x=(i%2)*1200; y=(i//2)*480
        image=Image.open(source).convert("RGB").resize((1192,430),Image.Resampling.LANCZOS)
        canvas.paste(image,(x+4,y+4))
        draw.rectangle((x+4,y+4,x+444,y+53),fill=(10,17,22))
        draw.text((x+18,y+13),name.replace("_"," ").upper(),font=font(21),fill=(235,240,234))
    canvas.save(OUT/"supermarket_contact_sheet.png",optimize=True)
    return OUT/"supermarket_contact_sheet.png"

def sha256(path):
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""): digest.update(block)
    return digest.hexdigest()

def write_metadata():
    names=("01_supermarket_hero","02_shelf_detail","03_donate_now_macro","04_colour_status_system","05_illuminant_comparison","06_supermarket_isometric")
    files=[]
    for name in names:
        path=BASE/f"{name}.png"
        if not path.is_file(): continue
        with Image.open(path) as image: dimensions=list(image.size)
        files.append({"name":path.relative_to(ROOT).as_posix(),"width_px":dimensions[0],"height_px":dimensions[1],"bytes":path.stat().st_size,"sha256":sha256(path)})
    web_model=ROOT/"frontend"/"public"/"assets"/"supermarket"/"verdant_market.glb"
    blend=ROOT/"blender"/"q3_supermarket.blend"
    for path in (web_model,blend):
        if path.is_file(): files.append({"name":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)})
    metadata={
        "title":"VERDANT MARKET supermarket presentation and Blender-derived browser twin",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "software":{"blender":"5.2.3 LTS","python":sys.version.split()[0],"pillow":__import__("PIL").__version__,"platform":platform.platform()},
        "render":{"engine":"Cycles","device":"CPU","view_transform":"AgX","look":"AgX - Medium High Contrast","denoiser":"OpenImageDenoise","resolution_px":[2560,1440],"sample_counts":{"hero":12,"shelf_detail":14,"donate_now_macro":16,"colour_status_system":12,"illuminant_comparison_components":12,"isometric":12}},
        "configuration_sha256":sha256(ROOT/"config.json"),
        "random_seed_from_config":json.loads((ROOT/"config.json").read_text(encoding="utf-8"))["project"]["random_seed"],
        "research_boundary":"RGB presentation assets only. CIE D65 and parameterized LED spectral computations remain in Python; no printer, lamp, participant, or retail measurement is represented.",
        "product_families":["milk carton","juice carton","glass bottle","PET bottle","aluminium can","cereal box","snack pouch","glass jar","yogurt tub","refill pouch","pasta pack","produce crate"],
        "outputs":files,
    }
    path=BASE/"release_metadata.json"
    path.write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    return path

if __name__=="__main__":
    path=BASE/"illumination_components"
    if all((path/f"{i}_macro.png").exists() for i in ("L1","L2","L3")):
        print(f"Illuminant comparison: {comparison()}")
    print(f"Contact sheet: {contact_sheet()}")
    print(f"Release manifest: {write_metadata()}")
