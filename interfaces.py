from __future__ import annotations
import xml.etree.ElementTree as ET 
from typing import List

class Parsable: 
    def parse(row : str) -> Parsable: raise NotImplementedError() 

class XMLWritable: 
    def write(self, root : ET.Element) -> ET.Element: raise NotImplementedError() 
