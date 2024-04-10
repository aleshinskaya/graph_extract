
import json
import os
import textwrap 
import typer
import annotate_scenario
import importlib
import requests
from dotenv import dotenv_values
from dotenv import load_dotenv


# set some environment and global variables
load_dotenv() 
global config
config = dotenv_values(".env")


CUR_DIR = os.path.dirname(os.path.abspath(__name__))
DATA_DIR = CUR_DIR+'/data/'


# load some scenarios
# filename = 'scenarios.json'
# scenario_id = 0


def main(filename  = 'scenarios.json' ,scenario_id = 0):

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

    this_scenario_text = scenario_json["text"]    
    print('Scenario Text: \n\n')
    print(textwrap.fill(this_scenario_text, width = 100), '\n\n')



    for act_id in scenario_json['options'].keys(): 

        this_act = scenario_json['options'][act_id]
        output_filename = 'values_'+filename.split('.json')[0]+'_'+str(scenario_id)+'_choice_'+str(act_id)+'.json'
        print(this_act)
        values_positive = []
        values_negative = []
        values_positive= get_value_positive(this_scenario_text, this_act)
        values_negative= get_value_negative(this_scenario_text, this_act)
        values = values_positive+values_negative
        write_json(DATA_DIR+output_filename,values)
    
  




def write_json(fname,dictionary):
    json_file =  open(fname, 'w')     
    json_file.write(json.dumps(dictionary))
    json_file.close()


def write_jsonlines(fname,jlist):
    jsonl_file =  open(fname, 'w')  
    for dictionary in jlist:
        jsonl_file.write(json.dumps(dictionary) + '\n')

    jsonl_file.close()


def get_value_positive(this_scenario, this_act):

    system_prompt_content = f"""You are a helpful assistant who is an expert at understanding human situations. You will recieve a scenario from the user and an action they are considering. Your task is to identify the values and virtues that characterize in this action, in the context of this scenario. Give each of these values a score from 0 to 10, where 10 indicates that this value is considered incredibly important and good to most people, whereas 0 indicates this value is generally unimportant or not good. Return a json object called 'values' with the values and their scores."""

    user_prompt_content = f"Here is my scenario. {this_scenario} My action is to {this_act} List the virtues and values of this action and a score for how important each of them might be. "         

    # print(system_prompt_content, user_prompt_content)

    return get_response_dict(system_prompt_content, user_prompt_content,False)


def get_value_negative(this_scenario, this_act):

    system_prompt_content = f"""You are a helpful assistant who is an expert at understanding human situations. You will recieve a scenario from the user and an action they are considering. Your task is to identify the anti-values or vices that characterize in this action, in the context of this scenario. Give each of these values a score from 0 to 10, where 10 indicates that this anti-value is considered incredibly significant and bad to most people, whereas 0 indicates this anti-value is generally unimportant or not very bad. Return a json object called 'anti-values' with the anti-values and their scores."""

    user_prompt_content = f"Here is my scenario. {this_scenario} My action is to {this_act} List the vices and anti-values of this action and a score for how important each of them might be. "         

    # print(system_prompt_content, user_prompt_content)

    return get_response_dict(system_prompt_content, user_prompt_content,False)

# function to query GPT via openai API
def promptGPT_simple(prompt_message_list, gpt_temperature=0, debug=False):
    gpt_url = "https://api.openai.com/v1/chat/completions"
    gpt_headers = {
        "Content-Type": "application/json",
        "Authorization": config['OPENAI_API_KEY']
    }
    gpt_data = {
            "model": "gpt-3.5-turbo-1106", 
            # "model": "gpt-4-turbo-preview",
            "response_format": {"type": "json_object"}, # only works on 3.5-turbo-1106, 4 and above
            "temperature": gpt_temperature,
            "messages": prompt_message_list,
    }
    response = requests.post(gpt_url, headers=gpt_headers, json=gpt_data)    
    if(debug==True):
        output = response.json()
    else:
        output = response.json()['choices'][0]['message']['content']

    return output

def get_response_dict(system_prompt_content, user_prompt_content,debug):
    system_prompt= {
            "role": "system",
            "content": system_prompt_content
        }

    user_prompt = {
        "role": "user",
        "content": user_prompt_content,
    }
    # print([system_prompt,user_prompt])

    # response_dict = json.loads(promptGPT([system_prompt,user_prompt],0,debug))
    response = promptGPT_simple([system_prompt,user_prompt],0,debug)
    return response
