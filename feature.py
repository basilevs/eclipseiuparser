#!/bin/python3
from functools import partial
from io import TextIOWrapper
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, XMLParser
from re import compile
from uuid import uuid1
from os.path import dirname, abspath, join
from pathlib import Path
from zipfile import ZipFile
from networkx import DiGraph # python3 -m pip install networkx  


def _feature_import_to_id(node: Element):
	try:
		return 'feature:'+node.attrib['feature']
	except KeyError:
		return 'plugin:'+node.attrib['plugin']

def parse_feature_xml(file):
	tree = ElementTree.parse(file)
	id = tree.getroot().attrib['id']
	return (
		'feature:' + id,
		[node.attrib['id'] for node in tree.findall("plugin") or []],
		[node.attrib['id'] for node in tree.findall("includes") or []],
		#  <import feature="org.eclipse.ecf.core.feature" version="1.4.0" match="compatible"/>
		[_feature_import_to_id(node) for node in tree.findall("requires/import") or []],
	)

def read_manifest_lines(file):
	file = TextIOWrapper(file, encoding='utf-8')
	result = ""
	for line in file.readlines():
		if line and line.startswith(" "):
			result += line.rstrip("\r\n").lstrip(' ')
		else:
			yield result
			result = line.rstrip("\r\n")
	
#Bundle-SymbolicName: com.spirent.itest.applications.sf.agent.runtime;singleton:=true
_bundleIdPattern = compile(r'Bundle-SymbolicName:\s*([^;=:]+).*')
#Require-Bundle: org.eclipse.core.runtime, com.google.guava, com.fnfr.open.common, com.fnfr.open.runtime.activation, org.apache.commons.lang;bundle-version="2.6.0"
_requirePattern = compile(r'Require-Bundle:\s*(.*)')


class UnsupportedFormat(Exception) :
	pass 


def parse_manifest(file, include_optional: bool):
	id1 = None
	require = []	
	for line in read_manifest_lines(file):
		m = _bundleIdPattern.match(line)
		if m:
			id1 = m.group(1)
			continue
		m = _requirePattern.match(line)
		if m:
			require.extend(['plugin:' + id for id in parse_require(m.group(1), include_optional)])
	if not id1:
		raise UnsupportedFormat("No Bundle-SymbolicName")
	return ('plugin:' + id1, [], [], require)

def split_by_comma(input_string):
    current = []
    in_quotes = False
    for char in input_string:
        if char == '"':
            in_quotes = not in_quotes
            current.append(char)
        elif char == ',' and not in_quotes:
            yield ''.join(current)
            current = []
        else:
            current.append(char)
    yield ''.join(current)

#org.eclipse.core.runtime, com.google.guava, com.fnfr.open.common, com.fnfr.open.runtime.activation, org.apache.commons.lang;bundle-version="2.6.0"
_idPattern = compile(r'\s*([A-Za-z\\.]+)(?:;.*)?')
def parse_require(line, include_optional: bool):
	result = []
	for entry in split_by_comma(line):
		m = _idPattern.match(entry)
		if not m:
			raise ValueError("Can parse Require-Bundle: " + entry + ".")
		if not include_optional and ';resolution:=optional' in entry:
			continue
		result.append(m.group(1))
	return result
			

def parse_product_xml(file):
	tree = ElementTree.parse(file)
	return (
		'product:' + tree.getroot().attrib['uid'],
		[node.attrib['id'] for node in tree.findall("plugins/plugin") or []],
		[node.attrib['id'] for node in tree.findall("features/feature") or []],
		[]
	)

def parse_jar(file, include_optional: bool):
	with ZipFile(file) as zip:
		try:
			with zip.open('feature.xml') as feature:
				return parse_feature_xml(feature)
		except KeyError:
			pass
		try:
			with zip.open('META-INF/MANIFEST.MF') as manifest:
				return parse_manifest(manifest, include_optional)
		except KeyError:
			pass
	raise UnsupportedFormat()

def is_derived_file(path: Path):
	# Do not use temporary copies produced by previous builds
	# Like ./product/com.spirent.product.ndo/target/products/com.spirent.ndo.cli.OptimizedAgentProduct/win32/win32/x86_64/nda/features/com.spirent.features.resources-lite_9.4.0.202306021011/feature.xml
	for i in path.parents:
		if i.name in ["resources", "testData", "target", "tests", "testdata"]:
			return True
	if path.parent.joinpath('.project').exists():
		return False
	return False

def include_graph(path, include_dependencies=True, include_optional=False):
	g = DiGraph()
	def process_glob(globexpression, parser):
		for f in Path(path).rglob(globexpression):
			if is_derived_file(f):
				continue
			if f.is_dir():
				continue
			try:
				id, plugins, features, dependencies = parser(open(f, 'rb'))
				node = id
				g.add_node(node)
				g.nodes[node]['file'] = f
				for plugin in plugins:
					g.add_edge(node, "plugin:"+plugin)
				for feature in features:
					g.add_edge(node, "feature:"+feature)
				if include_dependencies:
					for dep in dependencies:
						g.add_edge(node, dep)
			except UnsupportedFormat:
				pass
			except:
				raise ValueError('Failed to parse ' + str(f))
	process_glob('feature.xml', parse_feature_xml)
	process_glob('*.product', parse_product_xml)
	process_glob('META-INF/MANIFEST.MF', lambda f: parse_manifest(f, include_optional))
	process_glob('features/*.jar', lambda f: parse_jar(f, include_optional))
	process_glob('plugins/*.jar', lambda f: parse_jar(f, include_optional))
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
