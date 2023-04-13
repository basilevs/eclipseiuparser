#!/bin/python3

from xml.etree import ElementTree
from xml.etree.ElementTree import XMLParser
from re import compile
from uuid import uuid1
from os.path import dirname, abspath, join
from pathlib import Path
from networkx import DiGraph



def parse_feature_xml(file):
	tree = ElementTree.parse(file)
	return (
		tree.getroot().attrib['id'],
		[node.attrib['id'] for node in tree.findall("plugin") or []],
		[node.attrib['id'] for node in tree.findall("includes") or []],
		[]
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
	return (id1, [], [], require)


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
		[node.attrib['id'] for node in tree.findall("plugins/plugin") or []],
		[node.attrib['id'] for node in tree.findall("features/feature") or []],
		[]
	)


def include_graph(path, include_dependencies=True):
	g = DiGraph()
	def process_glob(path, globexpression, parser, prefix):
		for f in Path(path).rglob(globexpression):
			try:
				id, plugins, features, plugin_dependencies = parser(open(f, 'r'))
				node = prefix+":"+id
				if include_dependencies:
					plugins = plugins + plugin_dependencies
				g.add_node(node)
				g.nodes[node]['file'] = f
				for plugin in plugins:
					g.add_edge(node, "plugin:"+plugin)
				for feature in features:
					g.add_edge(node, "feature:"+feature)
			except UnsupportedFormat:
				pass
			except:
				raise ValueError('Failed to parse ' + str(f))
	process_glob(path, 'feature.xml', parse_feature_xml, 'feature')
	process_glob(path, '*.product', parse_product_xml, 'product')
	process_glob(path, 'META-INF/MANIFEST.MF', parse_manifest, 'plugin')
	return g


def find_node_by_id(g, id):
	result = [p+id for p in ['', 'plugin:', 'feature:', 'product:'] if g.has_node(p+id)]
	if len(result) > 1:
		raise KeyError("Multiple elements found: " + str(result))
	if not result: 
		raise KeyError("Can't find " + id)
	return result[0] 


def print_sorted(data):
	for line in sorted(data):
		print(line)

def print_sorted_with_meta(graph, nodes):
	for node in sorted(nodes):
		print (node, '\t', graph.nodes[node]['file'])


if __name__ == '__main__':
	for f in find_feature_files('.'):
		print(parse_feature_xml(open(f, 'r')))
