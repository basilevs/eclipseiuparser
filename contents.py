#!/bin/python3
from feature import include_graph, find_node_by_id
from sys import argv
from pprint import pprint
from networkx import descendants

def print_sorted(data):
	for line in sorted(data):
		print(line)
		
g = include_graph('.')

def content(id):
	return set(descendants(g, id))

if __name__ == '__main__':
	result = set()
	for i in argv[1:]:
		result.update(content(find_node_by_id(g, i)))
	print_sorted(result)
