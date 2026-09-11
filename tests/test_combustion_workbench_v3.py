import pytest
from pyrolysis_furnace_intelligence.combustion_workbench import (
 DEFAULT_CASE,DEFAULT_COMPOSITION,BURNERS,PUBLIC_CASES,composition_check,
 rebalance_composition,mixture_properties,combustion_per_kmol_fuel,
 required_fired_duty,evaluate_case,response_sweep,comparison_rows)

def test_default_composition_closes():
 assert sum(DEFAULT_COMPOSITION.values())==pytest.approx(1)
 assert composition_check(DEFAULT_COMPOSITION)["H2"]==pytest.approx(.8)

def test_balance_component_closes_exactly():
 out=rebalance_composition(DEFAULT_COMPOSITION,"H2",.60,"CH4")
 assert out["H2"]==pytest.approx(.60)
 assert sum(out.values())==pytest.approx(1)
 assert out["CH4"]>DEFAULT_COMPOSITION["CH4"]

def test_hydrogen_richer_fuel_reduces_co2_at_constant_duty():
 low=dict(DEFAULT_CASE); low["composition"]=rebalance_composition(DEFAULT_COMPOSITION,"H2",.40,"CH4")
 high=dict(DEFAULT_CASE); high["composition"]=rebalance_composition(DEFAULT_COMPOSITION,"H2",.80,"CH4")
 assert evaluate_case(high)["combustion"]["co2_formed_kg_h"]<evaluate_case(low)["combustion"]["co2_formed_kg_h"]

def test_excess_air_changes_flow_not_co2_mass():
 low=dict(DEFAULT_CASE); low["excess_air"]=.05
 high=dict(DEFAULT_CASE); high["excess_air"]=.25
 a=evaluate_case(low); b=evaluate_case(high)
 assert b["combustion"]["air_flow_kg_h"]>a["combustion"]["air_flow_kg_h"]
 assert b["combustion"]["flue_flow_kg_h"]>a["combustion"]["flue_flow_kg_h"]
 assert b["combustion"]["co2_formed_kg_h"]==pytest.approx(a["combustion"]["co2_formed_kg_h"])
 assert b["combustion"]["dry_co2_pct"]<a["combustion"]["dry_co2_pct"]

def test_feed_and_steam_raise_required_duty():
 low=dict(DEFAULT_CASE); high=dict(DEFAULT_CASE)
 low["feed_kg_s"]=7; high["feed_kg_s"]=9
 assert required_fired_duty(high)["required_fired_duty_mw"]>required_fired_duty(low)["required_fired_duty_mw"]
 low=dict(DEFAULT_CASE); high=dict(DEFAULT_CASE)
 low["steam_ratio"]=.2; high["steam_ratio"]=.5
 assert required_fired_duty(high)["required_fired_duty_mw"]>required_fired_duty(low)["required_fired_duty_mw"]

def test_low_load_warning_below_75_percent():
 c=dict(DEFAULT_CASE); c["feed_kg_s"]=.74*PUBLIC_CASES["start_of_run"]["feed_kg_s"]
 assert evaluate_case(c)["status"]["normal_range"] is False

def test_default_case_hits_public_normal_burner_point():
 r=evaluate_case(DEFAULT_CASE)
 assert r["firing"]["fired_duty_mw"]==pytest.approx(60)
 assert r["firing"]["average_burner_mw"]==pytest.approx(BURNERS["normal_mw_per_burner"])

def test_bottom_split_conserves_duty():
 c=dict(DEFAULT_CASE); c["bottom_split"]=.60
 r=evaluate_case(c)
 q=r["firing"]["bottom_burner_mw"]*BURNERS["bottom_count"]+r["firing"]["sidewall_burner_mw"]*BURNERS["sidewall_count"]
 assert q==pytest.approx(r["firing"]["fired_duty_mw"])

def test_wobbe_and_mass_lhv_are_distinct_properties():
 methane=mixture_properties(rebalance_composition(DEFAULT_COMPOSITION,"H2",.20,"CH4"))
 hydrogen=mixture_properties(rebalance_composition(DEFAULT_COMPOSITION,"H2",.80,"CH4"))
 assert hydrogen["lhv_MJ_kg"]>methane["lhv_MJ_kg"]
 assert hydrogen["wobbe_MJ_Nm3"]!=pytest.approx(methane["wobbe_MJ_Nm3"])

def test_hold_fuel_flow_changes_fired_duty_for_fuel_change():
 before=dict(DEFAULT_CASE); now=dict(DEFAULT_CASE)
 now["composition"]=rebalance_composition(DEFAULT_COMPOSITION,"H2",.30,"CH4")
 rb=evaluate_case(before); rn=evaluate_case(now,before,"fuel_flow","H2")
 assert rn["fuel"]["fuel_flow_kg_h"]==pytest.approx(rb["fuel"]["fuel_flow_kg_h"])
 assert rn["firing"]["fired_duty_mw"]!=pytest.approx(rb["firing"]["fired_duty_mw"])

def test_hold_burner_dp_follows_wobbe_ratio():
 before=dict(DEFAULT_CASE); now=dict(DEFAULT_CASE)
 now["composition"]=rebalance_composition(DEFAULT_COMPOSITION,"H2",.30,"CH4")
 rb=evaluate_case(before); rn=evaluate_case(now,before,"burner_dp","H2")
 assert rn["firing"]["fired_duty_mw"]/rb["firing"]["fired_duty_mw"]==pytest.approx(
  rn["fuel"]["wobbe_MJ_Nm3"]/rb["fuel"]["wobbe_MJ_Nm3"])

def test_response_sweep_tracks_changed_input():
 before=dict(DEFAULT_CASE); now=dict(DEFAULT_CASE); now["excess_air"]=.20
 s=response_sweep(now,before,"excess_air","dry_o2")
 assert s["input_label"]=="Excess air"
 assert s["y_now"]>s["y_before"]
 assert len(s["x"])==81

def test_comparison_rows_show_before_and_now():
 before=dict(DEFAULT_CASE); now=dict(DEFAULT_CASE); now["feed_kg_s"]=9
 rows=comparison_rows(before,now,changed_input="feed_kg_s")
 assert any(r["label"]=="Fuel flow" and r["now"]>r["before"] for r in rows)

def test_combustion_products_are_physical():
 c=combustion_per_kmol_fuel(DEFAULT_COMPOSITION,.10)
 assert c["dry_flue_pct"]["O2"]>0
 assert c["wet_flue_pct"]["H2O"]>0
 assert c["humid_air_mass_kg_per_kmol_fuel"]>0
