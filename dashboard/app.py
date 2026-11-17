"""Streamlit demonstration interface; all calculations and files come from FastAPI."""
from __future__ import annotations

import os
from io import BytesIO
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st

API_BASE=os.getenv("Q3_API_URL","http://127.0.0.1:8000").rstrip("/")
TIMEOUT=(4,90)

st.set_page_config(page_title="Q3 Spectral Research",page_icon="🎨",layout="wide",initial_sidebar_state="expanded")
st.markdown("""
<style>
  .stApp { background:#f4f7fa; color:#17283c; }
  [data-testid="stSidebar"] { background:#13263a; }
  [data-testid="stSidebar"] * { color:#edf3f8; }
  .q3-kicker { color:#55748f;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase; }
  .q3-muted { color:#63778b;font-size:.9rem; }
  .q3-card { background:white;border:1px solid #dce5ee;border-radius:12px;padding:16px 18px;min-height:96px;box-shadow:0 2px 8px rgba(24,48,72,.04); }
  .q3-color { display:flex;align-items:center;gap:12px;padding:10px;border:1px solid #e0e7ef;border-radius:10px;background:white;margin-bottom:8px; }
  .q3-swatch { width:40px;height:40px;border-radius:9px;border:1px solid #0002;flex:0 0 40px; }
  div[data-testid="stMetric"] { background:#fff;border:1px solid #dce5ee;padding:12px 16px;border-radius:11px; }
  h1,h2,h3 { color:#17283c; }
</style>
""",unsafe_allow_html=True)

def api_get(path: str, params: dict | None=None):
    response=requests.get(f"{API_BASE}{path}",params=params,timeout=TIMEOUT)
    response.raise_for_status()
    return response

def api_post(path: str, payload: dict):
    response=requests.post(f"{API_BASE}{path}",json=payload,timeout=TIMEOUT)
    response.raise_for_status()
    return response

def show_api_error(exc: Exception):
    detail=exc
    if isinstance(exc,requests.HTTPError) and exc.response is not None:
        try: detail=exc.response.json().get("detail",exc.response.text)
        except ValueError: detail=exc.response.text
    st.error(f"Backend request failed: {detail}")

def load_csv(artifact_name: str) -> pd.DataFrame:
    response=api_get(f"/api/v1/artifacts/{quote(artifact_name,safe='/')}")
    return pd.read_csv(BytesIO(response.content))

def show_figure(artifact_name: str,caption: str|None=None):
    try:
        image=api_get(f"/api/v1/artifacts/{quote(artifact_name,safe='/')}").content
        st.image(image,caption=caption or artifact_name.split("/")[-1],width="stretch")
    except requests.HTTPError:
        st.info("This figure is not generated yet. Start a colour-analysis job to create it.")

def metric_row(items: list[tuple[str,str,str|None]]):
    columns=st.columns(len(items))
    for column,(label,value,help_text) in zip(columns,items):
        column.metric(label,value,help=help_text)

def wait_for_job(job_id: str,resource: str,timeout_seconds: int=360):
    import time
    box=st.status("Waiting for processing job…",expanded=True)
    bar=st.progress(0)
    for elapsed in range(timeout_seconds):
        try:
            job=api_get(f"/api/v1/{resource}/{job_id}").json()
        except requests.RequestException as exc:
            box.update(label="Could not refresh job status",state="error");show_api_error(exc);return
        state=job["status"]
        box.write(f"Job `{job_id}` · {state}")
        bar.progress(min(.96,(elapsed+1)/timeout_seconds))
        if state=="completed":
            bar.progress(1.0);box.update(label="Processing completed",state="complete",expanded=False)
            st.session_state[f"last_{resource}"]=job
            return
        if state=="failed":
            box.update(label="Processing failed",state="error",expanded=True)
            st.error(job.get("error") or "The backend reported a processing error.")
            return
        time.sleep(1)
    box.update(label="Job is still running",state="running",expanded=True)
    st.info("The job continues in the backend. Use Refresh status to check it again.")

try:
    health=api_get("/api/v1/health").json()
    config_response=api_get("/api/v1/configuration").json()
    cfg=config_response["configuration"]
    dashboard=api_get("/api/v1/dashboard").json()
except requests.RequestException as error:
    st.title("Q3 Spectral Research")
    st.error("The FastAPI service is not reachable. Start it with `uvicorn backend.main:app --reload` and retry.")
    st.caption(f"Backend URL: {API_BASE}")
    st.stop()

st.sidebar.markdown("<div class='q3-kicker'>Q3 Research Application</div>",unsafe_allow_html=True)
st.sidebar.title("Shelf Colour Lab")
st.sidebar.caption("Spectral evaluation · donation trigger modelling")
page=st.sidebar.radio("Navigate",["Overview","Colour analysis","Blender renders","Donation & sustainability","Results & export"],label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.success(f"API {health['status']} · SQLite · user space")
st.sidebar.caption(f"Config SHA-256: `{config_response['sha256'][:16]}…`")
st.sidebar.caption("All outputs are computational simulations. No physical or human observations are represented.")

if page=="Overview":
    st.markdown("<div class='q3-kicker'>Research workspace</div>",unsafe_allow_html=True)
    st.title(cfg["project"]["title"])
    st.write("Compare the virtual print response of expiry-warning shelf colours under CIE D65 and parameterized store-LED spectra, then explore simulated donation-trigger and inventory outcomes.")
    metric_row([
        ("Application status","Online",f"FastAPI {health.get('project_version','')} · SQLite persistence"),
        ("Generated render PNGs",str(dashboard["render_count"]),f"Baseline matrix: {dashboard['baseline_render_count']}/12 · latest job: {dashboard['latest_render_job_status'] or 'none'}"),
        ("Colour measurements",str(dashboard["colour_measurement_count"]),dashboard["colour_analysis_status"]),
        ("Latest evidence run",dashboard.get("generated_at") or "Not run", "UTC timestamp from saved run metadata")])
    st.subheader("Research colour set")
    cols=st.columns(4)
    for col,(cid,c) in zip(cols,cfg["colours"].items()):
        col.markdown(f"<div class='q3-color'><span class='q3-swatch' style='background:{c['hex']}'></span><div><b>{cid} · {c['name']}</b><br><span class='q3-muted'>{c['hex']}</span></div></div>",unsafe_allow_html=True)
    st.subheader("Latest ΔE00 summary")
    if dashboard["delta_e_summary"]:
        st.dataframe(pd.DataFrame(dashboard["delta_e_summary"]),hide_index=True,width="stretch")
        show_figure("figures/delta_e_by_condition.png","ΔE00 by label and illumination")
    else:st.info("Colour analysis has not generated results yet. Use Colour analysis → Run full analysis.")
    st.subheader("Donation-trigger warning colour")
    if dashboard["red_trigger_summary"]:
        st.dataframe(pd.DataFrame(dashboard["red_trigger_summary"]),hide_index=True,width="stretch")
    else:st.info("Trigger outcomes will appear after a colour-analysis run.")
    st.subheader("Recent processing jobs")
    if dashboard["recent_jobs"]:st.dataframe(pd.DataFrame(dashboard["recent_jobs"]),hide_index=True,width="stretch")
    else:st.caption("No persisted jobs yet.")
    if dashboard.get("generated_at"):st.caption(f"Evidence generated at {dashboard['generated_at']} · config {dashboard['configuration_sha256'][:16]}…")

elif page=="Colour analysis":
    st.title("Colour analysis")
    st.write("The backend runs the CIE spectral pipeline and persists each selected comparison. The reference configuration is read-only in the dashboard.")
    with st.expander("Configured colours and illumination models",expanded=True):
        color_cols=st.columns(4)
        for col,(cid,c) in zip(color_cols,cfg["colours"].items()):
            col.markdown(f"<div class='q3-color'><span class='q3-swatch' style='background:{c['hex']}'></span><div><b>{c['name']}</b><br>{cid} · {c['hex']}<br><small>Action: {c['action']}</small></div></div>",unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{"ID":lid,"Illumination":light["name"],"Kind":light["kind"],"CCT target (K)":light["cct_kelvin"],"Standard reference":light["is_standard"]} for lid,light in cfg["illuminations"].items()]),hide_index=True,width="stretch")
        st.caption(f"Wavelength range: {cfg['project']['wavelength_nm']['start']}–{cfg['project']['wavelength_nm']['end']} nm at {cfg['project']['wavelength_nm']['step']} nm steps · observer: {cfg['project']['observer']} · configuration digest: {config_response['sha256']}")
    controls=st.columns([1,1,1.5])
    selected_color=controls[0].selectbox("Filter colour",list(cfg["colours"]),format_func=lambda x:f"{x} · {cfg['colours'][x]['name']}",index=3)
    selected_light=controls[1].selectbox("Illumination",list(cfg["illuminations"]),format_func=lambda x:f"{x} · {cfg['illuminations'][x]['name']}")
    controls[2].markdown("**Red warning focus**: the selected `R` rows directly support the donate-now comparison.")
    button_cols=st.columns([1,1,2])
    if button_cols[0].button("Compute selected comparison",type="primary"):
        try:
            result=api_post("/api/v1/colour-comparisons",{"colour_id":selected_color,"illumination_id":selected_light}).json()
            st.session_state["selected_comparison"]=result
        except requests.RequestException as exc:show_api_error(exc)
    if button_cols[1].button("Run full colour analysis"):
        try:
            job=api_post("/api/v1/analysis-jobs",{"donation_replicates":500}).json()
            st.session_state["analysis_job_id"]=job["id"]
            wait_for_job(job["id"],"analysis-jobs")
            st.rerun()
        except requests.RequestException as exc:show_api_error(exc)
    if st.session_state.get("selected_comparison"):
        result=st.session_state["selected_comparison"]["result"]
        st.subheader(f"Computed result · {selected_color} under {selected_light}")
        metric_row([("ΔE00",f"{result['delta_e00']:.4f}","CIEDE2000 virtual-print comparison"),("ΔL*",f"{result['delta_l_star']:.4f}","Signed CIELAB lightness difference"),("ΔC*",f"{result['delta_c_star']:.4f}","Signed CIELAB chroma difference"),("ΔH′",f"{result['delta_h_prime']:.4f}","CIEDE2000 adjusted hue difference")])
        st.caption(f"Synthetic observer error-probability assumption: {result['probability_assumption']:.2%} · comparison id `{st.session_state['selected_comparison']['id']}`")
    if dashboard["colour_measurement_count"]:
        try:
            measurements=load_csv("colour_measurements.csv")
            filtered=measurements[(measurements.colour_id==selected_color)&(measurements.illumination_id==selected_light)]
            columns=["colour_id","colour_name","hex","illumination_id","illumination","delta_e00","delta_l_star","delta_c_star","delta_h_prime","digital_x","digital_y","print_x","print_y","digital_dominant_or_complementary_wavelength_nm"]
            st.subheader("Saved computational measurements")
            st.dataframe(filtered[[x for x in columns if x in filtered]],hide_index=True,width="stretch")
            if selected_color=="R":show_figure("figures/red_delta_e_by_illumination.png","Donate-now red: ΔE00 across the three illumination conditions")
            show_figure("figures/red_delta_components.png","CIEDE2000 diagnostic components for the red warning colour")
            with st.expander("Chromaticity and wavelength analyses"):
                figures=st.columns(3)
                with figures[0]:show_figure("figures/chromaticity_diagram.png")
                with figures[1]:show_figure("figures/cie1931_srgb_gamut.png")
                with figures[2]:show_figure("figures/dominant_wavelength_purity.png")
                chroma=load_csv("chromaticity_data.csv")
                sub=chroma[(chroma.colour_id==selected_color)&(chroma.illumination_id==selected_light)]
                st.dataframe(sub,hide_index=True,width="stretch")
            show_figure("figures/trigger_error_vs_delta_e.png","Synthetic trigger-error sensitivity versus calculated ΔE00")
            csv=api_get("/api/v1/artifacts/colour_measurements.csv").content
            st.download_button("Download full measurement CSV",csv,"colour_measurements.csv","text/csv")
        except requests.RequestException as exc:show_api_error(exc)
    else:st.info("No saved measurement table is available yet. Start the full analysis to generate all 12 comparisons and research figures.")

elif page=="Blender renders":
    st.title("Blender render batch")
    st.write("The API invokes the installed Blender executable with the project's fixed render script. The output path and command are not user-controlled.")
    render_col,info_col=st.columns([1,2])
    if render_col.button("Start 12-condition Blender batch",type="primary"):
        try:
            job=api_post("/api/v1/render-jobs",{"render_all":True,"samples":16}).json()
            st.session_state["render_job_id"]=job["id"]
            st.success(f"Render job queued: {job['id']}")
        except requests.RequestException as exc:show_api_error(exc)
    if st.session_state.get("render_job_id"):
        job_id=st.session_state["render_job_id"]
        if info_col.button("Wait for / refresh render status"):
            wait_for_job(job_id,"render-jobs",timeout_seconds=1800)
        try:
            job=api_get(f"/api/v1/render-jobs/{job_id}").json()
            info_col.info(f"Job {job['id']} · {job['status']} · created {job['created_at']}")
            if job.get("error"):info_col.error(job["error"])
            elif job.get("result"):info_col.success(f"Generated {job['result']['count']} PNG renders with the configured Blender executable.")
        except requests.RequestException as exc:show_api_error(exc)
    try:
        catalog=api_get("/api/v1/renders").json()["items"]
        contact=next((item for item in catalog if item.get("kind")=="contact_sheet"),None)
        if contact:
            st.subheader("Twelve-condition contact sheet")
            st.image(api_get(contact["url"]).content,width="stretch")
        renders=[item for item in catalog if item.get("colour_id")]
        st.subheader(f"Individual renders · {len(renders)} available")
        if renders:
            for offset in range(0,len(renders),3):
                row=st.columns(3)
                for col,item in zip(row,renders[offset:offset+3]):
                    col.image(api_get(item["url"]).content,width="stretch")
                    col.caption(f"{item['colour_id']} · {item['colour_name']} {item['hex']}\n{item['illumination_id']} · {item['illumination_name']}")
        else:st.info("No render files were found. Start the Blender batch above.")
    except requests.RequestException as exc:show_api_error(exc)
    st.caption("Cycles uses Blender's RGB renderer for visualization. The spectral CIE calculations are performed separately by the Python engine.")

elif page=="Donation & sustainability":
    st.title("Donation-trigger and near-expiry simulation")
    st.warning("Outputs below are Monte Carlo model outcomes under explicitly selected assumptions. They are not measured human recognition, retail donation, food waste, or carbon reductions.")
    with st.form("simulation_form"):
        top=st.columns(3)
        illumination=top[0].selectbox("Illumination",list(cfg["illuminations"]),format_func=lambda x:f"{x} · {cfg['illuminations'][x]['name']}")
        recognition=top[1].selectbox("Recognition model",["simulated_errors","perfect"],format_func=lambda x:{"simulated_errors":"Synthetic observer errors","perfect":"Perfect classification baseline"}[x])
        capacity=top[2].number_input("Donation capacity (units/day)",min_value=0,max_value=100000,value=25,step=5)
        second=st.columns(3)
        days=second[0].number_input("Simulation horizon (days)",min_value=1,max_value=3650,value=30)
        arrivals=second[1].number_input("Mean near-expiry arrivals/day",min_value=0.0,max_value=100000.0,value=80.0,step=5.0)
        replicates=second[2].number_input("Monte Carlo replicates",min_value=1,max_value=2000,value=100,step=25)
        seed=st.number_input("Random seed",min_value=0,max_value=2147483647,value=int(cfg["project"]["random_seed"]),step=1)
        with st.expander("Observer model sensitivity parameters"):
            defaults=cfg["observer"]
            obs=st.columns(4)
            base=obs[0].number_input("Base error probability",min_value=0.0,max_value=1.0,value=float(defaults["base_error_probability"]),step=.01,format="%.3f")
            maximum=obs[1].number_input("Maximum added error",min_value=0.0,max_value=1.0,value=float(defaults["maximum_additional_error_probability"]),step=.01,format="%.3f")
            midpoint=obs[2].number_input("ΔE midpoint",min_value=0.0,max_value=100.0,value=float(defaults["delta_e_midpoint"]),step=.5)
            scale=obs[3].number_input("ΔE scale",min_value=.01,max_value=100.0,value=float(defaults["delta_e_scale"]),step=.25)
            weights=st.columns(2)
            adjacent=weights[0].number_input("Adjacent-action confusion weight",min_value=.001,max_value=1.0,value=float(defaults["confusion_weights"]["adjacent"]),step=.05)
            nonadjacent=weights[1].number_input("Non-adjacent-action confusion weight",min_value=.001,max_value=1.0,value=float(defaults["confusion_weights"]["nonadjacent"]),step=.05)
        run=st.form_submit_button("Run seeded simulation",type="primary")
    if run:
        payload={"illumination_id":illumination,"recognition":recognition,"capacity_per_day":int(capacity),"days":int(days),
            "mean_arrivals_per_day":float(arrivals),"replicates":int(replicates),"seed":int(seed),
            "observer_parameters":{"base_error_probability":float(base),"maximum_additional_error_probability":float(maximum),
                "delta_e_midpoint":float(midpoint),"delta_e_scale":float(scale),
                "confusion_weights":{"adjacent":float(adjacent),"nonadjacent":float(nonadjacent)}}}
        try:
            response=api_post("/api/v1/donation-simulations",payload).json()
            st.session_state["last_donation_simulation"]=response
        except requests.RequestException as exc:show_api_error(exc)
    response=st.session_state.get("last_donation_simulation")
    if response:
        result=response["result"];mean=result["mean"];ci=result["ci95_percentile"]
        st.subheader("Persisted simulation result")
        st.caption(f"Simulation `{response['id']}` · config {result['configuration_sha256'][:16]}… · seed {result['seed']} · {result['replicates']} runs")
        st.caption(f"ΔE00 by action: {result['delta_e00_by_action']}")
        main_metrics=st.columns(4)
        main_metrics[0].metric("Simulated recognition accuracy",f"{mean['recognition_accuracy']:.1%}","Computed over modeled inventory arrivals")
        main_metrics[1].metric("Observer-model miss p(red)",f"{result['confusion_matrix']['missed_donation_probability_given_red']:.1%}","Synthetic observer probability; not applied in perfect mode")
        main_metrics[2].metric("False donate per arrival",f"{result['confusion_matrix']['false_donation_probability_per_arrival']:.1%}")
        main_metrics[3].metric("Mean units saved",f"{mean['units_saved']:.1f}",f"95% Monte Carlo interval {ci['units_saved'][0]:.1f}–{ci['units_saved'][1]:.1f}")
        table=pd.DataFrame({"Outcome":["Correctly donated units","All donated units","Discount-recovered units","Expired stock","Missed donation triggers","False donation triggers","Capacity overflow"],
            "Monte Carlo mean":[mean["true_donated_units"],mean["donated_units"],mean["discount_recovered_units"],mean["expired_stock"],mean["missed_donation_triggers"],mean["false_donation_triggers"],mean["capacity_overflow_units"]],
            "95% low":[ci[k][0] for k in ["true_donated_units","donated_units","discount_recovered_units","expired_stock","missed_donation_triggers","false_donation_triggers","capacity_overflow_units"]],
            "95% high":[ci[k][1] for k in ["true_donated_units","donated_units","discount_recovered_units","expired_stock","missed_donation_triggers","false_donation_triggers","capacity_overflow_units"]]})
        st.dataframe(table,hide_index=True,width="stretch")
        st.subheader("Model confusion matrix")
        cm=result["confusion_matrix"]["probabilities_by_true_action"]
        cm_table=pd.DataFrame(cm).T.reindex(index=["fresh","watch","discount","donate"],columns=["fresh","watch","discount","donate"])*100
        cm_table.index.name="Configured action · % probability"
        st.dataframe(cm_table.style.format("{:.2f}%"),width="stretch")
        applied="This observer matrix is applied to inventory outcomes." if result["confusion_matrix"]["applied_to_inventory"] else "Perfect-recognition mode bypasses this matrix for inventory outcomes."
        st.caption(f"Rows are true/configured actions; columns are modeled perceived actions. {applied} Probabilities follow the request's monotone ΔE00 error curve; they are not empirically calibrated.")
        st.subheader("Sustainability sensitivity scenarios")
        sc=result["sustainability_scenarios"]
        scenario_table=pd.DataFrame([{"Scenario":name.replace("_"," ").title(),"Emissions factor (kg CO₂e/kg)":value["emissions_factor_kgco2e_per_kg"],
            "Modeled avoided CO₂e (kg)":value["mean_avoided_emissions_kgco2e"],"95% low":value["ci95_percentile_kgco2e"][0],"95% high":value["ci95_percentile_kgco2e"][1]} for name,value in sc.items()])
        st.dataframe(scenario_table,hide_index=True,width="stretch")
        st.caption(result["sustainability_scenarios_source_note"]+" Calculation: mean units saved × configured average product mass × scenario emissions factor.")
        st.caption(f"Observer assumptions stored with this result: {result['observer_parameters']}")
    st.subheader("Saved capacity sensitivity analysis")
    show_figure("figures/donation_capacity_sensitivity.png","Seeded 500-replicate capacity sensitivity generated by the full analysis pipeline")
    show_figure("figures/near_expiry_simulation_comparison.png","Perfect recognition compared with the synthetic observer under each illumination")
    st.subheader("Persisted simulation history")
    hist_cols=st.columns([1,1,2])
    limit=hist_cols[0].selectbox("Rows per page",[5,10,25],index=1)
    offset=hist_cols[1].number_input("Offset",min_value=0,value=0,step=int(limit))
    if hist_cols[2].button("Refresh history"):
        st.session_state["donation_history"]=api_get("/api/v1/donation-simulations",{"limit":int(limit),"offset":int(offset)}).json()
    if st.session_state.get("donation_history"):
        history=st.session_state["donation_history"]
        st.caption(f"Page {offset//limit+1} · {len(history['items'])} shown of {history['total']} persisted simulations")
        st.dataframe(pd.DataFrame([{"id":x["id"],"illumination":x["illumination_id"],"recognition":x["recognition"],"capacity/day":x["capacity_per_day"],"created":x["created_at"],"mean saved":x["result"].get("mean",{}).get("units_saved")} for x in history["items"]]),hide_index=True,width="stretch")

elif page=="Results & export":
    st.title("Research results and exports")
    st.write("Browse persisted API jobs and the reproducible evidence files. Downloads are served through a fixed artifact allow-list.")
    a,b,c=st.columns(3)
    if a.button("Start new full evidence run",type="primary"):
        try:
            job=api_post("/api/v1/analysis-jobs",{"donation_replicates":500}).json()
            st.session_state["analysis_job_id"]=job["id"]
            wait_for_job(job["id"],"analysis-jobs")
            st.rerun()
        except requests.RequestException as exc:show_api_error(exc)
    if b.button("Refresh all outputs"):
        st.cache_data.clear();st.rerun()
    if c.button("Download complete evidence package"):
        try:
            package=api_get("/api/v1/exports/evidence-package").content
            st.download_button("Save q3_research_evidence.zip",package,"q3_research_evidence.zip","application/zip",key="save_evidence")
        except requests.RequestException as exc:show_api_error(exc)
    st.subheader("Recent persisted operations")
    try:
        jobs=api_get("/api/v1/analysis-jobs",{"limit":10,"offset":0}).json()
        renders=api_get("/api/v1/render-jobs",{"limit":10,"offset":0}).json()
        comps=api_get("/api/v1/colour-comparisons",{"limit":10,"offset":0}).json()
        sims=api_get("/api/v1/donation-simulations",{"limit":10,"offset":0}).json()
        for label,result in [("Full analysis jobs",jobs),("Blender render jobs",renders),("Colour comparisons",comps),("Donation simulations",sims)]:
            with st.expander(f"{label} · {result['total']} total"):
                st.dataframe(pd.DataFrame(result["items"]),hide_index=True,width="stretch")
                st.caption(f"Pagination: limit={result['limit']} · offset={result['offset']}")
        artifacts=api_get("/api/v1/artifacts").json()["items"]
        ready=[x for x in artifacts if x["available"]]
        st.subheader("Generated files")
        selected=st.selectbox("Select an artifact to download",[x["name"] for x in ready])
        chosen=next(x for x in ready if x["name"]==selected)
        file_response=api_get(f"/api/v1/artifacts/{quote(selected,safe='/')}")
        mime="text/csv" if selected.endswith(".csv") else "image/png" if selected.endswith(".png") else "application/json"
        st.download_button(f"Download {selected}",file_response.content,selected.split("/")[-1],mime)
        st.caption(f"{chosen['bytes']:,} bytes · API-served allow-listed result file")
        if selected.endswith(".png"):st.image(file_response.content,width="stretch")
        if selected.endswith(".csv"):
            frame=pd.read_csv(BytesIO(file_response.content))
            st.dataframe(frame.head(100),hide_index=True,width="stretch")
            if len(frame)>100:st.caption(f"Showing 100 of {len(frame)} rows.")
        show_figure("figures/sustainability_impact_sensitivity.png","Low, central, and high illustrative factor scenarios")
    except requests.RequestException as exc:show_api_error(exc)
