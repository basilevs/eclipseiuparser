#!/bin/python3
from feature import include_graph, find_node_by_id, print_sorted
from sys import argv
from networkx import descendants

g = include_graph('.')

def content(id):
	return set(descendants(g, id))


subjects = set([ find_node_by_id(g, arg) for arg in argv[1:] ])
content = set.intersection( *[ content(subject) for subject in subjects ] )

print_sorted(content)
