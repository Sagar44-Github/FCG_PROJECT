"""Monte Carlo near-expiry inventory and capacity model; no Nigam equation is claimed."""
from __future__ import annotations
import numpy as np
from colour_engine.config import CONFIG
from .observer_model import ACTION_ORDER, confusion_matrix_for

def simulate_inventory(capacity_per_day: int, delta_e: float | dict[str,float], recognition: str, seed: int,
                       days: int | None = None, mean_arrivals: float | None = None,
                       observer_parameters: dict | None = None) -> dict[str, float | int | str]:
    p = CONFIG["donation"]
    days = int(p["simulation_days"] if days is None else days)
    mean_arrivals = float(p["mean_near_expiry_arrivals_per_day"] if mean_arrivals is None else mean_arrivals)
    if capacity_per_day < 0 or days < 1 or mean_arrivals < 0:
        raise ValueError("capacity and arrivals must be nonnegative and days must be positive")
    if recognition not in {"perfect", "simulated_errors"}:
        raise ValueError("recognition must be 'perfect' or 'simulated_errors'")
    if isinstance(delta_e,dict):
        if set(delta_e)!=set(ACTION_ORDER) or any(not np.isfinite(v) or v<0 for v in delta_e.values()):
            raise ValueError(f"delta_e mapping must contain finite nonnegative values for {ACTION_ORDER}")
        matrices=[confusion_matrix_for(float(delta_e[action]),observer_parameters) for action in ACTION_ORDER]
    else:
        if not np.isfinite(delta_e) or delta_e<0:raise ValueError("delta_e must be finite and nonnegative")
        matrix=confusion_matrix_for(float(delta_e),observer_parameters)
        matrices=[matrix]*4
    rng = np.random.default_rng(seed)
    red_fraction = float(p["red_fraction"])
    other_fraction = (1-red_fraction)/3
    category_probabilities = np.array([other_fraction, other_fraction, other_fraction, red_fraction])
    totals = {k: 0 for k in ["arrivals", "true_red_items", "donation_triggers", "missed_donation_triggers",
                              "false_donation_triggers", "donated_units", "true_donated_units", "false_donated_units", "capacity_overflow_units",
                              "discount_recovery_candidates", "discount_recovered_units", "expired_stock",
                              "correctly_classified_items", "classification_errors"]}
    for _ in range(days):
        n = int(rng.poisson(mean_arrivals))
        if not n:
            continue
        if recognition == "perfect":
            actual_counts = rng.multinomial(n, category_probabilities)
            predicted_counts = actual_counts
            true_red = int(actual_counts[3])
            red_donation_candidates = true_red
            false_triggers = 0
            correctly_classified=int(n)
        else:
            actual_counts = rng.multinomial(n, category_probabilities)
            by_true_action = np.stack([rng.multinomial(int(actual_counts[a]), matrices[a][a]) for a in range(4)])
            predicted_counts = by_true_action.sum(axis=0)
            true_red = int(actual_counts[3])
            red_donation_candidates = int(by_true_action[3,3])
            false_triggers = int(by_true_action[:3,3].sum())
            correctly_classified=int(np.trace(by_true_action))
        donation_n = int(predicted_counts[3])
        donated = min(donation_n, capacity_per_day)
        overflow = donation_n - donated
        # Capacity overflow is offered as a discount; accepted discount candidates
        # recover stock independently under the configured scenario probability.
        discount_candidates = int(predicted_counts[2]) + overflow
        recovered = int(rng.binomial(discount_candidates, float(p["discount_recovery_probability"])))
        # Donation triggers are pooled under a daily capacity; non-red false
        # triggers can use part of the capacity intended for red items.
        missed = true_red-red_donation_candidates
        false_donated = int(rng.hypergeometric(false_triggers, red_donation_candidates, donated)) if donated else 0
        true_donated = donated-false_donated
        expired = max(0, n - donated - recovered)
        totals["arrivals"] += n
        totals["correctly_classified_items"] += correctly_classified
        totals["classification_errors"] += n-correctly_classified
        totals["true_red_items"] += true_red
        totals["donation_triggers"] += donation_n
        totals["missed_donation_triggers"] += missed
        totals["false_donation_triggers"] += false_triggers
        totals["donated_units"] += donated
        totals["true_donated_units"] += true_donated
        totals["false_donated_units"] += false_donated
        totals["capacity_overflow_units"] += overflow
        totals["discount_recovery_candidates"] += discount_candidates
        totals["discount_recovered_units"] += recovered
        totals["expired_stock"] += expired
    saved = totals["true_donated_units"] + totals["discount_recovered_units"]
    kg_saved = saved * float(p["average_product_kg"])
    return {
        **totals,
        "recognition": recognition,
        "capacity_per_day": int(capacity_per_day),
        "days": days,
        "mean_arrivals_per_day": mean_arrivals,
        "recognition_accuracy": totals["correctly_classified_items"] / totals["arrivals"] if totals["arrivals"] else 0.0,
        "units_saved": saved,
        "waste_rate": totals["expired_stock"] / totals["arrivals"] if totals["arrivals"] else 0.0,
        "missed_donation_rate": totals["missed_donation_triggers"] / totals["true_red_items"] if totals["true_red_items"] else 0.0,
        "modeled_food_mass_saved_kg": kg_saved,
        "modeled_avoided_emissions_kgco2e": kg_saved * float(p["avoided_emissions_kgco2e_per_kg"]),
    }

