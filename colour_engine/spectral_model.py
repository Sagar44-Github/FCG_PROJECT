"""Spectral illuminants and a synthetic, explicitly non-measured print model."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import csv
import numpy as np
from scipy.optimize import minimize, lsq_linear
from scipy.sparse import diags, eye, vstack
from .config import CONFIG, ROOT
from .conversion import D65_WHITE, hex_to_srgb, srgb_to_xyz, xyz_to_lab

WAVELENGTHS = np.arange(380.0, 781.0, 1.0)
DATA_DIR = ROOT / "data"

def _read_two_columns(path: Path) -> np.ndarray:
    return np.loadtxt(path, delimiter=",")

@lru_cache(maxsize=1)
def cie_1931_2deg() -> np.ndarray:
    raw = _read_two_columns(DATA_DIR / "CIE_xyz_1931_2deg.csv")
    return np.stack([np.interp(WAVELENGTHS, raw[:, 0], raw[:, i]) for i in (1, 2, 3)], axis=1)

@lru_cache(maxsize=1)
def d65_spd() -> np.ndarray:
    raw = _read_two_columns(DATA_DIR / "CIE_std_illum_D65.csv")
    return np.interp(WAVELENGTHS, raw[:, 0], raw[:, 1])

def _planck_spd(cct: float) -> np.ndarray:
    lam = WAVELENGTHS * 1e-9
    c2 = 1.438776877e-2
    return 1 / (lam**5 * np.expm1(c2 / (lam * cct)))

def _integrate_xyz(spd: np.ndarray, reflectance: np.ndarray | None = None) -> np.ndarray:
    cmf = cie_1931_2deg()
    r = np.ones_like(spd) if reflectance is None else np.asarray(reflectance)
    k = 100 / np.sum(spd * cmf[:, 1])
    return k * np.sum((spd * r)[:, None] * cmf, axis=0)

def _led_spd(cct: float) -> np.ndarray:
    # Generic phosphor-converted LED approximation: blue pump + broad green/yellow
    # phosphor + red tail. Amplitudes fit the Planckian-locus xy at the target CCT.
    basis = np.stack([
        np.exp(-0.5*((WAVELENGTHS-450)/17)**2),
        np.exp(-0.5*((WAVELENGTHS-555)/72)**2),
        np.exp(-0.5*((WAVELENGTHS-615)/48)**2),
    ], axis=1)
    cmf = cie_1931_2deg()
    target_spd = _planck_spd(cct)
    target = np.sum(target_spd[:, None] * cmf, axis=0)
    tx, ty = target[0] / target.sum(), target[1] / target.sum()
    # Keep a common scale across the basis spectra here. Normalizing each
    # Gaussian separately to Y=100 would change the physical mixing weights.
    xyz_basis = np.stack([np.sum(basis[:, i, None] * cmf, axis=0) for i in range(3)], axis=1)
    def objective(weights):
        xyz = xyz_basis @ weights
        x, y = xyz[0]/xyz.sum(), xyz[1]/xyz.sum()
        return (x-tx)**2 + (y-ty)**2
    fit = minimize(objective, np.array([0.18, 0.62, 0.20]), method="SLSQP",
                   bounds=[(0.001, 0.998)]*3, constraints=[{"type":"eq", "fun":lambda w: w.sum()-1}],
                   options={"ftol":1e-14, "maxiter":300})
    spd = basis @ fit.x
    return spd * (100 / np.interp(560, WAVELENGTHS, spd))

@lru_cache(maxsize=4)
def illuminant_spd(illumination_id: str) -> np.ndarray:
    cfg = CONFIG["illuminations"].get(illumination_id)
    if cfg is None:
        raise ValueError(f"Unknown illumination_id: {illumination_id}")
    if cfg["kind"] == "cie_d65":
        return d65_spd().copy()
    return _led_spd(float(cfg["cct_kelvin"]))

def illuminant_white_xyz(illumination_id: str) -> np.ndarray:
    return _integrate_xyz(illuminant_spd(illumination_id)) / 100

def spectrum_to_xyz(reflectance: np.ndarray, illumination_id: str) -> np.ndarray:
    return _integrate_xyz(illuminant_spd(illumination_id), reflectance) / 100

def _smooth_spectral_reconstruction(target_xyz: np.ndarray) -> np.ndarray:
    # Smooth bounded reflectance reconstruction constrained to match D65 XYZ.
    # The inverse is non-unique; regularization selects one smooth metamer.
    cmf = cie_1931_2deg()
    light = d65_spd()
    M = ((light[:, None] * cmf).T / np.sum(light * cmf[:, 1]))
    n = len(WAVELENGTHS)
    second = diags([np.ones(n-2), -2*np.ones(n-2), np.ones(n-2)], [0, 1, 2], shape=(n-2, n), format="csr")
    A = vstack([25*M, 0.8*second, 0.015*eye(n, format="csr")], format="csr")
    b = np.concatenate([25*target_xyz, np.zeros(n-2), 0.015*np.full(n, 0.72)])
    result = lsq_linear(A, b, bounds=(0.005, 0.995), method="trf", lsq_solver="lsmr", tol=2e-8, max_iter=100)
    return result.x

@lru_cache(maxsize=8)
def digital_reflectance(hex_colour: str) -> np.ndarray:
    target = srgb_to_xyz(hex_to_srgb(hex_colour))
    return _smooth_spectral_reconstruction(target)

def virtual_print_reflectance(hex_colour: str) -> np.ndarray:
    """Apply configured synthetic absorbance density and substrate assumptions."""
    p = CONFIG["virtual_print"]
    reflectance = digital_reflectance(hex_colour)
    absorbance = -np.log(np.clip(reflectance, p["reflectance_floor"], 1.0))
    blue_bias = p["blue_absorbance_bias"] * np.exp(-0.5*((WAVELENGTHS-p["blue_bias_center_nm"])/p["blue_bias_sigma_nm"])**2)
    return np.clip(p["substrate_reflectance"] * np.exp(-p["ink_density_gain"]*absorbance - blue_bias), 0.005, 0.995)

def spectral_info(reflectance: np.ndarray, illumination_id: str) -> dict[str, float]:
    xyz = spectrum_to_xyz(reflectance, illumination_id)
    white = illuminant_white_xyz(illumination_id)
    lab = xyz_to_lab(xyz, white)
    total = xyz.sum()
    return {"x": float(xyz[0]/total), "y": float(xyz[1]/total), "X": float(xyz[0]), "Y": float(xyz[1]), "Z": float(xyz[2]),
            "L": float(lab[0]), "a": float(lab[1]), "b": float(lab[2])}

