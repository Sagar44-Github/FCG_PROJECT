"""CIEDE2000 implementation with Sharma-Wu-Dalal diagnostic components."""
from __future__ import annotations
import numpy as np

def delta_e_2000(lab1, lab2, k_l: float = 1.0, k_c: float = 1.0, k_h: float = 1.0) -> dict[str, float]:
    L1, a1, b1 = map(float, lab1)
    L2, a2, b2 = map(float, lab2)
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    cbar = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(cbar**7 / (cbar**7 + 25**7))) if cbar else 0.5
    ap1, ap2 = (1 + G) * a1, (1 + G) * a2
    cp1, cp2 = np.hypot(ap1, b1), np.hypot(ap2, b2)
    hp1 = np.degrees(np.arctan2(b1, ap1)) % 360 if cp1 else 0.0
    hp2 = np.degrees(np.arctan2(b2, ap2)) % 360 if cp2 else 0.0
    dL = L2 - L1
    dC = cp2 - cp1
    if cp1 * cp2 == 0:
        dh_angle = 0.0
    else:
        dh_angle = hp2 - hp1
        if dh_angle > 180:
            dh_angle -= 360
        elif dh_angle < -180:
            dh_angle += 360
    dH = 2 * np.sqrt(cp1 * cp2) * np.sin(np.radians(dh_angle / 2))
    Lbar = (L1 + L2) / 2
    cpbar = (cp1 + cp2) / 2
    if cp1 * cp2 == 0:
        hpbar = hp1 + hp2
    elif abs(hp1 - hp2) <= 180:
        hpbar = (hp1 + hp2) / 2
    elif hp1 + hp2 < 360:
        hpbar = (hp1 + hp2 + 360) / 2
    else:
        hpbar = (hp1 + hp2 - 360) / 2
    T = (1 - 0.17*np.cos(np.radians(hpbar - 30)) + 0.24*np.cos(np.radians(2*hpbar))
         + 0.32*np.cos(np.radians(3*hpbar + 6)) - 0.20*np.cos(np.radians(4*hpbar - 63)))
    dtheta = 30 * np.exp(-((hpbar - 275) / 25)**2)
    rc = 2 * np.sqrt(cpbar**7 / (cpbar**7 + 25**7)) if cpbar else 0.0
    sl = 1 + 0.015 * (Lbar - 50)**2 / np.sqrt(20 + (Lbar - 50)**2)
    sc = 1 + 0.045 * cpbar
    sh = 1 + 0.015 * cpbar * T
    rt = -np.sin(np.radians(2 * dtheta)) * rc
    term_l, term_c, term_h = dL / (k_l * sl), dC / (k_c * sc), dH / (k_h * sh)
    de = np.sqrt(max(0.0, term_l**2 + term_c**2 + term_h**2 + rt * term_c * term_h))
    return {"delta_e00": float(de), "delta_l": float(dL), "delta_c": float(dC), "delta_h": float(dH),
            "delta_l_star": float(dL), "delta_c_star": float(C2-C1),
            "delta_c_prime": float(dC), "delta_h_prime": float(dH)}
