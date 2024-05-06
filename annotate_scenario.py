#import packages
import os
import sys
import math
import requests
import json, jsonlines
import pandas as pd
import numpy as np
import re
import textwrap
from dotenv import dotenv_values
from dotenv import load_dotenv
import typer
import get_emb_distances
import importlib
importlib.reload(get_emb_distances)

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

  def __init__(self):        
    self.nodes = [];
    self.links = [];


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
    self.nodes = [];
    self.links = [];



# function to query GPT via openai API
def promptGPT(prompt_message_list, gpt_temperature=0, debug=False):
    gpt_url = "https://api.openai.com/v1/chat/completions"
    gpt_headers = {
        "Content-Type": "application/json",
        "Authorization": config['OPENAI_API_KEY']
    }
    gpt_data = {
            # "model": "gpt-3.5-turbo-1106", 
            "model": "gpt-4-turbo-preview",
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

def get_response_dict(system_prompt_content, user_prompt_content):
    system_prompt= {
            "role": "system",
            "content": system_prompt_content
        }

    user_prompt = {
        "role": "user",
        "content": user_prompt_content,
    }
    # print([system_prompt,user_prompt])

    response_dict = json.loads(promptGPT([system_prompt,user_prompt],0,False))
    return response_dict

def get_beings(this_scenario):

    system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. The user will describe a scenario from a first-person perspective. Your task is to identify each sentient being involved, including the first-person character "I". Sentient beings are entities who are alive and have the capacity to experience the world, for example, a human or an animal. List each individual being, but do not also list groups that include all of these individual beings. Return a json object with key:value pair of "results": list of beings. Please be diligent, complete, and succinct in your response.'

    user_prompt_content = f'Here is my scenario: {this_scenario}.'

    return get_response_dict(system_prompt_content, user_prompt_content)
        
def get_events(this_scenario, this_act, beings):

    system_prompt_content = f"""You are an expert at understanding human situations. A human named Ziv has described a scenario and how they decided to act. Your task is to identify all the outcomes that will probably occur as a result of Ziv's action decision, especially any impacts on sentient beings involved. Please state each outcome as the most simple, immediately occuring result, and not chains of events. Describe the outcomes referring to Ziv using their name, not pronouns. Return a json object with key:value pair of "results": list of events. Please be diligent, complete, and succinct in your response."""
    # print(system_prompt_content)
    user_prompt_content = f'Here is Ziv\'s scenario: {this_scenario}. Ziv decided to {this_act}. What outcomes are likely to arise a result of Ziv\'s decision?'

    return get_response_dict(system_prompt_content, user_prompt_content)

# # def get_impacts(this_scenario, this_act, this_event, beings):

#         system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. \
#         The user will describe a scenario from a first-person perspective. \
#         Given this scenario, evaluate how the resulting event indicated impacts each sentient being.\
#         Please score this impact on a scale from -10, indicating very harmful and negative utility for that being, \
#         to +10, indicating very beneficial and high utility for that being. If there is no obvious impact on a being, score the impact as 0. \
#         Return a json object with key:value pair of "results": list containing, for each being, a key:value pair of being: impact score.'

#         user_prompt_content = f'Here is my scenario: {this_scenario}. It involves these beings: {beings}. \
#         I decide to {this_act}, which results in this event: {this_event}. What is the impact of that event on each being?'

#         return get_response_dict(system_prompt_content, user_prompt_content)

def get_impacts_Ziv(this_scenario, this_act, this_event, this_being):

        system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. You will be given a scenario and asked to evaluate how strongly an event will impact the character "{this_being}". Rate the direct impact on this character using a scale from -10 to +10, where a rating of -10 indicates that the outcome will directly cause the character substantial harm, while a rating of +10 indicates that it will directly cause the character substantial benefit. If the outcome is not likely to affect the characte very much, return a rating of 0. Return a json object called "score" with your rating.'

        user_prompt_content = f'Here is the scenario: {this_scenario} {this_act} Consider the outcome that {this_event}. How does this outcome impact the character {this_being}?'

        # print(system_prompt_content, user_prompt_content)
        return get_response_dict(system_prompt_content, user_prompt_content)


def get_impacts_Ziv_multi(this_scenario, this_act, this_event, these_beings):

        system_prompt_content = f"You are a helpful assistant who is an expert at understanding human situations. The following scenario is context for the user's question. {this_scenario} {this_act}  End of scenario. Suppose this leads to the outcome that {convert_lower(this_event)} Please rate how this specific outcome, on its own without considering any further consequences, is likely to directly and immediately impact each character listed by the user. Use a scale from -10 to +10, where -10 indicates that the outcome will immediately and directly cause the character substantial harm, and +10 indicates that it will immediately and directly cause the character substantial benefit. If you are not sure that the outcome will immediately and directly affect the character, return a rating of 0 or close to 0. Return a json object called 'results' with a key:value pair for being: rating."        
        
        user_prompt_content = f'Consider the event that {convert_lower(this_event)} Without considering any further consequences of this event, how does this event by itself directly impact each of these characters: {these_beings}?'

        # print(system_prompt_content, user_prompt_content)
        return get_response_dict(system_prompt_content, user_prompt_content)


def find_semantic_match(item,list1):
  system_prompt_content = f"You are helpful assistant. You will be given a word or phrase and a list. Find the item in the list that is most similar in meaning to the word or phrase given. Return a json called 'result' with the word/phrase as key and the item as value."
  user_prompt_content = f"Here is my list: {list1}. Return the item in the list is most similar to the meaning of this word or phrase: {item}"
            
  return get_response_dict(system_prompt_content, user_prompt_content)

def get_impacts_Ziv_noscenario(this_scenario, this_act, this_event, these_beings):

        system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. You will be given the description of an event and asked to evaluate how this event on its own (without considering any further consequences) is likely to impact the listed characters provided by the user. Rate the direct impact on each character using a scale from -10 to +10, where a rating of -10 indicates that the outcome will directly cause the character substantial harm, while a rating of +10 indicates that it will directly cause the character substantial benefit. Please evaluate only the immediate, direct impact of the event on its own, without considering any further consequences or outcomes downstream. If you are not sure that the outcome will immediately and directly affect the character very much, return a rating of 0 or close to 0. Return a json object called "results" with a key:value pair for being: rating.'

        user_prompt_content = f'Consider the event that {convert_lower(this_event)} Without considering any further consequences of this event, how does this event by itself directly impact each of these characters: {these_beings}?'

        # print(system_prompt_content, user_prompt_content)
        return get_response_dict(system_prompt_content, user_prompt_content)

# def get_being_links(this_scenario, this_act, this_event, beings):
        
#         system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations and causality. The user will describe a scenario from a first-person perspective. The user decided on an action decision and an event resulted. Please answer 3 questions regarding the sentient beings in the scenario. For each being, (1) did they directly cause the event? Causality means that the event would not have happened if the being did not act. (2) Did they know the event would happen, knowing that the action was taken? (3) Did they want or desire for the event to occur? Each question has a yes or no answer. Return a json object with entry "results", containing the exact name of each being as provided as keys, and your answer as the value, where answer is an ordered list of answers to the 3 questions.'

#         user_prompt_content = f'Here is my scenario: {this_scenario}. It involves these beings: {beings}. \
#         I decide to {this_act}, which results in this event: {this_event}. For each being, please answer the three questions relating to the event.'

#         print(system_prompt_content, user_prompt_content)

#         return get_response_dict(system_prompt_content, user_prompt_content)


def get_being_links_Ziv_only(this_scenario, this_act, this_event, this_being):
        
        system_prompt_content = f"""You are a helpful assistant who is an expert at understanding human situations. You will recieve a scenario about a person named Ziv, an action they took, and an outcome that took place. Answer three questions. 1) Did Ziv directly cause the outcome? If they caused it, it would not occur if they had not acted. 2) Did Ziv expect it would happen as a result of the action?  3) Did Ziv intend for this outcome to occur, either by taking the action or by planning for it? Each question has a yes or no answer. Return a json object with an entry named "results" containing a key with the name of the character, Ziv, and a value with the ordered list of answers to the three questions."""

        user_prompt_content = f"Here is the scenario: {this_scenario}. {this_act}, resulting in this outcome: {this_event}. For the character {this_being}, please answer the three questions relating to the outcome."         

        return get_response_dict(system_prompt_content, user_prompt_content)

# def get_being_links_Ziv(this_scenario, this_act, this_event, this_being):
        
#         system_prompt_content = f"""You are a helpful assistant who is an expert at understanding human situations. You will recieve a scenario about a person named Ziv, an action they took, and an outcome resulting from that action. You will also be given the name of a character. Consider how this character relates to the outcome. Answer three questions. 1) Did they directly cause the outcome? If they caused it, it would not occur if they had not acted. 2) Did they expect it would happen as a result of the action? and 3) Did they intend for this outcome to occur? Each question has a yes or no answer. Return a json object with an entry named "results" containing a key with the name of the character and a value with the ordered list of answers to the three questions."""

#         user_prompt_content = f"Here is the scenario: {this_scenario}. Ziv chose to {this_act}, resulting in this outcome: {this_event}. For the character {this_being}, please answer the three questions relating to the outcome."         

#         return get_response_dict(system_prompt_content, user_prompt_content)

def get_event_links(this_scenario, this_act, this_event, beings):
        print('hello world')

def write_jsonlines(fname,jlist):
    jsonl_file =  open(fname, 'w')  
    for dictionary in jlist:
        jsonl_file.write(json.dumps(dictionary) + '\n')

    jsonl_file.close()


def write_json(fname,dictionary):
    json_file =  open(fname, 'w')     
    json_file.write(json.dumps(dictionary))
    json_file.close()


def fix_braces(this_list):

  # Define the regular expression pattern to match numerical text within brackets or parentheses
  # pattern = r'[0-9\[\]\(\)]'
  pattern = r'\((.*?)\)'
  new_list = []
  for this_string in this_list:
    # Use re.sub() to replace matched patterns with an empty string
    new_list.append(re.sub(pattern, '', this_string))

  # also remove trailing whitespace
  new_list = [this_string.rstrip() for this_string in new_list]
  
  return new_list


def fix_I(this_list):   
    
    matches_list =  []
    for this_string in this_list:  
        this_string_split = this_string.lower().split()
        for this_word in this_string_split:      
          if(this_word in ['i', 'me', 'myself']):
            matches_list.append(this_string)        
            break
        
    #we found some matches, now deal with them.     
            
     # if "I" is in the set, then remove the rest and return
    if("I" in set(this_list)):
        matches_list.remove("I")
        for x in matches_list:
            this_list.remove(x)
    # if it isn't, replace other matches with I and return
    else:       
        for x in matches_list:
            this_list.remove(x)

        this_list.append("I")

    return(this_list)
           
def convert_Ziv_I(old_sentence):
   
  #  function to turn Ziv into first person for output
  #  use a call to GPT to do this. 
  this_resp=get_response_dict("You are an expert in English grammar. Rewrite the following text so that it is written in the first person perspective instead of in the third person about Ziv, replacing each reference to Ziv by name or pronoun with the correct first-person pronoun (I, me, or my). Return a json called 'converted sentence' with the converted text only.", old_sentence)
  this_key=list(this_resp.keys())
  new_sentence = this_resp[this_key[0]]

  return(new_sentence)
        
def convert_Ziv_I_item(old_item):
   
  #  function to turn Ziv into first person for output
  #  use a call to GPT to do this. 
  this_resp=get_response_dict("You are an expert in English grammar. Take this phrase and replace each reference to the person Ziv with a first-person pronoun (I, me, or my). If Ziv is not explicitly mentioned, return the original text. Return a json called 'converted sentence' with the converted text only.", old_item)
  this_key=list(this_resp.keys())
  new_sentence = this_resp[this_key[0]]

  return(new_sentence)

def convert_I_Ziv_item(old_item):
   
  #  function to turn Ziv into first person for output
  #  use a call to GPT to do this. 
  this_resp=get_response_dict("You are an expert in English grammar. Take this phrase and replace each mention of the first-person pronouns I, me, or my with the name Ziv or Ziv's. If I, me, or my is not present, return the original text. Return a json called 'converted sentence' with the converted text only.", old_item)
  this_key=list(this_resp.keys())
  new_sentence = this_resp[this_key[0]]

  return(new_sentence)
def convert_I_Ziv(old_sentence):
    
    this_resp=get_response_dict("You are an expert in English grammar. Rewrite the following text so that it is written from the perspective of a character name Ziv in third person instead of being written in the first person. Replace every instance of the first person pronoun (I, me, my, etc) with either the name Ziv or the pronouns they, their, them, etc. Return a json called 'converted text' with the converted text only.", old_sentence)

    this_key=list(this_resp.keys())
    new_sentence = this_resp[this_key[0]]

    return(new_sentence)
   
def convert_lower(sentence):
    # convert to lower case except instances of Ziv
    new_s = sentence.lower()
    new_s = new_s.replace("ziv","Ziv")
    new_s = new_s.replace("ziv's","Ziv's")

    return new_s

def get_value_positive(this_scenario, this_act):

    system_prompt_content = f"""You are an expert on what humans value and don't value. The user will share an action they chose to take. Your task is to identify the values and virtues that the user exhibits by taking this action.  Give each of these values a score from 0 to 10, where 10 indicates that this value is considered incredibly important to people on avarege, whereas 0 indicates this value is generally unimportant to people on average. Return a json object called 'values' with the values and their scores."""

    # user_prompt_content = f"Here is my scenario. {this_scenario} My action is to {this_act} List the virtues and values of this action and a score for how important each of them might be. "    
    
    user_prompt_content = f"My action is to {this_act} List the virtues and values of this action and a score for how important each of them might be. "     

    # print(system_prompt_content, user_prompt_content)

    return get_response_dict(system_prompt_content, user_prompt_content)

def get_value_negative(this_scenario, this_act):

    system_prompt_content = f"""You are an expert on what humans value and don't value. The user will share an action they chose to take. Your task is to identify the anti-values and vices that the user exhibits by taking this action. Give each of these values a score from 0 to -10, where -10 indicates that this anti-value is considered incredibly important to people on avarege, whereas 0 indicates this anti-value is generally unimportant to people on average. Return a json object called 'anti-values' with the values and their scores."""

        # user_prompt_content = f"Here is my scenario. {this_scenario} My action is to {this_act} List the virtues and values of this action and a score for how important each of them might be. "    
        
    user_prompt_content = f"My action is to {this_act} List the anti-values of this action and a score for how important each of them might be. "           

    # print(system_prompt_content, user_prompt_content)

    return get_response_dict(system_prompt_content, user_prompt_content)


# scenario json must be a single line with scenario json with entries 'id', 'text', and 'options' {1:, 2: , etc}
def main(scenario_json,output_filename,act_id):
   
   # validate the scenario json
    assert isinstance(scenario_json['id'],int)
    assert scenario_json['text']
    assert scenario_json['options']

    print(output_filename)

    g = Graph()

    this_act = scenario_json['options'][act_id]

    this_act_I = "I decide to" + this_act

    this_act_Ziv = convert_I_Ziv(this_act_I)

    print('\n\nProcessing choice '+act_id +', '+this_act) 

    this_scenario = scenario_json['text']
    this_scenario_Ziv = convert_I_Ziv(this_scenario)

    # create a dictionary to write out to csv later
    scenario_dict = {'scenario': this_scenario, 'scenario_idx': scenario_json['id'],
                      'choice': this_act_I}
    #initialize Graph
    del(g)
    g = Graph()
    g.reset()        
    # print(g.print_graph())

    # get all beings, ensuring "I" is always a character 
    beings = (get_beings(this_scenario))
    beings_fixed =fix_I(fix_braces(beings['results']))        
    beings_fixed_Ziv = [convert_I_Ziv_item(x) for x in beings_fixed]

    print("\nIdentified these entities: \n\n"+"\n".join(beings_fixed))

    beings_list = ",".join(beings_fixed)
    scenario_dict["entities"]= beings_list

    #add each being to the graph
    for b in beings_fixed:
        #create new node & add to graph               
        g.add_node(Node(b,'being'))

    #create link between being "I" and action choice
    this_being_node = g.return_node("I")[0]
    act_node = g.add_node(Node(this_act,'action_choice'))
    # Link(kind,value):
    this_link = g.add_link(Link('b-link','C+D+K+'))
    this_being_node.link_link(this_link,act_node)


    # score action virtues
    values_positive= get_value_positive(this_scenario, this_act_I)
    values_negative= get_value_negative(this_scenario, this_act_I)
    values_positive.update(values_negative)
    all_values = values_positive
    # assert(all_values['values'])
    # assert(all_values['anti-values'])
    all_values_flat=all_values['values']    
    all_values_flat.update(all_values['anti-values'])

    # create nodes and links for these items 
    for value in all_values_flat.items(): 
        # print(value)       
        this_name = value[0]
        this_score = value[1]        
        # create node and add it to graph
        this_v_node = g.add_node(Node(this_name,'value'))
        # create link with score
        this_link = g.add_link(Link('v-link',str(this_score)))
        # connect it to the action node                 
        act_node.link_link(this_link,this_v_node)
        

    #get all outcome events arising from the action
    events = get_events(this_scenario, this_act, beings)
    events_Ziv= events['results']
    # remove overly similar outcomes
    print('\nExtracted events: ')
    print(events_Ziv)
    events_Ziv=get_emb_distances.threshold_by_sim(events_Ziv,.06)
    print('\n Similarity Thresholded events: ')
    print(events_Ziv)

    # replace Ziv with first person pronoun.        
    events_I = [convert_Ziv_I(x) if x.find("Ziv")>-1 else x for x in events_Ziv]   

    # print("\n".join(events_I))         
    scenario_dict["outcomes"]= events_I

    #add links from each action to each event outcome and score impacts
    # we will do this maintaining the Ziv pronouns

    impacts_list = []
    for this_evt_Ziv, this_evt_I in zip(events_Ziv,events_I):
        
        print('\nProcessing impacts of event: '+this_evt_I)

        #create a node for this "event"
        this_out_node = g.add_node(Node(this_evt_I,'event'))

        #create a link between act and event
        # Link(kind,value):
        this_link = g.add_link(Link('e_link',''))
        act_node.link_link(this_link,this_out_node)

        # score impacts using Ziv pronouns, for each being in turn
        # impacts_Ziv = {}
        # for this_being in beings_fixed_Ziv:
        #   impacts_d = {}
        #   this_impact = get_impacts_Ziv(this_scenario_Ziv, this_act_Ziv, this_evt_Ziv, this_being) 
        #   # impacts_d['being'] = this_being
        #   # impacts_d['score'] = this_impact['score']
        #   # impacts_Ziv.append(impacts_d)
        #   impacts_Ziv[this_being] = this_impact['score']
        
        beings_string = ', '.join(beings_fixed_Ziv)
        impacts_Ziv = get_impacts_Ziv_multi(this_scenario_Ziv, this_act_Ziv, this_evt_Ziv, beings_string) 
        try:        
          impacts_Ziv = impacts_Ziv['results']
        except:
          pass

        # try to align the returned beings list with the known beings list
        # create Ziv version of beings
        # convert both into sets
        beings_known_set = set(beings_fixed)
        beings_found_list = list(impacts_Ziv.keys())

        beings_found_list_I = []
        for x in beings_found_list:
            if(x!='I'):
                  x=x.lower()                
            beings_found_list_I.append(convert_Ziv_I_item(x))
        
       
        # beings_found_set = set(beings_found_list_I)

        beings_not_found = []
        for this_b in beings_found_list_I:
          # is it listed exactly in beings list? great, remove it!
          # print(this_b)
          if(this_b in beings_known_set):
            beings_known_set.discard(this_b)
          else:
            beings_not_found.append(this_b)
        

        #beings_found_list_I represents ordered list of new keys for impacts_Ziv.


        #handle any remaining beings in being_set were not identified
        #some known beings were not found

        # beings_known are any known beings not found in returned list
        # beings_not_found are any in the returned list not found in known set

        if(beings_known_set and beings_not_found):                        
            #if there is one known unfound and one returned unfound, assume they match and replace with each other
            if(len(beings_known_set)==len(beings_not_found)==1):
                print('\nReplacing '+beings_not_found[0]+' with: ')
                print(beings_known_set)
                beings_found_list_I.remove(beings_not_found[0]) 
                beings_found_list_I.append(beings_known_set.pop())
                
            else:
            #the main errors arise if there is a returned being not in the known_beings list
            # for each one of those, see if you can find its corresponding item by semantic sim. 
              for item in beings_not_found:
                matches = find_semantic_match(item,beings_fixed)
                beings_found_list_I.remove(item)
                rep_item = list(matches['result'].values())
                beings_found_list_I.append(rep_item[0])

        print("Scored impacts for these beings:")
        print(beings_found_list_I)
        print(list(impacts_Ziv.values()))
              
        for being,score in zip(beings_found_list_I,impacts_Ziv.values()):
            # print(being)
            # print(score)
            # Link(kind,value):
            this_link = g.add_link(Link('utility',str(score)))
            this_b_node = g.return_node(being.lstrip())[0]
            # print(being)
            this_event_node = g.return_node(this_evt_I)[0]
            this_event_node.link_link(this_link,this_b_node)
        
        for being,score in zip(beings_found_list_I,impacts_Ziv.values()):

            items_to_write = ",".join([this_evt_I,being,str(score)])
            impacts_list.append(items_to_write)

    # scenario_dict["impacts"] = impacts_list

      #write dict as json here for now
    this_output_filename_qual = DATA_DIR+'qualtrics_'+output_filename+'_choice_'+str(act_id)+'.json'
    write_json(this_output_filename_qual,[scenario_dict])
      
    # add links from beings to events
            
    # dictionaries for translating into labels
    cause = {"No": 'C-', "Yes": 'C+',"no": 'C-', "yes": 'C+'}
    know = {"No": 'K-',"Yes": 'K+',"no": 'K-',"yes": 'K+'}
    desire = {"No": 'D-', "Yes": 'D+',"no": 'D-', "yes": 'D+'}

    for this_evt,this_evt_I in zip(events_Ziv,events_I):

        # for this_being in beings_fixed_Ziv:
        # for now just for main character
        this_being = 'Ziv'
        this_being_I = 'I'
        print('\nProcessing event: ' + this_evt_I)

        #try to get the right links, ensure correct labels 
        success = 0
        count = 0
        while(success==0):        

            links = get_being_links_Ziv_only(this_scenario_Ziv, this_act_Ziv, this_evt, this_being)
            count = count+1
            
            resp=links['results'][this_being]
                
            #check that resp consists of exactly three yes or no's
            x = [y for y in resp if y in ['Yes','yes','No','no']]
            #if this works, good, otherwise set success back to 0
            if(len(x) == 3):
                success = 1
            else:
                success = 0
        
            if(count >5):
                print('\n\n***Failed to get all correct links, check your scenario.**\n\n')
            
        # for now, just do being I
        # for each being, add the link to the graph with the right label
        # for being,resp in links['results'].items():                

        this_label = cause[resp[0]] + know[resp[1]] + desire[resp[2]]   
        print('CDK links for I')
        print(this_label)            

        #create a new link
        # Link(kind,value):
        this_link = g.add_link(Link('b_link',this_label))
        this_b_node = g.return_node(this_being_I)[0]
        this_event_node = g.return_node(this_evt_I)[0]
        this_b_node.link_link(this_link,this_event_node)

    g_print = g.print_graph()
            
    this_output_filename = output_filename+'_choice_'+str(act_id)+'.json'
    print('\n\nWriting to file: '+this_output_filename)
    # write out json file
    write_jsonlines(DATA_DIR+this_output_filename,g_print)

    return (DATA_DIR+this_output_filename)
    




