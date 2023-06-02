#!/bin/python3
from feature import include_graph, find_node_by_id, print_sorted_with_meta
from sys import argv
from pprint import pprint
from networkx import ancestors


g = include_graph('.', include_dependencies=True)


def content(id):
    return set(ancestors(g, id))


if __name__ == '__main__':
    result = set()
    for i in argv[1:]:
        result.update(content(find_node_by_id(g, i)))
    subgraph = g.subgraph(result)

    def distance_from_root(node):
        return len(list(ancestors(subgraph, node)))
    sorted = list(result)
    sorted.sort(key=distance_from_root)
    for node in sorted:
        print(node)
