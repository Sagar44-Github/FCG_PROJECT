#!/usr/bin/env python3
"""Generate the paper's result tables from the copied final handoff CSV files."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "results" / "CSV"
TABLES = ROOT / "tables"
TABLES.mkdir(parents=True, exist_ok=True)
END = r"\\"

def read(name: str):
    with (CSV / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def put(name: str, lines: list[str]) -> None:
    (TABLES / name).write_text("\n".join(lines) + "\n", encoding="utf-8")

# All 12 colour by illumination calculations.
measurements = read("colour_measurements.csv")
labels = [("G", "Green / Fresh"), ("Y", "Yellow / Watch"),
          ("O", "Orange / Discount"), ("R", "Red / Donate now")]
lights = [("L1", "D65"), ("L2", "Neutral LED model"), ("L3", "Warm LED model")]
by_pair = {(r["colour_id"], r["illumination_id"]): r for r in measurements}
lines = [r"\begin{table*}[!t]", r"\caption{Calculated CIEDE2000 differences for all 12 configured conditions.}",
         r"\label{tab:deltae}\centering\small",
         r"\begin{tabular}{llrrr}", r"\toprule",
         r"Label & sRGB & D65 & Neutral LED & Warm LED " + END,
         r"\midrule"]
for cid, label in labels:
    first = by_pair[(cid, "L1")]
    values = [by_pair[(cid, lid)]["delta_e00"] for lid, _ in lights]
    hex_value = first["hex"].replace("#", r"\#")
    lines.append(f"{label} & {hex_value} & " + " & ".join(f"{float(v):.4f}" for v in values) + " " + END)
lines += [r"\bottomrule", r"\end{tabular}",
          r"\par\vspace{3pt}\footnotesize Each cell is one deterministic digital-metamer versus virtual-print calculation; these are not physical label measurements.",
          r"\end{table*}"]
put("deltae_table.tex", lines)

# Red-label difference and components, directly from colour_measurements.csv.
red = [r for r in measurements if r["colour_id"] == "R"]
lines = [r"\begin{table*}[!t]", r"\caption{Primary red DONATE NOW colour result and CIEDE2000 component terms.}",
         r"\label{tab:redcolour}\centering\scriptsize",
         r"\begin{tabular}{lrrrrr}", r"\toprule",
         r"Illuminant & $\Delta E_{00}$ & $\Delta L^*$ & Raw $\Delta C^*_{ab}$ & Adjusted $\Delta C'$ & Adjusted $\Delta H'$ " + END,
         r"\midrule"]
light_names = {"L1": "D65", "L2": "4000-K LED model", "L3": "3000-K LED model"}
for lid in ("L1", "L2", "L3"):
    r = next(x for x in red if x["illumination_id"] == lid)
    vals = [float(r[k]) for k in ("delta_e00", "delta_l_star", "delta_c_star", "delta_c_prime", "delta_h_prime")]
    lines.append(light_names[lid] + " & " + " & ".join(f"{v:.4f}" for v in vals) + " " + END)
lines += [r"\bottomrule", r"\end{tabular}",
          r"\par\vspace{3pt}\footnotesize Signed changes are virtual print minus digital. Raw $\Delta C^*_{ab}$ is distinct from the adjusted CIEDE2000 term.",
          r"\end{table*}"]
put("red_trigger_table.tex", lines)

# Red trigger Monte Carlo draws.
rates = [r for r in read("trigger_rates.csv") if r["colour_id"] == "R"]
lines = [r"\begin{table*}[!t]", r"\caption{Simulated red-trigger misses under the configured observer model.}",
         r"\label{tab:triggers}\centering\small",
         r"\begin{tabular}{lrrrr}", r"\toprule",
         r"Illuminant & Assumed error probability & Misses / trials & Simulated miss rate & Wilson 95\% interval " + END,
         r"\midrule"]
for lid in ("L1", "L2", "L3"):
    r = next(x for x in rates if x["illumination_id"] == lid)
    interval = f"[{100*float(r['error_rate_ci95_low']):.3f}, {100*float(r['error_rate_ci95_high']):.3f}]\\%"
    lines.append(f"{light_names[lid]} & {100*float(r['assumed_error_probability']):.4f}\\% & {r['simulated_missed_donation_count']} / {r['trials']} & {100*float(r['simulated_missed_donation_rate']):.2f}\\% & {interval} " + END)
lines += [r"\bottomrule", r"\end{tabular}",
          r"\par\vspace{3pt}\footnotesize Intervals quantify binomial Monte Carlo variation under the assumed synthetic observer, not human-population uncertainty.",
          r"\end{table*}"]
put("trigger_table.tex", lines)

# Donation simulation for the D65 scenario.
don = read("donation_simulation.csv")
metrics = ("units_saved", "expired_stock", "missed_donation_triggers",
           "false_donation_triggers", "waste_rate")
lookup = {(r["illumination_id"], r["recognition"], int(r["capacity_per_day"]), r["metric"]): r for r in don}
lines = [r"\begin{table*}[!t]", r"\caption{Near-expiry Monte Carlo outcomes under D65 (500 replicates per scenario).}",
         r"\label{tab:donation}\centering\scriptsize",
         r"\begin{tabular}{llrrrrr}", r"\toprule",
         r"Recognition & Capacity/day & Saved units, mean [2.5th, 97.5th pct.] & Expired, mean & Missed triggers, mean & False triggers, mean & Waste rate " + END,
         r"\midrule"]
for rec, rec_label in (("perfect", "Perfect"), ("simulated_errors", "Simulated errors")):
    for cap in (10, 25, 50):
        saved = lookup[("L1", rec, cap, "units_saved")]
        expired = lookup[("L1", rec, cap, "expired_stock")]
        missed = lookup[("L1", rec, cap, "missed_donation_triggers")]
        false = lookup[("L1", rec, cap, "false_donation_triggers")]
        waste = lookup[("L1", rec, cap, "waste_rate")]
        s = f"{float(saved['mean']):.1f} [{float(saved['mc_ci95_low']):.1f}, {float(saved['mc_ci95_high']):.1f}]"
        lines.append(f"{rec_label} & {cap} & {s} & {float(expired['mean']):.1f} & {float(missed['mean']):.1f} & {float(false['mean']):.1f} & {float(waste['mean']):.4f} " + END)
lines += [r"\bottomrule", r"\end{tabular}",
          r"\par\vspace{3pt}\footnotesize Saved-unit intervals are the 2.5th and 97.5th percentiles across 500 replicates; outcomes are modeled units, not observed stock.",
          r"\end{table*}"]
put("donation_table.tex", lines)

# Sustainability sensitivity, L1 / simulated recognition errors / 25 per day.
sust = read("sustainability_analysis.csv")
selected = [r for r in sust if r["illumination_id"] == "L1" and r["recognition"] == "simulated_errors"
            and int(r["capacity_per_day"]) == 25]
lines = [r"\begin{table}[!t]", r"\caption{Illustrative sustainability sensitivity for the L1, capacity-25 simulated-errors case.}",
         r"\label{tab:sustainability}\centering\footnotesize",
         r"\begin{tabular}{lrr}", r"\toprule",
         r"Factor scenario & kg CO$_2$e/kg & Modeled kg CO$_2$e " + END, r"\midrule"]
for scenario in ("low_impact", "central", "high_impact"):
    r = next(x for x in selected if x["scenario"] == scenario)
    label = {"low_impact":"Low", "central":"Central", "high_impact":"High"}[scenario]
    lines.append(f"{label} & {float(r['emissions_factor_kgco2e_per_kg']):.1f} & {float(r['modeled_avoided_emissions_kgco2e']):.3f} " + END)
lines += [r"\bottomrule", r"\end{tabular}",
          r"\par\vspace{3pt}\footnotesize Factors are illustrative assumptions, not sourced product emission factors.",
          r"\end{table}"]
put("sustainability_table.tex", lines)
print("Generated tables from final CSVs:", ", ".join(p.name for p in sorted(TABLES.glob("*.tex"))))

