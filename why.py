#!/bin/python3
from functools import cache
from feature import include_graph, find_node_by_id, print_sorted_with_meta
from sys import argv
from pprint import pprint
from networkx import all_simple_paths, NetworkXNoPath, has_path, ancestors, descendants
from itertools import chain
from itertools import permutations


g = include_graph('.', include_dependencies=True)


def content(source, target):
	result = set(ancestors(g, source)).intersection(descendants(g, target))
	result.add(source)
	result.add(target)
	return result


def find_root(graph, node):
	try:
		return next(ancestors(graph, node))
	except StopIteration:
		return node


if __name__ == '__main__':
	result = set()
	origin_nodes = map(lambda id:  find_node_by_id(g, id), argv[1:])
	for i, k in permutations(origin_nodes, 2):
		result.update(content(i, k))
	#print(result)
	subgraph = g.subgraph(result)
#	for n, d in  subgraph.in_degree():
#		print(n, d)
	roots = set([n for n, d in subgraph.in_degree() if d == 0])
	#print("Roots:", roots)
	
	@cache
	def distance_from_root(node):
		return len(list(ancestors(subgraph, node)))
	
	sorted = list(result)
	sorted.sort(key=distance_from_root)
	for node in sorted:
		print (node, '\t', subgraph.nodes[node]['file'])
	
	#print_sorted_with_meta(g, result)
