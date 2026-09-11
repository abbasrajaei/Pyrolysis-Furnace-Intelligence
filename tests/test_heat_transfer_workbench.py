from copy import deepcopy

import pytest

from pyrolysis_furnace_intelligence.combustion_workbench import (
    DEFAULT_CASE,
    rebalance_composition,
)
from pyrolysis_furnace_intelligence.heat_transfer_workbench import (
    CONVECTION_BANK_SHARES,
    DEFAULT_THERMAL_SETTINGS,
    evaluate_thermal,
    thermal_sweep,
)


def test_heat_balance_closes():
    result = evaluate_thermal(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS)
    energy = result["energy"]
    assert energy["balance_error_mw"] == pytest.approx(0.0, abs=1e-10)
    assert (
        energy["radiant_duty_mw"]
        + energy["convection_duty_mw"]
        + energy["stack_loss_mw"]
        + energy["other_loss_mw"]
    ) == pytest.approx(energy["fired_duty_mw"])


def test_hotter_stack_increases_loss_and_reduces_efficiency():
    low = deepcopy(DEFAULT_THERMAL_SETTINGS)
    high = deepcopy(DEFAULT_THERMAL_SETTINGS)
    low["stack_temperature_c"] = 130.0
    high["stack_temperature_c"] = 220.0
    a = evaluate_thermal(DEFAULT_CASE, low)
    b = evaluate_thermal(DEFAULT_CASE, high)
    assert b["energy"]["stack_loss_mw"] > a["energy"]["stack_loss_mw"]
    assert b["energy"]["overall_efficiency"] < a["energy"]["overall_efficiency"]
    assert b["energy"]["useful_duty_mw"] < a["energy"]["useful_duty_mw"]


def test_more_excess_air_increases_stack_loss_at_same_stack_temperature():
    low = deepcopy(DEFAULT_CASE)
    high = deepcopy(DEFAULT_CASE)
    low["excess_air"] = 0.05
    high["excess_air"] = 0.25
    a = evaluate_thermal(low, DEFAULT_THERMAL_SETTINGS)
    b = evaluate_thermal(high, DEFAULT_THERMAL_SETTINGS)
    assert b["flue"]["flow_kg_h"] > a["flue"]["flow_kg_h"]
    assert b["energy"]["stack_loss_mw"] > a["energy"]["stack_loss_mw"]
    assert b["energy"]["overall_efficiency"] < a["energy"]["overall_efficiency"]


def test_radiant_share_changes_heat_split_not_total_useful_heat():
    low = deepcopy(DEFAULT_THERMAL_SETTINGS)
    high = deepcopy(DEFAULT_THERMAL_SETTINGS)
    low["radiant_fraction"] = 0.40
    high["radiant_fraction"] = 0.50
    a = evaluate_thermal(DEFAULT_CASE, low)
    b = evaluate_thermal(DEFAULT_CASE, high)
    assert b["energy"]["radiant_duty_mw"] > a["energy"]["radiant_duty_mw"]
    assert b["energy"]["convection_duty_mw"] < a["energy"]["convection_duty_mw"]
    assert b["energy"]["useful_duty_mw"] == pytest.approx(a["energy"]["useful_duty_mw"])
    assert b["energy"]["overall_efficiency"] == pytest.approx(a["energy"]["overall_efficiency"])


def test_more_radiant_heat_raises_average_and_peak_flux():
    low = deepcopy(DEFAULT_THERMAL_SETTINGS)
    high = deepcopy(DEFAULT_THERMAL_SETTINGS)
    low["radiant_fraction"] = 0.40
    high["radiant_fraction"] = 0.50
    a = evaluate_thermal(DEFAULT_CASE, low)
    b = evaluate_thermal(DEFAULT_CASE, high)
    assert b["radiant"]["average_flux_kw_m2"] > a["radiant"]["average_flux_kw_m2"]
    assert b["radiant"]["peak_flux_kw_m2"] > a["radiant"]["peak_flux_kw_m2"]
    assert b["radiant"]["peak_flux_kw_m2"] > b["radiant"]["average_flux_kw_m2"]


def test_higher_feed_moves_fired_radiant_and_flux_up():
    low_case = deepcopy(DEFAULT_CASE)
    high_case = deepcopy(DEFAULT_CASE)
    low_case["feed_kg_s"] = 7.0
    high_case["feed_kg_s"] = 9.0
    a = evaluate_thermal(low_case, DEFAULT_THERMAL_SETTINGS)
    b = evaluate_thermal(high_case, DEFAULT_THERMAL_SETTINGS)
    assert b["energy"]["fired_duty_mw"] > a["energy"]["fired_duty_mw"]
    assert b["energy"]["radiant_duty_mw"] > a["energy"]["radiant_duty_mw"]
    assert b["radiant"]["average_flux_kw_m2"] > a["radiant"]["average_flux_kw_m2"]


def test_convection_bank_duties_close_to_total_convection():
    result = evaluate_thermal(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS)
    assert sum(CONVECTION_BANK_SHARES.values()) == pytest.approx(1.0)
    assert sum(result["convection"]["bank_duties_mw"].values()) == pytest.approx(
        result["energy"]["convection_duty_mw"]
    )


def test_end_of_run_uses_lower_public_radiant_fraction():
    sor = deepcopy(DEFAULT_CASE)
    eor = deepcopy(DEFAULT_CASE)
    eor["operating_case"] = "end_of_run"
    a = evaluate_thermal(sor)
    b = evaluate_thermal(eor)
    assert b["settings"]["radiant_fraction"] < a["settings"]["radiant_fraction"]


def test_thermal_sweep_is_square_plot_ready_and_monotonic_for_stack_temperature():
    sweep = thermal_sweep(
        DEFAULT_CASE,
        DEFAULT_THERMAL_SETTINGS,
        "stack_temperature_c",
        "overall_efficiency",
        points=31,
    )
    assert len(sweep["x"]) == 31
    assert len(sweep["y"]) == 31
    assert sweep["y"][0] > sweep["y"][-1]


def test_methane_richer_fuel_increases_thermal_stack_loss_at_same_duty():
    before = deepcopy(DEFAULT_CASE)
    methane_richer = deepcopy(DEFAULT_CASE)
    methane_richer["composition"] = rebalance_composition(
        before["composition"],
        "H2",
        0.30,
        "CH4",
    )
    a = evaluate_thermal(before, DEFAULT_THERMAL_SETTINGS)
    b = evaluate_thermal(methane_richer, DEFAULT_THERMAL_SETTINGS)
    assert b["energy"]["fired_duty_mw"] == pytest.approx(a["energy"]["fired_duty_mw"])
    assert b["flue"]["flow_kg_h"] > a["flue"]["flow_kg_h"]
    assert b["energy"]["stack_loss_mw"] > a["energy"]["stack_loss_mw"]


def test_fuel_component_can_drive_thermal_response_curve():
    sweep = thermal_sweep(
        DEFAULT_CASE,
        DEFAULT_THERMAL_SETTINGS,
        "H2",
        "overall_efficiency",
        points=31,
    )
    assert len(sweep["x"]) == 31
    assert sweep["input_label"] == "Hydrogen"
    assert sweep["input_unit"] == "%"
    assert sweep["y"][0] != pytest.approx(sweep["y"][-1])
