from __future__ import annotations
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, element
from interfaces import * 
from intervals import * 
from typing import List
from parse_helper import ParseHelper

class ZWorkoutFile(XMLWritable, Parsable): 
    def __init__(self, article: element.Tag) -> None:
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

    def purify_workout_data(data : element.Tag): 
        workout = []
        for row in data.find_all('div'):
            workout_set = [ParseHelper.convert_to_string(c) for c in row.contents] 
            workout.append("".join(workout_set))
        return workout

    def parse(article: element.Tag, filename: str) -> Parsable:
        workout_data = article.select_one('div.one-third.column.workoutlist')
        pure_workout_data = ParseHelper.purify_workout_data(workout_data) 

        from workout import ZWorkout, ZWorkoutFile
        parsed_workout = ZWorkout.parse(pure_workout_data)

        workout_overview = article.select_one('div.overview')
        workout_author = 'Zwift Workouts Parser'
        workout_desc = workout_overview.next_sibling
        if 'Author:' in workout_overview.next_sibling.get_text():
            workout_author = workout_overview.next_sibling
            workout_desc = workout_author.next_sibling

        if not isinstance(workout_author, str) and 'Author:' in workout_author.get_text(): 
            _, workout_author = workout_author.get_text().split('Author:')
        workout_desc = workout_desc.get_text("\n")

        workout_file = ZWorkoutFile(parsed_workout, 
                                    name=filename, author=workout_author.strip(), description=workout_desc) 

        data = workout_file.write()
        import xml.etree.ElementTree as ET
        text = ET.tostring(data)
        xml_header = b'<?xml version="1.0" encoding="utf-8"?>'
        text = BeautifulSoup(text, 'xml').prettify().encode('utf-8')
        text = text.replace(xml_header, b'').strip()
        
        return text

    def __getitem__(self, key): return self.lookup[key]

    def write(self, root : ET.Element = None) -> ET.Element:
        root = ET.Element('workout_file')
        for k,v in self.lookup.items(): 
            ET.SubElement(root, k).text = v
        tags = ET.SubElement(root, 'tags')
        for t in tags: 
            tag = ET.SubElement(tags, 'tag')
            tag.set('name', t)

        self.intervals.write(root)
        return root 

class ZWorkout(Parsable, XMLWritable): 
    def parse(rows : List[str]) -> ZWorkout: 
        return ZWorkout([ZInterval.parse(r) for r in rows])

    def __init__(self, rows: List[str]) -> None:
        super().__init__()

    def __init__(self, intervals : List[ZSteadyState]) -> None:
        self.intervals = intervals
        
    def __repr__(self) -> str:
        intervals_str = [f'{i}' for i in self.intervals]
        return f"ZWorkout [{intervals_str}]"

    def write(self, root : ET.Element) -> ET.Element: 
        workout = ET.SubElement(root, 'workout')
        for i in self.intervals: i.write(workout)
        return workout 
