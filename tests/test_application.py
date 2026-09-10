from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
APP=Path(__file__).resolve().parents[1]/'app/app.py'
@pytest.mark.parametrize('page',['Overview','Thermal performance','Fuel comparison','Firing distribution','Control architecture','Scenario Lab','AI Engineering Supervisor','Model boundaries'])
def test_application_pages(page):
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception

def test_scenario_supervisor_and_shutdown():
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    app.sidebar.radio[0].set_value('Scenario Lab').run()
    app.sidebar.selectbox[0].set_value('total_shutdown').run()
    app.checkbox[0].check().run()
    assert not app.exception
    app.checkbox[1].check().run()
    assert not app.exception
