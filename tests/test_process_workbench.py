from copy import deepcopy

import pytest

from pyrolysis_furnace_intelligence.combustion_workbench import DEFAULT_CASE
from pyrolysis_furnace_intelligence.heat_transfer_workbench import (
    DEFAULT_THERMAL_SETTINGS,
    thermal_defaults,
)
from pyrolysis_furnace_intelligence.process_workbench import (
    PUBLIC_PROCESS_CASES,
    evaluate_process,
    process_defaults,
    process_sweep,
)


def test_start_of_run_process_anchor_closes():
    result = evaluate_process(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS)
    p = result["process"]
    assert p["pressure_drop_bar"] == pytest.approx(
        PUBLIC_PROCESS_CASES["start_of_run"]["pressure_drop_bar"]
    )
    assert p["residence_time_s"] == pytest.approx(
        PUBLIC_PROCESS_CASES["start_of_run"]["residence_time_s"]
    )
    assert p["time_temperature_index"] == pytest.approx(100.0)
    assert p["reaction_duty_mw"] > 0


def test_end_of_run_uses_separate_process_anchor():
    case = deepcopy(DEFAULT_CASE)
    case["operating_case"] = "end_of_run"
    result = evaluate_process(
        case,
        thermal_defaults("end_of_run"),
        process_defaults("end_of_run"),
    )
    p = result["process"]
    assert p["pressure_drop_bar"] == pytest.approx(
        PUBLIC_PROCESS_CASES["end_of_run"]["pressure_drop_bar"]
    )
    assert p["residence_time_s"] == pytest.approx(
        PUBLIC_PROCESS_CASES["end_of_run"]["residence_time_s"]
    )
    assert p["time_temperature_index"] == pytest.approx(100.0)
    assert p["conversion_anchor_pct"] == pytest.approx(62.0)


def test_higher_cot_increases_time_temperature_severity():
    base = process_defaults("start_of_run")
    hot = deepcopy(base)
    hot["cot_c"] += 10.0
    a = evaluate_process(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS, base)
    b = evaluate_process(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS, hot)
    assert b["process"]["time_temperature_index"] > a["process"]["time_temperature_index"]
    assert b["process"]["temperature_rise_c"] > a["process"]["temperature_rise_c"]
    assert b["process"]["sensible_duty_mw"] > a["process"]["sensible_duty_mw"]
    assert b["process"]["reaction_duty_mw"] < a["process"]["reaction_duty_mw"]


def test_lower_feed_increases_residence_and_reduces_pressure_drop():
    low = deepcopy(DEFAULT_CASE)
    low["feed_kg_s"] *= 0.80
    base = evaluate_process(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS)
    reduced = evaluate_process(low, DEFAULT_THERMAL_SETTINGS)
    assert reduced["process"]["residence_time_s"] > base["process"]["residence_time_s"]
    assert reduced["process"]["pressure_drop_bar"] < base["process"]["pressure_drop_bar"]
    assert reduced["process"]["time_temperature_index"] > base["process"]["time_temperature_index"]


def test_more_dilution_steam_lowers_hydrocarbon_partial_pressure():
    high_steam = deepcopy(DEFAULT_CASE)
    high_steam["steam_ratio"] = 0.45
    base = evaluate_process(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS)
    changed = evaluate_process(high_steam, DEFAULT_THERMAL_SETTINGS)
    assert (
        changed["process"]["hydrocarbon_partial_pressure_bara"]
        < base["process"]["hydrocarbon_partial_pressure_bara"]
    )
    assert changed["process"]["pressure_drop_bar"] > base["process"]["pressure_drop_bar"]
    assert changed["process"]["sensible_duty_mw"] > base["process"]["sensible_duty_mw"]


def test_low_load_process_state_is_flagged():
    low = deepcopy(DEFAULT_CASE)
    low["feed_kg_s"] = 0.70 * DEFAULT_CASE["feed_kg_s"]
    result = evaluate_process(low, DEFAULT_THERMAL_SETTINGS)
    assert result["status"]["warnings"]
    assert "Low-load" in result["status"]["warnings"][0]


def test_process_sweep_recalculates_cot_response():
    settings = process_defaults("start_of_run")
    sweep = process_sweep(
        DEFAULT_CASE,
        DEFAULT_THERMAL_SETTINGS,
        settings,
        "cot_c",
        "time_temperature_index",
    )
    assert len(sweep["x"]) == 31
    assert len(sweep["y"]) == 31
    assert sweep["y"][-1] > sweep["y"][0]
    assert sweep["output_label"] == "Time-temperature index"


def test_process_sweep_recalculates_feed_response():
    settings = process_defaults("start_of_run")
    sweep = process_sweep(
        DEFAULT_CASE,
        DEFAULT_THERMAL_SETTINGS,
        settings,
        "feed_kg_s",
        "residence_time_s",
    )
    assert sweep["y"][0] > sweep["y"][-1]


def test_conversion_is_anchor_not_off_design_prediction():
    settings = process_defaults("start_of_run")
    changed = deepcopy(settings)
    changed["cot_c"] += 15
    result = evaluate_process(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS, changed)
    assert result["process"]["conversion_anchor_pct"] == pytest.approx(65.0)
    assert result["process"]["time_temperature_index"] != pytest.approx(100.0)


def test_invalid_temperature_order_is_rejected():
    settings = process_defaults("start_of_run")
    settings["coil_inlet_temperature_c"] = 850
    settings["cot_c"] = 840
    with pytest.raises(ValueError):
        evaluate_process(DEFAULT_CASE, DEFAULT_THERMAL_SETTINGS, settings)
