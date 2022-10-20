#!/bin/python3
from feature import include_graph, find_node_by_id, print_sorted
from sys import argv
from functools import cache
from networkx import descendants

g = include_graph('.')

@cache
def content(id):
	return set(descendants(g, id))


subjects = set([ find_node_by_id(g, arg) for arg in argv[1:] ])

for s in subjects:
	print('Included only in', s, ':')
	included = set(content(s))
	for another in subjects:
		if another == s:
			continue
		included.difference_update(content(another))
	print_sorted(included)
	
all_content = frozenset([c for subject in subjects for c in content(subject) ] )

@cache
def excluded_from(node):
	return all_content.difference(content(node))
	
for s in subjects:
	print('Excluded only from', s, ':')
	print_sorted(excluded_from(s).difference(*[ excluded_from(another) for another in subjects if another != s ]))
	


#print('Shared:')
#print_sorted(content(next(iter(subjects))).intersection(*[content(i) for i in subjects]))
