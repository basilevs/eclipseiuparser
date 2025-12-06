#!/bin/python3
from feature import include_graph, find_node_by_id, print_sorted
from sys import argv
from pprint import pprint
from networkx import ancestors


g = include_graph('.')


def content(id):
	return set(g.predecessors(id))

def main():
	result = set()
	for i in argv[1:]:
		result.update(content(find_node_by_id(g, i)))
	print_sorted(result)

if __name__ == '__main__':
	main()