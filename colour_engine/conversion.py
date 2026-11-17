"""sRGB, XYZ, CIELAB and chromaticity conversions (D65, CIE 1931 2°)."""
from __future__ import annotations
import numpy as np

SRGB_TO_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041],
])
XYZ_TO_SRGB = np.linalg.inv(SRGB_TO_XYZ)
D65_WHITE = np.array([0.95047, 1.0, 1.08883])

def srgb_to_linear(rgb: np.ndarray | list[float]) -> np.ndarray:
    v = np.asarray(rgb, dtype=float)
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)

def linear_to_srgb(rgb: np.ndarray | list[float]) -> np.ndarray:
    v = np.asarray(rgb, dtype=float)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * np.maximum(v, 0) ** (1 / 2.4) - 0.055)

def hex_to_srgb(value: str) -> np.ndarray:
    value = value.strip().lstrip("#")
    if len(value) != 6 or any(c not in "0123456789abcdefABCDEF" for c in value):
        raise ValueError("Expected a six-digit sRGB hex colour, such as #D62828")
    return np.array([int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=float)

def srgb_to_xyz(rgb: np.ndarray | list[float]) -> np.ndarray:
    return SRGB_TO_XYZ @ srgb_to_linear(rgb)

def xyz_to_lab(xyz: np.ndarray | list[float], white: np.ndarray | list[float] = D65_WHITE) -> np.ndarray:
    xyz = np.asarray(xyz, dtype=float)
    white = np.asarray(white, dtype=float)
    delta = 6 / 29
    q = xyz / white
    f = np.where(q > delta ** 3, np.cbrt(q), q / (3 * delta**2) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])

def lab_to_xyz(lab: np.ndarray | list[float], white: np.ndarray | list[float] = D65_WHITE) -> np.ndarray:
    L, a, b = np.asarray(lab, dtype=float)
    fy, fx, fz = (L + 16) / 116, (L + 16) / 116 + a / 500, (L + 16) / 116 - b / 200
    delta = 6 / 29
    f = np.array([fx, fy, fz])
    q = np.where(f > delta, f**3, 3 * delta**2 * (f - 4 / 29))
    return q * np.asarray(white, dtype=float)

def xyz_to_xy(xyz: np.ndarray | list[float]) -> tuple[float, float]:
    x, y, z = np.asarray(xyz, dtype=float)
    total = x + y + z
    if total <= 0:
        return float("nan"), float("nan")
    return float(x / total), float(y / total)
