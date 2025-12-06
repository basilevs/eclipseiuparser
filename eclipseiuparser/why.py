#!/bin/python3
from functools import cache
from .feature import include_graph, find_node_by_id
from sys import argv
from networkx import ancestors, descendants
from itertools import permutations


g = include_graph('.', include_dependencies=True)


def content(source, target):
	result = set(ancestors(g, source)).intersection(descendants(g, target))
	result.add(source)
	result.add(target)
	return result

def main():
	result = set()
	origin_nodes = map(lambda id:  find_node_by_id(g, id), argv[1:])
	for i, k in permutations(origin_nodes, 2):
		result.update(content(i, k))
	subgraph = g.subgraph(result)	
	@cache
	def distance_from_root(node):
		return len(list(ancestors(subgraph, node)))
	
	sorted = list(result)
	sorted.sort(key=distance_from_root)
	for node in sorted:
		print (node)

if __name__ == '__main__':
	main()