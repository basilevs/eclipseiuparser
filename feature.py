#!/bin/python3

from xml.etree import ElementTree
from xml.etree.ElementTree import XMLParser
from re import compile
from uuid import uuid1
from os.path import dirname, abspath, join
from pathlib import Path
from networkx import DiGraph



def find_feature_files(path):
	return Path(path).rglob("feature.xml")
	
def find_product_files(path):
	return Path(path).rglob("*.product")


def parse_feature_xml(file):
	tree = ElementTree.parse(file)
	return (
		tree.getroot().attrib['id'],
		[node.attrib['id'] for node in tree.findall("includes") or []],
		[node.attrib['id'] for node in tree.findall("plugin") or []]
	)

def read_manifest_lines(file):
	result = ""
	for line in file.readlines():
		if line and line.startswith(" "):
			result += line.rstrip("\r\n")
		else:
			yield result
			result = line.rstrip("\r\n")
	
#Bundle-SymbolicName: com.spirent.itest.applications.sf.agent.runtime;singleton:=true
_bundleIdPattern = compile(r'Bundle-SymbolicName:\s*([^;=:]+).*')
#Require-Bundle: org.eclipse.core.runtime, com.google.guava, com.fnfr.open.common, com.fnfr.open.runtime.activation, org.apache.commons.lang;bundle-version="2.6.0"
_requirePattern = compile(r'Require-Bundle:\s*(.*)')


class UnsupportedFormat(Exception) :
	pass 


def parse_manifest(file):
	id1 = None
	require = []	
	for line in read_manifest_lines(file):
		m = _bundleIdPattern.match(line)
		if m:
			id1 = m.group(1)
			continue
		m = _requirePattern.match(line)
		if m:
			require.extend(parse_require(m.group(1)))
	if not id1:
		raise UnsupportedFormat("No Bundle-SymbolicName")
	return (id1, require)


#org.eclipse.core.runtime, com.google.guava, com.fnfr.open.common, com.fnfr.open.runtime.activation, org.apache.commons.lang;bundle-version="2.6.0"
_idPattern = compile(r'\s*([a-z\\.]+)(?:;.*)?')
def parse_require(line):
	result = []
	for entry in line.split(", "):
		m = _idPattern.match(entry)
		if not m:
			raise ValueError("Can parse Require-Bundle: " + entry + ".")
		result.append(m.group(1))
	return result
			

def parse_product_xml(file):
	tree = ElementTree.parse(file)
	return (
		tree.getroot().attrib['id'],
		[node.attrib['id'] for node in tree.findall("features/feature") or []],
		[node.attrib['id'] for node in tree.findall("plugins/plugin") or []]
	)

def get_feature(path, id):
	for f in find_feature_files(path):
		feature = parse_feature_xml(open(f, 'r'))
		if feature[0] == id:
			return feature[1:]
	raise KeyError("Feature {} was not found in {}".format(id, path))


def include_graph(path):
	g = DiGraph()
	def add_children(node, features, plugins, file):
		g.add_node(node)
		g.nodes[node]['file'] = file
		for plugin in plugins:
			g.add_edge(node, "plugin:"+plugin)
		for feature in features:
			g.add_edge(node, "feature:"+feature)
	for f in find_feature_files('.'):
		id, features, plugins = parse_feature_xml(open(f, 'r'))
		node = "feature:"+id
		add_children(node, features, plugins, f)
	for f in find_product_files('.'):
		id, features, plugins = parse_product_xml(open(f, 'r'))
		node = 'product:'+id
		add_children(node, features, plugins, f)
	for f in Path(path).rglob("MANIFEST.MF"):
		try:
			id, plugins = parse_manifest(open(f, 'r'))
			node = 'plugin:'+id
			add_children(node, [], plugins, f)
		except UnsupportedFormat:
			print('Failed to parse', f)
		except:
			raise ValueError('Failed to parse ' + str(f))
	return g


def find_node_by_id(g, id):
	result = [p+id for p in ['', 'plugin:', 'feature:', 'product:'] if g.has_node(p+id)]
	if len(result) > 1:
		raise KeyError("Multiple elements found: " + result)
	if not result: 
		raise KeyError("Can't find " + id)
	return result[0] 


def print_sorted(data):
	for line in sorted(data):
		print(line)


if __name__ == '__main__':
	for f in find_feature_files('.'):
		print(parse_feature_xml(open(f, 'r')))