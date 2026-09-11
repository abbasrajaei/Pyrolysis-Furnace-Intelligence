"""Public heat-transfer and thermal-efficiency workbench.

This layer connects combustion results to a simple furnace energy balance.
It is intentionally source-informed but uses generalised public teaching values.
It does not predict CFD, local flame radiation, tube-metal temperature, coking
rate, or plant-specific convection performance.
"""
from copy import deepcopy
from math import isfinite

from .combustion_workbench import (
    COMPONENTS,
    DEFAULT_CASE,
    FUEL_INPUTS,
    PUBLIC_CASES,
    evaluate_case,
    rebalance_composition,
)

FLUE_CP_KJ_KG_K = 1.34
AMBIENT_TEMPERATURE_C = 27.0
RADIANT_AREA_M2 = 420.0
PEAK_TO_AVERAGE_FLUX = 1.14

PUBLIC_THERMAL_CASES = {
    "start_of_run": {
        "stack_temperature_c": 160.0,
        "radiant_fraction": 0.45,
        "other_loss_fraction": 0.01,
    },
    "end_of_run": {
        "stack_temperature_c": 160.0,
        "radiant_fraction": 0.44,
        "other_loss_fraction": 0.01,
    },
}

CONVECTION_BANK_SHARES = {
    "HTC-II": 0.26,
    "HPSSH-II": 0.15,
    "HPSSH-I": 0.16,
    "HTC-I": 0.22,
    "ECO": 0.12,
    "FPH": 0.09,
}

DEFAULT_THERMAL_SETTINGS = deepcopy(PUBLIC_THERMAL_CASES["start_of_run"])

THERMAL_OUTPUTS = {
    "overall_efficiency": ("Overall efficiency", "%"),
    "useful_duty_mw": ("Useful heat", "MW"),
    "radiant_duty_mw": ("Radiant heat absorbed", "MW"),
    "convection_duty_mw": ("Convection heat recovered", "MW"),
    "stack_loss_mw": ("Stack heat loss", "MW"),
    "other_loss_mw": ("Other heat loss", "MW"),
    "average_flux_kw_m2": ("Average radiant heat flux", "kW/m²"),
    "peak_flux_kw_m2": ("Peak radiant heat flux", "kW/m²"),
    "flue_flow_t_h": ("Flue-gas flow", "t/h"),
    "fired_duty_mw": ("Fired duty", "MW"),
}

THERMAL_RESPONSE_OPTIONS = {
    "stack_temperature_c": [
        "overall_efficiency",
        "stack_loss_mw",
        "useful_duty_mw",
        "convection_duty_mw",
    ],
    "radiant_fraction": [
        "radiant_duty_mw",
        "convection_duty_mw",
        "average_flux_kw_m2",
        "peak_flux_kw_m2",
    ],
    "other_loss_fraction": [
        "overall_efficiency",
        "other_loss_mw",
        "useful_duty_mw",
        "convection_duty_mw",
    ],
    "excess_air": [
        "overall_efficiency",
        "stack_loss_mw",
        "flue_flow_t_h",
        "useful_duty_mw",
    ],
    "feed_kg_s": [
        "fired_duty_mw",
        "radiant_duty_mw",
        "convection_duty_mw",
        "average_flux_kw_m2",
        "stack_loss_mw",
    ],
    **{
        component: [
            "overall_efficiency",
            "stack_loss_mw",
            "flue_flow_t_h",
            "useful_duty_mw",
        ]
        for component in COMPONENTS
    },
}

THERMAL_DEFAULT_RESPONSE = {
    "stack_temperature_c": "overall_efficiency",
    "radiant_fraction": "average_flux_kw_m2",
    "other_loss_fraction": "overall_efficiency",
    "excess_air": "overall_efficiency",
    "feed_kg_s": "fired_duty_mw",
    **{component: "overall_efficiency" for component in COMPONENTS},
}


def _finite(value, name):
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def thermal_defaults(operating_case):
    if operating_case not in PUBLIC_THERMAL_CASES:
        raise ValueError("Unsupported operating case")
    return deepcopy(PUBLIC_THERMAL_CASES[operating_case])


def evaluate_thermal(combustion_case=None, thermal_settings=None):
    case = deepcopy(DEFAULT_CASE)
    case.update(deepcopy(combustion_case or {}))
    settings = thermal_defaults(case["operating_case"])
    settings.update(deepcopy(thermal_settings or {}))

    stack_c = _finite(settings["stack_temperature_c"], "stack temperature")
    radiant_fraction = _finite(settings["radiant_fraction"], "radiant fraction")
    other_loss_fraction = _finite(settings["other_loss_fraction"], "other loss fraction")

    if stack_c < AMBIENT_TEMPERATURE_C:
        raise ValueError("Stack temperature cannot be below ambient in this model")
    if not 0 <= radiant_fraction <= 1:
        raise ValueError("Radiant fraction must be between 0 and 1")
    if not 0 <= other_loss_fraction < 1:
        raise ValueError("Other loss fraction must be between 0 and 1")

    combustion = evaluate_case(case)
    fired = combustion["firing"]["fired_duty_mw"]
    flue_kg_h = combustion["combustion"]["flue_flow_kg_h"]

    stack_loss = (
        flue_kg_h
        * FLUE_CP_KJ_KG_K
        * (stack_c - AMBIENT_TEMPERATURE_C)
        / 3_600_000.0
    )
    other_loss = fired * other_loss_fraction
    useful = fired - stack_loss - other_loss

    warning = None
    if useful < 0:
        useful = 0.0
        warning = "Calculated heat losses exceed fired duty"

    radiant_requested = fired * radiant_fraction
    radiant = min(radiant_requested, useful)
    convection = max(0.0, useful - radiant)

    if radiant_requested > useful:
        warning = (
            "Radiant absorption setting leaves no positive convection recovery "
            "with the current heat-loss assumptions"
        )

    efficiency = useful / fired if fired else 0.0
    average_flux = radiant * 1000.0 / RADIANT_AREA_M2
    peak_flux = average_flux * PEAK_TO_AVERAGE_FLUX

    bank_duties = {
        name: convection * share
        for name, share in CONVECTION_BANK_SHARES.items()
    }

    balance_error = fired - (radiant + convection + stack_loss + other_loss)

    return {
        "combustion": combustion,
        "settings": settings,
        "energy": {
            "fired_duty_mw": fired,
            "radiant_duty_mw": radiant,
            "convection_duty_mw": convection,
            "stack_loss_mw": stack_loss,
            "other_loss_mw": other_loss,
            "useful_duty_mw": useful,
            "overall_efficiency": 100.0 * efficiency,
            "box_efficiency": 100.0 * radiant / fired if fired else 0.0,
            "balance_error_mw": balance_error,
        },
        "radiant": {
            "area_m2": RADIANT_AREA_M2,
            "average_flux_kw_m2": average_flux,
            "peak_flux_kw_m2": peak_flux,
            "peak_to_average_ratio": PEAK_TO_AVERAGE_FLUX,
        },
        "convection": {
            "bank_duties_mw": bank_duties,
            "bank_shares": deepcopy(CONVECTION_BANK_SHARES),
        },
        "flue": {
            "flow_kg_h": flue_kg_h,
            "flow_t_h": flue_kg_h / 1000.0,
            "effective_cp_kj_kg_k": FLUE_CP_KJ_KG_K,
            "stack_temperature_c": stack_c,
            "ambient_temperature_c": AMBIENT_TEMPERATURE_C,
        },
        "status": {
            "warning": warning,
            "text": "Heat balance closed" if warning is None else warning,
        },
    }


def thermal_value(result, output_name):
    if output_name == "overall_efficiency":
        return result["energy"]["overall_efficiency"]
    if output_name in {
        "useful_duty_mw",
        "radiant_duty_mw",
        "convection_duty_mw",
        "stack_loss_mw",
        "other_loss_mw",
        "fired_duty_mw",
    }:
        return result["energy"][output_name]
    if output_name in {"average_flux_kw_m2", "peak_flux_kw_m2"}:
        return result["radiant"][output_name]
    if output_name == "flue_flow_t_h":
        return result["flue"]["flow_t_h"]
    raise ValueError("Unsupported thermal output")


def thermal_input_label(name):
    return {
        "stack_temperature_c": "Stack temperature",
        "radiant_fraction": "Radiant share",
        "other_loss_fraction": "Other heat loss",
        "excess_air": "Excess air",
        "feed_kg_s": "Feed rate",
        **FUEL_INPUTS,
    }.get(name, name)


def thermal_input_unit(name):
    return {
        "stack_temperature_c": "°C",
        "radiant_fraction": "%",
        "other_loss_fraction": "%",
        "excess_air": "%",
        "feed_kg_s": "kg/s",
        **{component: "%" for component in COMPONENTS},
    }.get(name, "")


def thermal_input_value(combustion_case, thermal_settings, name):
    if name in COMPONENTS:
        return float(combustion_case["composition"][name])
    if name in {"feed_kg_s", "excess_air"}:
        return float(combustion_case[name])
    return float(thermal_settings[name])


def thermal_sweep_bounds(combustion_case, thermal_settings, name):
    if name == "stack_temperature_c":
        return 110.0, 240.0
    if name == "radiant_fraction":
        return 0.35, 0.55
    if name == "other_loss_fraction":
        return 0.005, 0.03
    if name == "excess_air":
        return 0.0, 0.35
    if name == "feed_kg_s":
        ref = PUBLIC_CASES[combustion_case["operating_case"]]["feed_kg_s"]
        return 0.60 * ref, 1.15 * ref
    if name in COMPONENTS:
        balance = combustion_case.get("balance_component", "CH4")
        if balance == name:
            balance = max(
                (k for k in COMPONENTS if k != name),
                key=lambda k: combustion_case["composition"][k],
            )
        fixed = sum(
            float(value)
            for key, value in combustion_case["composition"].items()
            if key not in {name, balance}
        )
        return 0.0, max(0.0, 1.0 - fixed)
    raise ValueError("Unsupported thermal sweep input")


def _changed_case_and_settings(combustion_case, thermal_settings, name, value):
    case = deepcopy(combustion_case)
    settings = deepcopy(thermal_settings)
    if name in COMPONENTS:
        case["composition"] = rebalance_composition(
            case["composition"],
            name,
            value,
            case.get("balance_component", "CH4"),
        )
    elif name in {"feed_kg_s", "excess_air"}:
        case[name] = value
    else:
        settings[name] = value
    return case, settings


def thermal_sweep(
    combustion_case,
    thermal_settings,
    changed_input,
    output_name=None,
    points=31,
):
    if changed_input not in THERMAL_RESPONSE_OPTIONS:
        changed_input = "stack_temperature_c"
    if output_name not in THERMAL_RESPONSE_OPTIONS[changed_input]:
        output_name = THERMAL_DEFAULT_RESPONSE[changed_input]

    lo, hi = thermal_sweep_bounds(
        combustion_case,
        thermal_settings,
        changed_input,
    )
    x = [lo + (hi - lo) * i / (points - 1) for i in range(points)]
    y = []
    for value in x:
        case, settings = _changed_case_and_settings(
            combustion_case,
            thermal_settings,
            changed_input,
            value,
        )
        y.append(thermal_value(evaluate_thermal(case, settings), output_name))

    return {
        "x": x,
        "y": y,
        "x_now": thermal_input_value(
            combustion_case,
            thermal_settings,
            changed_input,
        ),
        "y_now": thermal_value(
            evaluate_thermal(combustion_case, thermal_settings),
            output_name,
        ),
        "input": changed_input,
        "input_label": thermal_input_label(changed_input),
        "input_unit": thermal_input_unit(changed_input),
        "output": output_name,
        "output_label": THERMAL_OUTPUTS[output_name][0],
        "output_unit": THERMAL_OUTPUTS[output_name][1],
    }


def thermal_explanation(changed_input):
    return {
        "stack_temperature_c": (
            "A hotter stack means more sensible heat leaves with the flue gas. "
            "Stack loss rises and overall efficiency falls."
        ),
        "radiant_fraction": (
            "A larger radiant share moves more of the useful heat into the firebox "
            "and raises average and peak radiant heat flux. Total useful heat does "
            "not increase simply because the split changes."
        ),
        "other_loss_fraction": (
            "Higher external or unaccounted heat loss reduces the useful heat "
            "available to the radiant and convection sections."
        ),
        "excess_air": (
            "More excess air increases flue-gas mass flow. At the same stack "
            "temperature, more sensible heat leaves the furnace and efficiency falls."
        ),
        "feed_kg_s": (
            "Higher process load increases required firing. With the same heat split "
            "and geometry, radiant duty and average heat flux rise."
        ),
        **{
            component: (
                f"Changing {FUEL_INPUTS[component].lower()} changes fuel properties "
                "and flue-gas flow. At the same stack temperature this changes stack "
                "heat loss and therefore the useful heat recovered by the furnace."
            )
            for component in COMPONENTS
        },
    }.get(changed_input, "The heat balance has changed.")


def thermal_comparison(before_result, now_result):
    metrics = [
        ("Fired duty", "fired_duty_mw", "MW"),
        ("Radiant heat", "radiant_duty_mw", "MW"),
        ("Convection heat", "convection_duty_mw", "MW"),
        ("Stack loss", "stack_loss_mw", "MW"),
        ("Overall efficiency", "overall_efficiency", "%"),
        ("Average heat flux", "average_flux_kw_m2", "kW/m²"),
        ("Peak heat flux", "peak_flux_kw_m2", "kW/m²"),
    ]
    rows = []
    for label, key, unit in metrics:
        before = thermal_value(before_result, key)
        now = thermal_value(now_result, key)
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
