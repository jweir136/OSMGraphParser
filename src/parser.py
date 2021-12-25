import re
import xml.etree.ElementTree
from tqdm import tqdm

class OSMGraphParser:
    def __init__(self, filename):
        self.roads = []
        self.nodes = {}
        self.VALID_ROADS = ["motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential"]
        buffer = ""

        with open(filename, "r") as f:
            for line in tqdm(f):
                buffer += line

                contains_way = self._contains_way(buffer)
                if contains_way:
                    buffer = ""
                    if self._is_valid_road(contains_way.group(0)):
                        self.roads.append(self._parse_way(contains_way.group(0)))

                contains_node = self._contains_node(buffer)
                if contains_node:
                    buffer = ""
                    node = self._parse_node(contains_node.group(0))
                    self.nodes[node['id']] = node


    def _contains_node(self, buffer):
        node_reg1 = re.compile(r'<node .*/>')
        node_reg2 = re.compile(r'<node [\s\S]*</node>')

        node_reg1_search = node_reg1.search(buffer)
        node_reg2_search = node_reg2.search(buffer)

        if node_reg1_search:
            return node_reg1_search
        elif node_reg2_search:
            return node_reg2_search
        else:
            return None

    def _parse_node(self, node):
        doc = xml.etree.ElementTree.fromstring(node)

        node = {}
        node['id'] = doc.attrib['id']
        node['visible'] = doc.attrib['visible']
        node['lon'] = doc.attrib['lon']
        node['lat'] = doc.attrib['lat']
        node['tags'] = {}

        for tag in doc.findall("tag"):
            node['tags'][tag.attrib['k']] = tag.attrib['v']

        return node
                
    def _contains_way(self, buffer):
        way_reg = re.compile(r'<way [\s\S]*</way>')
        return way_reg.search(buffer)

    def _is_valid_road(self, way):
        for road in self.VALID_ROADS:
            if road in way:
                return True
        return False

    def _parse_way(self, way):
        doc = xml.etree.ElementTree.fromstring(way)
        way_dict = dict(doc.attrib)
        way_dict['tags'] = {}
        for tag in doc.findall("tag"):
            way_dict['tags'][tag.attrib['k']] = tag.attrib['v']
        way_dict['nodes'] = [self.nodes[x.attrib['ref']] for x in doc.findall("nd")]
        return way_dict
    