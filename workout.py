from __future__ import annotations
import xml.etree.ElementTree as ET
from interfaces import * 
from intervals import * 

class ZWorkoutFile(XMLWritable): 
    def __init__(self, workout : ZWorkout, **kwargs) -> None:
        def get(key, default): return kwargs[key] if key in kwargs else default

        self.workout = workout 
        self.author = get('author', 'Zwift Parser')
        self.name = get('name', 'Zwift Workout')
        self.description = get('description', 'Parsed Zwift Workout')
        self.sport_type = get('sport_type', 'bike')
        self.tags = get('tags', '')
        self.lookup = {
            'author': self.author,
            'name': self.name,
            'description': self.description,
            'sport_type': self.sport_type,
        }

    def __getitem__(self, key): return self.lookup[key]

    def write(self, root : ET.Element = None) -> ET.Element:
        root = ET.Element('workout_file')
        for k,v in self.lookup.items(): 
            ET.SubElement(root, k).text = v
        tags = ET.SubElement(root, 'tags')
        for t in tags: 
            tag = ET.SubElement(tags, 'tag')
            tag.set('name', t)

        self.workout.write(root)
        return root 

class ZWorkout(Parsable, XMLWritable): 
    def parse(rows : List[str]) -> ZWorkout: 
        return ZWorkout([ZInterval.parse(r) for r in rows])

    def __init__(self, intervals : List[ZSteadyState]) -> None:
        self.intervals = intervals
        
    def __repr__(self) -> str:
        intervals_str = [f'{i}' for i in self.intervals]
        return f"ZWorkout [{intervals_str}]"

    def write(self, root : ET.Element) -> ET.Element: 
        workout = ET.SubElement(root, 'workout')
        for i in self.intervals: i.write(workout)
        return workout 
