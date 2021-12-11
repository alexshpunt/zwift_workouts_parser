from typing import List
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, element
from zwift_intervals import * 

class ZWorkout(): 
    def is_valid_sport_type(class_values: List[str]):
        """Checks if workout's sport type is supported by the parser

        At the moment the parser supports only the bike workouts, 
        so this function checks if there is a bike type in the sport 
        types.

        Parameters 
        ----------
        class_values : List[str]
                    A list of the class values on the workout's html page         
        """
        return len([s for s in class_values if 'bike' in s]) > 0

    def __init__(self, article: element.Tag) -> None:
        self.directory, self.filename = (None, None)
        breadcrumbs = article.select_one('div.breadcrumbs')
        sport_type = breadcrumbs.find('h4')['class']

        self.valid = ZWorkout.is_valid_sport_type(sport_type)
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

        def convert_to_string(data):
            output = [] 
            if isinstance(data, element.NavigableString): return data.string
            for content in data.contents:
                if isinstance(content, str): output.append(content)
                else: output.extend([convert_to_string(c) for c in content.contents])
            return "".join(output)

        self.intervals = [] 
        data = article.select_one('div.one-third.column.workoutlist')
        for div in data.find_all('div'):
            interval = "".join([convert_to_string(c) for c in div.contents]) 
            self.intervals.append(ZWorkout.parse_interval(interval))

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

        directory = f"{export_dir}/{slugify(self.directory)}"

        from os import path, makedirs
        if not path.isdir(directory): makedirs(directory)

        with open(f"{directory}/{slugify(self.filename, True)}.zwo", 'wb') as f: 
            f.write(text)

        print(f"-- Parsed workout {self.directory}/{self.filename}")

    def parse_interval(row: str): 
        if 'free ride' in row: return ZFreeRide(row) #10min free ride 
        if 'from' in row and 'to' in row: return ZRangedInterval(row) #1min from 50 to 90% FTP
        if 'x' in row: return ZIntervalsT(row) #10x 3min @ 100% FTP, 1min @ 55% FTP
        return ZSteadyState(row) #3min @ 100rpmm, 95% FTP

import unicodedata
import re
def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')