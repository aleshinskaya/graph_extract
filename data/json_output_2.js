<html>
<head>
<script type='text/javascript'    
src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js'></script>    
	<style type='text/css'>      
  #mynetwork {        
		width: 800px;         
		height: 800px;         
		border: 1px solid lightgray;       
	 }   
	 </style>
</head>
<body>
<script type="text/javascript">    

function window.onload {       
		launch_visualization()    
}    
function launch_visualization() {         
	this_dset =  return_vis_dataset()        
	nodes = this_dset[1]        
	edges = this_dset[0]        
	// create a network        
	var container = document.getElementById("mynetwork");        
	var data = {            
		nodes: nodes,            
		 edges: edges         
};     
var options = {};       
 // initialize your network!         
	var network = new vis.Network(container, data, options);    
}    
<div id="mynetwork"></div>"function return_vis_dataset() {
	var nodes = new vis.DataSet([ 
		{id: 1, label: 'I'},
		{id: 2, label: 'person on the bike'},
		{id: 3, label: 'boss'},
		{id: 4, label: 'stop to help and be late for work'},
		{id: 5, label: 'I am late for my first day of work, which may create a negative impression on my boss and colleagues.'},
		{id: 6, label: 'The person who crashed their bike may be injured and in need of assistance.'},
		{id: 7, label: 'I may miss out on important instructions or training at the beginning of my shift.'},
		{id: 8, label: 'My willingness to help someone in need may be appreciated by the person I assist and others who witness the situation.'},
		{id: 9, label: 'I may feel a sense of guilt or anxiety about being late for work and the potential consequences of my tardiness.'},
		{id: 10, label: 'My decision to stop and help may demonstrate my values and character to my boss and colleagues, potentially earning their respect in the long run.'}
		]);
	var edges = new vis.DataSet([ 
		{from: 1, to: 4, label: 'b-link_C+D+K+'},
		,
		{from: 4, to: 5, label: 'e_link_'},
		{from: 4, to: 6, label: 'e_link_'},
		{from: 4, to: 7, label: 'e_link_'},
		{from: 4, to: 8, label: 'e_link_'},
		{from: 4, to: 9, label: 'e_link_'},
		{from: 4, to: 10, label: 'e_link_'},
		,
		{from: 6, to: 1, label: 'utility_-7'},
		{from: 6, to: 2, label: 'utility_8'},
		{from: 6, to: 3, label: 'utility_-5'},
		
		]);

	return ([edges,nodes])

    }
</script>
</body>
</html>