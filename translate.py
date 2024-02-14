import os
from dotenv import dotenv_values
from dotenv import load_dotenv
import json, jsonlines
import requests
import pandas as pd
import numpy as np
import typer


# set some environment and global variables
load_dotenv() 
global config
config = dotenv_values(".env")

CUR_DIR = os.path.dirname(os.path.abspath(__name__))
DATA_DIR = CUR_DIR+'/data/'
VIS_JS_FORMAT = "{id: %d, label: '%s'}"
VIS_JS_FORMAT_LINK = "{from: %d, to: %d, label: '%s'}"

HEADER = "<html>\n<head>\n<script type='text/javascript'\
    \nsrc='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js'></script>\
    \n\t<style type='text/css'>\
      \n  #mynetwork {\
        \n\t\twidth: %dpx;\
         \n\t\theight: %dpx;\
         \n\t\tborder: 1px solid lightgray;\
       \n\t }\
   \n\t </style>\
\n</head>\
\n<body>\
\n<div id='mynetwork'></div>\n"
    

BODY = '\n<script type="text/javascript">\
    \n\nwindow.onload = function(){\
       \n\t\tlaunch_visualization()\
    \n}\
    \nfunction launch_visualization() { \
        \n\tthis_dset =  return_vis_dataset()\
        \n\tnodes = this_dset[1]\
        \n\tedges = this_dset[0]\
        \n\t// create a network\
        \n\tvar container = document.getElementById("mynetwork");\
        \n\tvar data = {\
            \n\t\tnodes: nodes,\
            \n\t\t edges: edges\
         \n\t\t};\
    \n\tvar options = {};\
\
       \n // initialize your network!\
         \n\tvar network = new vis.Network(container, data, options);\
    \n}\n'
    

CODA = '\n</script>\
\n</body>\
\n</html>'



json_file = 'json_output_2.jsonl';
main(json_file)

def main(json_file: str = typer.Option(None, help="name of json file to use")):

    # define reader 
    reader = jsonlines.open(DATA_DIR+json_file, 'r')

    # get every node from the input file and store in list
    node_list = list(reader)

    #graph size
    n_nodes = len(node_list)

    width = n_nodes * 80
    height = n_nodes * 80



    # define output file
    output_file = open(DATA_DIR+json_file.split('.json')[0]+'.html','w')    

    #write and fill in header
    output_file.write(HEADER % (width, height))
    output_file.write(BODY)

    # define initial function and variable in the output file
    output_file.write("""function return_vis_dataset() {\n\tvar nodes = new vis.DataSet([ \n\t\t""")
    

    # iterate through nodes and write them to node datastructure in js file
    # create list of nodes
    # store labels
    node_labs_list = {}
    for ind,item in enumerate(node_list):        
        
        this_lab = item['node']['label']
        this_line = VIS_JS_FORMAT % (ind+1, this_lab)
        node_labs_list[this_lab ] = ind
        if(ind<(len(node_list)-1)):
            this_line=this_line+',\n\t\t'
        else:
            this_line=this_line+'\n\t\t]);'
       
        output_file.write(this_line)
    
    output_file.write('\n\tvar edges = new vis.DataSet([ \n\t\t')

    # print(node_list)

    # create list of edges for each node
    # loop through each node and write out each of its links!


    for node_ind,item in enumerate(node_list):        
        
        this_node_lab = item['node']['label']        
        these_links = item['links'] 
        

        is_last_node = node_ind==(len(node_list)-1)
        is_first_node = node_ind==0

        #decide if we will close this list or not.. 
        if(is_last_node and len(these_links)==0):
            output_file.write('\n\t\t]);')
        elif(is_first_node==False and len(these_links)>0):
            output_file.write(',\n\t\t')

        for link_ind,link in enumerate(these_links):

            link_lab  = link['link']['kind']+"_"+link['link']['value']
            from_node = node_ind+1
            to_node = node_labs_list[link['to_node']]+1
            this_line = VIS_JS_FORMAT_LINK % (from_node, to_node, link_lab)       

            #add a comma only if there are more links to list
            if(link_ind<len(these_links)):
                this_line=this_line+',\n\t\t'
            if(is_last_node):
                this_line=this_line+'\n\t\t]);'

            output_file.write(this_line)

    
    output_file.write('''\n
	return ([edges,nodes])\n
    }''')

    output_file.write(CODA)
                      
    output_file.close()


    # TO DO: add more annotations; color the nodes based on type; see what else we can do with this graph!



    # an array with edges
    # var edges = new vis.DataSet([
    #     {from: 1, to: 3, label: 'test'},
    #     {from: 1, to: 2},
    #     {from: 2, to: 4},
    #     {from: 2, to: 5}
    # ]);
        


   


    # // create an array with nodes
    # var nodes = new vis.DataSet([
    #     {id: 1, label: 'Node 1'},
    #     {id: 2, label: 'Node 2'},
    #     {id: 3, label: 'Node 3'},
    #     {id: 4, label: 'Node 4'},
    #     {id: 5, label: 'Node 5'}
    # ]);

    # // create an array with edges
    # var edges = new vis.DataSet([
    #     {from: 1, to: 3, label: 'test'},
    #     {from: 1, to: 2},
    #     {from: 2, to: 4},
    #     {from: 2, to: 5}
    # ]);

# class Node():


#   def __init__ (self,label,kind):
#     self.label = label
#     self.kind = kind
#     self.links = list()

#   def add_link(self,a_link,a_node):
#     x = (a_link,a_node)
#     self.links.append(x)

#   def print(self):

if __name__ == "__main__":
    typer.run(main)