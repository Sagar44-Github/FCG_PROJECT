#!/usr/bin/env python3
"""Regenerate clearer manuscript plots directly from the copied final CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = ROOT / "data" / "results" / "CSV"
FIG_DIR = ROOT / "figures"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def donation_comparison() -> None:
    rows = load_rows(CSV_DIR / "donation_simulation.csv")
    labels = (("L1", "D65"), ("L2", "Neutral LED"), ("L3", "Warm LED"))
    metrics = (("units_saved", "Modeled units saved"),
               ("expired_stock", "Modeled expired stock"))
    recognition = (("perfect", "Perfect recognition", "#228A78"),
                   ("simulated_errors", "Synthetic recognition errors", "#D26B4A"))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharex=True)
    x = np.arange(len(labels), dtype=float)
    width = 0.32
    for ax, (metric, title) in zip(axes, metrics):
        subset = [r for r in rows if r["illumination_id"] in {x[0] for x in labels}
                  and r["recognition"] in {x[0] for x in recognition}
                  and int(r["capacity_per_day"]) == 25 and r["metric"] == metric]
        for index, (key, label, color) in enumerate(recognition):
            ys, lower, upper = [], [], []
            for light, _ in labels:
                row = next(r for r in subset if r["illumination_id"] == light
                           and r["recognition"] == key)
                mean = float(row["mean"])
                ys.append(mean)
                lower.append(mean - float(row["mc_ci95_low"]))
                upper.append(float(row["mc_ci95_high"]) - mean)
            xpos = x + (index - 0.5) * width
            ax.bar(xpos, ys, width=width, color=color, label=label,
                   yerr=np.asarray([lower, upper]), capsize=3,
                   error_kw={"elinewidth": 0.9, "ecolor": "#283747"})
        ax.set_title(title)
        ax.set_xticks(x, [name for _, name in labels])
        ax.set_ylabel("Units per 30-day simulated period")
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=0.22)
        ax.set_axisbelow(True)
    axes[0].legend(frameon=False, loc="upper right", fontsize=8)
    fig.suptitle("Near-expiry inventory outcomes · donation capacity 25 units/day")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "near_expiry_simulation_comparison_paper.png",
                dpi=240, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    donation_comparison()
    print("Wrote paper plot from final donation_simulation.csv")
