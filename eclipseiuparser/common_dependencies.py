#!/bin/python3
from functools import cache
from feature import include_graph, find_node_by_id, print_sorted_with_meta
from sys import argv
from pprint import pprint
from networkx import all_simple_paths, NetworkXNoPath, has_path, ancestors, descendants
from itertools import chain
from itertools import permutations


g = include_graph('.', include_dependencies=True)


def content(node):
	result = set(descendants(g, node))
	result.add(node)
	return result

def main():
	# parse command line argument --exclude
	exclude = set()
	for i, arg in enumerate(argv):
		if arg == '--exclude':
			exclude.update(argv[i+1].split(','))
			del argv[i:i+2]

	result = set()
	origin_nodes = map(lambda id:  find_node_by_id(g, id), argv[1:])
	exclude_nodes = set(map(lambda id:  find_node_by_id(g, id), exclude))
	
	for node in list(exclude_nodes):
		exclude_nodes.update(content(node))
	
	#remove excluded nodes from the graph
	g.remove_nodes_from(exclude_nodes)

	for origin in origin_nodes:
		if result:
			result.intersection_update(content(origin))
		else:
			result.update(content(origin))
	#print(result)
	subgraph = g.subgraph(result)

	@cache
	def distance_from_root(node):
		return len(list(ancestors(subgraph, node)))

	sorted = list(result)
	sorted.sort(key=distance_from_root)
	for node in sorted:
		proxy = subgraph.nodes[node]
		try:
			print(node, '\t', proxy.get('file', ''))
		except:
			raise ValueError("Failed to process " + node)


if __name__ == '__main__':
	main()