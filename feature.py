#!/bin/python3

from xml.etree import ElementTree
from xml.etree.ElementTree import XMLParser
from uuid import uuid1
from os.path import dirname, abspath, join
from pathlib import Path
from networkx import DiGraph


def find_feature_files(path):
	return Path(path).rglob("feature.xml")


def parse_feature_xml(file):
	tree = ElementTree.parse(file)
	return (
		tree.getroot().attrib['id'],
		[node.attrib['id'] for node in tree.findall("includes") or []],
		[node.attrib['id'] for node in tree.findall("plugin") or []]
	)


def get_feature(path, id):
	for f in find_feature_files(path):
		feature = parse_feature_xml(open(f, 'r'))
		if feature[0] == id:
			return feature[1:]
	raise KeyError("Feature {} was not found in {}".format(id, path))


def feature_include_graph(path):
	g = DiGraph()
	for f in find_feature_files('.'):
		id, features, plugins = parse_feature_xml(open(f, 'r'))
		node = "feature:"+id
		g.add_node(node)
		g.nodes[node]['file'] = f
		for plugin in plugins:
			g.add_edge(node, "plugin:"+plugin)
		for feature in features:
			g.add_edge(node, "feature:"+feature)
	return g
	

	
if __name__ == '__main__':
	for f in find_feature_files('.'):
		print(parse_feature_xml(open(f, 'r')))