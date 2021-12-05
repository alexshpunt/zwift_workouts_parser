from __future__ import annotations
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, element
from interfaces import * 
from intervals import * 
from typing import List
from parse_helper import ParseHelper
from parsersettings import ParserSettings

class ZWorkoutFile(XMLWritable, Parsable): 
    def __init__(self, article: element.Tag) -> None:
        self.directory, self.filename = (None, None)
        breadcrumbs = article.select_one('div.breadcrumbs')
        sport_type = breadcrumbs.find('h4')['class']

        self.valid = ParserSettings.is_valid_sport_type(sport_type)
        if not self.valid: return 
        
        try: 
            breadcrumbs = [item.string.strip() for item in breadcrumbs] 
        except Exception as e: 
            #Sometimes if @ is contained in the breadcrumbs, it might be obfuscated with Cloudflare, so 
            # it's not really possible to deobfuscate it back. This is why we just ignore it.  
            self.valid = False
            return 

        breadcrumbs = [b for b in breadcrumbs if len(b) > 0 and b != '»' and b != 'Workouts']
        self.filename = breadcrumbs.pop(-1)
        self.directory = '/'.join(breadcrumbs)

        self.intervals = [] 
        data = article.select_one('div.one-third.column.workoutlist')
        for div in data.find_all('div'):
            interval = "".join([ParseHelper.convert_to_string(c) for c in div.contents]) 
            self.intervals.append(ZInterval.parse(interval))

        overview = article.select_one('div.overview')
        self.author = 'Zwift Workouts Parser'
        self.description = overview.next_sibling
        if 'Author:' in overview.next_sibling.get_text():
            self.author = overview.next_sibling
            self.description = self.author.next_sibling

        if not isinstance(self.author, str) and 'Author:' in self.author.get_text(): 
            _, self.author = self.author.get_text().split('Author:')
        self.description = self.description.get_text("\n")

        self.name = 'Zwift Workout'
        self.sport_type = 'bike' 
        self.lookup = {
            'author': self.author,
            'name': self.name,
            'description': self.description,
            'sport_type': self.sport_type,
        }

    def to_xml(self, root : ET.Element = None) -> ET.Element:
        root = ET.Element('workout_file')
        for k,v in self.lookup.items(): 
            ET.SubElement(root, k).text = v
        tags = ET.SubElement(root, 'tags')
        for t in tags: 
            tag = ET.SubElement(tags, 'tag')
            tag.set('name', t)

        workout = ET.SubElement(root, 'workout')
        for i in self.intervals: i.write(workout)
        return root 

    def save(self, export_dir: str): 
        if not self.valid: return

        data = self.to_xml() 
        import xml.etree.ElementTree as ET
        text = ET.tostring(data)
        xml_header = b'<?xml version="1.0" encoding="utf-8"?>'
        text = BeautifulSoup(text, 'xml').prettify().encode('utf-8')
        text = text.replace(xml_header, b'').strip()

        from utility import slugify
        directory = f"{export_dir}/{slugify(self.directory)}"

        from os import path, makedirs
        if not path.isdir(directory): makedirs(directory)

        with open(f"{directory}/{slugify(self.filename, True)}.zwo", 'wb') as f: 
            f.write(text)

        print(f"--- Parsed workout {self.directory}/{self.filename}")