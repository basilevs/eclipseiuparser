#!/bin/python3

from networkx import DiGraph, bfs_edges, induced_subgraph, subgraph, multipartite_layout, spectral_layout, spring_layout, kamada_kawai_layout, draw_networkx_nodes, draw_networkx_edges, draw_networkx_labels
from matplotlib import pyplot
from pathlib import Path
from feature import find_feature_files, parse_feature_xml, feature_include_graph

g = feature_include_graph('.')
		
nodes = []

for root in ['com.spirent.features.itest.restagent', 'com.spirent.features.velocity.agent.cli']:
	for edge in bfs_edges(g, root):
		nodes.extend(edge[1])
	
g = induced_subgraph(g, nodes)

pos = kamada_kawai_layout(g)

draw_networkx_nodes(g, pos)
draw_networkx_edges(g, pos)
draw_networkx_labels(g, pos)
pyplot.show()