#!/bin/python3
from feature import include_graph, find_node_by_id, print_sorted
from sys import argv
from functools import cache
from networkx import descendants, ancestors

g = include_graph('.', include_dependencies=True)


subjects = set([find_node_by_id(g, arg) for arg in argv[1:]])


def compare_by(content, label):
    print("Common", label + ":")
    print_sorted(set.intersection(*[content(subject) for subject in subjects]))

    for s in subjects:
        print(label, "only from", s + ":")
        included = set(content(s))
        for another in subjects:
            if another == s:
                continue
            included.difference_update(content(another))
        print_sorted(included)

    all_content = frozenset(
        [c for subject in subjects for c in content(subject)])

    @cache
    def excluded_from(node):
        return all_content.difference(content(node))

    for s in subjects:
        print(label, 'not in', s+':')
        print_sorted(excluded_from(s).difference(
            *[excluded_from(another) for another in subjects if another != s]))


@cache
def dependencies(id):
    return set(descendants(g, id))


@cache
def parents(id):
    return set(ancestors(g, id))

compare_by(parents, 'anscestors')
compare_by(dependencies, 'dependencies')
