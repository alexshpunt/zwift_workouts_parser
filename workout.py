from __future__ import annotations
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, element
from intervals import * 
from typing import List
import helper as Helper 
from intervals import * 

class ZWorkoutFile(): 
    def __init__(self, article: element.Tag) -> None:
        self.directory, self.filename = (None, None)
        breadcrumbs = article.select_one('div.breadcrumbs')
        sport_type = breadcrumbs.find('h4')['class']

        self.valid = Helper.is_valid_sport_type(sport_type)
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
            interval = "".join([Helper.convert_to_string(c) for c in div.contents]) 
            self.intervals.append(ZWorkoutFile.parse_interval(interval))

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

        directory = f"{export_dir}/{Helper.slugify(self.directory)}"

        from os import path, makedirs
        if not path.isdir(directory): makedirs(directory)

        with open(f"{directory}/{Helper.slugify(self.filename, True)}.zwo", 'wb') as f: 
            f.write(text)

        print(f"--- Parsed workout {self.directory}/{self.filename}")

    def parse_interval(row: str): 
        if 'free ride' in row: return ZFreeRide(row) #10min free ride 
        if 'from' in row and 'to' in row: return ZRangedInterval(row) #1min from 50 to 90% FTP
        if 'x' in row: return ZIntervalsT(row) #10x 3min @ 100% FTP, 1min @ 55% FTP
        return ZSteadyState(row) #3min @ 100rpmm, 95% FTP