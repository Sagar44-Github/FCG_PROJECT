"""Bradford chromatic adaptation for cross-illuminant comparison to a common white."""
from __future__ import annotations
import numpy as np

BRADFORD=np.array([[0.8951,0.2664,-0.1614],[-0.7502,1.7135,0.0367],[0.0389,-0.0685,1.0296]])

def bradford_adapt_xyz(xyz, source_white, destination_white):
    """Adapt XYZ (any common scale) from source to destination reference white."""
    xyz=np.asarray(xyz,dtype=float); source=np.asarray(source_white,dtype=float); destination=np.asarray(destination_white,dtype=float)
    src_lms=BRADFORD@source; dst_lms=BRADFORD@destination
    if np.any(np.abs(src_lms)<1e-12):
        raise ValueError("source white is not suitable for Bradford adaptation")
    transform=np.linalg.inv(BRADFORD)@np.diag(dst_lms/src_lms)@BRADFORD
    return transform@xyz
