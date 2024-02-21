
import json
import os
import textwrap 
import typer
import annotate_scenario
import importlib
importlib.reload(annotate_scenario)

CUR_DIR = os.path.dirname(os.path.abspath(__name__))
DATA_DIR = CUR_DIR+'/data/'

def main(filename: str = 'scenarios.json"', scenario_id: int = 0):

    with open(DATA_DIR+filename, 'r') as file:
        scenarios=json.load(file)

    # error handling for assumptions about json entries
    try:
        scenario_json = scenarios[scenario_id]
    except:
        # print("Check scenario filename or scenario id")
        raise IndexError('Check scenario id exists in json file!')

    assert isinstance(scenario_json['id'],int)
    assert scenario_json['text']
    assert scenario_json['options']

    # display the scnenario text read in 
    this_scenario_text = scenario_json["text"]    
    print('Scenario Text: \n\n')
    print(textwrap.fill(this_scenario_text, width = 100), '\n\n')

    # generate output file name based on input filename
    output_filename = filename.split('.json')[0]+'_'+str(scenario_id)

    # run the annotation process
    annotate_scenario.main(scenario_json,output_filename)


if __name__ == "__main__":
    typer.run(main)