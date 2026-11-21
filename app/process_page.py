from __future__ import annotations

from copy import deepcopy

from dash import Input, Output, State, ctx, dcc, html, no_update
import plotly.graph_objects as go

from pyrolysis_furnace_intelligence.combustion_workbench import (
    DEFAULT_CASE,
    PUBLIC_CASES,
)
from pyrolysis_furnace_intelligence.heat_transfer_workbench import (
    DEFAULT_THERMAL_SETTINGS,
    thermal_defaults,
)
from pyrolysis_furnace_intelligence.process_workbench import (
    DEFAULT_PROCESS_SETTINGS,
    PROCESS_DEFAULT_RESPONSE,
    PROCESS_OUTPUTS,
    PROCESS_RESPONSE_OPTIONS,
    PUBLIC_PROCESS_CASES,
    evaluate_process,
    process_comparison,
    process_defaults,
    process_explanation,
    process_input_label,
    process_input_unit,
    process_input_value,
    process_sweep,
    process_value,
)

C = {
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


def _fmt(value, unit):
    value = float(value)
    if unit == "%":
        return f"{value:.2f}"
    if unit == "MW":
        return f"{value:.2f}"
    if unit == "kW/m²":
        return f"{value:.1f}"
    if unit in {"kg/s", "bar(a)", "bar"}:
        return f"{value:.3f}" if unit != "kg/s" else f"{value:.2f}"
    if unit == "s":
        return f"{value:.3f}"
    if unit == "°C":
        return f"{value:.1f}"
    if unit == "index":
        return f"{value:.1f}"
    if unit == "kg/kg":
        return f"{value:.3f}"
    return f"{value:.3f}"


def process_actions_layout():
    return html.Div(
        [
            html.Button(
                "Why did this happen?",
                id="process-why-open",
                className="btn secondary",
                n_clicks=0,
            ),
            html.Button(
                "Reset process study",
                id="process-reset",
                className="btn",
                n_clicks=0,
            ),
        ],
        id="process-actions",
        className="top-actions page-hidden",
    )


def _linked_card(label, value_id, unit):
    return html.Div(
        [
            html.Div(label, className="linked-label"),
            html.Div(
                [
                    html.Span(id=value_id, className="linked-value"),
                    html.Span(" " + unit, className="linked-unit"),
                ]
            ),
        ],
        className="linked-card",
    )


def process_main_layout():
    return html.Div(
        [
            dcc.Store(
                id="process-current-store",
                data=deepcopy(DEFAULT_PROCESS_SETTINGS),
            ),
            dcc.Store(
                id="process-before-store",
                data=deepcopy(DEFAULT_PROCESS_SETTINGS),
            ),
            dcc.Store(id="process-changed-store", data=None),
            html.Main(
                [
                    html.Section(
                        [
                            html.Div("Process inputs", className="section-title"),
                            html.Div("From other modules", className="mini-title"),
                            html.Div(
                                [
                                    _linked_card(
                                        "Hydrocarbon feed",
                                        "process-linked-feed",
                                        "kg/s",
                                    ),
                                    _linked_card(
                                        "Steam / feed",
                                        "process-linked-steam",
                                        "kg/kg",
                                    ),
                                    _linked_card(
                                        "Radiant heat",
                                        "process-linked-radiant",
                                        "MW",
                                    ),
                                    _linked_card(
                                        "Average heat flux",
                                        "process-linked-flux",
                                        "kW/m²",
                                    ),
                                ],
                                className="linked-grid",
                            ),
                            html.Div(
                                "Feed and steam come from Combustion. Radiant heat and heat flux come from Heat transfer.",
                                className="input-help",
                            ),
                            html.Div("Radiant coil temperatures", className="mini-title"),
                            html.Label(
                                "Coil inlet temperature",
                                className="input-label",
                            ),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="process-inlet-temp",
                                        type="number",
                                        value=DEFAULT_PROCESS_SETTINGS[
                                            "coil_inlet_temperature_c"
                                        ],
                                        min=600,
                                        max=760,
                                        step=1,
                                        debounce=True,
                                    ),
                                    html.Span("°C"),
                                ],
                                className="input-line",
                            ),
                            html.Label(
                                "Coil outlet temperature (COT)",
                                className="input-label",
                            ),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="process-cot",
                                        type="number",
                                        value=DEFAULT_PROCESS_SETTINGS["cot_c"],
                                        min=780,
                                        max=900,
                                        step=1,
                                        debounce=True,
                                    ),
                                    html.Span("°C"),
                                ],
                                className="input-line",
                            ),
                            html.Div("How to read this", className="mini-title"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("Conversion"),
                                            html.Strong(id="process-conversion-anchor"),
                                        ],
                                        className="basis-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Time-temperature index"),
                                            html.Strong("100 = selected case"),
                                        ],
                                        className="basis-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Reaction heat"),
                                            html.Strong("Radiant − sensible"),
                                        ],
                                        className="basis-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Coking"),
                                            html.Strong("Drivers only"),
                                        ],
                                        className="basis-row",
                                    ),
                                ],
                                className="basis-box",
                            ),
                            html.Div(
                                "The conversion value is a case anchor, not an off-design kinetic prediction.",
                                className="input-help",
                            ),
                        ],
                        className="panel process-input-panel",
                    ),
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "Process heat inside the coil",
                                                className="section-title",
                                            ),
                                            html.Div(
                                                "Radiant heat = sensible heating + residual reaction heat",
                                                className="graph-context",
                                            ),
                                        ]
                                    )
                                ],
                                className="process-balance-head",
                            ),
                            html.Div(id="process-heat-split"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "See the effect",
                                                className="section-title",
                                            ),
                                            html.Div(
                                                id="process-graph-context",
                                                className="graph-context",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                "Show effect on",
                                                className="response-label",
                                            ),
                                            dcc.Dropdown(
                                                id="process-response-choice",
                                                clearable=False,
                                                className="response-dropdown",
                                            ),
                                        ]
                                    ),
                                ],
                                className="graph-head process-graph-head",
                            ),
                            dcc.Graph(
                                id="process-effect-graph",
                                config={
                                    "displayModeBar": False,
                                    "responsive": True,
                                },
                                className="effect-graph process-effect-graph",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "Before",
                                        className="legend-pill before-pill",
                                    ),
                                    html.Div(
                                        "Now",
                                        className="legend-pill now-pill",
                                    ),
                                    html.Div(
                                        "Each square is recalculated from the same process model.",
                                        className="graph-note",
                                    ),
                                ],
                                className="graph-footer",
                            ),
                        ],
                        className="panel process-graph-panel",
                    ),
                    html.Section(
                        [
                            html.Div("Results", className="section-title"),
                            html.Div(id="process-results-panel"),
                            html.Div(
                                [
                                    html.Div(
                                        "Before → Now",
                                        className="section-title compare-title",
                                    ),
                                    html.Div(id="process-before-now"),
                                ],
                                className="compare-section",
                            ),
                        ],
                        className="panel process-right-panel",
                    ),
                ],
                className="main-grid process-main-grid",
            ),
            html.Div(
                [
                    html.Div(
                        id="process-status-strip",
                        className="status-left",
                    ),
                    html.Div(
                        id="process-interpretation-strip",
                        className="interpretation",
                    ),
                ],
                id="process-footer",
                className="bottom-strip",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        "Why did this happen?",
                                        className="modal-title",
                                    ),
                                    html.Button(
                                        "×",
                                        id="process-why-close",
                                        className="close-btn",
                                        n_clicks=0,
                                    ),
                                ],
                                className="modal-head",
                            ),
                            html.Div(
                                id="process-why-content",
                                className="modal-content",
                            ),
                        ],
                        className="modal-card",
                    )
                ],
                id="process-why-modal",
                className="modal-backdrop hidden",
            ),
        ],
        id="process-page",
        className="module-page page-hidden",
    )


def _result_card(label, value, unit):
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


def _process_results(result):
    p = result["process"]
    return html.Div(
        [
            _result_card("COT", f"{p['cot_c']:.1f}", "°C"),
            _result_card(
                "Radiant temperature rise",
                f"{p['temperature_rise_c']:.1f}",
                "°C",
            ),
            _result_card(
                "Residence time",
                f"{p['residence_time_s']:.3f}",
                "s",
            ),
            _result_card(
                "Coil pressure drop",
                f"{p['pressure_drop_bar']:.3f}",
                "bar",
            ),
            _result_card(
                "Hydrocarbon partial pressure",
                f"{p['hydrocarbon_partial_pressure_bara']:.3f}",
                "bar(a)",
            ),
            _result_card(
                "Time-temperature index",
                f"{p['time_temperature_index']:.1f}",
                "",
            ),
            _result_card(
                "Estimated sensible heating",
                f"{p['sensible_duty_mw']:.2f}",
                "MW",
            ),
            _result_card(
                "Residual reaction heat",
                f"{p['reaction_duty_mw']:.2f}",
                "MW",
            ),
        ],
        className="results-grid",
    )


def _process_heat_split(result):
    p = result["process"]
    radiant = result["thermal"]["energy"]["radiant_duty_mw"]
    sensible = max(0.0, p["sensible_duty_mw"])
    reaction = max(0.0, p["reaction_duty_mw"])
    total = sensible + reaction
    if total <= 0:
        sensible_width = reaction_width = 0.0
    else:
        sensible_width = 100 * sensible / total
        reaction_width = 100 * reaction / total
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        className="process-segment process-sensible",
                        style={"width": f"{sensible_width:.4f}%"},
                        title=f"Sensible heating: {sensible:.2f} MW",
                    ),
                    html.Div(
                        className="process-segment process-reaction",
                        style={"width": f"{reaction_width:.4f}%"},
                        title=f"Residual reaction heat: {reaction:.2f} MW",
                    ),
                ],
                className="process-heat-bar",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                className="process-key process-sensible"
                            ),
                            html.Span("Sensible"),
                            html.Strong(f"{sensible:.2f} MW"),
                        ],
                        className="process-balance-label",
                    ),
                    html.Div(
                        [
                            html.Span(
                                className="process-key process-reaction"
                            ),
                            html.Span("Reaction"),
                            html.Strong(f"{reaction:.2f} MW"),
                        ],
                        className="process-balance-label",
                    ),
                    html.Div(
                        [
                            html.Span("Radiant total"),
                            html.Strong(f"{radiant:.2f} MW"),
                        ],
                        className="process-balance-label process-total-label",
                    ),
                ],
                className="process-balance-labels",
            ),
        ],
        className="process-heat-split",
    )


def _before_result(
    current_case,
    before_case,
    thermal_settings,
    current_settings,
    before_settings,
    changed,
    hold_constant,
    combustion_changed,
):
    if changed in {"feed_kg_s", "steam_ratio"}:
        return evaluate_process(
            before_case,
            thermal_settings,
            current_settings,
            before_case,
            hold_constant,
            changed,
        )
    return evaluate_process(
        current_case,
        thermal_settings,
        before_settings,
        before_case,
        hold_constant,
        combustion_changed,
    )


def _changed_row(
    current_case,
    before_case,
    current_settings,
    before_settings,
    changed,
):
    if changed in {"feed_kg_s", "steam_ratio"}:
        before = process_input_value(before_case, current_settings, changed)
        now = process_input_value(current_case, current_settings, changed)
    else:
        before = process_input_value(current_case, before_settings, changed)
        now = process_input_value(current_case, current_settings, changed)
    unit = process_input_unit(changed)
    delta = now - before
    if abs(before) > 1e-12 and unit != "°C":
        change = f"{100*delta/before:+.1f}%"
    elif unit == "°C":
        change = f"{delta:+.1f} °C"
    else:
        change = "—"
    return html.Div(
        [
            html.Div(
                process_input_label(changed),
                className="compare-name compare-input-name",
            ),
            html.Div(_fmt(before, unit), className="compare-value"),
            html.Div("→", className="compare-arrow"),
            html.Div(_fmt(now, unit), className="compare-value now"),
            html.Div(unit, className="compare-unit"),
            html.Div(
                change,
                className="compare-change compare-input-change",
            ),
        ],
        className="compare-row compare-input-row",
    )


def _process_comparison(
    before_result,
    now_result,
    current_case,
    before_case,
    current_settings,
    before_settings,
    changed,
):
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
    rows = [
        _changed_row(
            current_case,
            before_case,
            current_settings,
            before_settings,
            changed,
        )
    ]
    for row in process_comparison(before_result, now_result):
        change = row["change_pct"]
        text = "—" if change is None else f"{change:+.1f}%"
        cls = (
            "change-flat"
            if change is None or abs(change) < 1e-10
            else ("change-up" if change > 0 else "change-down")
        )
        rows.append(
            html.Div(
                [
                    html.Div(row["label"], className="compare-name"),
                    html.Div(
                        _fmt(row["before"], row["unit"]),
                        className="compare-value",
                    ),
                    html.Div("→", className="compare-arrow"),
                    html.Div(
                        _fmt(row["now"], row["unit"]),
                        className="compare-value now",
                    ),
                    html.Div(row["unit"], className="compare-unit"),
                    html.Div(
                        text,
                        className=f"compare-change {cls}",
                    ),
                ],
                className="compare-row",
            )
        )
    return html.Div([head, *rows], className="compare-body")


def _process_figure(
    current_case,
    before_case,
    thermal_settings,
    current_settings,
    before_settings,
    changed,
    response,
    hold_constant,
    combustion_changed,
):
    sweep = process_sweep(
        current_case,
        thermal_settings,
        current_settings,
        changed,
        response,
        points=31,
        before_combustion_case=before_case,
        hold_constant=hold_constant,
        active_combustion_change=combustion_changed,
    )
    now_result = evaluate_process(
        current_case,
        thermal_settings,
        current_settings,
        before_case,
        hold_constant,
        combustion_changed,
    )
    before_result = _before_result(
        current_case,
        before_case,
        thermal_settings,
        current_settings,
        before_settings,
        changed,
        hold_constant,
        combustion_changed,
    )

    x = list(sweep["x"])
    x_now = sweep["x_now"]
    if changed in {"feed_kg_s", "steam_ratio"}:
        x_before = process_input_value(before_case, current_settings, changed)
    else:
        x_before = process_input_value(current_case, before_settings, changed)

    y_now = process_value(now_result, sweep["output"])
    y_before = process_value(before_result, sweep["output"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=sweep["y"],
            mode="markers",
            marker={
                "symbol": "square",
                "size": 8,
                "color": C["blue"],
                "opacity": 0.90,
            },
            hovertemplate=(
                f"{sweep['input_label']}: %{{x:.3f}}"
                f"<br>{sweep['output_label']}: %{{y:.3f}} {sweep['output_unit']}"
                "<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x_before],
            y=[y_before],
            mode="markers+text",
            text=["Before"],
            textposition="top center",
            marker={
                "symbol": "square-open",
                "size": 17,
                "color": C["before"],
                "line": {"width": 2, "color": C["text"]},
            },
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[x_now],
            y=[y_now],
            mode="markers+text",
            text=["Now"],
            textposition="bottom center",
            marker={
                "symbol": "square",
                "size": 17,
                "color": C["amber"],
                "line": {"width": 2, "color": C["text"]},
            },
            hoverinfo="skip",
        )
    )

    if changed == "feed_kg_s":
        low_limit = 0.75 * PUBLIC_CASES[current_case["operating_case"]]["feed_kg_s"]
        fig.add_vrect(
            x0=min(x),
            x1=low_limit,
            fillcolor=C["yellow"],
            opacity=0.08,
            line_width=0,
            annotation_text="Low-load range",
            annotation_position="top left",
        )

    x_title = sweep["input_label"]
    if sweep["input_unit"]:
        x_title += f" ({sweep['input_unit']})"

    fig.update_layout(
        margin={"l": 70, "r": 24, "t": 52, "b": 58},
        paper_bgcolor=C["panel"],
        plot_bgcolor=C["panel"],
        font={
            "color": C["text"],
            "family": "Inter, Segoe UI, sans-serif",
        },
        title={
            "text": (
                f"How {sweep['output_label'].lower()} changes "
                f"with {sweep['input_label'].lower()}"
            ),
            "x": 0.01,
            "xanchor": "left",
            "font": {"size": 19},
        },
        xaxis={
            "title": x_title,
            "gridcolor": C["line"],
            "zeroline": False,
        },
        yaxis={
            "title": f"{sweep['output_label']} ({sweep['output_unit']})",
            "gridcolor": C["line"],
            "zeroline": False,
        },
        showlegend=False,
        hovermode="closest",
        uirevision=f"process-{changed}-{response}",
    )
    return (
        fig,
        sweep,
        before_result,
        now_result,
        x_before,
        x_now,
    )


def register_process_callbacks(app):
    @app.callback(
        Output("process-current-store", "data"),
        Output("process-before-store", "data"),
        Output("process-changed-store", "data"),
        Input("process-inlet-temp", "value"),
        Input("process-cot", "value"),
        Input("operating-case", "value"),
        Input("module-select", "value"),
        Input("process-reset", "n_clicks"),
        State("changed-store", "data"),
        State("process-current-store", "data"),
        prevent_initial_call=True,
    )
    def update_process_settings(
        inlet_temp,
        cot,
        operating_case,
        module,
        _reset,
        combustion_changed,
        current,
    ):
        trigger = ctx.triggered_id
        old = deepcopy(current or DEFAULT_PROCESS_SETTINGS)

        if trigger in {"process-reset", "operating-case"}:
            new = process_defaults(operating_case or "start_of_run")
            return new, deepcopy(new), "cot_c"

        if trigger == "module-select":
            if module != "process":
                return no_update, no_update, no_update
            if combustion_changed in {"feed_kg_s", "steam_ratio"}:
                return old, deepcopy(old), combustion_changed
            return old, deepcopy(old), "cot_c"

        new = deepcopy(old)
        if trigger == "process-inlet-temp" and inlet_temp is not None:
            new["coil_inlet_temperature_c"] = float(inlet_temp)
            changed = "coil_inlet_temperature_c"
        elif trigger == "process-cot" and cot is not None:
            new["cot_c"] = float(cot)
            changed = "cot_c"
        else:
            return no_update, no_update, no_update
        return new, old, changed

    @app.callback(
        Output("process-inlet-temp", "value"),
        Output("process-cot", "value"),
        Input("process-reset", "n_clicks"),
        Input("operating-case", "value"),
        prevent_initial_call=True,
    )
    def reset_process_controls(_reset, operating_case):
        settings = process_defaults(operating_case or "start_of_run")
        return (
            settings["coil_inlet_temperature_c"],
            settings["cot_c"],
        )

    @app.callback(
        Output("process-response-choice", "options"),
        Output("process-response-choice", "value"),
        Input("process-changed-store", "data"),
    )
    def process_response_options(changed):
        key = changed if changed in PROCESS_RESPONSE_OPTIONS else "cot_c"
        return (
            [
                {"label": PROCESS_OUTPUTS[name][0], "value": name}
                for name in PROCESS_RESPONSE_OPTIONS[key]
            ],
            PROCESS_DEFAULT_RESPONSE[key],
        )

    @app.callback(
        Output("process-linked-feed", "children"),
        Output("process-linked-steam", "children"),
        Output("process-linked-radiant", "children"),
        Output("process-linked-flux", "children"),
        Output("process-conversion-anchor", "children"),
        Output("process-heat-split", "children"),
        Output("process-effect-graph", "figure"),
        Output("process-graph-context", "children"),
        Output("process-results-panel", "children"),
        Output("process-before-now", "children"),
        Output("process-status-strip", "children"),
        Output("process-interpretation-strip", "children"),
        Output("process-why-content", "children"),
        Input("current-store", "data"),
        Input("before-store", "data"),
        Input("changed-store", "data"),
        Input("hold-constant", "value"),
        Input("heat-current-store", "data"),
        Input("process-current-store", "data"),
        Input("process-before-store", "data"),
        Input("process-changed-store", "data"),
        Input("process-response-choice", "value"),
    )
    def render_process(
        current_case,
        before_case,
        combustion_changed,
        hold_constant,
        thermal_settings,
        current_settings,
        before_settings,
        changed,
        response,
    ):
        current_case = current_case or deepcopy(DEFAULT_CASE)
        before_case = before_case or deepcopy(DEFAULT_CASE)
        thermal_settings = thermal_settings or thermal_defaults(
            current_case["operating_case"]
        )
        current_settings = current_settings or process_defaults(
            current_case["operating_case"]
        )
        before_settings = before_settings or deepcopy(current_settings)
        changed = (
            changed
            if changed in PROCESS_RESPONSE_OPTIONS
            else "cot_c"
        )
        response = (
            response
            if response in PROCESS_RESPONSE_OPTIONS[changed]
            else PROCESS_DEFAULT_RESPONSE[changed]
        )

        (
            fig,
            sweep,
            before_result,
            now_result,
            x_before,
            x_now,
        ) = _process_figure(
            current_case,
            before_case,
            thermal_settings,
            current_settings,
            before_settings,
            changed,
            response,
            hold_constant,
            combustion_changed,
        )

        process = now_result["process"]
        thermal = now_result["thermal"]
        explanation = process_explanation(changed)

        suffix = (
            f" {sweep['input_unit']}"
            if sweep["input_unit"]
            else ""
        )
        context = html.Div(
            [
                html.Span(
                    f"Changed: {sweep['input_label']}",
                    className="context-strong",
                ),
                html.Span(
                    f"Before {x_before:.3f}{suffix} → Now {x_now:.3f}{suffix}"
                ),
                html.Span(
                    "Other study inputs are kept at their current values"
                ),
            ],
            className="context-lines",
        )

        warnings = now_result["status"]["warnings"]
        status_parts = [
            PUBLIC_CASES[current_case["operating_case"]]["label"],
            process["coking_driver"],
        ]
        if warnings:
            status_parts.append(warnings[0])
        else:
            status_parts.append("Process study within teaching range")

        why = html.Div(
            [
                html.P(explanation, className="why-lead"),
                html.Div(
                    [
                        html.Span(
                            process_input_label(changed),
                            className="path-step",
                        ),
                        html.Span("→", className="path-arrow"),
                        html.Span(
                            "Residence / pressure / heat demand",
                            className="path-step",
                        ),
                        html.Span("→", className="path-arrow"),
                        html.Span(
                            "Time-temperature severity",
                            className="path-step",
                        ),
                        html.Span("→", className="path-arrow"),
                        html.Span(
                            "Yield and coking tendency",
                            className="path-step",
                        ),
                    ],
                    className="cause-path",
                ),
                html.Div(
                    [
                        html.Div(
                            "Key equations",
                            className="modal-subtitle",
                        ),
                        html.Div(
                            "Sensible heat ≈ (feed + steam) × effective Cp × (COT − coil inlet temperature)",
                            className="equation",
                        ),
                        html.Div(
                            "Residual reaction heat = linked radiant heat − estimated sensible heat",
                            className="equation",
                        ),
                        html.Div(
                            "Hydrocarbon partial pressure ≈ hydrocarbon mole fraction × average coil pressure",
                            className="equation",
                        ),
                        html.Div(
                            "Time-temperature index = residence-time ratio × temperature sensitivity, normalised to 100",
                            className="equation",
                        ),
                    ],
                    className="equation-block",
                ),
                html.Div(
                    "The time-temperature index is a transparent teaching indicator, not a kinetic conversion model. "
                    "The public module does not predict product yields, coke thickness, tube-metal temperature or tube life.",
                    className="limit-note",
                ),
            ]
        )

        return (
            f"{current_case['feed_kg_s']:.2f}",
            f"{current_case['steam_ratio']:.3f}",
            f"{thermal['energy']['radiant_duty_mw']:.2f}",
            f"{thermal['radiant']['average_flux_kw_m2']:.1f}",
            f"{process['conversion_anchor_pct']:.0f}% case anchor",
            _process_heat_split(now_result),
            fig,
            context,
            _process_results(now_result),
            _process_comparison(
                before_result,
                now_result,
                current_case,
                before_case,
                current_settings,
                before_settings,
                changed,
            ),
            "  |  ".join(status_parts),
            explanation,
            why,
        )

    @app.callback(
        Output("process-why-modal", "className"),
        Input("process-why-open", "n_clicks"),
        Input("process-why-close", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_process_why(_open, _close):
        return (
            "modal-backdrop"
            if ctx.triggered_id == "process-why-open"
            else "modal-backdrop hidden"
        )
