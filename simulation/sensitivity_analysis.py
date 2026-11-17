"""Monte Carlo aggregation helpers and reproducible seed mapping."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from .donation_model import simulate_inventory
from colour_engine.config import CONFIG

def run_capacity_sensitivity(delta_e: float | dict[str,float], illumination_id: str, replicates: int | None = None) -> pd.DataFrame:
    cfg = CONFIG
    p = cfg["donation"]
    reps = int(replicates or p["replicates"])
    seed0 = int(cfg["project"]["random_seed"])
    rows = []
    illumination_index = list(cfg["illuminations"]).index(illumination_id)
    for recognition_i, recognition in enumerate(["perfect", "simulated_errors"]):
        for capacity_i, capacity in enumerate(p["donation_capacities_per_day"]):
            outcomes = [simulate_inventory(int(capacity), delta_e, recognition,
                         seed0 + illumination_index*1_000_000 + recognition_i*100_000 + r,
                         p["simulation_days"], p["mean_near_expiry_arrivals_per_day"]) for r in range(reps)]
            frame = pd.DataFrame(outcomes)
            for metric in ["units_saved", "expired_stock", "missed_donation_triggers", "false_donation_triggers",
                           "donated_units", "true_donated_units", "false_donated_units", "discount_recovered_units",
                           "waste_rate", "recognition_accuracy", "classification_errors", "modeled_avoided_emissions_kgco2e"]:
                vals = frame[metric].astype(float)
                rows.append({"illumination_id": illumination_id, "recognition": recognition,
                             "capacity_per_day": int(capacity), "metric": metric,
                             "delta_e_by_action":json.dumps(delta_e,sort_keys=True) if isinstance(delta_e,dict) else json.dumps({"all_actions":float(delta_e)}),
                             "mean": float(vals.mean()), "sd": float(vals.std(ddof=1)),
                             "mc_ci95_low": float(vals.quantile(.025)), "mc_ci95_high": float(vals.quantile(.975)),
                             "replicates": reps, "seed_base": seed0})
    return pd.DataFrame(rows)

