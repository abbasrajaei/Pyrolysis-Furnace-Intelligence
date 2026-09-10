from app.app import app,server

def _ids(component):
    found=set()
    if getattr(component,'id',None):found.add(component.id)
    children=getattr(component,'children',None)
    if isinstance(children,(list,tuple)):
        for child in children:found|=_ids(child)
    elif children is not None and not isinstance(children,(str,int,float)):
        found|=_ids(children)
    return found

def test_dash_application_shell():
    ids=_ids(app.layout)
    required={'workspace-tab','current-store','baseline-store','composition-store','duty','excess-air','draft','fuel-component','fuel-target','heat-recovery','radiant-share','inout-ratio','bottomside-ratio','feed','steam-ratio','zone-select','zone-correction','pressure-state','scenario-select','sens-x','sens-y','guidance-content','page-content'}
    assert required<=ids

def test_dash_http_root():
    client=server.test_client();response=client.get('/')
    assert response.status_code==200
    assert b'Pyrolysis Furnace Intelligence' in response.data

def test_callbacks_registered():
    assert len(app.callback_map)>=8
    outputs=' '.join(app.callback_map)
    assert 'guidance-content' in outputs
    assert 'page-content' in outputs
