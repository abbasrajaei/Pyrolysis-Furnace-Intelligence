from __future__ import annotations

from copy import deepcopy

from dash import Input, Output, State, ctx, dcc, html, no_update
import plotly.graph_objects as go

from pyrolysis_furnace_intelligence.combustion_workbench import COMPONENTS, DEFAULT_CASE, evaluate_case
from pyrolysis_furnace_intelligence.heat_transfer_workbench import (
    AMBIENT_TEMPERATURE_C,
    CONVECTION_BANK_SHARES,
    DEFAULT_THERMAL_SETTINGS,
    PUBLIC_THERMAL_CASES,
    THERMAL_DEFAULT_RESPONSE,
    THERMAL_OUTPUTS,
    THERMAL_RESPONSE_OPTIONS,
    evaluate_thermal,
    thermal_comparison,
    thermal_defaults,
    thermal_explanation,
    thermal_input_label,
    thermal_input_unit,
    thermal_input_value,
    thermal_sweep,
    thermal_value,
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
    if unit == "t/h":
        return f"{value:.2f}"
    if unit == "kg/s":
        return f"{value:.2f}"
    if unit == "°C":
        return f"{value:.0f}"
    return f"{value:.3f}"


def heat_actions_layout():
    return html.Div(
        [
            html.Button(
                "Why did this happen?",
                id="heat-why-open",
                className="btn secondary",
                n_clicks=0,
            ),
            html.Button(
                "Reset heat study",
                id="heat-reset",
                className="btn",
                n_clicks=0,
            ),
        ],
        id="heat-actions",
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


def heat_main_layout():
    return html.Div(
        [
            dcc.Store(
                id="heat-current-store",
                data=deepcopy(DEFAULT_THERMAL_SETTINGS),
            ),
            dcc.Store(
                id="heat-before-store",
                data=deepcopy(DEFAULT_THERMAL_SETTINGS),
            ),
            dcc.Store(id="heat-changed-store", data=None),
            html.Main(
                [
                    html.Section(
                        [
                            html.Div("Heat-transfer inputs", className="section-title"),
                            html.Div("From combustion", className="mini-title"),
                            html.Div(
                                [
                                    _linked_card("Fired duty", "heat-linked-fired", "MW"),
                                    _linked_card("Flue gas", "heat-linked-flue", "t/h"),
                                    _linked_card("Excess air", "heat-linked-air", "%"),
                                    _linked_card("Feed rate", "heat-linked-feed", "kg/s"),
                                ],
                                className="linked-grid",
                            ),
                            html.Div(
                                "These values come directly from the Combustion Workbench.",
                                className="input-help",
                            ),
                            html.Div("Heat leaving the furnace", className="mini-title"),
                            html.Label("Stack gas temperature", className="input-label"),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="heat-stack-temp",
                                        type="number",
                                        value=DEFAULT_THERMAL_SETTINGS["stack_temperature_c"],
                                        min=AMBIENT_TEMPERATURE_C,
                                        max=350,
                                        step=5,
                                        debounce=True,
                                    ),
                                    html.Span("°C"),
                                ],
                                className="input-line",
                            ),
                            html.Label("Other heat loss", className="input-label"),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="heat-other-loss",
                                        type="number",
                                        value=100
                                        * DEFAULT_THERMAL_SETTINGS[
                                            "other_loss_fraction"
                                        ],
                                        min=0,
                                        max=10,
                                        step=0.1,
                                        debounce=True,
                                    ),
                                    html.Span("% fired"),
                                ],
                                className="input-line",
                            ),
                            html.Div("Heat distribution", className="mini-title"),
                            html.Label("Radiant share of fired duty", className="input-label"),
                            html.Div(
                                [
                                    dcc.Input(
                                        id="heat-radiant-share",
                                        type="number",
                                        value=100
                                        * DEFAULT_THERMAL_SETTINGS[
                                            "radiant_fraction"
                                        ],
                                        min=20,
                                        max=70,
                                        step=0.5,
                                        debounce=True,
                                    ),
                                    html.Span("%"),
                                ],
                                className="input-line",
                            ),
                            html.Div(
                                "Radiant share is a study assumption in the public model; "
                                "it is not a direct operator control.",
                                className="input-help",
                            ),
                            html.Div("Model basis", className="mini-title"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("Flue-gas heat capacity"),
                                            html.Strong("1.34 kJ/kg·K"),
                                        ],
                                        className="basis-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Radiant area"),
                                            html.Strong("420 m²"),
                                        ],
                                        className="basis-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Peak / average flux"),
                                            html.Strong("1.14"),
                                        ],
                                        className="basis-row",
                                    ),
                                    html.Div(
                                        [
                                            html.Span("Ambient temperature"),
                                            html.Strong("27 °C"),
                                        ],
                                        className="basis-row",
                                    ),
                                ],
                                className="basis-box",
                            ),
                        ],
                        className="panel heat-input-panel",
                    ),
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "Where the fired heat goes",
                                                className="section-title",
                                            ),
                                            html.Div(
                                                "Radiant + convection + stack + other loss = fired duty",
                                                className="graph-context",
                                            ),
                                        ]
                                    )
                                ],
                                className="heat-balance-head",
                            ),
                            html.Div(id="heat-distribution-bar"),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "See the effect",
                                                className="section-title",
                                            ),
                                            html.Div(
                                                id="heat-graph-context",
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
                                                id="heat-response-choice",
                                                clearable=False,
                                                className="response-dropdown",
                                            ),
                                        ]
                                    ),
                                ],
                                className="graph-head heat-graph-head",
                            ),
                            dcc.Graph(
                                id="heat-effect-graph",
                                config={
                                    "displayModeBar": False,
                                    "responsive": True,
                                },
                                className="effect-graph heat-effect-graph",
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
                                        "Each square is recalculated from the same heat-balance model.",
                                        className="graph-note",
                                    ),
                                ],
                                className="graph-footer",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "Convection heat recovery",
                                        className="mini-title bank-title",
                                    ),
                                    html.Div(id="heat-bank-strip"),
                                ],
                                className="bank-section",
                            ),
                        ],
                        className="panel heat-graph-panel",
                    ),
                    html.Section(
                        [
                            html.Div("Results", className="section-title"),
                            html.Div(id="heat-results-panel"),
                            html.Div(
                                [
                                    html.Div(
                                        "Before → Now",
                                        className="section-title compare-title",
                                    ),
                                    html.Div(id="heat-before-now"),
                                ],
                                className="compare-section",
                            ),
                        ],
                        className="panel heat-right-panel",
                    ),
                ],
                className="main-grid heat-main-grid",
            ),
            html.Div(
                [
                    html.Div(
                        id="heat-status-strip",
                        className="status-left",
                    ),
                    html.Div(
                        id="heat-interpretation-strip",
                        className="interpretation",
                    ),
                ],
                id="heat-footer",
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
                                        id="heat-why-close",
                                        className="close-btn",
                                        n_clicks=0,
                                    ),
                                ],
                                className="modal-head",
                            ),
                            html.Div(
                                id="heat-why-content",
                                className="modal-content",
                            ),
                        ],
                        className="modal-card",
                    )
                ],
                id="heat-why-modal",
                className="modal-backdrop hidden",
            ),
        ],
        id="heat-page",
        className="module-page page-hidden",
    )


def _heat_result_card(label, value, unit):
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


def _heat_results(result):
    energy = result["energy"]
    radiant = result["radiant"]
    return html.Div(
        [
            _heat_result_card(
                "Overall efficiency",
                f"{energy['overall_efficiency']:.2f}",
                "%",
            ),
            _heat_result_card(
                "Useful heat",
                f"{energy['useful_duty_mw']:.2f}",
                "MW",
            ),
            _heat_result_card(
                "Radiant heat",
                f"{energy['radiant_duty_mw']:.2f}",
                "MW",
            ),
            _heat_result_card(
                "Convection heat",
                f"{energy['convection_duty_mw']:.2f}",
                "MW",
            ),
            _heat_result_card(
                "Stack loss",
                f"{energy['stack_loss_mw']:.2f}",
                "MW",
            ),
            _heat_result_card(
                "Box efficiency",
                f"{energy['box_efficiency']:.2f}",
                "%",
            ),
            _heat_result_card(
                "Average heat flux",
                f"{radiant['average_flux_kw_m2']:.1f}",
                "kW/m²",
            ),
            _heat_result_card(
                "Peak heat flux",
                f"{radiant['peak_flux_kw_m2']:.1f}",
                "kW/m²",
            ),
        ],
        className="results-grid",
    )


def _heat_distribution(result):
    energy = result["energy"]
    fired = energy["fired_duty_mw"]
    items = [
        ("Radiant", energy["radiant_duty_mw"], "heat-radiant"),
        ("Convection", energy["convection_duty_mw"], "heat-convection"),
        ("Stack", energy["stack_loss_mw"], "heat-stack"),
        ("Other", energy["other_loss_mw"], "heat-other"),
    ]
    segments = []
    labels = []
    for label, value, cls in items:
        width = 100 * value / fired if fired else 0
        segments.append(
            html.Div(
                className=f"heat-segment {cls}",
                style={"width": f"{max(width, 0):.4f}%"},
                title=f"{label}: {value:.2f} MW",
            )
        )
        labels.append(
            html.Div(
                [
                    html.Span(className=f"heat-key {cls}"),
                    html.Span(label),
                    html.Strong(f"{value:.2f} MW"),
                ],
                className="heat-balance-label",
            )
        )
    return html.Div(
        [
            html.Div(segments, className="heat-balance-bar"),
            html.Div(labels, className="heat-balance-labels"),
        ],
        className="heat-distribution",
    )


def _bank_strip(result):
    duties = result["convection"]["bank_duties_mw"]
    return html.Div(
        [
            html.Div(
                [
                    html.Div(name, className="bank-name"),
                    html.Div(f"{duties[name]:.2f} MW", className="bank-duty"),
                ],
                className="bank-card",
            )
            for name in CONVECTION_BANK_SHARES
        ],
        className="bank-grid",
    )


def _heat_comparison(before_result, now_result):
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
    rows = []
    for row in thermal_comparison(before_result, now_result):
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


def _before_result(
    current_case,
    before_case,
    current_settings,
    before_settings,
    changed,
):
    if changed in {"feed_kg_s", "excess_air"} or changed in COMPONENTS:
        return evaluate_thermal(before_case, current_settings)
    return evaluate_thermal(current_case, before_settings)


def _heat_figure(
    current_case,
    before_case,
    current_settings,
    before_settings,
    changed,
    response,
):
    sweep = thermal_sweep(
        current_case,
        current_settings,
        changed,
        response,
        points=31,
    )
    now_result = evaluate_thermal(current_case, current_settings)
    before_result = _before_result(
        current_case,
        before_case,
        current_settings,
        before_settings,
        changed,
    )

    x = list(sweep["x"])
    x_now = sweep["x_now"]
    if changed in {"feed_kg_s", "excess_air"}:
        x_before = thermal_input_value(
            before_case,
            current_settings,
            changed,
        )
    else:
        x_before = thermal_input_value(
            current_case,
            before_settings,
            changed,
        )

    unit = sweep["input_unit"]
    if unit == "%":
        x = [100 * value for value in x]
        x_now *= 100
        x_before *= 100

    y_now = thermal_value(now_result, sweep["output"])
    y_before = thermal_value(before_result, sweep["output"])

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
                f"{sweep['input_label']}: %{{x:.2f}}"
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

    x_title = sweep["input_label"]
    if unit:
        x_title += f" ({unit})"

    fig.update_layout(
        margin={"l": 68, "r": 24, "t": 52, "b": 58},
        paper_bgcolor=C["panel"],
        plot_bgcolor=C["panel"],
        font={"color": C["text"], "family": "Inter, Segoe UI, sans-serif"},
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
        uirevision=f"heat-{changed}-{response}",
    )
    return fig, sweep, before_result, now_result, x_before, x_now


def register_heat_callbacks(app):
    @app.callback(
        Output("heat-current-store", "data"),
        Output("heat-before-store", "data"),
        Output("heat-changed-store", "data"),
        Input("heat-stack-temp", "value"),
        Input("heat-radiant-share", "value"),
        Input("heat-other-loss", "value"),
        Input("operating-case", "value"),
        Input("module-select", "value"),
        Input("heat-reset", "n_clicks"),
        State("changed-store", "data"),
        State("heat-current-store", "data"),
        prevent_initial_call=True,
    )
    def update_heat_settings(
        stack_temp,
        radiant_share,
        other_loss,
        operating_case,
        module,
        _reset,
        combustion_changed,
        current,
    ):
        trigger = ctx.triggered_id
        old = deepcopy(current or DEFAULT_THERMAL_SETTINGS)

        if trigger in {"heat-reset", "operating-case"}:
            new = thermal_defaults(operating_case or "start_of_run")
            return new, deepcopy(new), "stack_temperature_c"

        if trigger == "module-select":
            if module != "heat":
                return no_update, no_update, no_update
            if combustion_changed in THERMAL_RESPONSE_OPTIONS:
                return old, deepcopy(old), combustion_changed
            return old, deepcopy(old), "stack_temperature_c"

        new = deepcopy(old)
        if trigger == "heat-stack-temp" and stack_temp is not None:
            new["stack_temperature_c"] = float(stack_temp)
            changed = "stack_temperature_c"
        elif trigger == "heat-radiant-share" and radiant_share is not None:
            new["radiant_fraction"] = float(radiant_share) / 100.0
            changed = "radiant_fraction"
        elif trigger == "heat-other-loss" and other_loss is not None:
            new["other_loss_fraction"] = float(other_loss) / 100.0
            changed = "other_loss_fraction"
        else:
            return no_update, no_update, no_update

        return new, old, changed

    @app.callback(
        Output("heat-stack-temp", "value"),
        Output("heat-radiant-share", "value"),
        Output("heat-other-loss", "value"),
        Input("heat-reset", "n_clicks"),
        Input("operating-case", "value"),
        prevent_initial_call=True,
    )
    def reset_heat_controls(_reset, operating_case):
        settings = thermal_defaults(operating_case or "start_of_run")
        return (
            settings["stack_temperature_c"],
            100 * settings["radiant_fraction"],
            100 * settings["other_loss_fraction"],
        )

    @app.callback(
        Output("heat-response-choice", "options"),
        Output("heat-response-choice", "value"),
        Input("heat-changed-store", "data"),
    )
    def heat_response_options(changed):
        key = (
            changed
            if changed in THERMAL_RESPONSE_OPTIONS
            else "stack_temperature_c"
        )
        return (
            [
                {"label": THERMAL_OUTPUTS[name][0], "value": name}
                for name in THERMAL_RESPONSE_OPTIONS[key]
            ],
            THERMAL_DEFAULT_RESPONSE[key],
        )

    @app.callback(
        Output("heat-linked-fired", "children"),
        Output("heat-linked-flue", "children"),
        Output("heat-linked-air", "children"),
        Output("heat-linked-feed", "children"),
        Output("heat-distribution-bar", "children"),
        Output("heat-effect-graph", "figure"),
        Output("heat-graph-context", "children"),
        Output("heat-results-panel", "children"),
        Output("heat-before-now", "children"),
        Output("heat-bank-strip", "children"),
        Output("heat-status-strip", "children"),
        Output("heat-interpretation-strip", "children"),
        Output("heat-why-content", "children"),
        Input("current-store", "data"),
        Input("before-store", "data"),
        Input("heat-current-store", "data"),
        Input("heat-before-store", "data"),
        Input("heat-changed-store", "data"),
        Input("heat-response-choice", "value"),
    )
    def render_heat(
        current_case,
        before_case,
        current_settings,
        before_settings,
        changed,
        response,
    ):
        current_case = current_case or deepcopy(DEFAULT_CASE)
        before_case = before_case or deepcopy(current_case)
        current_settings = current_settings or thermal_defaults(
            current_case["operating_case"]
        )
        before_settings = before_settings or deepcopy(current_settings)
        changed = (
            changed
            if changed in THERMAL_RESPONSE_OPTIONS
            else "stack_temperature_c"
        )
        response = (
            response
            if response in THERMAL_RESPONSE_OPTIONS[changed]
            else THERMAL_DEFAULT_RESPONSE[changed]
        )

        combustion = evaluate_case(current_case)
        fig, sweep, before_result, now_result, x_before, x_now = _heat_figure(
            current_case,
            before_case,
            current_settings,
            before_settings,
            changed,
            response,
        )

        unit = sweep["input_unit"]
        context = html.Div(
            [
                html.Span(
                    f"Changed: {sweep['input_label']}",
                    className="context-strong",
                ),
                html.Span(
                    f"Before {_fmt(x_before, unit)}{unit if unit == '%' else (' ' + unit if unit else '')}"
                    f" → Now {_fmt(x_now, unit)}{unit if unit == '%' else (' ' + unit if unit else '')}"
                ),
            ],
            className="context-lines",
        )

        explanation = thermal_explanation(changed)
        status = now_result["status"]["text"]
        why_path = {
            "stack_temperature_c": [
                "Stack temperature",
                "Flue-gas sensible heat",
                "Stack loss",
                "Useful heat",
                "Efficiency",
            ],
            "radiant_fraction": [
                "Radiant share",
                "Radiant duty",
                "Heat flux",
                "Convection remainder",
            ],
            "other_loss_fraction": [
                "Other heat loss",
                "Useful heat",
                "Convection recovery",
                "Efficiency",
            ],
            "excess_air": [
                "Excess air",
                "Flue-gas flow",
                "Stack loss",
                "Efficiency",
            ],
            "feed_kg_s": [
                "Feed rate",
                "Required firing",
                "Radiant duty",
                "Heat flux",
            ],
        }.get(
            changed,
            [
                "Fuel composition",
                "Flue-gas flow",
                "Stack loss",
                "Useful heat",
                "Efficiency",
            ],
        )

        path_children = []
        for index, item in enumerate(why_path):
            if index:
                path_children.append(
                    html.Span("→", className="path-arrow")
                )
            path_children.append(
                html.Span(item, className="path-step")
            )

        why = html.Div(
            [
                html.P(explanation, className="why-lead"),
                html.Div(path_children, className="cause-path"),
                html.Div(
                    [
                        html.Div("Key equations", className="modal-subtitle"),
                        html.Div(
                            "Stack loss = flue-gas flow × effective Cp × (stack temperature − ambient)",
                            className="equation",
                        ),
                        html.Div(
                            "Overall efficiency = useful heat / fired duty",
                            className="equation",
                        ),
                        html.Div(
                            "Average radiant heat flux = radiant heat / radiant area",
                            className="equation",
                        ),
                        html.Div(
                            "Fired duty = radiant + convection + stack loss + other loss",
                            className="equation",
                        ),
                    ],
                    className="equation-block",
                ),
                html.Div(
                    "The public heat-transfer layer uses a lumped furnace energy balance. "
                    "It does not calculate local flame radiation, local tube-metal "
                    "temperature, detailed convection coefficients or coking rate.",
                    className="limit-note",
                ),
            ]
        )

        return (
            f"{combustion['firing']['fired_duty_mw']:.2f}",
            f"{combustion['combustion']['flue_flow_kg_h']/1000:.2f}",
            f"{100*current_case['excess_air']:.1f}",
            f"{current_case['feed_kg_s']:.2f}",
            _heat_distribution(now_result),
            fig,
            context,
            _heat_results(now_result),
            _heat_comparison(before_result, now_result),
            _bank_strip(now_result),
            status,
            explanation,
            why,
        )

    @app.callback(
        Output("heat-why-modal", "className"),
        Input("heat-why-open", "n_clicks"),
        Input("heat-why-close", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_heat_why(_open, _close):
        return (
            "modal-backdrop"
            if ctx.triggered_id == "heat-why-open"
            else "modal-backdrop hidden"
        )
