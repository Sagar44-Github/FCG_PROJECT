"""Synthetic, uncalibrated observer response model driven by calculated ΔE00."""
from __future__ import annotations
import numpy as np
from colour_engine.config import CONFIG

ACTION_ORDER = ["fresh", "watch", "discount", "donate"]

def error_probability(delta_e: float, parameters: dict | None = None) -> float:
    p = parameters or CONFIG["observer"]
    logistic = 1 / (1 + np.exp(-(float(delta_e) - p["delta_e_midpoint"]) / p["delta_e_scale"]))
    return float(np.clip(p["base_error_probability"] + p["maximum_additional_error_probability"]*logistic, 0, 0.95))

def confusion_matrix_for(delta_e: float, parameters: dict | None = None) -> np.ndarray:
    """Rows are correct class; columns are perceived action in ACTION_ORDER."""
    p_error = error_probability(delta_e, parameters)
    weights = (parameters or CONFIG["observer"])["confusion_weights"]
    matrix = np.zeros((4, 4), dtype=float)
    for actual in range(4):
        matrix[actual, actual] = 1 - p_error
        alternatives = [j for j in range(4) if j != actual]
        raw = np.array([weights["adjacent"] if abs(j-actual) == 1 else weights["nonadjacent"] for j in alternatives], dtype=float)
        raw /= raw.sum()
        matrix[actual, alternatives] = p_error * raw
    return matrix

def simulate_classifications(delta_e: float, actual_actions: list[str], seed: int) -> tuple[np.ndarray, np.ndarray]:
    matrix = confusion_matrix_for(delta_e)
    rng = np.random.default_rng(seed)
    actual_idx = np.array([ACTION_ORDER.index(x) for x in actual_actions], dtype=int)
    predicted = np.array([rng.choice(4, p=matrix[i]) for i in actual_idx], dtype=int)
    return actual_idx, predicted

