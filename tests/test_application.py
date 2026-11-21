from copy import deepcopy

from app.app import app, server, effect_figure, sync_fuel_editor
from pyrolysis_furnace_intelligence.combustion_workbench import DEFAULT_CASE


def _ids(component):
    found = set()
    if getattr(component, "id", None):
        found.add(component.id)
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            found |= _ids(child)
    elif children is not None and not isinstance(children, (str, int, float)):
        found |= _ids(children)
    return found


def test_dash_application_shell():
    ids = _ids(app.layout)
    required = {
        "current-store",
        "before-store",
        "changed-store",
        "operating-case",
        "feed",
        "steam-ratio",
        "fuel-component",
        "fuel-target",
        "balance-component",
        "excess-air",
        "bottom-split",
        "hold-constant",
        "response-choice",
        "effect-graph",
        "results-panel",
        "before-now",
        "status-strip",
        "interpretation-strip",
        "why-open",
        "why-modal",
        "why-content",
        "module-select",
        "heat-page",
        "heat-stack-temp",
        "heat-radiant-share",
        "heat-other-loss",
        "heat-effect-graph",
        "heat-results-panel",
        "heat-before-now",
        "heat-why-open",
        "heat-why-modal",
        "process-page",
        "process-inlet-temp",
        "process-cot",
        "process-effect-graph",
        "process-results-panel",
        "process-before-now",
        "process-why-open",
        "process-why-modal",
    }
    assert required <= ids


def test_dash_http_root():
    client = server.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Pyrolysis Furnace Intelligence" in response.data


def test_callbacks_registered():
    assert len(app.callback_map) >= 16
    outputs = " ".join(app.callback_map)
    assert "effect-graph" in outputs
    assert "before-now" in outputs
    assert "why-modal" in outputs
    assert "heat-effect-graph" in outputs
    assert "heat-before-now" in outputs
    assert "heat-why-modal" in outputs
    assert "process-effect-graph" in outputs
    assert "process-before-now" in outputs
    assert "process-why-modal" in outputs
    assert "combustion-page" in outputs
    assert "process-page" in outputs


def test_response_chart_uses_square_points_not_a_line():
    before = deepcopy(DEFAULT_CASE)
    now = deepcopy(DEFAULT_CASE)
    now["composition"]["H2"] = 0.60
    now["composition"]["CH4"] = 0.395
    fig, _ = effect_figure(now, before, "H2", "co2", "fired_duty")
    response_trace = fig.data[0]
    assert response_trace.mode == "markers"
    assert response_trace.marker.symbol == "square"
    assert fig.data[1].marker.symbol == "square-open"
    assert fig.data[2].marker.symbol == "square"


def test_fuel_editor_never_offers_changed_component_as_balance():
    current = deepcopy(DEFAULT_CASE)
    target, options, balance = sync_fuel_editor("CH4", current, "CH4")
    values = {item["value"] for item in options}
    assert "CH4" not in values
    assert balance == "H2"
    assert target == 19.5
