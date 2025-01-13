import utils


def get_beings(this_scenario):

    system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. The user will describe a scenario from a first-person perspective. Your task is to identify each sentient being involved, including the first-person character "I". Sentient beings are entities who are alive and have the capacity to experience the world, for example, a human or an animal. List each individual being, but do not also list groups that include all of these individual beings. Return a json object with key:value pair of "results": list of beings. Please be diligent, complete, and succinct in your response.'

    user_prompt_content = f'Here is my scenario: {this_scenario}.'

    return utils.get_response_dict(system_prompt_content, user_prompt_content)
        
def get_events(this_scenario, this_act):

    system_prompt_content = f"""You are an expert at understanding human situations. A human named Ziv has described a scenario and how they decided to act. Your task is to identify all the outcomes that will probably occur as a result of Ziv's action decision, especially any impacts on sentient beings involved. Please state each outcome as the most simple, immediately occuring result, and not chains of events. Describe the outcomes referring to Ziv using their name, not pronouns. Return a json object with key:value pair of "results": list of events. Please be diligent, complete, and succinct in your response."""
    # print(system_prompt_content)
    user_prompt_content = f'Here is Ziv\'s scenario: {this_scenario}. Ziv decided to {this_act}. What outcomes are likely to arise a result of Ziv\'s decision?'

    return utils.get_response_dict(system_prompt_content, user_prompt_content)
           
def convert_Ziv_I(old_sentence):
   
  #  function to turn Ziv into first person for output
  #  use a call to GPT to do this. 
  this_resp=utils.get_response_dict("You are an expert in English grammar. Rewrite the following text so that it is written in the first person perspective instead of in the third person about Ziv, replacing each reference to Ziv by name or pronoun with the correct first-person pronoun (I, me, or my). Return a json called 'converted sentence' with the converted text only.", old_sentence)
  this_key=list(this_resp.keys())
  new_sentence = this_resp[this_key[0]]

  return(new_sentence)
        
def convert_Ziv_I_item(old_item):
   
  #  function to turn Ziv into first person for output
  #  use a call to GPT to do this. 
  this_resp=utils.get_response_dict("You are an expert in English grammar. Take this phrase and replace each reference to the person Ziv with a first-person pronoun (I, me, or my). If Ziv is not explicitly mentioned, return the original text. Return a json called 'converted sentence' with the converted text only.", old_item)
  this_key=list(this_resp.keys())
  new_sentence = this_resp[this_key[0]]

  return(new_sentence)

def convert_I_Ziv_item(old_item):
   
  #  function to turn Ziv into first person for output
  #  use a call to GPT to do this. 
  this_resp=utils.get_response_dict("You are an expert in English grammar. Take this phrase and replace each mention of the first-person pronouns I, me, or my with the name Ziv or Ziv's. If I, me, or my is not present, return the original text. Return a json called 'converted sentence' with the converted text only.", old_item)
  this_key=list(this_resp.keys())
  new_sentence = this_resp[this_key[0]]

  return(new_sentence)
  
def convert_I_Ziv(old_sentence):
    
    this_resp=utils.get_response_dict("You are an expert in English grammar. Rewrite the following text so that it is written from the perspective of a character name Ziv in third person instead of being written in the first person. Replace every instance of the first person pronoun (I, me, my, etc) with either the name Ziv or the pronouns they, their, them, etc. Return a json called 'converted text' with the converted text only.", old_sentence)

    this_key=list(this_resp.keys())
    new_sentence = this_resp[this_key[0]]

    return(new_sentence)
   
def convert_lower(sentence):
    # convert to lower case except instances of Ziv
    new_s = sentence.lower()
    new_s = new_s.replace("ziv","Ziv")
    new_s = new_s.replace("ziv's","Ziv's")

    return new_s

# pass list of values and score their importance
def score_values(this_scenario, this_act, values_list):
   
   system_prompt_content = f"""You are an expert on human values and actions. The user will share a situation and an action they took, plus a list of values and anti-values that the action might have exhibited. Please rate to what extent the action is characterized by each value or anti-value. Use a scale of 0 to 100, where 0 indicates that this value or anti-value does not characterize this action, and 100 indicates that it very much characterizes this action. Return a json object with each value as a key and your rating as a value."""

   user_prompt_content = f"Here is my situation. {this_scenario} My action is to {this_act} To what extent is this action characterized by these values and anti-values? {values_list}"     



   return utils.get_response_dict(system_prompt_content, user_prompt_content)


#    system_prompt_content = f"""You are an expert on what humans value and don't value. The user will share an action they chose to take in a situation. Your task is to identify the values and virtues that the user exhibits by taking this action. Return a json object called 'values' listing the values and nothing more."""
          
#     user_prompt_content = f"""Here is my scenario. {this_scenario} My action is to {this_act} List the virtues and values of this action."""

def get_value_positive(this_scenario, this_act):

    system_prompt_content = f"""You are an expert on human values. The user will share a situation and an action they decided to take. Identify the most important positive values and virtues that characterize this action. Return a json object called 'values' listing the values and nothing more."""
          
    user_prompt_content = f"""Here is my scenario. {this_scenario} My action is to {this_act} List the most important values and virtues exhibited by this action."""

   

    return utils.get_response_dict(system_prompt_content, user_prompt_content)

def get_value_negative(this_scenario, this_act):

    system_prompt_content = f"""You are an expert on human vices. The user will share a situation and an action they decided to take. Identify the most important anti-values and vices that characterize this action. Return a json object called 'anti-values' listing the vices and nothing more."""
          
    user_prompt_content = f"""Here is my scenario. {this_scenario}. My action is to {this_act} List the most important vices exhibited by this action."""
         

    return utils.get_response_dict(system_prompt_content, user_prompt_content)




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
        return utils.get_response_dict(system_prompt_content, user_prompt_content)


def get_impacts_Ziv_multi(this_scenario, this_act, this_event, these_beings):

        system_prompt_content = f"You are a helpful assistant who is an expert at understanding human situations. The following scenario is context for the user's question. {this_scenario} {this_act}  End of scenario. Suppose this leads to the outcome that {convert_lower(this_event)} Please rate how this specific outcome, on its own without considering any further consequences, is likely to directly and immediately impact each character listed by the user. Use a scale from -10 to +10, where -10 indicates that the outcome will immediately and directly cause the character substantial harm, and +10 indicates that it will immediately and directly cause the character substantial benefit. If you are not sure that the outcome will immediately and directly affect the character, return a rating of 0 or close to 0. Please evaluate only the immediate, direct impact of the event on its own, without considering any further consequences or outcomes downstream. Return a json object called 'results' with a key:value pair for being: rating."        
        
        user_prompt_content = f'Consider the event that {convert_lower(this_event)} Without considering any further consequences of this event, how does this event by itself directly impact each of these characters: {these_beings}?'

        # print(system_prompt_content, user_prompt_content)
        return utils.get_response_dict(system_prompt_content, user_prompt_content)


def find_semantic_match(item,list1):
  system_prompt_content = f"You are helpful assistant. You will be given a word or phrase and a list. Find the item in the list that is most similar in meaning to the word or phrase given. Return a json called 'result' with the word/phrase as key and the item as value."
  user_prompt_content = f"Here is my list: {list1}. Return the item in the list is most similar to the meaning of this word or phrase: {item}"
            
  return utils.get_response_dict(system_prompt_content, user_prompt_content)

def get_impacts_Ziv_noscenario(this_scenario, this_act, this_event, these_beings):

        system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations. You will be given a description of an event and asked to evaluate how this event on its own (without considering any further consequences) is likely to impact the listed characters. Rate the direct impact on each character using a scale from -10 to +10, where a rating of -10 indicates that the outcome will directly cause the character substantial harm, while a rating of +10 indicates that it will directly cause the character substantial benefit. Please evaluate only the immediate, direct impact of the event on its own, without considering any further consequences or outcomes downstream. If you are not sure that the outcome will immediately and directly affect the character very much, return a rating of 0 or close to 0. Return a json object called "results" with a key:value pair for being: rating.'

        user_prompt_content = f'Consider the event that {convert_lower(this_event)} Without considering any further consequences of this event, how does this event by itself directly impact each of these characters: {these_beings}?'

        # print(system_prompt_content, user_prompt_content)
        return utils.get_response_dict(system_prompt_content, user_prompt_content)

# def get_being_links(this_scenario, this_act, this_event, beings):
        
#         system_prompt_content = f'You are a helpful assistant who is an expert at understanding human situations and causality. The user will describe a scenario from a first-person perspective. The user decided on an action decision and an event resulted. Please answer 3 questions regarding the sentient beings in the scenario. For each being, (1) did they directly cause the event? Causality means that the event would not have happened if the being did not act. (2) Did they know the event would happen, knowing that the action was taken? (3) Did they want or desire for the event to occur? Each question has a yes or no answer. Return a json object with entry "results", containing the exact name of each being as provided as keys, and your answer as the value, where answer is an ordered list of answers to the 3 questions.'

#         user_prompt_content = f'Here is my scenario: {this_scenario}. It involves these beings: {beings}. \
#         I decide to {this_act}, which results in this event: {this_event}. For each being, please answer the three questions relating to the event.'

#         print(system_prompt_content, user_prompt_content)

#         return utils.get_response_dict(system_prompt_content, user_prompt_content)


def get_being_links_Ziv_only(this_scenario, this_act, this_event, this_being):
        
        system_prompt_content = f"""You are a helpful assistant who is an expert at understanding human situations. You will recieve a scenario about a person named Ziv, an action they took, and an outcome that took place. Answer three questions. 1) Did Ziv directly cause the outcome? If they caused it, it would not occur if they had not acted. 2) Did Ziv expect it would happen as a result of the action?  3) Did Ziv intend for this outcome to occur, either by taking the action or by planning for it? Each question has a yes or no answer. Return a json object with an entry named "results" containing a key with the name of the character, Ziv, and a value with the ordered list of answers to the three questions."""

        user_prompt_content = f"Here is the scenario: {this_scenario}. {this_act}, resulting in this outcome: {this_event}. For the character {this_being}, please answer the three questions relating to the outcome."         

        return utils.get_response_dict(system_prompt_content, user_prompt_content)

# def get_being_links_Ziv(this_scenario, this_act, this_event, this_being):
        
#         system_prompt_content = f"""You are a helpful assistant who is an expert at understanding human situations. You will recieve a scenario about a person named Ziv, an action they took, and an outcome resulting from that action. You will also be given the name of a character. Consider how this character relates to the outcome. Answer three questions. 1) Did they directly cause the outcome? If they caused it, it would not occur if they had not acted. 2) Did they expect it would happen as a result of the action? and 3) Did they intend for this outcome to occur? Each question has a yes or no answer. Return a json object with an entry named "results" containing a key with the name of the character and a value with the ordered list of answers to the three questions."""

#         user_prompt_content = f"Here is the scenario: {this_scenario}. Ziv chose to {this_act}, resulting in this outcome: {this_event}. For the character {this_being}, please answer the three questions relating to the outcome."         

#         return utils.get_response_dict(system_prompt_content, user_prompt_content)
