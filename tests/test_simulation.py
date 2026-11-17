import numpy as np
import pytest
from simulation.observer_model import ACTION_ORDER, confusion_matrix_for, error_probability
from simulation.donation_model import simulate_inventory
from simulation.sensitivity_analysis import run_capacity_sensitivity
from colour_engine.config import CONFIG

def test_error_probability_is_bounded_and_monotonic():
    values=[error_probability(d) for d in [0,2,5,10,20,100]]
    assert values==sorted(values)
    assert all(0<=p<=1 for p in values)

def test_confusion_matrix_rows_are_probabilities():
    matrix=confusion_matrix_for(6.5)
    assert matrix.shape==(4,4)
    assert np.allclose(matrix.sum(axis=1),1)
    assert np.all(np.diag(matrix)>0.5)

def test_inventory_is_seed_reproducible_and_capacity_changes_flow():
    args=(4.0,"simulated_errors",22026)
    low=simulate_inventory(0,*args,days=10,mean_arrivals=45)
    again=simulate_inventory(0,*args,days=10,mean_arrivals=45)
    higher=simulate_inventory(50,*args,days=10,mean_arrivals=45)
    assert low==again
    assert higher["donated_units"]>=low["donated_units"]
    assert higher["capacity_overflow_units"]<=low["capacity_overflow_units"]
    assert low["arrivals"]==low["donated_units"]+low["discount_recovered_units"]+low["expired_stock"]

def test_inventory_accepts_color_specific_delta_e_and_rejects_incomplete_map():
    by_action={"fresh":1.0,"watch":2.0,"discount":4.0,"donate":8.0}
    a=simulate_inventory(25,by_action,"simulated_errors",42,days=3,mean_arrivals=12)
    b=simulate_inventory(25,by_action,"simulated_errors",42,days=3,mean_arrivals=12)
    assert a==b
    with pytest.raises(ValueError):simulate_inventory(25,{"donate":8.0},"simulated_errors",42)

def test_inventory_reports_applied_recognition_accuracy():
    perfect=simulate_inventory(25,2.0,"perfect",42,days=3,mean_arrivals=30)
    errors=simulate_inventory(25,2.0,"simulated_errors",42,days=3,mean_arrivals=30)
    assert perfect["recognition_accuracy"]==1.0
    assert perfect["classification_errors"]==0
    assert errors["recognition_accuracy"]<1.0
    assert errors["correctly_classified_items"]+errors["classification_errors"]==errors["arrivals"]

def test_invalid_simulation_inputs_rejected():
    with pytest.raises(ValueError):simulate_inventory(-1,1,"perfect",1)
    with pytest.raises(ValueError):simulate_inventory(2,1,"invented",1)
    with pytest.raises(ValueError):simulate_inventory(2,1,"perfect",1,days=0)

def test_capacity_sensitivity_includes_every_scenario():
    frame=run_capacity_sensitivity(3.0,"L1",replicates=1)
    assert set(frame.capacity_per_day)=={10,25,50}
    assert set(frame.recognition)=={"perfect","simulated_errors"}

