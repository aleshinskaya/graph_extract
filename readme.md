
<b>Read Me</b>

Input Data

scenario text in json format. See data/scenarios.json for examples. You can add your own to scenarios.json.

Requirements & How to Run

clone this repo and ensure you have installed the packages listed in requirements.txt

to run, call this command within the downloaded parent folder.

python wrapper.py --filename "scenarios.json" --scenario-id 1

you can use scenario-id to specify which scenario you wish to process within scenarios.json. 


outputfiles will be found under data/, and written out with with this format: input-filename_scenario-id_action choice.html, e.g, scenarios_2_choice_1.html. 




