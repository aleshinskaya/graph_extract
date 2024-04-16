
## <b>Read Me</b>

This package takes a text scenario and an action choice and outputs a graph (as a json and js/html visualization) that identifies the entities, actions, events, and relations among them within the scenario. 

## <i>Input Data</i>

Supply a jsonlines file with scenario text and action choice; see data/scenarios.json for format example. You can add your own json to the file scenarios.json if you wish.

## <i>Requirements</i>

Clone this repo and  install the packages listed in requirements.txt

Ensure you have an openAI API key in a .env file in the root directory:
OPENAI_API_KEY='Bearer sk-...'

To run the annotator, call this command within the downloaded parent folder:

python wrapper.py --filename "scenarios.json" --scenario-id <line number in the file>

Filename indicates the json file under data/ you wish to use. Scenario-id specifies which scenario you wish to process within the file, which assumes a jsonlines format.

## <i>Output Data</i>

All outputs will be saved to data/ and named with with this format: input-filename_scenario-id_action choice.html, e.g, scenarios_2_choice_1.html. 

Load the html file in a browser to view your visualization, or use the json file in whatever further processing you wish.




