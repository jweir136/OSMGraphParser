import re
import xml.etree.ElementTree
from tqdm import tqdm

class OSMGraphParser:
    def __init__(self, filename):
        self.roads = []
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
        way_dict['nodes'] = [x.attrib['ref'] for x in doc.findall("nd")]
        return way_dict

if __name__ == "__main__":
    print(OSMGraphParser("test-data/map-2.osm").roads)
    