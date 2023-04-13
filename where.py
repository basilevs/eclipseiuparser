#!/bin/python3
from feature import include_graph, find_node_by_id, print_sorted_with_meta
from sys import argv
from pprint import pprint


g = include_graph('.', include_dependencies=False)


def content(id):
	return set(g.predecessors(id))

if __name__ == '__main__':
	result = set()
	for i in argv[1:]:
		result.update(content(find_node_by_id(g, i)))
	print_sorted_with_meta(g,  result)