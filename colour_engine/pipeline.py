"""End-to-end, deterministic colour and simulated retail-evidence generation."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import os
import shutil
import subprocess
import sys
import numpy as np
import pandas as pd
from scipy.stats import t
from . import __version__
from .chromaticity import dominant_wavelength
from .config import CONFIG, ROOT
from .conversion import D65_WHITE, hex_to_srgb, srgb_to_xyz, xyz_to_lab
from .adaptation import bradford_adapt_xyz
from .delta_e import delta_e_2000
from .spectral_model import (WAVELENGTHS, cie_1931_2deg, d65_spd, digital_reflectance,
                             illuminant_spd, illuminant_white_xyz, spectrum_to_xyz,
                             spectral_info, virtual_print_reflectance)
from simulation.observer_model import ACTION_ORDER, confusion_matrix_for, error_probability
from simulation.sensitivity_analysis import run_capacity_sensitivity

RESULTS = ROOT / "results"

def _write_frame(frame: pd.DataFrame, name: str) -> Path:
    path = RESULTS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.8f")
    return path

def _wilson(success: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    phat = success / total
    denom = 1 + z*z/total
    center = (phat + z*z/(2*total))/denom
    half = z*np.sqrt(phat*(1-phat)/total + z*z/(4*total*total))/denom
    return center-half, center+half

def build_colour_evidence() -> tuple[pd.DataFrame, pd.DataFrame]:
    measurements, chromaticity = [], []
    for colour_id, colour in CONFIG["colours"].items():
        digital = digital_reflectance(colour["hex"])
        printed = virtual_print_reflectance(colour["hex"])
        digital_d65 = spectrum_to_xyz(digital, "L1")
        input_xyz = srgb_to_xyz(hex_to_srgb(colour["hex"]))
        for illum_id, illum in CONFIG["illuminations"].items():
            white = illuminant_white_xyz(illum_id)
            src = spectral_info(digital, illum_id)
            out = spectral_info(printed, illum_id)
            diff = delta_e_2000([src["L"], src["a"], src["b"]], [out["L"], out["a"], out["b"]])
            digital_xyz=spectrum_to_xyz(digital,illum_id); print_xyz=spectrum_to_xyz(printed,illum_id)
            digital_d65_adapted=bradford_adapt_xyz(digital_xyz,white,D65_WHITE)
            print_d65_adapted=bradford_adapt_xyz(print_xyz,white,D65_WHITE)
            adapted_diff=delta_e_2000(xyz_to_lab(digital_d65_adapted,D65_WHITE),xyz_to_lab(print_d65_adapted,D65_WHITE))
            white_xy = (white[0]/white.sum(), white[1]/white.sum())
            src_wl = dominant_wavelength((src["x"], src["y"]), white_xy)
            out_wl = dominant_wavelength((out["x"], out["y"]), white_xy)
            measurements.append({
                "colour_id": colour_id, "colour_name": colour["name"], "hex": colour["hex"], "correct_action": colour["action"],
                "illumination_id": illum_id, "illumination": illum["name"], "cct_target_kelvin": illum["cct_kelvin"],
                "source_model": illum["kind"], "observer": CONFIG["project"]["observer"],
                "digital_X": float(digital_xyz[0]), "digital_Y": float(digital_xyz[1]),
                "digital_Z": float(digital_xyz[2]),
                "print_X": float(print_xyz[0]), "print_Y": float(print_xyz[1]),
                "print_Z": float(print_xyz[2]),
                "digital_L": src["L"], "digital_a": src["a"], "digital_b": src["b"],
                "print_L": out["L"], "print_a": out["a"], "print_b": out["b"],
                "delta_e00": diff["delta_e00"], "delta_l": diff["delta_l"], "delta_c": diff["delta_c"], "delta_h": diff["delta_h"],
                "delta_l_star": diff["delta_l_star"], "delta_c_star": diff["delta_c_star"],
                "delta_c_prime": diff["delta_c_prime"], "delta_h_prime": diff["delta_h_prime"],
                "digital_x": src["x"], "digital_y": src["y"], "print_x": out["x"], "print_y": out["y"],
                "digital_xyz_bradford_to_d65_X": float(digital_d65_adapted[0]),
                "digital_xyz_bradford_to_d65_Y": float(digital_d65_adapted[1]),
                "digital_xyz_bradford_to_d65_Z": float(digital_d65_adapted[2]),
                "print_xyz_bradford_to_d65_X": float(print_d65_adapted[0]),
                "print_xyz_bradford_to_d65_Y": float(print_d65_adapted[1]),
                "print_xyz_bradford_to_d65_Z": float(print_d65_adapted[2]),
                "delta_e00_after_bradford_to_d65": adapted_diff["delta_e00"],
                "d65_reflectance_reconstruction_error_xyz": float(np.linalg.norm(digital_d65-input_xyz)),
                "print_model": CONFIG["virtual_print"]["model"]
            })
            chromaticity.append({"colour_id": colour_id, "colour_name": colour["name"], "illumination_id": illum_id,
                "digital_x": src["x"], "digital_y": src["y"], "print_x": out["x"], "print_y": out["y"],
                "white_x": white_xy[0], "white_y": white_xy[1],
                "digital_dominant_or_complementary_wavelength_nm": src_wl["dominant_wavelength_nm"],
                "digital_excitation_purity": src_wl["excitation_purity"], "digital_wavelength_type": src_wl["wavelength_type"],
                "print_dominant_or_complementary_wavelength_nm": out_wl["dominant_wavelength_nm"],
                "print_excitation_purity": out_wl["excitation_purity"], "print_wavelength_type": out_wl["wavelength_type"]})
    return pd.DataFrame(measurements), pd.DataFrame(chromaticity)

def build_spectral_evidence() -> tuple[pd.DataFrame,pd.DataFrame]:
    illumination={"wavelength_nm":WAVELENGTHS}
    for illum_id,illum in CONFIG["illuminations"].items():
        illumination[f"{illum_id}_relative_spd"] = illuminant_spd(illum_id)
        illumination[f"{illum_id}_name"] = illum["name"]
    reflectance={"wavelength_nm":WAVELENGTHS}
    for colour_id,colour in CONFIG["colours"].items():
        reflectance[f"{colour_id}_digital_reflectance"] = digital_reflectance(colour["hex"])
        reflectance[f"{colour_id}_virtual_print_reflectance"] = virtual_print_reflectance(colour["hex"])
    return pd.DataFrame(illumination),pd.DataFrame(reflectance)

def build_trigger_evidence(measurements: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(int(CONFIG["project"]["random_seed"]))
    trials = int(CONFIG["observer"]["trials_per_condition"])
    detail, summary, logistic_observations = [], [], []
    for row_i, row in measurements.reset_index(drop=True).iterrows():
        matrix = confusion_matrix_for(float(row.delta_e00))
        truth = ACTION_ORDER.index(row.correct_action)
        counts = rng.multinomial(trials, matrix[truth])
        for j, action in enumerate(ACTION_ORDER):
            detail.append({"colour_id": row.colour_id, "illumination_id": row.illumination_id,
                "delta_e00": row.delta_e00, "true_action": row.correct_action, "predicted_action": action,
                "probability_assumption": matrix[truth, j], "simulated_count": int(counts[j]), "trials": trials,
                "missed_donation_trigger": bool(row.correct_action == "donate" and action != "donate"),
                "false_donation_trigger": bool(row.correct_action != "donate" and action == "donate")})
        err = trials-int(counts[truth])
        low, high = _wilson(err, trials)
        missed = int(trials-counts[3]) if truth == 3 else 0
        summary.append({"colour_id": row.colour_id, "illumination_id": row.illumination_id,
                        "delta_e00": row.delta_e00, "assumed_error_probability": error_probability(row.delta_e00),
                        "simulated_error_rate": err/trials, "error_rate_ci95_low": low, "error_rate_ci95_high": high,
                        "simulated_missed_donation_count": missed,
                        "simulated_missed_donation_rate": missed/trials if truth == 3 else 0.0,
                        "simulated_false_donation_count": int(counts[3]) if truth != 3 else 0,
                        "trials": trials, "seed": int(CONFIG["project"]["random_seed"])+row_i})
        # Directly generated Bernoulli outcomes are retained for the descriptive
        # logistic calibration model; they are not human-subject observations.
        logistic_observations.append((float(row.delta_e00), err, trials))
    import statsmodels.api as sm
    d = np.concatenate([np.full(n, de) for de, _, n in logistic_observations])
    y = np.concatenate([np.r_[np.ones(e, dtype=int), np.zeros(n-e, dtype=int)] for _, e, n in logistic_observations])
    fitted = sm.Logit(y, sm.add_constant(d)).fit(disp=False)
    logistic = pd.DataFrame([{"term": name, "coefficient": float(value), "std_error": float(fitted.bse[i]),
                              "model": "descriptive_logit_on_assumption_generated_trials",
                              "p_value_interpretation": "not empirical; no human data"}
                             for i, (name, value) in enumerate(zip(["intercept", "delta_e00"], fitted.params))])
    return pd.DataFrame(detail), pd.DataFrame(summary), logistic

def _illumination_comparisons(measurements: pd.DataFrame) -> pd.DataFrame:
    pivot=measurements.pivot(index="colour_id",columns="illumination_id",values="delta_e00")
    rows=[]
    for left,right in [("L1","L2"),("L1","L3"),("L2","L3")]:
        values=(pivot[left]-pivot[right]).to_numpy(dtype=float);n=len(values)
        mean=float(values.mean());sd=float(values.std(ddof=1));half=float(t.ppf(.975,n-1)*sd/np.sqrt(n))
        rows.append({"comparison":f"{left}-{right}","left_illumination_id":left,"right_illumination_id":right,
                     "n_paired_colours":n,"mean_paired_delta_e00_difference":mean,"sd":sd,
                     "ci95_low_descriptive":mean-half,"ci95_high_descriptive":mean+half,
                     "interpretation":"paired descriptive interval across four configured labels; not population inference"})
    return pd.DataFrame(rows)

def _blender_version() -> dict:
    candidate=os.getenv("BLENDER_EXECUTABLE") or shutil.which("blender")
    candidates=[Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"),Path("/usr/bin/blender")]
    if candidate is None:
        candidate=next((str(p) for p in candidates if p.is_file()),None)
    if not candidate:
        return {"available":False,"version":"not found"}
    try:
        result=subprocess.run([str(candidate),"--version"],capture_output=True,text=True,timeout=15,check=False)
        version=(result.stdout or result.stderr).splitlines()[0]
        return {"available":result.returncode==0,"executable":str(candidate),"version":version}
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {"available":False,"executable":str(candidate),"version":f"unavailable: {exc}"}

def _sustainability_evidence(donation: pd.DataFrame) -> pd.DataFrame:
    factors=CONFIG["sustainability"]["emissions_factor_scenarios_kgco2e_per_kg"]
    kg_per_unit=float(CONFIG["donation"]["average_product_kg"])
    rows=[]
    for item in donation[donation.metric=="units_saved"].to_dict("records"):
        for scenario,factor in factors.items():
            rows.append({"illumination_id":item["illumination_id"],"recognition":item["recognition"],
                "capacity_per_day":item["capacity_per_day"],"scenario":scenario,
                "mean_units_saved":item["mean"],"units_saved_ci95_low":item["mc_ci95_low"],
                "units_saved_ci95_high":item["mc_ci95_high"],"average_product_kg":kg_per_unit,
                "emissions_factor_kgco2e_per_kg":factor,
                "mean_food_mass_saved_kg":item["mean"]*kg_per_unit,
                "modeled_avoided_emissions_kgco2e":item["mean"]*kg_per_unit*factor,
                "ci95_low_kgco2e":item["mc_ci95_low"]*kg_per_unit*factor,
                "ci95_high_kgco2e":item["mc_ci95_high"]*kg_per_unit*factor,
                "replicates":item["replicates"],"seed_base":item["seed_base"],
                "interpretation":CONFIG["sustainability"]["factor_source_note"]})
    return pd.DataFrame(rows)

def _make_figures(measurements: pd.DataFrame, chroma: pd.DataFrame, donation: pd.DataFrame,
                  trigger: pd.DataFrame, trigger_rates: pd.DataFrame, sustainability: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figdir = RESULTS / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    order = list(CONFIG["colours"])
    fig, ax = plt.subplots(figsize=(9, 5.2))
    width = .24
    for j, illum in enumerate(CONFIG["illuminations"]):
        subset = measurements.set_index("colour_id").loc[order].reset_index()
        subset = subset[subset.illumination_id == illum]
        ax.bar(np.arange(4)+(j-1)*width, subset.delta_e00, width, label=CONFIG["illuminations"][illum]["name"])
    ax.set_xticks(np.arange(4), [CONFIG["colours"][c]["name"] for c in order]); ax.set_ylabel("CIEDE2000 ΔE00")
    ax.set_title("Virtual print-response colour difference by label and illumination"); ax.legend(fontsize=8); ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig(figdir/"delta_e_by_condition.png", dpi=180); plt.close(fig)

    cmf = cie_1931_2deg(); locus = cmf[:, :2] / cmf.sum(axis=1)[:, None]
    fig, ax = plt.subplots(figsize=(8, 6.2)); ax.plot(locus[:,0], locus[:,1], color="black", lw=1.1, label="CIE 1931 spectral locus")
    ax.plot([locus[-1,0], locus[0,0]],[locus[-1,1],locus[0,1]],color="black",lw=.8)
    primaries=np.array([[.64,.33],[.30,.60],[.15,.06],[.64,.33]])
    ax.fill(primaries[:,0],primaries[:,1],color="#718096",alpha=.12,label="sRGB gamut triangle")
    ax.plot(primaries[:,0],primaries[:,1],color="#555",ls="--")
    for cid, color in CONFIG["colours"].items():
        sub=chroma[chroma.colour_id==cid]
        ax.scatter(sub.digital_x,sub.digital_y,label=f"{cid} digital",s=30)
        ax.scatter(sub.print_x,sub.print_y,marker="x",s=38)
    whites=chroma.drop_duplicates("illumination_id")
    ax.scatter(whites.white_x,whites.white_y,marker="+",color="black",s=75,label="Illuminant whites")
    ax.set(xlabel="x",ylabel="y",title="CIE 1931 xy chromaticity (digital circles; print crosses)",xlim=(0,.8),ylim=(0,.9)); ax.grid(alpha=.2); ax.legend(fontsize=7,ncol=2)
    fig.tight_layout(); fig.savefig(figdir/"chromaticity_diagram.png",dpi=180); plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.5,6))
    ax.plot(locus[:,0],locus[:,1],color="#25364a",lw=1.4,label="CIE 1931 spectral locus")
    ax.plot([locus[-1,0],locus[0,0]],[locus[-1,1],locus[0,1]],color="#25364a",lw=.9)
    tri=np.array([[.64,.33],[.30,.60],[.15,.06],[.64,.33]])
    ax.fill(tri[:,0],tri[:,1],color="#2E9E4F",alpha=.17,label="sRGB gamut")
    ax.plot(tri[:,0],tri[:,1],color="#236b3b",lw=1.8)
    ax.set(xlabel="CIE x",ylabel="CIE y",title="CIE 1931 chromaticity with sRGB gamut",xlim=(0,.8),ylim=(0,.9))
    ax.set_aspect("equal",adjustable="box");ax.grid(alpha=.2);ax.legend(loc="upper right")
    fig.tight_layout();fig.savefig(figdir/"cie1931_srgb_gamut.png",dpi=190);plt.close(fig)

    fig, ax=plt.subplots(figsize=(9,5.2))
    for illum in CONFIG["illuminations"]:
        sub=chroma[chroma.illumination_id==illum]
        ax.scatter(sub.digital_dominant_or_complementary_wavelength_nm,sub.digital_excitation_purity,label=illum,s=55)
    ax.set(xlabel="Dominant or complementary wavelength (nm)",ylabel="Excitation purity",title="Chromaticity-derived wavelength and excitation purity"); ax.grid(alpha=.25); ax.legend()
    fig.tight_layout(); fig.savefig(figdir/"dominant_wavelength_purity.png",dpi=180); plt.close(fig)

    fig,ax=plt.subplots(figsize=(8.2,5.2))
    red=measurements[measurements.colour_id=="R"].set_index("illumination_id").loc[list(CONFIG["illuminations"])]
    ax.bar([CONFIG["illuminations"][x]["name"] for x in red.index],red.delta_e00,color="#D62828",alpha=.82)
    ax.set(ylabel="CIEDE2000 ΔE00",title="Red donate-now label: virtual print difference by illumination")
    ax.grid(axis="y",alpha=.25);fig.tight_layout();fig.savefig(figdir/"red_delta_e_by_illumination.png",dpi=180);plt.close(fig)

    fig,axes=plt.subplots(1,3,figsize=(12,4.4),sharex=True)
    for ax,(column,label) in zip(axes,[("delta_l_star","ΔL*"),("delta_c_star","ΔC*"),("delta_h_prime","ΔH′ (CIEDE2000)")]):
        for illum in CONFIG["illuminations"]:
            sub=measurements[(measurements.colour_id=="R")&(measurements.illumination_id==illum)]
            ax.bar(illum,float(sub[column].iloc[0]),color={"L1":"#496A81","L2":"#D8A14D","L3":"#BA6A58"}[illum])
        ax.axhline(0,color="#333",lw=.8);ax.set_title(label);ax.set_xticks(list(CONFIG["illuminations"]));ax.grid(axis="y",alpha=.2)
    axes[0].set_ylabel("Signed CIELAB difference")
    fig.suptitle("CIEDE2000 diagnostic components for red warning label",y=1.03)
    fig.tight_layout();fig.savefig(figdir/"red_delta_components.png",dpi=180,bbox_inches="tight");plt.close(fig)

    fig,ax=plt.subplots(figsize=(8,5.4))
    for cid,color in CONFIG["colours"].items():
        sub=trigger_rates[trigger_rates.colour_id==cid]
        ax.errorbar(sub.delta_e00,sub.simulated_error_rate*100,
            yerr=[(sub.simulated_error_rate-sub.error_rate_ci95_low)*100,(sub.error_rate_ci95_high-sub.simulated_error_rate)*100],
            fmt="o",capsize=3,label=f"{cid} · {color['name']}",color=color["hex"])
    ax.set(xlabel="CIEDE2000 ΔE00",ylabel="Simulated classification errors (%)",
           title="Assumption-generated trigger error versus ΔE00")
    ax.grid(alpha=.25);ax.legend(fontsize=8,ncol=2)
    fig.tight_layout();fig.savefig(figdir/"trigger_error_vs_delta_e.png",dpi=180);plt.close(fig)

    fig,axes=plt.subplots(1,3,figsize=(12.8,4.4),sharey=True)
    action_names=["Fresh","Watch","Discount","Donate"]
    for ax,illum in zip(axes,CONFIG["illuminations"]):
        sub=trigger[trigger.illumination_id==illum]
        counts=sub.pivot(index="true_action",columns="predicted_action",values="simulated_count").reindex(index=ACTION_ORDER,columns=ACTION_ORDER).to_numpy(dtype=float)
        row_sums=counts.sum(axis=1,keepdims=True)
        pct=np.divide(counts,row_sums,out=np.zeros_like(counts),where=row_sums!=0)*100
        image=ax.imshow(pct,vmin=0,vmax=100,cmap="Blues")
        ax.set(xticks=range(4),xticklabels=action_names,yticks=range(4),yticklabels=action_names,
               xlabel="Predicted action",ylabel="Configured action",title=CONFIG["illuminations"][illum]["name"])
        ax.tick_params(axis="x",rotation=35)
        if ax is not axes[0]:ax.tick_params(axis="y",labelleft=False);ax.set_ylabel("")
        for i in range(4):
            for j in range(4):ax.text(j,i,f"{pct[i,j]:.1f}",ha="center",va="center",fontsize=7,color="#10263d" if pct[i,j]<60 else "white")
    fig.subplots_adjust(left=.10,right=.92,bottom=.24,top=.82,wspace=.10)
    fig.colorbar(image,ax=axes.ravel().tolist(),label="Simulated row proportion (%)",shrink=.8,pad=.03)
    fig.suptitle("Recognition confusion matrices · synthetic observer model")
    fig.savefig(figdir/"recognition_confusion_matrices.png",dpi=180,bbox_inches="tight");plt.close(fig)

    d=donation[(donation.metric=="units_saved")]
    fig,ax=plt.subplots(figsize=(8.5,5.2))
    for recognition in ["perfect","simulated_errors"]:
        sub=d[(d.illumination_id=="L1")&(d.recognition==recognition)].sort_values("capacity_per_day")
        ax.plot(sub.capacity_per_day,sub["mean"],marker="o",label=recognition)
        ax.fill_between(sub.capacity_per_day,sub.mc_ci95_low,sub.mc_ci95_high,alpha=.15)
    ax.set(xlabel="Donation capacity (units/day)",ylabel="Mean units saved per simulated period",title="Donation capacity sensitivity (D65 error model)"); ax.grid(alpha=.25); ax.legend()
    fig.tight_layout(); fig.savefig(figdir/"donation_capacity_sensitivity.png",dpi=180); plt.close(fig)

    fixed=donation[donation.capacity_per_day==25]
    fig,axes=plt.subplots(1,2,figsize=(11,4.8))
    for ax,metric,title in zip(axes,["units_saved","expired_stock"],["Modeled units saved","Modeled expired stock"]):
        sub=fixed[fixed.metric==metric]
        x=np.arange(3);width=.24
        for i,rec in enumerate(["perfect","simulated_errors"]):
            values=[]
            for illum in CONFIG["illuminations"]:
                found=sub[(sub.illumination_id==illum)&(sub.recognition==rec)]
                values.append(float(found["mean"].iloc[0]) if len(found) else 0)
            ax.bar(x+(i-.5)*width,values,width,label=rec)
        ax.set(xticks=x,xticklabels=[CONFIG["illuminations"][i]["name"] for i in CONFIG["illuminations"]],ylabel="Units per 30-day simulated period",title=title)
        ax.grid(axis="y",alpha=.2);ax.legend(fontsize=8)
    fig.suptitle("Near-expiry inventory comparison · capacity 25 units/day")
    fig.tight_layout();fig.savefig(figdir/"near_expiry_simulation_comparison.png",dpi=180);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11,4.8),sharey=True)
    colors={"low_impact":"#77A974","central":"#4C78A8","high_impact":"#E07B39"}
    for ax,recognition in zip(axes,["perfect","simulated_errors"]):
        sub=sustainability[(sustainability.illumination_id=="L1")&(sustainability.recognition==recognition)]
        for scenario,color in colors.items():
            points=sub[sub.scenario==scenario].sort_values("capacity_per_day")
            ax.plot(points.capacity_per_day,points.modeled_avoided_emissions_kgco2e,marker="o",label=scenario.replace("_"," "),color=color)
        ax.set(xlabel="Donation capacity (units/day)",title=recognition.replace("_"," ").title())
        ax.grid(alpha=.22);ax.legend(fontsize=8)
    axes[0].set_ylabel("Modeled CO₂e avoided (kg / 30-day scenario)")
    fig.suptitle("Sustainability sensitivity · illustrative emissions-factor scenarios")
    fig.tight_layout();fig.savefig(figdir/"sustainability_impact_sensitivity.png",dpi=180);plt.close(fig)

def _version(package: str) -> str:
    try:
        from importlib.metadata import version
        return version(package)
    except Exception:
        return "not installed"

def run_pipeline(replicates: int | None = None) -> dict[str, str]:
    """Generate all color, trigger, donation, statistics, and figure evidence."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    measurements, chroma = build_colour_evidence()
    _write_frame(measurements, "colour_measurements.csv")
    illumination_spectra,reflectance_spectra=build_spectral_evidence()
    _write_frame(illumination_spectra,"illumination_spectra.csv")
    _write_frame(reflectance_spectra,"reflectance_spectra.csv")
    delta_rows=[]
    for illum, group in measurements.groupby("illumination_id", sort=False):
        values=group.delta_e00.to_numpy(); n=len(values); mean=float(values.mean()); sd=float(values.std(ddof=1))
        half=float(t.ppf(.975,n-1)*sd/np.sqrt(n)) if n>1 else 0
        delta_rows.append({"illumination_id":illum,"n_labels":n,"mean_delta_e00":mean,"sd_delta_e00":sd,
                           "ci95_low_descriptive":mean-half,"ci95_high_descriptive":mean+half,
                           "interpretation":"descriptive interval across four configured labels; not population inference"})
    delta_summary=pd.DataFrame(delta_rows)
    _write_frame(delta_summary,"delta_e_summary.csv")
    illumination_comparison=_illumination_comparisons(measurements)
    _write_frame(illumination_comparison,"illumination_comparisons.csv")
    _write_frame(chroma,"chromaticity_data.csv")
    trigger, trigger_summary, logistic = build_trigger_evidence(measurements)
    _write_frame(trigger,"trigger_simulation.csv")
    _write_frame(trigger_summary,"trigger_rates.csv")
    _write_frame(logistic,"trigger_logistic_model.csv")
    donation_parts=[]
    for illum, group in measurements.groupby("illumination_id",sort=False):
        action_delta={row.correct_action:float(row.delta_e00) for row in group.itertuples()}
        donation_parts.append(run_capacity_sensitivity(action_delta,illum,replicates=replicates))
    donation=pd.concat(donation_parts,ignore_index=True)
    _write_frame(donation,"donation_simulation.csv")
    sustainability=_sustainability_evidence(donation)
    _write_frame(sustainability,"sustainability_analysis.csv")
    stat_rows=[]
    for _, row in delta_summary.iterrows():
        stat_rows.append({"analysis":"delta_e_mean_across_four_labels","illumination_id":row.illumination_id,
                          "mean":row.mean_delta_e00,"sd":row.sd_delta_e00,"ci95_low":row.ci95_low_descriptive,
                          "ci95_high":row.ci95_high_descriptive,"n":row.n_labels,
                          "interpretation":row.interpretation})
    for _, row in illumination_comparison.iterrows():
        stat_rows.append({"analysis":"paired_illumination_difference","comparison":row.comparison,
                          "mean":row.mean_paired_delta_e00_difference,"sd":row.sd,
                          "ci95_low":row.ci95_low_descriptive,"ci95_high":row.ci95_high_descriptive,
                          "n":row.n_paired_colours,"interpretation":row.interpretation})
    for _, row in trigger_summary.iterrows():
        stat_rows.append({"analysis":"assumption_generated_trigger_error_rate","illumination_id":row.illumination_id,
                          "colour_id":row.colour_id,"mean":row.simulated_error_rate,"sd":np.nan,
                          "ci95_low":row.error_rate_ci95_low,"ci95_high":row.error_rate_ci95_high,
                          "n":row.trials,"interpretation":"Wilson interval for Monte Carlo trials; synthetic observer model"})
    for _, row in donation[(donation.metric.isin(["units_saved","waste_rate"]))].iterrows():
        stat_rows.append({"analysis":f"monte_carlo_{row.metric}","illumination_id":row.illumination_id,
                          "recognition":row.recognition,"capacity_per_day":row.capacity_per_day,
                          "mean":row["mean"],"sd":row.sd,"ci95_low":row.mc_ci95_low,
                          "ci95_high":row.mc_ci95_high,"n":row.replicates,
                          "interpretation":"Monte Carlo replicate percentile interval; model outcomes"})
    _write_frame(pd.DataFrame(stat_rows),"statistical_summary.csv")
    (RESULTS/"tables").mkdir(parents=True,exist_ok=True)
    delta_summary.to_csv(RESULTS/"tables"/"table_delta_e_summary.csv",index=False,float_format="%.6f")
    trigger_summary.to_csv(RESULTS/"tables"/"table_trigger_rates.csv",index=False,float_format="%.6f")
    _make_figures(measurements,chroma,donation,trigger,trigger_summary,sustainability)
    checksums={name:hashlib.md5((ROOT/"data"/name).read_bytes()).hexdigest() for name in ["CIE_std_illum_D65.csv","CIE_xyz_1931_2deg.csv"]}
    meta={"generated_utc":datetime.now(timezone.utc).isoformat(),"config":CONFIG,"data_md5":checksums,
          "software":{"python":sys.version,"platform":platform.platform(),"numpy":_version("numpy"),"pandas":_version("pandas"),
                      "scipy":_version("scipy"),"statsmodels":_version("statsmodels"),"matplotlib":_version("matplotlib"),
                      "colour-science":_version("colour-science"),"fastapi":_version("fastapi"),
                      "streamlit":_version("streamlit"),"uvicorn":_version("uvicorn"),"blender":_blender_version()},
          "evidence_note":"All print, observer, inventory and sustainability outputs are software simulations; no human or physical measurements.",
          "donation_replicates_per_scenario":int(replicates or CONFIG["donation"]["replicates"])}
    (RESULTS/"run_metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    return {"measurements":str(RESULTS/"colour_measurements.csv"),"figures":str(RESULTS/"figures"),
            "donation":str(RESULTS/"donation_simulation.csv")}

def compare_colour(colour_id: str, illumination_id: str) -> dict:
    colour=CONFIG["colours"].get(colour_id); illum=CONFIG["illuminations"].get(illumination_id)
    if colour is None or illum is None:
        raise ValueError("Unknown colour_id or illumination_id")
    source=digital_reflectance(colour["hex"]); printed=virtual_print_reflectance(colour["hex"])
    a=spectral_info(source,illumination_id); b=spectral_info(printed,illumination_id)
    xyz_a=spectrum_to_xyz(source,illumination_id);xyz_b=spectrum_to_xyz(printed,illumination_id)
    white=illuminant_white_xyz(illumination_id)
    adapt_de=delta_e_2000(xyz_to_lab(bradford_adapt_xyz(xyz_a,white,D65_WHITE),D65_WHITE),
                          xyz_to_lab(bradford_adapt_xyz(xyz_b,white,D65_WHITE),D65_WHITE))
    return {"colour_id":colour_id,"illumination_id":illumination_id,"digital":a,"virtual_print":b,
            **delta_e_2000([a["L"],a["a"],a["b"]],[b["L"],b["a"],b["b"]]),
            "delta_e00_after_bradford_to_d65":adapt_de["delta_e00"],
            "probability_assumption":error_probability(delta_e_2000([a["L"],a["a"],a["b"]],[b["L"],b["a"],b["b"]])["delta_e00"])}

