#!/bin/python3
from .feature import include_graph, find_node_by_id, print_sorted
from sys import argv
from networkx import descendants, ancestors

g = include_graph('.')

def content(id):
	return set(descendants(g, id))


subjects = set([ find_node_by_id(g, arg) for arg in argv[1:] ])
content = set.intersection( *[ content(subject) for subject in subjects ] )
subgraph = g.subgraph(content)

def distance_from_root(node):
	return len(list(ancestors(subgraph, node)))

def count_dependencies(id):
	return len(set(descendants(g, id)))

def main():
	content = sorted(content, key=distance_from_root)
	for line in content:
		print(line)

if __name__ == '__main__':
    main()
