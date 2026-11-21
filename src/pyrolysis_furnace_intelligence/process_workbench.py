"""Public process/cracking workbench.

This layer connects the combustion and heat-transfer models to the process side of
an ethane-rich pyrolysis furnace. It uses generalised public teaching values and
transparent engineering approximations. It does not predict detailed cracking
kinetics, product yields, coke thickness, tube-metal temperature, or tube life.
"""
from copy import deepcopy
from math import exp, isfinite

from .combustion_workbench import DEFAULT_CASE, PUBLIC_CASES
from .heat_transfer_workbench import (
    DEFAULT_THERMAL_SETTINGS,
    evaluate_thermal,
    thermal_defaults,
)

WATER_MW_KG_KMOL = 18.015
PUBLIC_FEED_MW_KG_KMOL = 30.0
GAS_CONSTANT_BAR_M3_KMOL_K = 0.08314
ATMOSPHERIC_PRESSURE_BAR = 1.01325
EFFECTIVE_PROCESS_CP_KJ_KG_K = 3.70
TIME_TEMPERATURE_BETA_PER_C = 0.018

PUBLIC_PROCESS_CASES = {
    "start_of_run": {
        "coil_inlet_temperature_c": 680.0,
        "cot_c": 845.0,
        "outlet_pressure_barg": 0.80,
        "pressure_drop_bar": 0.40,
        "residence_time_s": 0.50,
        "conversion_anchor_pct": 65.0,
    },
    "end_of_run": {
        "coil_inlet_temperature_c": 685.0,
        "cot_c": 845.0,
        "outlet_pressure_barg": 0.80,
        "pressure_drop_bar": 0.58,
        "residence_time_s": 0.46,
        "conversion_anchor_pct": 62.0,
    },
}

DEFAULT_PROCESS_SETTINGS = {
    "coil_inlet_temperature_c": PUBLIC_PROCESS_CASES["start_of_run"][
        "coil_inlet_temperature_c"
    ],
    "cot_c": PUBLIC_PROCESS_CASES["start_of_run"]["cot_c"],
}

PROCESS_OUTPUTS = {
    "temperature_rise_c": ("Radiant temperature rise", "°C"),
    "total_process_flow_kg_s": ("Feed + steam flow", "kg/s"),
    "sensible_duty_mw": ("Estimated sensible heating", "MW"),
    "reaction_duty_mw": ("Residual reaction heat", "MW"),
    "reaction_share_pct": ("Reaction share of radiant heat", "%"),
    "pressure_drop_bar": ("Coil pressure drop", "bar"),
    "residence_time_s": ("Residence time", "s"),
    "hydrocarbon_partial_pressure_bara": ("Hydrocarbon partial pressure", "bar(a)"),
    "time_temperature_index": ("Time-temperature index", "index"),
    "fired_duty_mw": ("Fired duty", "MW"),
    "radiant_duty_mw": ("Radiant heat", "MW"),
    "average_flux_kw_m2": ("Average radiant heat flux", "kW/m²"),
}

PROCESS_RESPONSE_OPTIONS = {
    "cot_c": [
        "time_temperature_index",
        "temperature_rise_c",
        "sensible_duty_mw",
        "reaction_duty_mw",
    ],
    "coil_inlet_temperature_c": [
        "temperature_rise_c",
        "sensible_duty_mw",
        "reaction_duty_mw",
        "time_temperature_index",
    ],
    "feed_kg_s": [
        "fired_duty_mw",
        "radiant_duty_mw",
        "pressure_drop_bar",
        "residence_time_s",
        "time_temperature_index",
        "average_flux_kw_m2",
    ],
    "steam_ratio": [
        "hydrocarbon_partial_pressure_bara",
        "pressure_drop_bar",
        "residence_time_s",
        "sensible_duty_mw",
        "fired_duty_mw",
    ],
}

PROCESS_DEFAULT_RESPONSE = {
    "cot_c": "time_temperature_index",
    "coil_inlet_temperature_c": "sensible_duty_mw",
    "feed_kg_s": "residence_time_s",
    "steam_ratio": "hydrocarbon_partial_pressure_bara",
}


def _finite(value, name):
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def process_defaults(operating_case):
    if operating_case not in PUBLIC_PROCESS_CASES:
        raise ValueError("Unsupported operating case")
    ref = PUBLIC_PROCESS_CASES[operating_case]
    return {
        "coil_inlet_temperature_c": ref["coil_inlet_temperature_c"],
        "cot_c": ref["cot_c"],
    }


def _reference_flow_state(operating_case):
    ref_case = PUBLIC_CASES[operating_case]
    ref_process = PUBLIC_PROCESS_CASES[operating_case]
    feed = ref_case["feed_kg_s"]
    steam = feed * ref_case["steam_ratio"]
    total_mass = feed + steam
    avg_t_k = (
        ref_process["coil_inlet_temperature_c"] + ref_process["cot_c"]
    ) / 2.0 + 273.15
    avg_p_bara = (
        ATMOSPHERIC_PRESSURE_BAR
        + ref_process["outlet_pressure_barg"]
        + ref_process["pressure_drop_bar"] / 2.0
    )
    molar_flow_kmol_s = (
        feed / PUBLIC_FEED_MW_KG_KMOL
        + steam / WATER_MW_KG_KMOL
    )
    volumetric_flow_m3_s = (
        molar_flow_kmol_s
        * GAS_CONSTANT_BAR_M3_KMOL_K
        * avg_t_k
        / avg_p_bara
    )
    effective_volume_m3 = (
        ref_process["residence_time_s"] * volumetric_flow_m3_s
    )
    return {
        "feed_kg_s": feed,
        "steam_kg_s": steam,
        "total_mass_kg_s": total_mass,
        "avg_t_k": avg_t_k,
        "avg_p_bara": avg_p_bara,
        "molar_flow_kmol_s": molar_flow_kmol_s,
        "effective_volume_m3": effective_volume_m3,
    }


def evaluate_process(
    combustion_case=None,
    thermal_settings=None,
    process_settings=None,
    before_combustion_case=None,
    hold_constant="fired_duty",
    combustion_changed_input=None,
):
    case = deepcopy(DEFAULT_CASE)
    case.update(deepcopy(combustion_case or {}))
    operating_case = case["operating_case"]

    heat_settings = thermal_defaults(operating_case)
    heat_settings.update(deepcopy(thermal_settings or {}))

    settings = process_defaults(operating_case)
    settings.update(deepcopy(process_settings or {}))

    inlet_c = _finite(
        settings["coil_inlet_temperature_c"],
        "coil inlet temperature",
    )
    cot_c = _finite(settings["cot_c"], "coil outlet temperature")
    if cot_c <= inlet_c:
        raise ValueError("Coil outlet temperature must exceed coil inlet temperature")

    thermal = evaluate_thermal(
        case,
        heat_settings,
        before_combustion_case,
        hold_constant,
        combustion_changed_input,
    )

    feed = _finite(case["feed_kg_s"], "feed")
    steam_ratio = _finite(case["steam_ratio"], "steam/feed ratio")
    if feed <= 0 or steam_ratio < 0:
        raise ValueError("Feed must be positive and steam/feed ratio nonnegative")

    steam = feed * steam_ratio
    total_mass = feed + steam
    delta_t = cot_c - inlet_c

    sensible_mw = (
        total_mass * EFFECTIVE_PROCESS_CP_KJ_KG_K * delta_t / 1000.0
    )
    radiant_mw = thermal["energy"]["radiant_duty_mw"]
    reaction_mw = radiant_mw - sensible_mw
    reaction_share_pct = (
        100.0 * reaction_mw / radiant_mw if radiant_mw > 0 else 0.0
    )

    ref_process = PUBLIC_PROCESS_CASES[operating_case]
    ref_flow = _reference_flow_state(operating_case)

    avg_t_k = (inlet_c + cot_c) / 2.0 + 273.15
    flow_ratio = total_mass / ref_flow["total_mass_kg_s"]
    pressure_drop = (
        ref_process["pressure_drop_bar"]
        * flow_ratio**2
        * (avg_t_k / ref_flow["avg_t_k"])
    )

    outlet_barg = ref_process["outlet_pressure_barg"]
    avg_p_bara = (
        ATMOSPHERIC_PRESSURE_BAR + outlet_barg + pressure_drop / 2.0
    )
    inlet_barg = outlet_barg + pressure_drop

    hydrocarbon_kmol_s = feed / PUBLIC_FEED_MW_KG_KMOL
    steam_kmol_s = steam / WATER_MW_KG_KMOL
    total_kmol_s = hydrocarbon_kmol_s + steam_kmol_s
    hydrocarbon_mole_fraction = (
        hydrocarbon_kmol_s / total_kmol_s if total_kmol_s > 0 else 0.0
    )
    hydrocarbon_partial_pressure = hydrocarbon_mole_fraction * avg_p_bara

    volumetric_flow_m3_s = (
        total_kmol_s
        * GAS_CONSTANT_BAR_M3_KMOL_K
        * avg_t_k
        / avg_p_bara
    )
    residence_s = (
        ref_flow["effective_volume_m3"] / volumetric_flow_m3_s
        if volumetric_flow_m3_s > 0
        else 0.0
    )

    time_temperature_index = (
        100.0
        * (residence_s / ref_process["residence_time_s"])
        * exp(TIME_TEMPERATURE_BETA_PER_C * (cot_c - ref_process["cot_c"]))
    )

    warnings = []
    if thermal["combustion"]["process"]["low_load"]:
        warnings.append(
            "Low-load range: normal COT and steam/feed settings may no longer be appropriate"
        )
    if reaction_mw < 0:
        warnings.append(
            "Estimated sensible heating exceeds the linked radiant heat; this teaching state is inconsistent"
        )
    if time_temperature_index > 115:
        warnings.append(
            "Time-temperature severity is above the normal teaching reference; over-cracking and coking drivers may increase"
        )
    elif time_temperature_index < 85:
        warnings.append(
            "Time-temperature severity is below the normal teaching reference"
        )

    pressure_ratio = pressure_drop / ref_process["pressure_drop_bar"]
    if pressure_ratio > 1.20:
        warnings.append(
            "Coil pressure-drop estimate is well above the selected operating-case reference"
        )

    if time_temperature_index > 110 or pressure_ratio > 1.15:
        coking_driver = "Higher coking drivers"
    elif time_temperature_index < 90 and pressure_ratio < 0.95:
        coking_driver = "Lower coking drivers"
    else:
        coking_driver = "Near teaching reference"

    return {
        "combustion": thermal["combustion"],
        "thermal": thermal,
        "settings": settings,
        "process": {
            "feed_kg_s": feed,
            "steam_kg_s": steam,
            "steam_ratio": steam_ratio,
            "total_process_flow_kg_s": total_mass,
            "coil_inlet_temperature_c": inlet_c,
            "cot_c": cot_c,
            "temperature_rise_c": delta_t,
            "effective_cp_kj_kg_k": EFFECTIVE_PROCESS_CP_KJ_KG_K,
            "sensible_duty_mw": sensible_mw,
            "reaction_duty_mw": reaction_mw,
            "reaction_share_pct": reaction_share_pct,
            "pressure_drop_bar": pressure_drop,
            "inlet_pressure_barg": inlet_barg,
            "outlet_pressure_barg": outlet_barg,
            "average_pressure_bara": avg_p_bara,
            "hydrocarbon_mole_fraction": hydrocarbon_mole_fraction,
            "hydrocarbon_partial_pressure_bara": hydrocarbon_partial_pressure,
            "residence_time_s": residence_s,
            "time_temperature_index": time_temperature_index,
            "conversion_anchor_pct": ref_process["conversion_anchor_pct"],
            "coking_driver": coking_driver,
        },
        "status": {
            "warnings": warnings,
            "text": "Process study within teaching range" if not warnings else warnings[0],
        },
    }


def process_value(result, output_name):
    if output_name in {
        "temperature_rise_c",
        "total_process_flow_kg_s",
        "sensible_duty_mw",
        "reaction_duty_mw",
        "reaction_share_pct",
        "pressure_drop_bar",
        "residence_time_s",
        "hydrocarbon_partial_pressure_bara",
        "time_temperature_index",
    }:
        return float(result["process"][output_name])
    if output_name == "fired_duty_mw":
        return float(result["thermal"]["energy"]["fired_duty_mw"])
    if output_name == "radiant_duty_mw":
        return float(result["thermal"]["energy"]["radiant_duty_mw"])
    if output_name == "average_flux_kw_m2":
        return float(result["thermal"]["radiant"]["average_flux_kw_m2"])
    raise ValueError("Unsupported process output")


def process_input_label(name):
    return {
        "cot_c": "Coil outlet temperature",
        "coil_inlet_temperature_c": "Coil inlet temperature",
        "feed_kg_s": "Feed rate",
        "steam_ratio": "Steam/feed ratio",
    }.get(name, name)


def process_input_unit(name):
    return {
        "cot_c": "°C",
        "coil_inlet_temperature_c": "°C",
        "feed_kg_s": "kg/s",
        "steam_ratio": "kg/kg",
    }.get(name, "")


def process_input_value(combustion_case, process_settings, name):
    if name in {"feed_kg_s", "steam_ratio"}:
        return float(combustion_case[name])
    return float(process_settings[name])


def process_sweep_bounds(combustion_case, process_settings, name):
    operating_case = combustion_case["operating_case"]
    ref_process = PUBLIC_PROCESS_CASES[operating_case]
    if name == "cot_c":
        return ref_process["cot_c"] - 20.0, ref_process["cot_c"] + 20.0
    if name == "coil_inlet_temperature_c":
        return (
            ref_process["coil_inlet_temperature_c"] - 25.0,
            ref_process["coil_inlet_temperature_c"] + 25.0,
        )
    if name == "feed_kg_s":
        ref = PUBLIC_CASES[operating_case]["feed_kg_s"]
        return 0.60 * ref, 1.15 * ref
    if name == "steam_ratio":
        return 0.20, 0.50
    raise ValueError("Unsupported process sweep input")


def _changed_case_and_settings(combustion_case, process_settings, name, value):
    case = deepcopy(combustion_case)
    settings = deepcopy(process_settings)
    if name in {"feed_kg_s", "steam_ratio"}:
        case[name] = value
    else:
        settings[name] = value
    return case, settings


def process_sweep(
    combustion_case,
    thermal_settings,
    process_settings,
    changed_input,
    output_name=None,
    points=31,
    before_combustion_case=None,
    hold_constant="fired_duty",
    active_combustion_change=None,
):
    if changed_input not in PROCESS_RESPONSE_OPTIONS:
        changed_input = "cot_c"
    if output_name not in PROCESS_RESPONSE_OPTIONS[changed_input]:
        output_name = PROCESS_DEFAULT_RESPONSE[changed_input]

    lo, hi = process_sweep_bounds(
        combustion_case,
        process_settings,
        changed_input,
    )
    xs = [lo + (hi - lo) * i / (points - 1) for i in range(points)]
    ys = []

    for value in xs:
        case, settings = _changed_case_and_settings(
            combustion_case,
            process_settings,
            changed_input,
            value,
        )
        combustion_change = (
            changed_input
            if changed_input in {"feed_kg_s", "steam_ratio"}
            else active_combustion_change
        )
        result = evaluate_process(
            case,
            thermal_settings,
            settings,
            before_combustion_case,
            hold_constant,
            combustion_change,
        )
        ys.append(process_value(result, output_name))

    combustion_change = (
        changed_input
        if changed_input in {"feed_kg_s", "steam_ratio"}
        else active_combustion_change
    )
    current = evaluate_process(
        combustion_case,
        thermal_settings,
        process_settings,
        before_combustion_case,
        hold_constant,
        combustion_change,
    )

    return {
        "x": xs,
        "y": ys,
        "x_now": process_input_value(
            combustion_case,
            process_settings,
            changed_input,
        ),
        "y_now": process_value(current, output_name),
        "input": changed_input,
        "input_label": process_input_label(changed_input),
        "input_unit": process_input_unit(changed_input),
        "output": output_name,
        "output_label": PROCESS_OUTPUTS[output_name][0],
        "output_unit": PROCESS_OUTPUTS[output_name][1],
    }


def process_explanation(changed_input):
    return {
        "cot_c": (
            "A higher coil outlet temperature increases the time-temperature severity. "
            "For the same residence time, cracking proceeds more deeply, but the margin "
            "to over-cracking, coking and tube-temperature constraints becomes smaller."
        ),
        "coil_inlet_temperature_c": (
            "A hotter coil inlet reduces the sensible temperature rise required inside "
            "the radiant section. More of the linked radiant heat can then appear as "
            "reaction heat in this simplified energy split."
        ),
        "feed_kg_s": (
            "Higher feed increases required firing. It also raises coil flow and pressure "
            "drop while reducing residence time. At reduced feed the opposite happens, "
            "which is why maintaining the same COT can over-crack the feed."
        ),
        "steam_ratio": (
            "More dilution steam lowers hydrocarbon partial pressure, but it also adds "
            "mass that must be heated and increases coil pressure drop. The higher pressure "
            "partly offsets the simple residence-time reduction expected from extra steam."
        ),
    }.get(changed_input, "The process condition has changed.")


def process_comparison(before_result, now_result):
    metrics = [
        ("Radiant temperature rise", "temperature_rise_c", "°C"),
        ("Residence time", "residence_time_s", "s"),
        ("Coil pressure drop", "pressure_drop_bar", "bar"),
        ("Hydrocarbon partial pressure", "hydrocarbon_partial_pressure_bara", "bar(a)"),
        ("Time-temperature index", "time_temperature_index", "index"),
        ("Estimated sensible heating", "sensible_duty_mw", "MW"),
        ("Residual reaction heat", "reaction_duty_mw", "MW"),
    ]
    rows = []
    for label, key, unit in metrics:
        before = process_value(before_result, key)
        now = process_value(now_result, key)
        change_pct = None if abs(before) < 1e-12 else 100.0 * (now - before) / before
        rows.append(
            {
                "label": label,
                "before": before,
                "now": now,
                "change_pct": change_pct,
                "unit": unit,
            }
        )
    return rows
