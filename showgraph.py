#!/bin/python3

from sys import argv
from functools import cache
from math import sqrt
from pprint import pprint

from networkx import DiGraph, descendants, ancestors, induced_subgraph, subgraph, spiral_layout, multipartite_layout, spectral_layout, spring_layout, kamada_kawai_layout, draw_networkx_nodes, draw_networkx_edges, draw_networkx_labels
from matplotlib import pyplot
from pathlib import Path
from feature import parse_feature_xml, include_graph, find_node_by_id

g = include_graph('.', include_dependencies=True)

@cache
def content(id):
#	return frozenset(ancestors(g, id)) | frozenset(descendants(g, id))
	return frozenset(ancestors(g, id)).union([id])
	
subjects = set([ find_node_by_id(g, arg) for arg in argv[1:] ])
print(subjects)

result = frozenset([node for subject in subjects for node in content(subject) ])	
print(result) 
	
g = induced_subgraph(g, result)

weights = { 'product' : 1, 'feature' : 10, 'plugin' : 10 }


def prefix(node):
	return node.split(':')[0]

for f, to in g.edges:
	ws = [ weights[prefix(node)] for node in [f, to] ] 
	g.edges[f, to]['weight'] = ws[0]*ws[1]

pos = None
#for i in range(1, 10000):
#	pos = kamada_kawai_layout(g, pos=pos)

pos = spectral_layout(g)

#for node, point in pos.items():
#	if node.startswith('product:'):
#		pos[node]= (point[0], point[1] - 100)

pos = spring_layout(g, pos=pos, iterations = 10000, k=500)

fig = pyplot.figure()

def print_event(type, event):
	print('%s: %s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
		(type, 'double' if event.dblclick else 'single', event.button,
		event.x, event.y, event.xdata, event.ydata))

def button_press_event(event):
	
	print_event('button_press_event', event)

def button_release_event(event):
	print_event('button_release_event', event)
	

cid = fig.canvas.mpl_connect('button_press_event', button_press_event)
cid = fig.canvas.mpl_connect('button_release_event', button_release_event)


#pprint(pos['product:com.fnfr.svt.editions.team.iTest']) 
pprint(pos['product:com.spirent.velocity.agent.launcher.VelocityAgentProduct'])
draw_networkx_nodes(g, pos)
draw_networkx_edges(g, pos)
draw_networkx_labels(g, pos, font_size=7, clip_on=False)
pyplot.show()