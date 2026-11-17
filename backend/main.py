"""FastAPI integration layer for reproducible Q3 computations."""
from __future__ import annotations
import logging
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from colour_engine.config import CONFIG, ROOT

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT/".env",override=False)
except ImportError:
    pass

from colour_engine.pipeline import compare_colour
from colour_engine.pipeline import run_pipeline
from simulation.donation_model import simulate_inventory
from simulation.observer_model import ACTION_ORDER, confusion_matrix_for
from backend import database

logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"))
logger=logging.getLogger("q3.api")
_analysis_submission_lock=threading.Lock()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.initialize()
    yield

app=FastAPI(title="Q3 Spectral Shelf-Label Research API",version="0.1.0",
            description="Research computation service. Print, observer, inventory, and emissions results are model outputs, not physical or human measurements.",
            lifespan=lifespan)

class RenderJobRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    render_all: bool = True
    samples: int = Field(default=16,ge=1,le=256)

class ColourComparisonRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    colour_id: str
    illumination_id: str

class ConfusionWeights(BaseModel):
    model_config=ConfigDict(extra="forbid")
    adjacent: float = Field(default=CONFIG["observer"]["confusion_weights"]["adjacent"],gt=0,le=1)
    nonadjacent: float = Field(default=CONFIG["observer"]["confusion_weights"]["nonadjacent"],gt=0,le=1)

class ObserverParameters(BaseModel):
    model_config=ConfigDict(extra="forbid")
    base_error_probability: float = Field(default=CONFIG["observer"]["base_error_probability"],ge=0,le=1)
    maximum_additional_error_probability: float = Field(default=CONFIG["observer"]["maximum_additional_error_probability"],ge=0,le=1)
    delta_e_midpoint: float = Field(default=CONFIG["observer"]["delta_e_midpoint"],ge=0,le=100)
    delta_e_scale: float = Field(default=CONFIG["observer"]["delta_e_scale"],gt=0,le=100)
    confusion_weights: ConfusionWeights = Field(default_factory=ConfusionWeights)

    @model_validator(mode="after")
    def validate_probability_range(self):
        if self.base_error_probability+self.maximum_additional_error_probability>1:
            raise ValueError("base_error_probability plus maximum_additional_error_probability must not exceed 1")
        return self

class DonationSimulationRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    illumination_id: str
    recognition: Literal["perfect","simulated_errors"] = "simulated_errors"
    capacity_per_day: int = Field(default=25,ge=0,le=100000)
    days: int = Field(default=30,ge=1,le=3650)
    mean_arrivals_per_day: float = Field(default=80,ge=0,le=100000)
    replicates: int = Field(default=100,ge=1,le=2000)
    seed: int = Field(default=20261115,ge=0)
    observer_parameters: ObserverParameters | None = None

    @model_validator(mode="after")
    def validate_simulation_budget(self):
        if self.days*self.replicates>100_000:
            raise ValueError("days × replicates must not exceed 100,000 to keep requests bounded")
        if self.mean_arrivals_per_day*self.days*self.replicates>20_000_000:
            raise ValueError("expected simulated arrivals must not exceed 20,000,000 per request")
        return self

class AnalysisJobRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    donation_replicates: int = Field(default=500,ge=1,le=2000)

class RenderJobResponse(BaseModel):
    id: str
    status: Literal["queued","running","completed","failed"]
    request: dict
    result: dict | None = None
    error: str | None = None
    created_at: str
    updated_at: str

class ComparisonResponse(BaseModel):
    id: str
    colour_id: str
    illumination_id: str
    result: dict
    created_at: str | None = None

class DonationResponse(BaseModel):
    id: str
    illumination_id: str
    result: dict
    recognition: str | None = None
    capacity_per_day: int | None = None
    created_at: str | None = None

class RenderJobPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[RenderJobResponse]

class ComparisonPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ComparisonResponse]

class DonationPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DonationResponse]

class AnalysisJobResponse(BaseModel):
    id: str
    status: Literal["queued","running","completed","failed"]
    request: dict
    result: dict | None = None
    error: str | None = None
    created_at: str
    updated_at: str

class AnalysisJobPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[AnalysisJobResponse]

@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc: Exception):
    logger.exception("Unhandled API exception",exc_info=exc)
    return JSONResponse(status_code=500,content={"detail":"Internal computation or persistence error"})

@app.get("/api/v1/health")
def health():
    return {"status":"ok","project_version":CONFIG["project"]["version"],"database":"sqlite","mode":"user-space"}

def _configuration_digest() -> str:
    payload=json.dumps(CONFIG,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

@app.get("/api/v1/configuration")
def get_configuration():
    return {"configuration":CONFIG,"sha256":_configuration_digest(),"mutable_via_api":False,
            "note":"Configuration is read-only through this API. Every processing job stores this configuration digest."}

ARTIFACT_NAMES=[
    "colour_measurements.csv","delta_e_summary.csv","chromaticity_data.csv","trigger_simulation.csv",
    "trigger_rates.csv","trigger_logistic_model.csv","donation_simulation.csv","statistical_summary.csv",
    "sustainability_analysis.csv","illumination_comparisons.csv","illumination_spectra.csv",
    "reflectance_spectra.csv","run_metadata.json","blender_run_metadata.json",
    "figures/delta_e_by_condition.png","figures/red_delta_e_by_illumination.png","figures/red_delta_components.png",
    "figures/chromaticity_diagram.png","figures/cie1931_srgb_gamut.png","figures/dominant_wavelength_purity.png",
    "figures/trigger_error_vs_delta_e.png","figures/recognition_confusion_matrices.png",
    "figures/donation_capacity_sensitivity.png","figures/near_expiry_simulation_comparison.png",
    "figures/sustainability_impact_sensitivity.png","tables/table_delta_e_summary.csv","tables/table_trigger_rates.csv"
]
ARTIFACTS={name:(ROOT/"results"/name).resolve() for name in ARTIFACT_NAMES}
SUPERMARKET_VIEWS=("01_supermarket_hero","02_shelf_detail","03_donate_now_macro",
                   "04_colour_status_system","05_illuminant_comparison","06_supermarket_isometric")
ARTIFACTS.update({f"supermarket/{name}.png":(ROOT/"blender"/"renders"/"supermarket"/"final"/f"{name}.png").resolve()
                  for name in SUPERMARKET_VIEWS})
ARTIFACTS["supermarket/release_metadata.json"]=(ROOT/"blender"/"renders"/"supermarket"/"final"/"release_metadata.json").resolve()

def _records(path: Path) -> list[dict]:
    import pandas as pd
    if not path.is_file():return []
    try:return json.loads(pd.read_csv(path).to_json(orient="records"))
    except (OSError,ValueError) as exc:
        logger.exception("Could not read generated evidence %s",path.name)
        return []

def _render_catalog() -> list[dict]:
    catalog=[]
    baseline=ROOT/"renders"
    for path in sorted(baseline.glob("[GYOR]_L[123].png")):
        colour_id,illumination_id=path.stem.split("_")
        catalog.append({"render_id":"baseline","filename":path.name,"colour_id":colour_id,
            "colour_name":CONFIG["colours"][colour_id]["name"],"hex":CONFIG["colours"][colour_id]["hex"],
            "illumination_id":illumination_id,"illumination_name":CONFIG["illuminations"][illumination_id]["name"],
            "url":f"/api/v1/renders/baseline/{path.name}"})
    if (baseline/"contact_sheet.png").is_file():
        catalog.append({"render_id":"baseline","filename":"contact_sheet.png","kind":"contact_sheet",
                        "url":"/api/v1/renders/baseline/contact_sheet.png"})
    jobs,_=database.list_render_jobs(100,0,"completed")
    for job in jobs:
        for relative in (job.get("result") or {}).get("renders",[]):
            filename=Path(relative).name
            if not re.fullmatch(r"[GYOR]_L[123]\.png",filename):continue
            colour_id,illumination_id=Path(filename).stem.split("_")
            catalog.append({"render_id":job["id"],"filename":filename,"colour_id":colour_id,
                "colour_name":CONFIG["colours"][colour_id]["name"],"hex":CONFIG["colours"][colour_id]["hex"],
                "illumination_id":illumination_id,"illumination_name":CONFIG["illuminations"][illumination_id]["name"],
                "url":f"/api/v1/renders/{job['id']}/{filename}"})
        if (ROOT/"renders"/f"api_{job['id']}"/"contact_sheet.png").is_file():
            catalog.append({"render_id":job["id"],"filename":"contact_sheet.png","kind":"contact_sheet",
                "url":f"/api/v1/renders/{job['id']}/contact_sheet.png"})
    return catalog

@app.get("/api/v1/renders")
def list_renders():
    items=_render_catalog()
    return {"total":len(items),"items":items}

@app.get("/api/v1/renders/{render_id}/{filename}")
def get_render_file(render_id: str, filename: str):
    if filename=="contact_sheet.png":
        if render_id=="baseline":candidate=ROOT/"renders"/filename
        else:
            try:normalized=str(uuid.UUID(render_id))
            except ValueError:raise HTTPException(status_code=404,detail="Render not found")
            job=database.get_render_job(normalized)
            contact=(ROOT/"renders"/f"api_{normalized}"/filename).resolve()
            if not job or job["status"]!="completed" or not contact.is_file():
                raise HTTPException(status_code=404,detail="Render not found")
            candidate=contact
    elif re.fullmatch(r"[GYOR]_L[123]\.png",filename):
        if render_id=="baseline":candidate=ROOT/"renders"/filename
        else:
            try:normalized=str(uuid.UUID(render_id))
            except ValueError:raise HTTPException(status_code=404,detail="Render not found")
            job=database.get_render_job(normalized)
            allowed=[Path(x).name for x in ((job or {}).get("result") or {}).get("renders",[])]
            if not job or job["status"]!="completed" or filename not in allowed:
                raise HTTPException(status_code=404,detail="Render not found")
            candidate=ROOT/"renders"/f"api_{normalized}"/filename
    else:raise HTTPException(status_code=404,detail="Render not found")
    resolved=candidate.resolve()
    if not resolved.is_relative_to((ROOT/"renders").resolve()) or not resolved.is_file():
        raise HTTPException(status_code=404,detail="Render not found")
    return FileResponse(resolved,media_type="image/png",filename=filename)

@app.get("/api/v1/artifacts")
def list_artifacts():
    return {"items":[{"name":name,"available":path.is_file(),"bytes":path.stat().st_size if path.is_file() else None}
                      for name,path in ARTIFACTS.items()]}

@app.get("/api/v1/artifacts/{artifact_name:path}")
def download_artifact(artifact_name: str):
    path=ARTIFACTS.get(artifact_name)
    if path is None or not path.is_file():raise HTTPException(status_code=404,detail="Artifact not found")
    return FileResponse(path,filename=Path(artifact_name).name)

@app.get("/api/v1/dashboard")
def dashboard_summary():
    render_items=_render_catalog()
    baseline_render_count=sum(1 for x in render_items if x.get("render_id")=="baseline" and x.get("kind") is None)
    measurements=_records(ROOT/"results"/"colour_measurements.csv")
    delta_summary=_records(ROOT/"results"/"delta_e_summary.csv")
    red_trigger=[x for x in _records(ROOT/"results"/"trigger_rates.csv") if x.get("colour_id")=="R"]
    donation=[x for x in _records(ROOT/"results"/"donation_simulation.csv") if x.get("metric") in {"units_saved","expired_stock","waste_rate"}]
    sustainability=_records(ROOT/"results"/"sustainability_analysis.csv")
    metadata={}
    metadata_path=ROOT/"results"/"run_metadata.json"
    if metadata_path.is_file():
        try:metadata=json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):logger.exception("Unreadable run metadata")
    recent=[]
    for kind,items in [("render",database.list_render_jobs(5,0)[0]),
                       ("analysis",database.list_analysis_jobs(5,0)[0]),
                       ("colour_comparison",database.list_comparisons(5,0)[0]),
                       ("donation_simulation",database.list_donations(5,0)[0])]:
        for item in items:
            recent.append({"type":kind,"id":item.get("id"),"status":item.get("status","completed"),
                           "created_at":item.get("created_at"),"updated_at":item.get("updated_at")})
    recent.sort(key=lambda x:x.get("created_at") or "",reverse=True)
    render_jobs,_=database.list_render_jobs(100,0)
    return {"project_title":CONFIG["project"]["title"],"configuration_sha256":_configuration_digest(),
        "render_status":"complete" if baseline_render_count==12 else "partial_or_not_run",
        "render_count":sum(1 for x in render_items if x.get("kind") is None),"baseline_render_count":baseline_render_count,
        "render_job_count":len(render_jobs),"latest_render_job_status":render_jobs[0]["status"] if render_jobs else None,
        "render_catalog":render_items,"colour_analysis_status":"complete" if len(measurements)==12 else "not_run_or_incomplete",
        "colour_measurement_count":len(measurements),"delta_e_summary":delta_summary,
        "red_trigger_summary":red_trigger,"donation_summary":donation,"sustainability_summary":sustainability,
        "generated_at":metadata.get("generated_utc"),"software":metadata.get("software",{}),
        "recent_jobs":recent[:12],"artifact_count":sum(path.is_file() for path in ARTIFACTS.values())}

def _execute_analysis_job(job_id: str, replicates: int) -> None:
    database.update_analysis_job(job_id,"running")
    try:
        output=run_pipeline(replicates=replicates)
        database.update_analysis_job(job_id,"completed",result={"outputs":output,
            "configuration_sha256":_configuration_digest(),"donation_replicates_per_scenario":replicates})
    except Exception as exc:
        logger.exception("Analysis job %s failed",job_id)
        database.update_analysis_job(job_id,"failed",error=f"{type(exc).__name__}: {exc}")

@app.post("/api/v1/analysis-jobs",status_code=202,response_model=AnalysisJobResponse)
def create_analysis_job(body: AnalysisJobRequest, background: BackgroundTasks):
    with _analysis_submission_lock:
        if database.has_active_analysis_job():raise HTTPException(status_code=409,detail="A full evidence run is already queued or running")
        job_id=str(uuid.uuid4())
        record=database.insert_analysis_job(job_id,{**body.model_dump(),"configuration_sha256":_configuration_digest()})
    background.add_task(_execute_analysis_job,job_id,body.donation_replicates)
    return record

@app.get("/api/v1/analysis-jobs",response_model=AnalysisJobPage)
def list_analysis_jobs(limit: int=Query(50,ge=1,le=200),offset: int=Query(0,ge=0),
                       status: Literal["queued","running","completed","failed"]|None=None):
    items,total=database.list_analysis_jobs(limit,offset,status)
    return {"total":total,"limit":limit,"offset":offset,"items":items}

@app.get("/api/v1/analysis-jobs/{job_id}",response_model=AnalysisJobResponse)
def get_analysis_job(job_id: str):
    job=database.get_analysis_job(job_id)
    if not job:raise HTTPException(status_code=404,detail="Analysis job not found")
    return job

@app.get("/api/v1/exports/evidence-package")
def download_evidence_package():
    output=io.BytesIO()
    # Inputs are already-compressed PNG/GLB/Blend assets. Level 1 keeps the
    # reproducibility download responsive while preserving portable ZIP output.
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
        fixed=[ROOT/"config.json",ROOT/"README.md",ROOT/".env.example",ROOT/"docs"/"model_assumptions.md",ROOT/"docs"/"spectral_sources.md",
               ROOT/"docs"/"architecture.md",ROOT/"docs"/"api_reference.md",ROOT/"docs"/"faculty_demo_guide.md",
               ROOT/"docs"/"viva_preparation.md",ROOT/"docs"/"implementation_status.md",ROOT/"docs"/"blender_evidence.md",
               ROOT/"docs"/"config_history.md",ROOT/"docs"/"supermarket_visual_pipeline.md",ROOT/"results"/"blender_run_metadata.json",
               ROOT/"results"/"blender_scene_inspection.json",ROOT/"results"/"test_results.txt",
               ROOT/"docs"/"frontend_architecture.md",ROOT/"results"/"phase3_backend_tests.txt",
               ROOT/"results"/"phase3_frontend_tests.txt",ROOT/"results"/"phase3_e2e_tests.txt",
               ROOT/"blender"/"q3_project.blend",ROOT/"blender"/"q3_supermarket.blend",ROOT/"requirements.txt",ROOT/"run_pipeline.py",
               ROOT/"frontend"/"public"/"assets"/"supermarket"/"verdant_market.glb",
               ROOT/"blender"/"assets"/"generated_textures"/"packaging_catalog.json",
               ROOT/"Dockerfile",ROOT/"docker-compose.yml"]
        fixed.extend(ARTIFACTS.values())
        fixed.extend(path for path in (ROOT/"blender"/"assets"/"generated_textures").glob("*.png"))
        fixed.extend((ROOT/"data"/name for name in ["CIE_std_illum_D65.csv","CIE_xyz_1931_2deg.csv","ciede2000_reference_cases.csv"]))
        fixed.extend(path for path in (ROOT/"docs"/"diagrams").rglob("*") if path.is_file())
        for folder in ["backend","colour_engine","simulation","tests","dashboard","blender/scripts"]:
            fixed.extend(path for path in (ROOT/folder).rglob("*.py") if "__pycache__" not in path.parts)
        frontend_root=ROOT/"frontend"
        frontend_suffixes={".ts",".tsx",".css",".html",".json",".md",".conf",".svg",".png",".glb"}
        excluded_frontend_dirs={"node_modules","dist","coverage","test-results",".vite"}
        fixed.extend(path for path in frontend_root.rglob("*") if path.is_file()
                     and path.suffix.lower() in frontend_suffixes
                     and not any(part in excluded_frontend_dirs for part in path.parts))
        fixed.extend(path for path in (ROOT/"renders").glob("[GYOR]_L[123].png"))
        fixed.append(ROOT/"renders"/"contact_sheet.png")
        fixed.extend(path for path in (ROOT/"results"/"frontend_screenshots").glob("*.png"))
        completed_render_jobs,_=database.list_render_jobs(200,0,"completed")
        renders_root=(ROOT/"renders").resolve()
        case_names=[f"{colour}_L{illumination}.png" for colour in "GYOR" for illumination in range(1,4)]
        job_filenames=case_names+["contact_sheet.png","q3_project.blend","blender_run_metadata.json"]
        for job in completed_render_jobs:
            job_id=job["id"]
            if not re.fullmatch(r"[0-9a-fA-F-]{36}",job_id):continue
            job_dir=(renders_root/f"api_{job_id}").resolve()
            if not job_dir.is_relative_to(renders_root):continue
            fixed.extend(path for name in job_filenames if (path:=job_dir/name).is_file()
                         and path.resolve().is_relative_to(job_dir))
        seen=set()
        for path in fixed:
            if path.is_file() and path.resolve().is_relative_to(ROOT.resolve()):
                archive_name=path.relative_to(ROOT).as_posix()
                if archive_name not in seen:
                    archive.write(path,archive_name);seen.add(archive_name)
    return Response(output.getvalue(),media_type="application/zip",
                    headers={"Content-Disposition":"attachment; filename=q3_research_evidence.zip"})

def _blender_executable() -> str | None:
    configured=os.getenv("BLENDER_EXECUTABLE")
    if configured and Path(configured).is_file():return configured
    found=shutil.which("blender")
    if found:return found
    candidates=[Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"),
                Path("/usr/bin/blender"),Path("/usr/local/bin/blender")]
    return str(next((p for p in candidates if p.is_file()),"")) or None

def _run_render_job(job_id: str, samples: int):
    database.update_render_job(job_id,"running")
    output=ROOT/"renders"/f"api_{job_id}"
    output.mkdir(parents=True,exist_ok=True)
    exe=_blender_executable()
    if not exe:
        database.update_render_job(job_id,"failed",error="Blender executable unavailable; configure BLENDER_EXECUTABLE")
        return
    script=ROOT/"blender"/"scripts"/"render_batch.py"
    blend_output=output/"q3_project.blend"
    command=[exe,"--background","--python",str(script),"--","--output-dir",str(output),"--samples",str(samples),
             "--blend-output",str(blend_output)]
    try:
        completed=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=1800,check=False)
        if completed.returncode:
            logger.error("Blender failure for job %s: %s",job_id,completed.stderr[-4000:])
            database.update_render_job(job_id,"failed",error=completed.stderr[-4000:] or f"Blender exited {completed.returncode}")
        else:
            files=sorted(str(p.relative_to(ROOT)) for p in output.glob("*.png"))
            case_files=[p for p in files if re.fullmatch(r"renders/api_[^/]+/[GYOR]_L[123]\.png",p.replace("\\","/"))]
            if len(case_files)!=12:
                database.update_render_job(job_id,"failed",error=f"Expected 12 rendered case PNGs; found {len(case_files)}")
                return
            contact_script=ROOT/"make_contact_sheet.py"
            contact_command=[sys.executable,str(contact_script),
                "--samples",str(samples),"--source-dir",str(output),"--output",str(output/"contact_sheet.png"),
                "--metadata",str(output/"blender_run_metadata.json"),"--blend-file",str(blend_output)]
            contact=subprocess.run(contact_command,cwd=ROOT,capture_output=True,text=True,timeout=120,check=False)
            if contact.returncode:
                logger.error("Contact-sheet generation failed for job %s: %s",job_id,contact.stderr[-3000:])
                database.update_render_job(job_id,"failed",error=contact.stderr[-3000:] or "Contact sheet generation failed")
                return
            database.update_render_job(job_id,"completed",result={"renders":case_files,"count":len(case_files),
                "contact_sheet":str((output/"contact_sheet.png").relative_to(ROOT)),
                "metadata":str((output/"blender_run_metadata.json").relative_to(ROOT)),
                "blend_file":str(blend_output.relative_to(ROOT)),"blender_executable":exe,
                "configuration_sha256":_configuration_digest()})
    except (OSError,subprocess.TimeoutExpired) as exc:
        logger.exception("Render job failed")
        database.update_render_job(job_id,"failed",error=str(exc))

@app.post("/api/v1/render-jobs",status_code=202,response_model=RenderJobResponse)
def create_render_job(body: RenderJobRequest, background: BackgroundTasks):
    if not body.render_all:
        raise HTTPException(status_code=422,detail="This research build supports a complete 12-condition batch only")
    job_id=str(uuid.uuid4()); job=database.insert_render_job(job_id,{**body.model_dump(),"configuration_sha256":_configuration_digest()})
    background.add_task(_run_render_job,job_id,body.samples)
    return job

@app.get("/api/v1/render-jobs",response_model=RenderJobPage)
def list_render_jobs(limit: int=Query(50,ge=1,le=200),offset: int=Query(0,ge=0),status: Literal["queued","running","completed","failed"]|None=None):
    items,total=database.list_render_jobs(limit,offset,status)
    return {"total":total,"limit":limit,"offset":offset,"items":items}

@app.get("/api/v1/render-jobs/{job_id}",response_model=RenderJobResponse)
def get_render_job(job_id: str):
    job=database.get_render_job(job_id)
    if not job:raise HTTPException(status_code=404,detail="Render job not found")
    return job

@app.post("/api/v1/colour-comparisons",status_code=201,response_model=ComparisonResponse)
def create_colour_comparison(body: ColourComparisonRequest):
    if body.colour_id not in CONFIG["colours"]:raise HTTPException(status_code=422,detail="Unknown colour_id")
    if body.illumination_id not in CONFIG["illuminations"]:raise HTTPException(status_code=422,detail="Unknown illumination_id")
    try:result={**compare_colour(body.colour_id,body.illumination_id),"configuration_sha256":_configuration_digest()}
    except Exception as exc:
        logger.exception("Colour comparison failed")
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    comparison_id=str(uuid.uuid4())
    database.insert_comparison(comparison_id,body.colour_id,body.illumination_id,result)
    return {"id":comparison_id,"colour_id":body.colour_id,"illumination_id":body.illumination_id,"result":result}

@app.get("/api/v1/colour-comparisons/{comparison_id}",response_model=ComparisonResponse)
def get_colour_comparison(comparison_id: str):
    item=database.get_comparison(comparison_id)
    if not item:raise HTTPException(status_code=404,detail="Colour comparison not found")
    return item

@app.get("/api/v1/colour-comparisons",response_model=ComparisonPage)
def list_colour_comparisons(limit: int=Query(50,ge=1,le=200),offset: int=Query(0,ge=0),illumination_id: str|None=None):
    if illumination_id and illumination_id not in CONFIG["illuminations"]:raise HTTPException(status_code=422,detail="Unknown illumination_id")
    items,total=database.list_comparisons(limit,offset,illumination_id)
    return {"total":total,"limit":limit,"offset":offset,"items":items}

@app.post("/api/v1/donation-simulations",status_code=201,response_model=DonationResponse)
def create_donation_simulation(body: DonationSimulationRequest):
    if body.illumination_id not in CONFIG["illuminations"]:raise HTTPException(status_code=422,detail="Unknown illumination_id")
    observer=(body.observer_parameters.model_dump() if body.observer_parameters else {
        "base_error_probability":CONFIG["observer"]["base_error_probability"],
        "maximum_additional_error_probability":CONFIG["observer"]["maximum_additional_error_probability"],
        "delta_e_midpoint":CONFIG["observer"]["delta_e_midpoint"],"delta_e_scale":CONFIG["observer"]["delta_e_scale"],
        "confusion_weights":CONFIG["observer"]["confusion_weights"]})
    action_delta={CONFIG["colours"][cid]["action"]:compare_colour(cid,body.illumination_id)["delta_e00"] for cid in CONFIG["colours"]}
    rows=[simulate_inventory(body.capacity_per_day,action_delta,body.recognition,
                             body.seed+i,body.days,body.mean_arrivals_per_day,observer) for i in range(body.replicates)]
    import numpy as np
    fields=["arrivals","true_red_items","missed_donation_triggers","false_donation_triggers","donated_units",
            "true_donated_units","false_donated_units","capacity_overflow_units","discount_recovered_units","expired_stock","units_saved",
            "discount_recovery_candidates","waste_rate","correctly_classified_items","classification_errors",
            "recognition_accuracy","modeled_avoided_emissions_kgco2e"]
    result={"replicates":body.replicates,"seed":body.seed,"delta_e00_by_action":action_delta,
            "recognition":body.recognition,"capacity_per_day":body.capacity_per_day,"days":body.days,
            "mean_arrivals_per_day":body.mean_arrivals_per_day,"observer_parameters":observer,
            "configuration_sha256":_configuration_digest(),"mean":{},"ci95_percentile":{}}
    for key in fields:
        vals=np.asarray([r[key] for r in rows],dtype=float)
        result["mean"][key]=float(vals.mean())
        result["ci95_percentile"][key]=[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]
    matrices={action:confusion_matrix_for(action_delta[action],observer) for action in ACTION_ORDER}
    priors=[(1-CONFIG["donation"]["red_fraction"])/3]*3+[CONFIG["donation"]["red_fraction"]]
    result["confusion_matrix"]={"actions":ACTION_ORDER,
        "probabilities_by_true_action":{ACTION_ORDER[i]:{ACTION_ORDER[j]:float(matrices[ACTION_ORDER[i]][i,j]) for j in range(4)} for i in range(4)},
        "applied_to_inventory":body.recognition=="simulated_errors",
        "expected_recognition_accuracy":float(sum(priors[i]*matrices[ACTION_ORDER[i]][i,i] for i in range(4))),
        "missed_donation_probability_given_red":float(1-matrices["donate"][3,3]),
        "false_donation_probability_per_arrival":float(sum(priors[i]*matrices[ACTION_ORDER[i]][i,3] for i in range(3)))}
    sustainability=CONFIG["sustainability"]
    mass_per_unit=float(CONFIG["donation"]["average_product_kg"])
    result["mean"]["food_mass_saved_kg"]=result["mean"]["units_saved"]*mass_per_unit
    result["ci95_percentile"]["food_mass_saved_kg"]=[x*mass_per_unit for x in result["ci95_percentile"]["units_saved"]]
    result["sustainability_scenarios"]={name:{"mean_avoided_emissions_kgco2e":result["mean"]["units_saved"]*mass_per_unit*float(factor),
        "ci95_percentile_kgco2e":[x*mass_per_unit*float(factor) for x in result["ci95_percentile"]["units_saved"]],
        "emissions_factor_kgco2e_per_kg":float(factor)}
        for name,factor in sustainability["emissions_factor_scenarios_kgco2e_per_kg"].items()}
    result["sustainability_scenarios_source_note"]=sustainability["factor_source_note"]
    sim_id=str(uuid.uuid4())
    database.insert_donation(sim_id,body.illumination_id,body.recognition,body.capacity_per_day,result)
    return {"id":sim_id,"illumination_id":body.illumination_id,"result":result}

@app.get("/api/v1/donation-simulations",response_model=DonationPage)
def list_donation_simulations(limit: int=Query(50,ge=1,le=200),offset: int=Query(0,ge=0),
                              illumination_id: str|None=None,recognition: Literal["perfect","simulated_errors"]|None=None):
    if illumination_id and illumination_id not in CONFIG["illuminations"]:raise HTTPException(status_code=422,detail="Unknown illumination_id")
    items,total=database.list_donations(limit,offset,illumination_id,recognition)
    return {"total":total,"limit":limit,"offset":offset,"items":items}

@app.get("/api/v1/donation-simulations/{simulation_id}",response_model=DonationResponse)
def get_donation_simulation(simulation_id: str):
    item=database.get_donation(simulation_id)
    if not item:raise HTTPException(status_code=404,detail="Donation simulation not found")
    return item

