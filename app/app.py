from __future__ import annotations

import os
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
import plotly.graph_objects as go

from pyrolysis_furnace_intelligence.combustion_workbench import (
    BURNERS,
    COMPONENTS,
    DEFAULT_CASE,
    DEFAULT_RESPONSE,
    FUEL_INPUTS,
    OUTPUTS,
    PUBLIC_CASES,
    RESPONSE_OPTIONS,
    comparison_rows,
    current_input_value,
    evaluate_case,
    input_label,
    input_unit,
    rebalance_composition,
    response_sweep,
    simple_explanation,
)
from app.heat_transfer_page import (
    heat_actions_layout,
    heat_main_layout,
    register_heat_callbacks,
)
from app.process_page import (
    process_actions_layout,
    process_main_layout,
    register_process_callbacks,
)

app = Dash(\n    __name__,\n    title="Pyrolysis Furnace Intelligence",\n    suppress_callback_exceptions=True,\n    assets_folder=str(ROOT / "app" / "assets"),\n)
server = app.server

C = {
    "bg": "#07121D",
    "panel": "#0D1B29",
    "line": "#20384D",
    "text": "#F3F7FA",
    "muted": "#9CB0BF",
    "blue": "#36A7E9",
    "amber": "#F2A93B",
    "green": "#38C995",
    "yellow": "#F2C14E",
    "before": "#8BA0AE",
}
DISPLAY_FORMULAS = {
    "H2": "H₂",
    "CH4": "CH₄",
    "C2H4": "C₂H₄",
    "C2H6": "C₂H₆",
    "C3H8": "C₃H₈",
    "CO": "CO",
    "CO2": "CO₂",
    "N2": "N₂",
}


def fmt(value, unit):
    value = float(value)
    if unit == "kg/h":
        return f"{value:,.0f}"
    if unit in {"t/h", "MJ/kg", "MJ/Nm³", "kg/MWh", "MW"}:
        return f"{value:,.2f}"
    if unit == "MW/burner":
        return f"{value:.3f}"
    if unit == "%":
        return f"{value:.2f}"
    if unit == "kg/s":
        return f"{value:.2f}"
    if unit == "kg/kg":
        return f"{value:.3f}"
    return f"{value:.3f}"


def composition_view(case):
    rows = []
    for component in COMPONENTS:
        value = 100 * case["composition"].get(component, 0)
        rows.append(
            html.Div(
                [
                    html.Span(
                        DISPLAY_FORMULAS[component],
                        className="comp-name",
                        title=FUEL_INPUTS[component],
                    ),
                    html.Div(
                        html.Div(
                            className="comp-bar-fill",
                            style={"width": f"{min(value, 100):.2f}%"},
                        ),
                        className="comp-bar",
                    ),
                    html.Span(f"{value:.2f}%", className="comp-number"),
                ],
                className="comp-row",
            )
        )
    return html.Div(rows, className="composition-list")


def result_card(label, value, unit):
    return html.Div(
        [
            html.Div(label, className="result-label"),
            html.Div(
                [
                    html.Span(value, className="result-value"),
                    html.Span(" " + unit, className="result-unit"),
                ]
            ),
        ],
        className="result-card",
    )


def results_view(result):
    return html.Div(
        [
            result_card("Fired duty", f"{result['firing']['fired_duty_mw']:.2f}", "MW"),
            result_card("Fuel flow", f"{result['fuel']['fuel_flow_kg_h']:,.0f}", "kg/h"),
            result_card("LHV", f"{result['fuel']['lhv_MJ_kg']:.2f}", "MJ/kg"),
            result_card("Wobbe index", f"{result['fuel']['wobbe_MJ_Nm3']:.2f}", "MJ/Nm³"),
            result_card("Air flow", f"{result['combustion']['air_flow_kg_h']/1000:.2f}", "t/h"),
            result_card("Flue-gas flow", f"{result['combustion']['flue_flow_kg_h']/1000:.2f}", "t/h"),
            result_card("O₂, dry", f"{result['combustion']['dry_o2_pct']:.2f}", "%"),
            result_card("CO₂ produced", f"{result['combustion']['co2_formed_kg_h']/1000:.2f}", "t/h"),
            result_card("Average burner load", f"{result['firing']['average_burner_mw']:.3f}", "MW/burner"),
        ],
        className="results-grid",
    )


def _changed_row(before, current, changed):
    before_value = current_input_value(before, changed)
    now_value = current_input_value(current, changed)
    unit = input_unit(changed)
    if unit == "%":
        before_value *= 100
        now_value *= 100
    delta = now_value - before_value
    if abs(before_value) > 1e-12 and unit != "%":
        change = f"{100*delta/before_value:+.1f}%"
    elif unit == "%":
        change = f"{delta:+.1f} pp"
    else:
        change = "—"
    return html.Div(
        [
            html.Div(input_label(changed), className="compare-name compare-input-name"),
            html.Div(fmt(before_value, unit), className="compare-value"),
            html.Div("→", className="compare-arrow"),
            html.Div(fmt(now_value, unit), className="compare-value now"),
            html.Div(unit, className="compare-unit"),
            html.Div(change, className="compare-change compare-input-change"),
        ],
        className="compare-row compare-input-row",
    )


def compare_view(before, current, hold, changed):
    rows = [_changed_row(before, current, changed)]
    for row in comparison_rows(before, current, hold, changed):
        change_pct = row["change_pct"]
        text = "—" if change_pct is None else f"{change_pct:+.1f}%"
        cls = (
            "change-flat"
            if change_pct is None or abs(change_pct) < 1e-10
            else ("change-up" if change_pct > 0 else "change-down")
        )
        rows.append(
            html.Div(
                [
                    html.Div(row["label"], className="compare-name"),
                    html.Div(fmt(row["before"], row["unit"]), className="compare-value"),
                    html.Div("→", className="compare-arrow"),
                    html.Div(fmt(row["now"], row["unit"]), className="compare-value now"),
                    html.Div(row["unit"], className="compare-unit"),
                    html.Div(text, className=f"compare-change {cls}"),
                ],
                className="compare-row",
            )
        )
    head = html.Div(
        [
            html.Div(""),
            html.Div("Before"),
            html.Div(""),
            html.Div("Now"),
            html.Div(""),
            html.Div("Change"),
        ],
        className="compare-head",
    )
    return html.Div([head, *rows], className="compare-body")


def hold_text(value):
    return {
        "fired_duty": "Keeping fired duty constant",
        "fuel_flow": "Keeping fuel flow constant",
        "burner_dp": "Keeping burner pressure difference constant",
    }.get(value, "Keeping fired duty constant")


def effect_figure(current, before, changed, response, hold):
    data = response_sweep(
        current,
        before,
        changed,
        response,
        hold_constant=hold,
        points=31,
    )
    x = list(data["x"])
    x_before = float(data["x_before"])
    x_now = float(data["x_now"])
    x_title = data["input_label"]

    if data["input_unit"] == "%":
        x = [100 * value for value in x]
        x_before *= 100
        x_now *= 100
        x_title += " (%)"
    elif data["input_unit"]:
        x_title += f" ({data['input_unit']})"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=data["y"],
            mode="markers",
            marker={
                "symbol": "square",
                "size": 8,
                "color": C["blue"],
                "opacity": 0.90,
            },
            hovertemplate=(
                f"{data['input_label']}: %{{x:.2f}}"
                f"<br>{data['output_label']}: %{{y:.3f}} {data['output_unit']}"
                "<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x_before],
            y=[data["y_before"]],
            mode="markers+text",
            text=["Before"],
            textposition="top center",
            marker={
                "size": 17,
                "color": C["before"],
                "symbol": "square-open",
                "line": {"width": 2, "color": C["text"]},
            },
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x_now],
            y=[data["y_now"]],
            mode="markers+text",
            text=["Now"],
            textposition="bottom center",
            marker={
                "size": 17,
                "color": C["amber"],
                "symbol": "square",
                "line": {"width": 2, "color": C["text"]},
            },
            hoverinfo="skip",
        )
    )

    if data.get("low_load_boundary") is not None:
        fig.add_vrect(
            x0=min(x),
            x1=data["low_load_boundary"],
            fillcolor=C["yellow"],
            opacity=0.08,
            line_width=0,
            annotation_text="Low-load range",
            annotation_position="top left",
        )

    fig.update_layout(
        margin={"l": 68, "r": 24, "t": 58, "b": 62},
        paper_bgcolor=C["panel"],
        plot_bgcolor=C["panel"],
        font={"color": C["text"], "family": "Inter, Segoe UI, sans-serif"},
        title={
            "text": f"How {data['output_label'].lower()} changes with {data['input_label'].lower()}",
            "x": 0.01,
            "xanchor": "left",
            "font": {"size": 19},
        },
        xaxis={"title": x_title, "gridcolor": C["line"], "zeroline": False},
        yaxis={
            "title": f"{data['output_label']} ({data['output_unit']})",
            "gridcolor": C["line"],
            "zeroline": False,
        },
        showlegend=False,
        hovermode="closest",
        uirevision=f"{changed}-{response}",
    )
    return fig, data


app.layout = html.Div(
    [
        dcc.Store(id="current-store", data=deepcopy(DEFAULT_CASE)),
        dcc.Store(id="before-store", data=deepcopy(DEFAULT_CASE)),
        dcc.Store(id="changed-store", data="H2"),
        html.Header(
            [
                html.Div(
                    [
                        html.Div("Pyrolysis Furnace Intelligence", className="brand-title"),
                        html.Div("Furnace Engineering Workbench", className="brand-subtitle"),
                    ],
                    className="brand-block",
                ),
                html.Div(
                    [
                        html.Div("Module", className="top-label"),
                        dcc.RadioItems(
                            id="module-select",
                            options=[
                                {"label": "Combustion", "value": "combustion"},
                                {"label": "Heat transfer", "value": "heat"},
                                {"label": "Process", "value": "process"},
                            ],
                            value="combustion",
                            inline=True,
                            className="module-radio",
                        ),
                    ],
                    className="module-select-wrap",
                ),
                html.Div(
                    [
                        html.Div("Operating case", className="top-label"),
                        dcc.RadioItems(
                            id="operating-case",
                            options=[
                                {"label": "Start of run", "value": "start_of_run"},
                                {"label": "End of run", "value": "end_of_run"},
                            ],
                            value="start_of_run",
                            inline=True,
                            className="top-radio",
                        ),
                    ],
                    className="top-case",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Button(
                                    "Why did this happen?",
                                    id="why-open",
                                    className="btn secondary",
                                    n_clicks=0,
                                ),
                                html.Button("Reset", id="reset", className="btn", n_clicks=0),
                            ],
                            id="combustion-actions",
                            className="top-actions",
                        ),
                        heat_actions_layout(),
                        process_actions_layout(),
                    ],
                    className="action-stack",
                ),
            ],
            className="topbar",
        ),
        html.Div(
            [
                html.Div(
                    [
        html.Main(
            [
                html.Section(
                    [
                        html.Div("Inputs", className="section-title"),
                        html.Div("Process", className="mini-title"),
                        html.Label("Feed rate", className="input-label"),
                        html.Div(
                            [
                                dcc.Input(
                                    id="feed",
                                    type="number",
                                    value=DEFAULT_CASE["feed_kg_s"],
                                    min=1,
                                    max=12,
                                    step=0.1,
                                    debounce=True,
                                ),
                                html.Span("kg/s"),
                            ],
                            className="input-line",
                        ),
                        html.Label("Steam / feed", className="input-label"),
                        html.Div(
                            [
                                dcc.Input(
                                    id="steam-ratio",
                                    type="number",
                                    value=DEFAULT_CASE["steam_ratio"],
                                    min=0,
                                    max=1,
                                    step=0.01,
                                    debounce=True,
                                ),
                                html.Span("kg/kg"),
                            ],
                            className="input-line",
                        ),
                        html.Div("Fuel composition", className="mini-title"),
                        html.Div(id="composition-view"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Change", className="input-label"),
                                        dcc.Dropdown(
                                            id="fuel-component",
                                            options=[
                                                {"label": FUEL_INPUTS[k], "value": k}
                                                for k in COMPONENTS
                                            ],
                                            value="H2",
                                            clearable=False,
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Label("To", className="input-label"),
                                        html.Div(
                                            [
                                                dcc.Input(
                                                    id="fuel-target",
                                                    type="number",
                                                    value=100 * DEFAULT_CASE["composition"]["H2"],
                                                    min=0,
                                                    max=100,
                                                    step=0.1,
                                                    debounce=True,
                                                ),
                                                html.Span("%"),
                                            ],
                                            className="input-line compact",
                                        ),
                                    ]
                                ),
                            ],
                            className="fuel-edit-grid",
                        ),
                        html.Label("Balance with", className="input-label"),
                        dcc.Dropdown(
                            id="balance-component",
                            options=[
                                {"label": FUEL_INPUTS[k], "value": k}
                                for k in COMPONENTS
                                if k != "H2"
                            ],
                            value="CH4",
                            clearable=False,
                        ),
                        html.Div("Combustion", className="mini-title"),
                        html.Label("Excess air", className="input-label"),
                        html.Div(
                            [
                                dcc.Input(
                                    id="excess-air",
                                    type="number",
                                    value=100 * DEFAULT_CASE["excess_air"],
                                    min=0,
                                    max=50,
                                    step=0.5,
                                    debounce=True,
                                ),
                                html.Span("%"),
                            ],
                            className="input-line",
                        ),
                        html.Label("Bottom firing share", className="input-label"),
                        html.Div(
                            [
                                dcc.Input(
                                    id="bottom-split",
                                    type="number",
                                    value=100 * DEFAULT_CASE["bottom_split"],
                                    min=0,
                                    max=100,
                                    step=1,
                                    debounce=True,
                                ),
                                html.Span("%"),
                            ],
                            className="input-line",
                        ),
                        html.Label(
                            "Keep constant when fuel changes",
                            className="input-label keep-label",
                        ),
                        dcc.Dropdown(
                            id="hold-constant",
                            options=[
                                {"label": "Fired duty", "value": "fired_duty"},
                                {"label": "Fuel flow", "value": "fuel_flow"},
                                {
                                    "label": "Burner pressure difference",
                                    "value": "burner_dp",
                                },
                            ],
                            value="fired_duty",
                            clearable=False,
                        ),
                    ],
                    className="panel input-panel",
                ),
                html.Section(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div("See the effect", className="section-title"),
                                        html.Div(id="graph-context", className="graph-context"),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Div("Show effect on", className="response-label"),
                                        dcc.Dropdown(
                                            id="response-choice",
                                            clearable=False,
                                            className="response-dropdown",
                                        ),
                                    ]
                                ),
                            ],
                            className="graph-head",
                        ),
                        dcc.Graph(
                            id="effect-graph",
                            config={"displayModeBar": False, "responsive": True},
                            className="effect-graph",
                        ),
                        html.Div(
                            [
                                html.Div("Before", className="legend-pill before-pill"),
                                html.Div("Now", className="legend-pill now-pill"),
                                html.Div(
                                    "Each square is recalculated from the same combustion model used for the results.",
                                    className="graph-note",
                                ),
                            ],
                            className="graph-footer",
                        ),
                    ],
                    className="panel graph-panel",
                ),
                html.Section(
                    [
                        html.Div("Results", className="section-title"),
                        html.Div(id="results-panel"),
                        html.Div(
                            [
                                html.Div(
                                    "Before → Now",
                                    className="section-title compare-title",
                                ),
                                html.Div(id="before-now"),
                            ],
                            className="compare-section",
                        ),
                    ],
                    className="panel right-panel",
                ),
            ],
            className="main-grid",
        ),
        html.Footer(
            [
                html.Div(id="status-strip", className="status-left"),
                html.Div(id="interpretation-strip", className="interpretation"),
            ],
            className="bottom-strip",
        ),
                    ],
                    id="combustion-page",
                    className="module-page",
                ),
                heat_main_layout(),
                process_main_layout(),
            ],
            className="module-area",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Why did this happen?", className="modal-title"),
                                html.Button(
                                    "×",
                                    id="why-close",
                                    className="close-btn",
                                    n_clicks=0,
                                ),
                            ],
                            className="modal-head",
                        ),
                        html.Div(id="why-content", className="modal-content"),
                    ],
                    className="modal-card",
                )
            ],
            id="why-modal",
            className="modal-backdrop hidden",
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("combustion-page", "className"),
    Output("heat-page", "className"),
    Output("process-page", "className"),
    Output("combustion-actions", "className"),
    Output("heat-actions", "className"),
    Output("process-actions", "className"),
    Input("module-select", "value"),
)
def switch_module(module):
    if module == "heat":
        return (
            "module-page page-hidden",
            "module-page",
            "module-page page-hidden",
            "top-actions page-hidden",
            "top-actions",
            "top-actions page-hidden",
        )
    if module == "process":
        return (
            "module-page page-hidden",
            "module-page page-hidden",
            "module-page",
            "top-actions page-hidden",
            "top-actions page-hidden",
            "top-actions",
        )
    return (
        "module-page",
        "module-page page-hidden",
        "module-page page-hidden",
        "top-actions",
        "top-actions page-hidden",
        "top-actions page-hidden",
    )


@app.callback(
    Output("current-store", "data"),
    Output("before-store", "data"),
    Output("changed-store", "data"),
    Input("feed", "value"),
    Input("steam-ratio", "value"),
    Input("excess-air", "value"),
    Input("bottom-split", "value"),
    Input("operating-case", "value"),
    Input("fuel-target", "value"),
    Input("reset", "n_clicks"),
    State("fuel-component", "value"),
    State("balance-component", "value"),
    State("current-store", "data"),
    prevent_initial_call=True,
)
def update_case(feed, steam, excess_air, bottom_split, operating_case, fuel_target, _reset, fuel_component, balance_component, current):
    trigger = ctx.triggered_id
    old = deepcopy(current or DEFAULT_CASE)

    if trigger == "reset":
        return deepcopy(DEFAULT_CASE), deepcopy(DEFAULT_CASE), "H2"

    new = deepcopy(old)
    changed = "feed_kg_s"

    if trigger == "feed" and feed is not None:
        new["feed_kg_s"] = float(feed)
        changed = "feed_kg_s"
    elif trigger == "steam-ratio" and steam is not None:
        new["steam_ratio"] = float(steam)
        changed = "steam_ratio"
    elif trigger == "excess-air" and excess_air is not None:
        new["excess_air"] = float(excess_air) / 100
        changed = "excess_air"
    elif trigger == "bottom-split" and bottom_split is not None:
        new["bottom_split"] = float(bottom_split) / 100
        changed = "bottom_split"
    elif trigger == "operating-case" and operating_case:
        new["operating_case"] = operating_case
        changed = "feed_kg_s"
    elif trigger == "fuel-target" and fuel_component and fuel_target is not None:
        target_fraction = float(fuel_target) / 100
        if abs(target_fraction - old["composition"].get(fuel_component, 0.0)) < 1e-12:
            return no_update, no_update, fuel_component
        new["balance_component"] = balance_component or (
            "CH4" if fuel_component != "CH4" else "H2"
        )
        new["composition"] = rebalance_composition(
            old["composition"],
            fuel_component,
            target_fraction,
            new["balance_component"],
        )
        changed = fuel_component
    else:
        return no_update, no_update, no_update

    return new, old, changed


@app.callback(
    Output("feed", "value"),
    Output("steam-ratio", "value"),
    Output("excess-air", "value"),
    Output("bottom-split", "value"),
    Output("operating-case", "value"),
    Output("fuel-component", "value"),
    Output("hold-constant", "value"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_controls(_n):
    case = DEFAULT_CASE
    return (
        case["feed_kg_s"],
        case["steam_ratio"],
        100 * case["excess_air"],
        100 * case["bottom_split"],
        case["operating_case"],
        "H2",
        "fired_duty",
    )


@app.callback(
    Output("fuel-target", "value"),
    Output("balance-component", "options"),
    Output("balance-component", "value"),
    Input("fuel-component", "value"),
    State("current-store", "data"),
    State("balance-component", "value"),
)
def sync_fuel_editor(component, current, balance):
    if not component or not current:
        return no_update, no_update, no_update

    options = [
        {"label": FUEL_INPUTS[k], "value": k}
        for k in COMPONENTS
        if k != component
    ]
    valid_values = {item["value"] for item in options}

    if balance not in valid_values:
        if component != "CH4" and "CH4" in valid_values:
            balance = "CH4"
        elif "H2" in valid_values:
            balance = "H2"
        else:
            balance = next(iter(valid_values))

    target = round(100 * current["composition"].get(component, 0), 3)
    return target, options, balance


@app.callback(
    Output("response-choice", "options"),
    Output("response-choice", "value"),
    Input("changed-store", "data"),
)
def response_options(changed):
    key = changed if changed in RESPONSE_OPTIONS else "feed_kg_s"
    return (
        [{"label": OUTPUTS[name][0], "value": name} for name in RESPONSE_OPTIONS[key]],
        DEFAULT_RESPONSE[key],
    )


@app.callback(
    Output("composition-view", "children"),
    Output("effect-graph", "figure"),
    Output("graph-context", "children"),
    Output("results-panel", "children"),
    Output("before-now", "children"),
    Output("status-strip", "children"),
    Output("interpretation-strip", "children"),
    Output("why-content", "children"),
    Input("current-store", "data"),
    Input("before-store", "data"),
    Input("changed-store", "data"),
    Input("hold-constant", "value"),
    Input("response-choice", "value"),
)
def render(current, before, changed, hold, response):
    current = current or deepcopy(DEFAULT_CASE)
    before = before or deepcopy(DEFAULT_CASE)
    changed = changed if changed in RESPONSE_OPTIONS else "feed_kg_s"
    response = (
        response
        if response in RESPONSE_OPTIONS[changed]
        else DEFAULT_RESPONSE[changed]
    )

    result = evaluate_case(current, before, hold, changed)
    figure, data = effect_figure(current, before, changed, response, hold)
    explanation = simple_explanation(changed, before, current, hold)

    before_x = data["x_before"]
    now_x = data["x_now"]
    suffix = ""
    if data["input_unit"] == "%":
        before_x *= 100
        now_x *= 100
        suffix = "%"
    elif data["input_unit"]:
        suffix = " " + data["input_unit"]

    context = html.Div(
        [
            html.Span(
                f"Changed: {data['input_label']}",
                className="context-strong",
            ),
            html.Span(
                f"Before {before_x:.2f}{suffix} → Now {now_x:.2f}{suffix}"
            ),
            html.Span(
                hold_text(hold)
                if changed in COMPONENTS
                else "Other inputs are kept at their current values"
            ),
        ],
        className="context-lines",
    )

    status = [
        PUBLIC_CASES[current["operating_case"]]["label"],
        result["status"]["text"],
    ]
    if result["status"]["burner_warning"]:
        status.append(result["status"]["burner_warning"])

    path = []
    for index, item in enumerate(explanation["path"]):
        if index:
            path.append(html.Span("→", className="path-arrow"))
        path.append(html.Span(item, className="path-step"))

    why = html.Div(
        [
            html.P(explanation["short"], className="why-lead"),
            html.Div(path, className="cause-path"),
            html.Div(
                [
                    html.Div("Key equations", className="modal-subtitle"),
                    html.Div(
                        "Fired duty = fuel flow × LHV",
                        className="equation",
                    ),
                    html.Div(
                        "O₂ required = C + H/4 − O/2",
                        className="equation",
                    ),
                    html.Div(
                        "Wobbe index = volumetric LHV / √specific gravity",
                        className="equation",
                    ),
                    html.Div(
                        "Actual air = stoichiometric air × (1 + excess air)",
                        className="equation",
                    ),
                ],
                className="equation-block",
            ),
            html.Div(
                "This public workbench uses generalised teaching conditions. "
                "It does not calculate CFD flame shape, NOx, flashback limits, "
                "local tube heat flux or a calibrated draft-to-airflow curve.",
                className="limit-note",
            ),
        ]
    )

    return (
        composition_view(current),
        figure,
        context,
        results_view(result),
        compare_view(before, current, hold, changed),
        "  |  ".join(status),
        explanation["short"],
        why,
    )


@app.callback(
    Output("why-modal", "className"),
    Input("why-open", "n_clicks"),
    Input("why-close", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_why(_open, _close):
    return (
        "modal-backdrop"
        if ctx.triggered_id == "why-open"
        else "modal-backdrop hidden"
    )


register_heat_callbacks(app)
register_process_callbacks(app)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8050")),
        debug=False,
    )
