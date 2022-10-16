#!/bin/python3
from feature import feature_include_graph
from sys import argv
from pprint import pprint
from functools import cache
from networkx import descendants

g = feature_include_graph('.')

def get_plugins(f):
	return g.nodes[f].get('plugins', frozenset())

@cache
def plugins(id):
	result = set()
	result.update(*[ get_plugins(f) for f in included_features(id)])
	return result


@cache
def content(id):
#	return plugins(id)
	return set(descendants(g, id))
	
def print_sorted(data):
	for line in sorted(data):
		print(line)
	

#for s in subjects:
#	print('Content in', s)
#	print_sorted(content(s))
		

def find_node_by_id(id):
	result = [p+id for p in ['', 'plugin:', 'feature:', 'product:'] if g.has_node(p+id)]
	if len(result) > 1:
		raise KeyError("Multiple elements found: " + result)
	if not result: 
		raise KeyError("Can't find " + id)
	return result[0] 

subjects = set([ find_node_by_id(arg) for arg in argv[1:] ])

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
	


print('Shared:')
print_sorted(content(next(iter(subjects))).intersection(*[content(i) for i in subjects]))
