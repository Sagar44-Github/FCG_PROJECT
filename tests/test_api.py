from fastapi.testclient import TestClient
from backend.main import app
from backend import main as api_module
from io import BytesIO
from zipfile import ZipFile
import shutil
import uuid
from backend import database
from backend.main import ROOT

def test_health_openapi_and_validation():
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json()["status"]=="ok"
        assert client.get("/openapi.json").status_code==200
        assert client.post("/api/v1/colour-comparisons",json={"colour_id":"invalid","illumination_id":"L1"}).status_code==422
        assert client.get("/api/v1/render-jobs?limit=0").status_code==422

def test_comparison_persistence_pagination_and_not_found():
    with TestClient(app) as client:
        response=client.post("/api/v1/colour-comparisons",json={"colour_id":"R","illumination_id":"L1"})
        assert response.status_code==201
        item=response.json()
        assert item["result"]["delta_e00"]>=0
        assert client.get(f"/api/v1/colour-comparisons/{item['id']}").status_code==200
        page=client.get("/api/v1/colour-comparisons?limit=1&offset=0&illumination_id=L1").json()
        assert page["total"]==1 and len(page["items"])==1
        assert client.get("/api/v1/colour-comparisons/missing").status_code==404

def test_render_endpoint_has_no_user_controlled_path(monkeypatch):
    monkeypatch.setattr(api_module,"_run_render_job",lambda job_id,samples:None)
    with TestClient(app) as client:
        assert client.post("/api/v1/render-jobs",json={"render_all":False}).status_code==422
        assert client.post("/api/v1/render-jobs",json={"render_all":True,"samples":1,"output_dir":"../../outside"}).status_code==422
        response=client.post("/api/v1/render-jobs",json={"render_all":True,"samples":1})
        assert response.status_code==202
        assert "output_dir" not in response.json()["request"]

def test_donation_api_returns_computed_seeded_result():
    with TestClient(app) as client:
        response=client.post("/api/v1/donation-simulations",json={
            "illumination_id":"L1","capacity_per_day":20,
            "days":2,"mean_arrivals_per_day":8,"replicates":2,"seed":123})
        assert response.status_code==201
        body=response.json()
        assert body["result"]["mean"]["arrivals"]>0
        assert body["result"]["mean"]["food_mass_saved_kg"]==body["result"]["mean"]["units_saved"]*0.8
        assert len(body["result"]["ci95_percentile"]["food_mass_saved_kg"])==2
        assert client.get(f"/api/v1/donation-simulations/{body['id']}").status_code==200

def test_dashboard_configuration_artifacts_renders_and_evidence_package():
    with TestClient(app) as client:
        config=client.get("/api/v1/configuration").json()
        assert len(config["sha256"])==64 and config["mutable_via_api"] is False
        assert config["configuration"]["colours"]["R"]["hex"]=="#D62828"
        dashboard=client.get("/api/v1/dashboard").json()
        assert dashboard["render_count"]==12
        assert dashboard["colour_measurement_count"]==12
        artifacts=client.get("/api/v1/artifacts").json()["items"]
        assert any(x["name"]=="figures/recognition_confusion_matrices.png" and x["available"] for x in artifacts)
        supermarket=[x for x in artifacts if x["name"].startswith("supermarket/")]
        assert len(supermarket)==7 and all(x["available"] for x in supermarket)
        png=client.get("/api/v1/artifacts/figures/red_delta_components.png")
        assert png.status_code==200 and png.content.startswith(b"\x89PNG")
        hero=client.get("/api/v1/artifacts/supermarket/03_donate_now_macro.png")
        assert hero.status_code==200 and hero.content.startswith(b"\x89PNG")
        assert client.get("/api/v1/artifacts/../../config.json").status_code==404
        renders=client.get("/api/v1/renders").json()
        assert renders["total"]==13
        preview=client.get("/api/v1/renders/baseline/R_L1.png")
        assert preview.status_code==200 and preview.content.startswith(b"\x89PNG")
        assert client.get("/api/v1/renders/baseline/../../config.json").status_code==404
        package=client.get("/api/v1/exports/evidence-package")
        assert package.status_code==200
        with ZipFile(BytesIO(package.content)) as archive:
            names=set(archive.namelist())
            assert "config.json" in names and "results/colour_measurements.csv" in names
            assert "renders/R_L1.png" in names and "colour_engine/delta_e.py" in names
            assert "frontend/src/App.tsx" in names and "frontend/package-lock.json" in names
            assert "blender/q3_supermarket.blend" in names
            assert "frontend/public/assets/supermarket/verdant_market.glb" in names
            assert "docs/supermarket_visual_pipeline.md" in names

def test_evidence_package_includes_completed_api_render_job_files():
    job_id=str(uuid.uuid4())
    job_dir=ROOT/"renders"/f"api_{job_id}"
    job_dir.mkdir(parents=True)
    source=ROOT/"renders"/"G_L1.png"
    try:
        shutil.copyfile(source,job_dir/"G_L1.png")
        database.insert_render_job(job_id,{"render_all":True,"samples":1})
        database.update_render_job(job_id,"completed",result={"count":12})
        with TestClient(app) as client:
            package=client.get("/api/v1/exports/evidence-package")
        assert package.status_code==200
        with ZipFile(BytesIO(package.content)) as archive:
            assert f"renders/api_{job_id}/G_L1.png" in archive.namelist()
    finally:
        shutil.rmtree(job_dir,ignore_errors=True)

def test_request_scoped_observer_parameters_are_stored_and_validated():
    with TestClient(app) as client:
        payload={"illumination_id":"L1","capacity_per_day":10,"days":2,"mean_arrivals_per_day":8,
            "replicates":2,"seed":17,"observer_parameters":{"base_error_probability":0.1,
            "maximum_additional_error_probability":0.2,"delta_e_midpoint":2.0,"delta_e_scale":1.0,
            "confusion_weights":{"adjacent":0.8,"nonadjacent":0.2}}}
        result=client.post("/api/v1/donation-simulations",json=payload)
        assert result.status_code==201
        body=result.json()["result"]
        assert body["observer_parameters"]["base_error_probability"]==0.1
        assert body["confusion_matrix"]["missed_donation_probability_given_red"]>0.1
        assert set(body["sustainability_scenarios"])=={"low_impact","central","high_impact"}
        assert len(body["configuration_sha256"])==64
        invalid={**payload,"observer_parameters":{"base_error_probability":0.9,"maximum_additional_error_probability":0.2}}
        assert client.post("/api/v1/donation-simulations",json=invalid).status_code==422

def test_analysis_job_runs_pipeline_and_is_paginated(monkeypatch):
    monkeypatch.setattr(api_module,"run_pipeline",lambda replicates:{"measurements":"computed.csv","replicates":replicates})
    with TestClient(app) as client:
        response=client.post("/api/v1/analysis-jobs",json={"donation_replicates":7})
        assert response.status_code==202
        job=response.json()
        job=client.get(f"/api/v1/analysis-jobs/{job['id']}").json()
        assert job["status"]=="completed"
        assert job["request"]["donation_replicates"]==7
        assert job["result"]["donation_replicates_per_scenario"]==7
        assert client.get(f"/api/v1/analysis-jobs/{job['id']}").status_code==200
        page=client.get("/api/v1/analysis-jobs?limit=1&offset=0&status=completed").json()
        assert page["total"]==1 and len(page["items"])==1
