import argparse,json
from .scenario_engine import SCENARIOS,run_scenario
from .explanations import explain
def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',choices=SCENARIOS,default='normal');a=p.parse_args()
    s=run_scenario(a.scenario);print(json.dumps({'state':s,'explanation':explain(s)},indent=2))
if __name__=='__main__':main()
