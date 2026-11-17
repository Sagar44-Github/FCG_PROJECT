import hashlib
import numpy as np
import pytest
from colour_engine.config import CONFIG, ROOT
from colour_engine.spectral_model import (WAVELENGTHS, _read_two_columns, d65_spd,
    digital_reflectance, illuminant_spd, illuminant_white_xyz,
    spectrum_to_xyz, virtual_print_reflectance, _integrate_xyz, _planck_spd)

def test_official_cie_datasets_match_recorded_checksums():
    assert hashlib.md5((ROOT/"data"/"CIE_std_illum_D65.csv").read_bytes()).hexdigest()=="03d4eb9b837c60671627c946fb534deb"
    assert hashlib.md5((ROOT/"data"/"CIE_xyz_1931_2deg.csv").read_bytes()).hexdigest()=="17cca777db64b17170f06f67ce9d3ab7"

def test_d65_is_official_spd_and_white_is_expected():
    assert WAVELENGTHS[0]==380 and WAVELENGTHS[-1]==780 and len(WAVELENGTHS)==401
    assert len(d65_spd())==401
    white=illuminant_white_xyz("L1"); total=white.sum()
    assert abs(white[0]/total-0.3127)<2e-4
    assert abs(white[1]/total-0.3290)<2e-4

def test_led_approximations_are_separate_from_d65_and_repeatable():
    assert not np.allclose(illuminant_spd("L1"),illuminant_spd("L2"))
    assert not np.allclose(illuminant_spd("L2"),illuminant_spd("L3"))
    assert np.array_equal(illuminant_spd("L2"),illuminant_spd("L2"))

def test_led_approximation_hits_configured_planckian_chromaticity_targets():
    for illum_id in ["L2","L3"]:
        target=_integrate_xyz(_planck_spd(CONFIG["illuminations"][illum_id]["cct_kelvin"]))
        measured=illuminant_white_xyz(illum_id)
        assert abs(target[0]/target.sum()-measured[0]/measured.sum())<1e-5
        assert abs(target[1]/target.sum()-measured[1]/measured.sum())<1e-5

def test_virtual_print_is_bounded_and_differs_from_digital():
    for colour in CONFIG["colours"].values():
        source=digital_reflectance(colour["hex"]); printed=virtual_print_reflectance(colour["hex"])
        assert np.all((printed>=0.005)&(printed<=0.995))
        assert not np.allclose(source,printed)

def test_invalid_dataset_shape_is_rejected(tmp_path):
    path=tmp_path/"broken.csv";path.write_text("not,a,numeric,dataset\n",encoding="utf-8")
    with pytest.raises(ValueError):_read_two_columns(path)
