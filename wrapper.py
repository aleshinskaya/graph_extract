
import json
import os
import textwrap 
import typer
import annotate_scenario
import importlib
importlib.reload(annotate_scenario)

CUR_DIR = os.path.dirname(os.path.abspath(__name__))
DATA_DIR = CUR_DIR+'/data/'

def main(filename = "scenarios.json", scenario_id: int = 1):

    with open(DATA_DIR+"scenarios.json", 'r') as file:
        scenarios=json.load(file)

    this_scenario_text = scenarios[scenario_id]["text"]
    
    print('Scenario Text: \n\n')
    print(textwrap.fill(this_scenario_text, width = 100), '\n\n')

    output_filename = filename.split('.json')[0]+'_'+str(scenario_id)

    annotate_scenario.main(scenarios[scenario_id],output_filename)


if __name__ == "__main__":
    typer.run(main)