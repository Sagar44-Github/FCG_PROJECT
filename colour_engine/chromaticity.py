"""CIE 1931 xy chromaticity, dominant/complementary wavelength and purity."""
from __future__ import annotations
import numpy as np
from .spectral_model import WAVELENGTHS, cie_1931_2deg

def spectral_locus_xy() -> np.ndarray:
    cmf = cie_1931_2deg()
    sums = cmf.sum(axis=1)
    locus = cmf[:, :2] / sums[:, None]
    return np.vstack([locus, locus[0]])

def dominant_wavelength(xy: tuple[float, float], white_xy: tuple[float, float]) -> dict[str, float | str]:
    p = np.asarray(xy, dtype=float)
    w = np.asarray(white_xy, dtype=float)
    v = p-w
    if np.linalg.norm(v) < 1e-12:
        return {"dominant_wavelength_nm": float("nan"), "excitation_purity": 0.0, "wavelength_type": "neutral"}
    locus = spectral_locus_xy()
    best = None
    # Intersect the white-to-sample ray (or its extension for spectral locus).
    # q = w + t*v, with t >= 1; each locus edge is p0 + u*(p1-p0).
    for i in range(len(locus)-1):
        p0, edge = locus[i], locus[i+1]-locus[i]
        mat = np.column_stack([v, -edge])
        if abs(np.linalg.det(mat)) < 1e-12:
            continue
        t, u = np.linalg.solve(mat, p0-w)
        if t >= 1-1e-8 and -1e-8 <= u <= 1+1e-8 and (best is None or t < best[0]):
            best = (t, i + float(np.clip(u, 0, 1)))
    kind = "dominant"
    if best is None:
        # For purples, the ray points away from the spectral locus: report the
        # complementary wavelength at the opposite intersection.
        v = -v
        best = None
        for i in range(len(locus)-1):
            p0, edge = locus[i], locus[i+1]-locus[i]
            mat = np.column_stack([v, -edge])
            if abs(np.linalg.det(mat)) < 1e-12:
                continue
            t, u = np.linalg.solve(mat, p0-w)
            if t >= 1-1e-8 and -1e-8 <= u <= 1+1e-8 and (best is None or t < best[0]):
                best = (t, i + float(np.clip(u, 0, 1)))
        kind = "complementary"
    if best is None:
        return {"dominant_wavelength_nm": float("nan"), "excitation_purity": 0.0, "wavelength_type": "unresolved"}
    t, idx = best
    wavelength = float(np.interp(idx, np.arange(len(WAVELENGTHS)+1), np.append(WAVELENGTHS, WAVELENGTHS[-1])))
    return {"dominant_wavelength_nm": wavelength, "excitation_purity": float(1/t), "wavelength_type": kind}
