from app.app import app,server

def _ids(component):
    found=set()
    if getattr(component,"id",None): found.add(component.id)
    children=getattr(component,"children",None)
    if isinstance(children,(list,tuple)):
        for child in children: found|=_ids(child)
    elif children is not None and not isinstance(children,(str,int,float)):
        found|=_ids(children)
    return found

def test_dash_application_shell():
    ids=_ids(app.layout)
    required={
        "current-store","before-store","changed-store","operating-case","feed","steam-ratio",
        "fuel-component","fuel-target","balance-component","fuel-apply","excess-air","bottom-split",
        "hold-constant","response-choice","effect-graph","results-panel","before-now",
        "status-strip","interpretation-strip","why-open","why-modal","why-content"
    }
    assert required<=ids

def test_dash_http_root():
    client=server.test_client(); response=client.get("/")
    assert response.status_code==200
    assert b"Pyrolysis Furnace Intelligence" in response.data

def test_callbacks_registered():
    assert len(app.callback_map)>=5
    outputs=" ".join(app.callback_map)
    assert "effect-graph" in outputs
    assert "before-now" in outputs
    assert "why-modal" in outputs
