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
import importlib

# local imports

import get_emb_distances
import prompts
import node
import utils


importlib.reload(get_emb_distances)

importlib.reload(prompts)
importlib.reload(node)
importlib.reload(utils)

# set some environment and global variables
load_dotenv() 
global config
config = dotenv_values(".env")

CUR_DIR = os.path.dirname(os.path.abspath(__name__))
DATA_DIR = CUR_DIR+'/data/'



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


def process_beings(this_scenario,this_act,g):

  beings = prompts.get_beings(this_scenario)
  beings_fixed = fix_I(fix_braces(beings['results']))        
  beings_fixed_Ziv = [prompts.convert_I_Ziv_item(x) for x in beings_fixed]

  print("\nIdentified these entities: \n\n"+"\n".join(beings_fixed))

  beings_list = ",".join(beings_fixed)

  #add each being to the graph
  for b in beings_fixed:
      #create new node & add to graph               
      g.add_node(node.Node(b,'being'))

  #create link between being "I" and action choice
  this_being_node = g.return_node("I")[0]
  act_node = g.add_node(node.Node(this_act,'action_choice'))
  # Link(kind,value):
  this_link = g.add_link(node.Link('b-link','C+D+K+'))
  this_being_node.link_link(this_link,act_node)

  return [beings_fixed,beings_fixed_Ziv,beings_list]

def process_values(this_scenario, this_act_I, this_act, g):
   
  # elicit action virtues and vicces
  values_positive = prompts.get_value_positive(this_scenario, this_act_I)
  print('\nvalues:')
  values_positive=get_emb_distances.threshold_by_sim(values_positive,.06)
  print(values_positive)
  values_negative = prompts.get_value_negative(this_scenario, this_act_I)
  values_negative=get_emb_distances.threshold_by_sim(values_negative,.06)
  print(values_negative)
  #combine positive and negative values into a single list
  all_values = {}
  all_values.update(values_positive)
  all_values.update(values_negative)
  all_values_flat = []
  all_values_flat.extend(all_values['values'])  
  all_values_flat.extend(all_values['anti-values'])
  all_values_flat_list = [x.lower() for x in all_values_flat]
  #score action virtues
  all_values_scored = prompts.score_values(this_scenario, this_act_I,', '.join(all_values_flat_list))

  # create nodes and links for these items 
  for value in all_values_scored.items() : 
      # print(value)       
      this_name = value[0]
      this_score = value[1]        
      # create node and add it to graph
      this_v_node = g.add_node(node.Node(this_name,'value'))
      # create link with score
      this_link = g.add_link(node.Link('v-link',str(this_score)))
      # connect it to the action node    
      act_node = g.return_node(this_act)[0]             
      act_node.link_link(this_link,this_v_node)

  return (all_values_scored,all_values_flat_list)

def evaluate_values(processed_values, this_scenario, this_act_I, all_human_data):  
   
    #for evaluation: score values from annotation list
    #then compare with human value score data
    hd_value_names = list(all_human_data['value_scores'].keys())
    hd_value_scores = all_human_data['value_scores'].values()


 
    if type(all_human_data['values_missing'])=='str' and not np.isnan(all_human_data['values_missing']):
      hd_values_missing =set([x.lower() for x in all_human_data['values_missing'].split(',')])
    else:
      hd_values_missing = set()
    hd_highrated_valuenames = set([x for x in hd_value_names if all_human_data['value_scores'][x] > 70])

    #print the high rated values
    print('High-rated values:')
    print(hd_highrated_valuenames)
    #print the missing values
    print('Missing values:')
    print(hd_values_missing)

    #does the list of values generated overlap with those rated highly by humans? by how much?
    model_values = set(processed_values[1])
    common_list = model_values.intersection(hd_highrated_valuenames)
    print('Common high-rated values:')
    print(common_list)

    #compute percent overlap - of the model generated values, how many were highly rated?
    overlap = len(common_list)/len(model_values)
    print('Percent overlap with high-rated values: %.2f' %overlap)


    # re-score values from annotation data already collected to evaluate the importance scoring
    annot_values_scored = prompts.score_values(this_scenario, this_act_I,', '.join(hd_value_names))

   # compare to scores from human data
    #assert that the two dictionaries have the same keys  
    assert set(all_human_data['value_scores'].keys()) == set(annot_values_scored.keys()) 
    #run correlation on their values
    annot_values_scored_values = list(annot_values_scored.values())
    hd_value_scores_values = list(all_human_data['value_scores'].values())
    annot_values_scored_values = [float(x) for x in annot_values_scored_values]
    hd_value_scores_values = [float(x) for x in hd_value_scores_values]
    print("scored values:")
    print(annot_values_scored)
    print("human data:")
    print(all_human_data['value_scores'])
    #calculate correlation
    corr = np.corrcoef(annot_values_scored_values,hd_value_scores_values)
    print('Value score correlation with human data: %.2f' %corr[0,1])

def process_outcomes(this_scenario, this_act):   

  #get all outcome events arising from the action
  events = prompts.get_events(this_scenario, this_act)
  events_Ziv= events['results']
  # remove overly similar outcomes
  events_Ziv=get_emb_distances.threshold_by_sim(events_Ziv,.06)
  
  #replace Ziv with first person pronoun.        
  events_I = [prompts.convert_Ziv_I(x) if x.find("Ziv")>-1 else x for x in events_Ziv]   

  return(events_Ziv,events_I)

def process_impacts(this_scenario_Ziv, this_act, this_act_Ziv, events_Ziv, events_I, beings_fixed_Ziv, g):


  act_node = g.return_node(this_act)[0]   

  #create list of impacts on each being
  impacts_list = []
  for this_evt_Ziv, this_evt_I in zip(events_Ziv,events_I):

    print('\nProcessing impacts of event: '+this_evt_I)

    #create a node for this "event"
    this_out_node = g.add_node(node.Node(this_evt_I,'event'))

    #create a link between act and event
    this_link = g.add_link(node.Link('e_link',''))
    act_node.link_link(this_link,this_out_node)

    beings_string = ', '.join(beings_fixed_Ziv)

    impacts_Ziv = prompts.get_impacts_Ziv_multi(this_scenario_Ziv, this_act_Ziv, this_evt_Ziv, beings_string) 
    try:        
      impacts_Ziv = impacts_Ziv['results']
    except:
      pass

    # try to align the returned beings list with the known beings list
    # create Ziv version of beings
    # convert both into sets
    beings_known_set = set(beings_fixed_Ziv)
    beings_found_list = list(impacts_Ziv.keys())

    # beings_found_list_I = []
    # for x in beings_found_list:
    #   if(x!='I'):
    #         x=x.lower()                
    #   beings_found_list_I.append(prompts.convert_Ziv_I_item(x))

    beings_not_found = []
    for this_b in beings_found_list:
      # is it listed exactly in beings list? great, remove it!
      # print(this_b)
      if(this_b in beings_known_set):
        beings_known_set.discard(this_b)
      else:
        beings_not_found.append(this_b)
      #beings_found_list represents ordered list of new keys for impacts_Ziv.


    #handle any remaining beings in being_set were not identified
    #some known beings were not found
    # beings_known are any known beings not found in returned list
    # beings_not_found are any in the returned list not found in known set
    if(beings_known_set and beings_not_found):                        
          #if there is one known unfound and one returned unfound, assume they match and replace with each other
          if(len(beings_known_set)==len(beings_not_found)==1):
              print('\nReplacing '+beings_not_found[0]+' with: ')
              print(beings_known_set)
              beings_found_list.remove(beings_not_found[0]) 
              beings_found_list.append(beings_known_set.pop())
              
          else:
          #the main errors arise if there is a returned being not in the known_beings list
          # for each one of those, see if you can find its corresponding item by semantic sim. 
            for item in beings_not_found:
              matches = prompts.find_semantic_match(item,beings_fixed_Ziv)
              beings_found_list.remove(item)
              rep_item = list(matches['result'].values())
              beings_found_list.append(rep_item[0])

    print("Scored impacts for these beings:")
    print(beings_found_list)
    scored_values = list(impacts_Ziv.values())
    
    #add node links, converting Ziv to I again
    #convert item "Ziv" to "I" in beings_found_list

    beings_found_list_I = [prompts.convert_Ziv_I_item(x) for x in beings_found_list]  

    for being,score in zip(beings_found_list_I,scored_values):
        # print(being)
        # print(score)
        # Link(kind,value):
        this_link = g.add_link(node.Link('utility',str(score)))
        this_b_node = g.return_node(being.lstrip())[0]
        # print(being)
        this_event_node = g.return_node(this_evt_I)[0]
        this_event_node.link_link(this_link,this_b_node)
        items_to_write = ",".join([this_evt_I,being,str(score)])
        impacts_list.append(items_to_write)

  return(impacts_list)

def process_causal_links(this_scenario_Ziv, events_Ziv, events_I, this_act_Ziv,g):
   
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

            links = prompts.get_being_links_Ziv_only(this_scenario_Ziv, this_act_Ziv, this_evt, this_being)
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
        this_link = g.add_link(node.Link('b_link',this_label))
        this_b_node = g.return_node(this_being_I)[0]
        this_event_node = g.return_node(this_evt_I)[0]
        this_b_node.link_link(this_link,this_event_node)

# scenario json must be a single line with scenario json with entries 'id', 'text', and 'options' {1:, 2: , etc}
def main(scenario_json,output_filename,act_id,all_human_data):
   
   # validate the scenario json
    assert isinstance(scenario_json['id'],int)
    assert scenario_json['text']
    assert scenario_json['options']

    print(output_filename)
    
    # get the action choice and convert to various pronoun options
    this_act = scenario_json['options'][act_id]
    this_act_I = "I decide to " + this_act
    this_act_Ziv = prompts.convert_I_Ziv(this_act_I)
    print('\n\nProcessing choice '+act_id +', '+this_act) 

    #get the scenario and convert to various pronoun options
    this_scenario = scenario_json['text']
    this_scenario_Ziv = prompts.convert_I_Ziv(this_scenario)

    # create a dictionary to write out to csv later
    scenario_dict = {'scenario': this_scenario, 'scenario_idx': scenario_json['id'],
                      'choice': this_act_I}
    
    #initialize Graph object    
    g = node.Graph()
    g.reset()        

    #BEINGS
    # identify all sentient beings
    returned_beings = process_beings(this_scenario,this_act,g)
    beings_fixed = returned_beings[0]
    beings_fixed_Ziv = returned_beings[1]
    beings_list = returned_beings[2]

    #g.print_graph()
    #update the scenario dict with the beings
    scenario_dict["entities"]= beings_list

    #VALUE SCORES
    #get all values and anti-values

    importlib.reload(prompts)
    processed_values  = process_values(this_scenario, this_act_I, this_act,g) 

    all_values_scored = processed_values[0]
    scenario_dict["values"]= processed_values[1]
    print(processed_values[1])
    
    #compare to human data
    evaluate_values(processed_values,this_scenario, this_act_I, all_human_data)
    
    # #OUTCOMES
    processed_events = process_outcomes(this_scenario, this_act)
    events_I= processed_events[1]
    events_Ziv= processed_events[0]
    # print("\n".join(events_I))         
    scenario_dict["outcomes"]= events_I

    # #UTILITIES
    impacts_list = process_impacts(this_scenario_Ziv, this_act, this_act_Ziv, events_Ziv, events_I,beings_fixed_Ziv,g) 

    # #CAUSAL AND INTENTIONAL LINKS
    process_causal_links(this_scenario_Ziv, events_Ziv, events_I, this_act_Ziv,g)    

    # #write scenario dict as json for qualtrics output
    # this_output_filename_qual = DATA_DIR+'qualtrics_'+output_filename+'_choice_'+str(act_id)+'.json'
    # write_json(this_output_filename_qual,[scenario_dict])     
            
    this_output_filename = output_filename+'_choice_'+str(act_id)+'.json'
    print('\n\nWriting to file: '+this_output_filename)

    # # write out json file with the full graph
    g_print = g.print_graph()
    utils.write_jsonlines(DATA_DIR+this_output_filename,g_print)

    print('\n\n')

    return (DATA_DIR+this_output_filename)





