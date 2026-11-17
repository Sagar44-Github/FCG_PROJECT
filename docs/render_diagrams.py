"""Render implemented architecture diagrams to SVG and PNG with Matplotlib."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT=Path(__file__).resolve().parent/"diagrams"/"rendered"
OUT.mkdir(parents=True,exist_ok=True)
BLUE="#DCEAF7"; BLUE_EDGE="#2D5F8B"; GREEN="#E5F2E7"; GREEN_EDGE="#3F7650"; GOLD="#FFF1D2"; GOLD_EDGE="#A6791D"; GREY="#F1F3F5"; INK="#24313B"

def canvas(title, xmax=14, ymax=8):
    fig,ax=plt.subplots(figsize=(14,8)); ax.set_xlim(0,xmax);ax.set_ylim(0,ymax);ax.axis("off")
    ax.set_title(title,fontsize=18,fontweight="bold",color=INK,pad=18)
    return fig,ax

def box(ax,xy,w,h,title,body,fill=BLUE,edge=BLUE_EDGE,fs=9):
    x,y=xy
    shape=FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.04,rounding_size=0.08",facecolor=fill,edgecolor=edge,linewidth=1.5)
    ax.add_patch(shape)
    ax.text(x+w/2,y+h-.27,title,ha="center",va="center",fontsize=10,fontweight="bold",color=INK)
    ax.plot([x+.08,x+w-.08],[y+h-.48,y+h-.48],color=edge,lw=.8)
    ax.text(x+.16,y+h-.60,body,ha="left",va="top",fontsize=fs,color=INK,linespacing=1.35)

def arrow(ax,a,b,label="",rad=0.0,color="#62717C"):
    patch=FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=13,linewidth=1.35,color=color,
                          connectionstyle=f"arc3,rad={rad}",shrinkA=4,shrinkB=4)
    ax.add_patch(patch)
    if label:
        mx=(a[0]+b[0])/2;my=(a[1]+b[1])/2
        ax.text(mx,my+.12,label,ha="center",va="center",fontsize=8,color=INK,
                bbox=dict(facecolor="white",edgecolor="none",alpha=.8,pad=1))

def save(fig,name):
    fig.savefig(OUT/f"{name}.png",dpi=180,bbox_inches="tight",facecolor="white")
    fig.savefig(OUT/f"{name}.svg",bbox_inches="tight",facecolor="white")
    plt.close(fig)

def class_diagram():
    f,a=canvas("Q3 implemented classes and module responsibilities",16,9)
    box(a,(.3,6.6),4.6,1.7,"Donation request + observer schemas\n«Pydantic models»","DonationSimulationRequest\nObserverParameters · ConfusionWeights\nbounds and probability validation",GOLD,GOLD_EDGE,8)
    box(a,(5.5,6.6),4.5,1.7,"Analysis job schemas\n«Pydantic models»","AnalysisJobRequest · AnalysisJobResponse\nrequest · status · output · error · UTC timestamps",BLUE,BLUE_EDGE,8)
    box(a,(10.6,6.6),4.9,1.7,"Render and comparison schemas\n«Pydantic models»","RenderJobRequest / Response\nColourComparisonRequest\nfixed batch settings · configured IDs",BLUE,BLUE_EDGE,8)
    box(a,(.4,3.6),3.4,1.8,"colour_engine.pipeline\n«module»","compare_colour()\nrun_pipeline() · spectral tables\nCIEDE2000 + figures",GREEN,GREEN_EDGE,8)
    box(a,(4.3,3.6),3.4,1.8,"simulation modules\n«observer + inventory»","confusion_matrix_for(ΔE)\nsimulate_inventory()\nper-action ΔE · seeded capacity",GOLD,GOLD_EDGE,8)
    box(a,(8.3,3.6),3.1,1.8,"backend.main:app\n«FastAPI»","routing · validation · jobs\nartifact allow-list · exports",BLUE,BLUE_EDGE,8)
    box(a,(12,3.6),3.2,1.8,"backend.database\n«SQLite repository module»","insert / read / update\nfilters · bounded pagination",GREY,"#737E87",8)
    box(a,(2.2,.55),3.5,1.7,"frontend/ + dashboard/\n«React primary · Streamlit fallback»","Typed API client · six sections · R3F\nlegacy fallback calls the same API",BLUE,BLUE_EDGE,8)
    box(a,(8.2,.55),3.7,1.7,"Blender render service\n«fixed subprocess»","render_batch.py · server UUID path\nCycles PNG + saved .blend",GOLD,GOLD_EDGE,8)
    arrow(a,(3.8,3.6),(4.3,3.6));arrow(a,(7.7,4.5),(8.3,4.5));arrow(a,(11.4,4.5),(12,4.5))
    arrow(a,(5.7,1.4),(8.5,3.6),"REST / JSON",.08);arrow(a,(10,3.6),(10,2.25))
    arrow(a,(8.6,5.4),(8.6,6.6));arrow(a,(10.7,5.4),(12.8,6.6),"job response",.08)
    save(f,"class_diagram")

def object_diagram():
    f,a=canvas("Q3 runtime object snapshot",13,7)
    box(a,(.4,4.3),3.0,1.7,"config: CONFIG","4 sRGB colors\nL1 D65; L2 4000 K; L3 3000 K",GOLD,GOLD_EDGE)
    box(a,(4.2,4.3),3.0,1.7,"d65_spd()","CIE 1 nm dataset\n380–780 nm working grid",BLUE,BLUE_EDGE)
    box(a,(8,4.3),3.0,1.7,"digital_reflectance('#D62828')","smooth bounded metamer\nD65 XYZ residual retained",GREEN,GREEN_EDGE)
    box(a,(2.2,.8),3.2,1.7,"comparison: R × L2","Lab pair + ΔE00\nxy / wavelength / purity")
    box(a,(7.2,.8),3.4,1.7,"sqlite row: UUID","serialized computed result\ncreated_at in UTC",GREY,"#737E87")
    arrow(a,(3.4,5.1),(4.2,5.1));arrow(a,(7.2,5.1),(8,5.1));arrow(a,(9.1,4.3),(4.0,2.5),"spectral integration",.12);arrow(a,(5.4,1.65),(7.2,1.65),"API persistence")
    save(f,"object_diagram")

def component_diagram():
    f,a=canvas("Q3 implemented component diagram",16,8)
    box(a,(.3,5.4),2.5,1.6,"Faculty / researcher","browser · HTTP",GREY,"#737E87")
    box(a,(3.4,5.4),3.4,1.6,"React + TypeScript dashboard","Primary API client\n6 sections · Three.js/R3F",BLUE,BLUE_EDGE)
    box(a,(7.5,5.4),3.4,1.6,"FastAPI service","routing · validation\npagination · background jobs",BLUE,BLUE_EDGE)
    box(a,(11.6,5.4),3.7,1.6,"Scientific pipeline","spectra · color science\nobserver · inventory",GREEN,GREEN_EDGE)
    box(a,(.3,2.0),3.3,1.6,"CIE datasets + config","D65 · 1931 CMFs\nread-only parameters",GOLD,GOLD_EDGE)
    box(a,(4.2,2.0),3.2,1.6,"SQLite repository","persisted jobs\nand computed results",GREY,"#737E87")
    box(a,(8.0,2.0),3.4,1.6,"Blender Cycles RGB","server-built process args\n12 PNG · contact sheet · .blend",GOLD,GOLD_EDGE,8)
    box(a,(12.0,2.0),3.3,1.6,"Evidence files","CSV · figures · metadata\nPNG · tables · ZIP export",GREEN,GREEN_EDGE)
    arrow(a,(2.8,6.2),(3.4,6.2));arrow(a,(6.8,6.2),(7.5,6.2),"REST / JSON");arrow(a,(10.9,6.2),(11.6,6.2))
    arrow(a,(8.2,5.4),(7.0,3.6));arrow(a,(9.4,5.4),(9.4,3.6),"fixed render job")
    arrow(a,(13.4,5.4),(13.7,3.6))
    a.text(8,1.0,"The retained Streamlit fallback is a second API client; the backend remains the source of truth.",ha="center",fontsize=9,color=INK)
    save(f,"component_diagram")

def data_flow():
    f,a=canvas("Q3 data-flow diagram",16,6)
    boxes=[("1 · Parameters","config.json\ncolors · SPDs · seeds"),("2 · Spectra","CIE D65 + CMFs\nparameterized LED SPDs"),
           ("3 · Color","reflectance → XYZ/Lab\nΔE00 · xy · λdom"),("4 · Simulation","confusion matrices\ncapacity Monte Carlo"),("5 · Evidence","CSV · CI · figures\nmetadata + SQLite")]
    xs=[.3,3.5,6.7,9.9,13.1]
    for x,(title,body) in zip(xs,boxes):box(a,(x,2.25),2.6,1.9,title,body,BLUE,BLUE_EDGE,8)
    for i in range(4):arrow(a,(xs[i]+2.6,3.2),(xs[i+1],3.2))
    a.text(8,5.2,"Inputs: official CIE datasets + explicit synthetic assumptions",ha="center",fontsize=11,color=INK)
    a.text(8,.8,"Blender supplies RGB visual renders; its output is not used as spectral measurement.",ha="center",fontsize=10,color=INK)
    save(f,"data_flow_diagram")

def methodology_flowchart():
    f,a=canvas("Reproducible computational research workflow",16,9)
    boxes=[
        (.35,6.25,3.0,1.55,"1 · Fixed inputs","config.json · CIE D65 / CMFs\nseed · RGB label specifications",GOLD,GOLD_EDGE),
        (4.3,6.25,3.0,1.55,"2 · Spectral models","D65 reference + LED approximations\nsmooth reflectance + virtual print",BLUE,BLUE_EDGE),
        (8.3,6.25,3.0,1.55,"3 · Color calculations","XYZ · CIELAB · ΔE00\nxy · dominant λ · purity",GREEN,GREEN_EDGE),
        (12.25,6.25,3.0,1.55,"4 · Synthetic observer","ΔE sensitivity assumption\nconfusion matrix · trigger rates",GOLD,GOLD_EDGE),
        (10.3,2.7,3.0,1.55,"5 · Inventory simulation","Poisson near-expiry arrivals\nrecognition · capacity · recovery",BLUE,BLUE_EDGE),
        (5.8,2.7,3.3,1.55,"6 · Evaluation","descriptive intervals · MC percentiles\ncapacity & CO₂e sensitivity",GREEN,GREEN_EDGE),
        (1.05,2.7,3.3,1.55,"7 · Reproducible evidence","CSV · figures · metadata · API/SQLite\nBlender RGB visuals on separate branch",GREY,"#737E87"),
    ]
    for x,y,w,h,title,body,fill,edge in boxes:
        box(a,(x,y),w,h,title,body,fill,edge,8)
    arrow(a,(3.35,7.02),(4.3,7.02));arrow(a,(7.3,7.02),(8.3,7.02));arrow(a,(11.3,7.02),(12.25,7.02))
    arrow(a,(13.7,6.25),(11.8,4.25),"assumed outcomes",.06)
    arrow(a,(10.3,3.48),(9.1,3.48));arrow(a,(5.8,3.48),(4.35,3.48))
    a.text(8,1.25,"Blender Cycles renders are visual artifacts and do not enter spectral ΔE computation.",ha="center",fontsize=10,color=INK)
    save(f,"research_methodology_flowchart")

def sequence_diagram():
    f,a=canvas("Q3 application and API sequence",16,8)
    participants=[("Researcher",.4), ("React UI",2.5), ("FastAPI",4.6), ("Color engine",6.7),
                  ("Simulation",8.8), ("SQLite",10.9), ("BackgroundTasks",13.0), ("Blender",15.1)]
    for name,x in participants:
        a.text(x,7.3,name,ha="center",va="center",fontweight="bold",fontsize=9,color=INK,
               bbox=dict(boxstyle="round,pad=.45",facecolor=BLUE,edgecolor=BLUE_EDGE))
        a.plot([x,x],[.5,6.85],ls="--",lw=1,color="#9AA7B1")
    a.text(.35,6.85,"Comparison and simulation request",ha="left",va="center",fontsize=8.5,fontweight="bold",color=GREEN_EDGE)
    a.text(8.0,3.45,"Isolated Blender render-job request",ha="left",va="center",fontsize=8.5,fontweight="bold",color=GOLD_EDGE)
    msgs=[(0,1,6.35,"choose action"),(1,2,5.95,"POST comparison / donation"),
          (2,3,5.55,"compute XYZ/Lab · ΔE00"),(3,2,5.15,"measurement"),
          (2,4,4.75,"seeded Monte Carlo"),(4,2,4.35,"outcomes + intervals"),
          (2,5,3.95,"persist result JSON"),(2,1,3.55,"return computed result"),
          (0,1,3.15,"start separate render job"),(1,2,2.75,"POST /render-jobs"),
          (2,5,2.35,"persist queued job"),(2,6,1.95,"fixed argv + timeout"),(6,7,1.55,"render 12 cases"),
          (7,6,1.15,"PNGs + contact sheet"),(6,2,.75,"exit status + render inventory"),(2,5,.35,"persist final status")]
    for src,dst,y,label in msgs:
        x1=participants[src][1];x2=participants[dst][1]
        a.annotate("",xy=(x2,y),xytext=(x1,y),arrowprops=dict(arrowstyle="->",lw=1,color=BLUE_EDGE))
        a.text((x1+x2)/2,y+.10,label,ha="center",va="bottom",fontsize=7.5,color=INK,bbox=dict(facecolor="white",edgecolor="none",pad=.5))
    save(f,"sequence_diagram")

def deployment_diagram():
    f,a=canvas("Q3 deployment view · prepared Compose topology",16,9)
    a.add_patch(FancyBboxPatch((.2,.35),15.5,8.1,boxstyle="round,pad=.08,rounding_size=.12",
        facecolor="#FBFCFD",edgecolor="#768695",linewidth=1.4,linestyle="--",zorder=-2))
    a.text(.55,8.15,"Host OS · Docker Compose network · all application logic remains in user space",fontsize=10,color=INK,fontweight="bold")
    box(a,(.6,6.2),2.6,1.35,"Faculty browser","React UI · Swagger\nlocal development ports",GREY,"#737E87",8)
    box(a,(4,6.2),3.2,1.35,"q3-frontend container","Nginx · React SPA\nproxy /api/v1 to q3-api",BLUE,BLUE_EDGE,8)
    box(a,(8.2,6.2),3.5,1.35,"q3-api container","Uvicorn + FastAPI\nread-only root · UID 10001",BLUE,BLUE_EDGE,8)
    box(a,(12.4,6.2),2.7,1.35,"Blender child process","Cycles background batch\nserver-built argv + UUID path",GOLD,GOLD_EDGE,8)
    box(a,(4,3.25),3.2,1.45,"Application image data","Python modules · config.json\nCIE reference datasets",GOLD,GOLD_EDGE,8)
    box(a,(8.2,3.25),3.5,1.45,"q3-data volume","SQLite database\n/var/lib/q3/q3.sqlite3",GREY,"#737E87",8)
    box(a,(12.4,3.25),2.7,1.45,"q3-results volume","CSV · figures · metadata\n/persistent results",GREEN,GREEN_EDGE,8)
    box(a,(12.4,.85),2.7,1.35,"q3-renders volume","12 PNG · contact sheet\n/persistent renders",GREEN,GREEN_EDGE,8)
    box(a,(.6,3.25),2.8,1.45,"Optional fallback service","Streamlit :8501\nQ3_API_URL=q3-api:8000",BLUE,BLUE_EDGE,8)
    arrow(a,(3.2,6.85),(4,6.85),"HTTP");arrow(a,(7.2,6.85),(8.2,6.85),"REST / JSON")
    arrow(a,(11.7,6.95),(12.4,6.95),"spawned process")
    arrow(a,(9.3,6.2),(9.3,4.7),"persist / paginate")
    arrow(a,(10.7,6.2),(12.5,4.7),"analysis evidence",.12)
    arrow(a,(13.8,6.2),(13.8,4.7),"render PNG + .blend")
    arrow(a,(13.8,3.25),(13.8,2.2),"named volume")
    arrow(a,(9.1,6.2),(7.1,4.7),"",.08)
    arrow(a,(1.9,6.2),(1.9,4.7),"fallback")
    arrow(a,(3.4,3.95),(8.3,6.2),"REST / JSON",.08)
    a.text(1.9,.62,"Docker build/runtime unverified on this host",ha="center",fontsize=8,color=INK)
    save(f,"deployment_diagram")

if __name__=="__main__":
    class_diagram();object_diagram();component_diagram();data_flow();methodology_flowchart();sequence_diagram();deployment_diagram()
    print(f"Rendered diagrams to {OUT}")
