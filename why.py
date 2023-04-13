#!/bin/python3
from feature import include_graph, find_node_by_id, print_sorted_with_meta
from sys import argv
from pprint import pprint
from networkx import all_simple_paths, NetworkXNoPath, has_path, ancestors, descendants
from itertools import chain
from itertools import permutations


g = include_graph('.', include_dependencies=True)


def content(source, target):
	return set(ancestors(g, source)).intersection(descendants(g, target))

if __name__ == '__main__':
	result = set()
	nodes = map(lambda id :  find_node_by_id(g, id), argv[1:])
	for i, k in permutations(nodes, 2):
		result.update(content(i, k))
	print_sorted_with_meta(g, result)