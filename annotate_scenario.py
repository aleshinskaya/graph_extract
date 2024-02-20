#import packages
import os
import sys
import math
import requests
import json, jsonlines
import pandas as pd
import numpy as np
import textwrap
from dotenv import dotenv_values
from dotenv import load_dotenv
import typer
import importlib
import translate_to_vis
importlib.reload(translate_to_vis)

# set some environment and global variables
load_dotenv() 
global config
config = dotenv_values(".env")

CUR_DIR = os.path.dirname(os.path.abspath(__name__))
DATA_DIR = CUR_DIR+'/data/'

# eventually nodes can be typed, inherit from node class but be distinctly Being, Action Choice, or Event.
class Node():

  def __init__ (self,label,kind):
    self.label = label
    self.kind = kind #can be: being, action choice, event.
    self.links = list()

  def link_link(self,a_link,a_node):
    x = (a_link,a_node)
    self.links.append(x)

  def print(self):

    return ({"kind": self.kind, "label": self.label})

  def print_all(self):

    link_list = []

    for l in self.links:
      link_list.append({'link': l[0].print(), 'to_node': l[1].print()['label']})

    node_dict = {'node': self.print(), 'links': link_list}

    return node_dict

class Link():

    def __init__(self,kind,value):
      self.kind = kind
      self.value = value
      # self.label = label

    def print(self):
      return ({"kind": self.kind, "value": self.value})

class Graph():

  nodes = [];
  links = [];

  def add_node(self,node):
    self.nodes.append(node)
    return(node)

  def add_link(self, link):
    self.links.append(link)
    return(link)

  def print_graph(self):
   return ([n.print_all() for n in self.nodes])


  def return_node(self,label):
    #finds node with a label and returns pointer to it
    nodes_with_label = [n for n in self.nodes if n.label == label]
    return(nodes_with_label)


  def list_nodes(self):
    print([n.label+'\n' for n in self.nodes])


  def reset(self):
    nodes = [];
    links = [];



# function to query GPT via openai API
def promptGPT(prompt_message_list, gpt_temperature=0, debug=False):
    gpt_url = "https://api.openai.com/v1/chat/completions"
    gpt_headers = {
        "Content-Type": "application/json",
        "Authorization": config['OPENAI_API_KEY']
    }
    gpt_data = {
            "model": "gpt-3.5-turbo-1106",
            "response_format": {"type": "json_object"}, # only works on 3.5-turbo-1106, 4 and above
            "temperature": gpt_temperature,
            "messages": prompt_message_list,
    }
    response = requests.post(gpt_url, headers=gpt_headers, json=gpt_data)
    output = response.json()['choices'][0]['message']['content']
    if(debug==True):
        output = response.json()

    return output

def get_response_dict(system_prompt_content, user_prompt_content):
    system_prompt= {
            "role": "system",
            "content": system_prompt_content
        }

    user_prompt = {
        "role": "user",
        "content": user_prompt_content,
    }

    response_dict = json.loads(promptGPT([system_prompt,user_prompt],0))
    return response_dict

def get_beings(this_scenario):

    system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. The user will describe a scenario from a first-person perspective. Your task is to identify each sentient being involved, including the first-person character "I". Sentient beings are entities who are alive and have the capacity to experience the world, for example, a human or an animal. Return a json object with key:value pair of "results": list of beings. Please be diligent, complete, and succinct in your response.'

    user_prompt_content = f'Here is my scenario: {this_scenario}.'

    return get_response_dict(system_prompt_content, user_prompt_content)
        
def get_events(this_scenario, this_act, beings):

    system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. \
    The user will describe a scenario and how they decided to act.\
    Your task is to identify all the outcomes that will probably occur as a result \
    of this action decision, especially any impacts on the beings involved.\
    Phrase the outcomes about the user using the first person.\
    Return a json object with key:value pair of "results": list of events.\
    Please be diligent, complete, and succinct in your response.'

    user_prompt_content = f'Here is my scenario: {this_scenario}. I decide to {this_act}. What events are likely to arise as outcomes of this decision?'

    return get_response_dict(system_prompt_content, user_prompt_content)

def get_impacts(this_scenario, this_act, this_event, beings):

        system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. \
        The user will describe a scenario from a first-person perspective. \
        Given this scenario, evaluate how the resulting event indicated impacts each sentient being.\
        Please score this impact on a scale from -10, indicating very harmful and negative utility for that being, \
        to +10, indicating very beneficial and high utility for that being. If there is no obvious impact on a being, score the impact as 0. \
        Return a json object with key:value pair of "results": list containing, for each being, a key:value pair of being: impact score.'

        user_prompt_content = f'Here is my scenario: {this_scenario}. It involves these beings: {beings}. \
        I decide to {this_act}, which results in this event: {this_event}. What is the impact of that event on each being?'

        return get_response_dict(system_prompt_content, user_prompt_content)

def get_being_links(this_scenario, this_act, this_event, beings):
        system_prompt_content = f'\
        You are a helpful assistant who is an expert at understanding human situations. \
        The user will describe a scenario from a first-person perspective. \
        \
        Each scenario will include a decision, and resulting event. \
        Please answer 3 questions regarding the several sentient beings in \
        the scenario. \
        For each being, (1) did they cause the event, (2) were they aware of the event, \
        (3), did they want or intend the event to occur? Each question has a yes or no answer.\
        \
        Return a json object with key:value pair of "results": list containing, for each being, \
        a key:value pair of being: answer, where answer is an ordered list of answers to the 3 questions.'

        user_prompt_content = f'Here is my scenario: {this_scenario}. It involves these beings: {beings}. \
        I decide to {this_act}, which results in this event: {this_event}. For each being, please answer the three questions relating to the event.'

        return get_response_dict(system_prompt_content, user_prompt_content)

def get_event_links(this_scenario, this_act, this_event, beings):
        print('hello world')

def write_jsonlines(fname,jlist):

  with open(fname, 'w') as jsonl_file:
    for dictionary in jlist:
        jsonl_file.write(json.dumps(dictionary) + '\n')


# scenario json must be a single line with scenario json with entries 'id', 'text', and 'options' {1:, 2: , etc}
def main(scenario_json,output_filename):
   
   # validate the scenario json
    assert scenario_json['id']
    assert scenario_json['text']
    assert scenario_json['options']
    
    # loop over actions 
    for act_id in scenario_json['options'].keys():     

        print('\n\nProcessing choice '+act_id)   
        this_act = scenario_json['options']["1"]
      
        this_scenario = scenario_json['text']

        #initialize Graph
        g = Graph()

        # get all beings
        beings = get_beings(this_scenario)    

        #ensure I is a being
        if("I" in set(beings['results'])==False):
            beings['results'].append("I")
            #TO DO: what if something like but not exactly "I" is in there?
            print("\n".join(beings['results']))

        #add each being to the graph
        for b in beings['results']:
            #create new node & add to graph               
            g.add_node(Node(b,'being'))

        #create link between being "I" and action choice
        this_being_node = g.return_node("I")[0]
        act_node = g.add_node(Node(this_act,'action_choice'))
        # Link(kind,value):
        this_link = g.add_link(Link('b-link','C+D+K+'))
        this_being_node.link_link(this_link,act_node)

        #get all outcome events arising from the action
        events = get_events(this_scenario, this_act, beings)
        print("\n".join(events['results'])) 

        #add links from each action to each event outcome and score impacts
        for this_evt in events['results']:

            #create a node for this "event"
            this_out_node = g.add_node(Node(this_evt,'event'))

            #create a link between act and event
            # Link(kind,value):
            this_link = g.add_link(Link('e_link',''))

            act_node.link_link(this_link,this_out_node)

            impacts = get_impacts(this_scenario, this_act, this_evt, beings)
            # print(impacts['results'])

            for being in impacts['results']:

                score = impacts['results'][being]

                # Link(kind,value):
                this_link = g.add_link(Link('utility',str(score)))
                this_b_node = g.return_node(being)[0]
                this_event_node = g.return_node(this_evt)[0]
                this_event_node.link_link(this_link,this_b_node)

        # add links from beings to events
                
        # dictionaries for translating into labels
        cause = {"No": 'C-', "Yes": 'C+'}
        know = {"No": 'K-',"Yes": 'K+'}
        desire = {"No": 'D-', "Yes": 'D+'}

        for this_evt in events['results']:

            links = get_being_links(this_scenario, this_act, this_evt, beings)
            
            # for each being, add the link to the graph with the right label
            for being,resp in links['results'].items():

                this_label = cause[resp[0]] + know[resp[1]] + desire[resp[2]]

                #create a new link
                # Link(kind,value):
                this_link = g.add_link(Link('b_link',this_label))
                this_b_node = g.return_node(being)[0]
                this_event_node = g.return_node(this_evt)[0]
                this_b_node.link_link(this_link,this_event_node)

        g_print = g.print_graph()
                
        this_output_filename = output_filename+'_choice_'+str(act_id)+'.json'
        print('\n\nWriting to file: '+this_output_filename)
        # write out json file
        write_jsonlines(DATA_DIR+this_output_filename,g_print)


        # send this json file as input to graph visualization, outputs html     

        translate_to_vis.main(DATA_DIR+this_output_filename)
        




