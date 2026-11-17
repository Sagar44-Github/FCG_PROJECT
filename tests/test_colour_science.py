from pathlib import Path
import numpy as np
import pandas as pd
import colour
from colour_engine.conversion import (D65_WHITE, hex_to_srgb, linear_to_srgb,
    srgb_to_linear, srgb_to_xyz, xyz_to_lab, xyz_to_xy)
from colour_engine.delta_e import delta_e_2000
from colour_engine.adaptation import bradford_adapt_xyz
from colour_engine.config import ROOT

def test_srgb_round_trip_and_white():
    rgb=np.array([0.18,0.5,0.9])
    assert np.allclose(linear_to_srgb(srgb_to_linear(rgb)),rgb,atol=1e-12)
    assert np.allclose(srgb_to_xyz([1,1,1]),D65_WHITE,atol=5e-5)

def test_xyz_lab_and_chromaticity_known_white():
    lab=xyz_to_lab(D65_WHITE,D65_WHITE)
    assert np.allclose(lab,[100,0,0],atol=1e-10)
    x,y=xyz_to_xy(D65_WHITE)
    assert abs(x-0.3127)<1e-4 and abs(y-0.3290)<1e-4

def test_bradford_adaptation_maps_source_white_to_destination_white():
    source=np.array([1.0985,1.0,.3558]);destination=D65_WHITE
    assert np.allclose(bradford_adapt_xyz(source,source,destination),destination,atol=1e-10)

def test_ciede2000_published_reference_cases_and_independent_library():
    cases=pd.read_csv(ROOT/"data"/"ciede2000_reference_cases.csv")
    for row in cases.itertuples(index=False):
        lab1=[row.L1,row.a1,row.b1]; lab2=[row.L2,row.a2,row.b2]
        result=delta_e_2000(lab1,lab2)["delta_e00"]
        assert abs(result-row.expected_delta_e00)<5e-5
        independent=float(colour.delta_E(np.array(lab1),np.array(lab2),method="CIE 2000"))
        assert abs(result-independent)<1e-8
        assert "delta_l_star" in delta_e_2000(lab1,lab2)
        assert "delta_c_prime" in delta_e_2000(lab1,lab2)
        assert "delta_h_prime" in delta_e_2000(lab1,lab2)

def test_ciede2000_symmetry_and_zero():
    a=[28.1,12.4,-8.2];b=[29.7,10.3,-6.1]
    assert delta_e_2000(a,a)["delta_e00"]==0
    assert np.isclose(delta_e_2000(a,b)["delta_e00"],delta_e_2000(b,a)["delta_e00"],atol=1e-12)

def test_hex_rejects_invalid_input():
    import pytest
    with pytest.raises(ValueError):hex_to_srgb("#12XYZ0")

def test_measurement_evidence_contains_native_xyz_for_all_twelve_conditions():
    from colour_engine.pipeline import build_colour_evidence
    measurements, _ = build_colour_evidence()
    assert len(measurements) == 12
    for prefix in ("digital", "print"):
        axes = [f"{prefix}_{axis}" for axis in ("X", "Y", "Z")]
        assert all(axis in measurements for axis in axes)
        assert np.isfinite(measurements[axes].to_numpy()).all()
