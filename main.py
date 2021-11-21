from __future__ import annotations
from typing import List

from bs4 import BeautifulSoup, element
import xml.etree.ElementTree as ET 

class Parsable: 
    def parse(row : str) -> Parsable: raise NotImplementedError() 

class XMLWritable: 
    def write(self, root : ET.Element) -> ET.Element: raise NotImplementedError() 

class ParseHelper: 
    def parse_interval(row : str) -> ZSteadyState: 
        if 'free ride' in row: return ZFreeRide.parse(row) #10min free ride 
        if 'from' in row and 'to' in row: return ZRangedInterval.parse(row) #1min from 50 to 90% FTP
        if 'x' in row: return ZIntervalsT.parse(row) #10x 3min @ 100% FTP, 1min @ 55% FTP
        return ZSteadyState.parse(row) #3min @ 100rpmm, 95% FTP
    
    def parse_cadence(row: str) -> int:
        if 'rpm,' not in row: return -1, row 
        cadence, rest = row.split('rpm,')
        return int(cadence), rest 

    def parse_power(row: str) -> int:
        power = row 
        if '%' in power: power, _ = power.split('%')
        return float(power)/100

    def parse_duration(row: str) -> int: 
        seconds = 0 
        if 'hr' in row: 
            hr, row = row.split('hr') 
            seconds += int(hr) * 3600 
        if 'min' in row: 
            min, row = row.split('min')
            seconds += int(min) * 60 
        if 'sec' in row: 
            sec, _ = row.split('sec')
            seconds += int(sec)
        return seconds

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
            print(k,v)
            ET.SubElement(root, k).text = v
        tags = ET.SubElement(root, 'tags')
        for t in tags: 
            tag = ET.SubElement(tags, 'tag')
            tag.set('name', t)

        self.workout.write(root)
        return root 

class ZWorkout(Parsable, XMLWritable): 
    def parse(rows : List[str]) -> ZWorkout: 
        return ZWorkout([ParseHelper.parse_interval(r) for r in rows])

    def __init__(self, intervals : List[ZSteadyState]) -> None:
        self.intervals = intervals
        
    def __repr__(self) -> str:
        intervals_str = [f'{i}' for i in self.intervals]
        return f"ZWorkout [{intervals_str}]"

    def write(self, root : ET.Element) -> ET.Element: 
        workout = ET.SubElement(root, 'workout')
        for i in self.intervals: i.write(workout)
        return workout 

class ZSteadyState(Parsable, XMLWritable): 
    def parse(row : str) -> ZSteadyState:
        duration, row = [r.strip() for r in row.split('@')]
        duration = ParseHelper.parse_duration(duration)
        cadence, row = ParseHelper.parse_cadence(row)
        return ZSteadyState(duration, ParseHelper.parse_power(row), cadence)

    def __init__(self, duration, power, cadence = -1) -> None:
        self.duration = duration 
        self.power = power 
        self.cadence = cadence 

    def __repr__(self) -> str:
        return f'SteadyState (duration: {self.duration} power: {self.power} cadence: {self.cadence}'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'SteadyState')
        interval.set('Duration', str(self.duration))
        interval.set('Power', str(self.power))
        if self.cadence > 0: interval.set('Cadence', str(self.cadence))
        return interval 

class ZRangedInterval(ZSteadyState): 
    def parse(row : str) -> ZRangedInterval:                 
        duration, row = row.split('from')
        cadence = -1
        if '@' in duration: 
            duration, cadence = duration.split('@')
            cadence, _ = ParseHelper.parse_cadence(cadence)
        duration = ParseHelper.parse_duration(duration)

        from_power, to_power = [ParseHelper.parse_power(p) for p in row.split('to')]
        if from_power < to_power: return ZWarmup(duration, from_power, to_power, cadence)
        
        else: return ZCooldown(duration, from_power, to_power, cadence)

    def __init__(self, duration, from_power, to_power, cadence = -1) -> None:
        self.duration = duration 
        self.from_power = from_power 
        self.to_power = to_power 
        self.cadence = cadence

    def __repr__(self) -> str:
        return f'{self.get_name()} (duration: {self.duration} from_power: {self.from_power} to_power: {self.to_power} cadence: {self.cadence})'

    def get_name(self) -> str: 
        return "ZRangedInterval"

    def write(self, root: ET.Element) -> ET.Element:
        name = self.get_name()#'Warmup' if self.from_power < self.to_power else 'Cooldown'
        interval = ET.SubElement(root, name)
        interval.set('Duration', str(self.duration))
        interval.set('PowerLow', str(self.from_power))
        interval.set("PowerHigh", str(self.to_power))
        if self.cadence > 0: interval.set('Cadence', str(self.cadence))

class ZWarmup(ZRangedInterval): 
    def get_name(self) -> str:
        return "Warmup"

class ZCooldown(ZRangedInterval): 
    def get_name(self) -> str:
        return "Cooldown"

class ZIntervalsT(ZSteadyState): 
    def parse(row : str) -> ZIntervalsT: 
        number, rest =  row.split('x')
        first_interval, second_interval = [ZSteadyState.parse(r) for r in rest.split(',')]
        return ZIntervalsT(number, first_interval, second_interval)

    def __init__(self, number, first_interval : ZSteadyState, second_interval : ZSteadyState) -> None:
        self.number = number
        self.first_interval = first_interval 
        self.second_interval = second_interval 

    def __repr__(self) -> str:
        return f'IntervalT ({self.number} x {self.first_interval}, {self.second_interval})'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'IntervalsT')
        interval.set('Repeat', str(self.number))
        interval.set('OnDuration', str(self.first_interval.duration))
        interval.set('OffDuration', str(self.second_interval.duration))
        interval.set("OnPower", str(self.first_interval.power))
        interval.set('OffPower', str(self.second_interval.power))
        interval.set('Cadence', str(self.first_interval.cadence))
        interval.set("CadenceResting", str(self.second_interval.cadence))
        pass 

class ZFreeRide(ZSteadyState): 
    def parse(row : str) -> ZFreeRide: 
        duration, _ = row.split('free ride')
        cadence = -1
        if '@' in duration: 
            duration, cadence = duration.split("@")
            cadence = ParseHelper.parse_cadence(cadence)
        duration = ParseHelper.parse_duration(duration)
        return ZFreeRide(duration, cadence)
        
    def __init__(self, duration, cadence = -1, flat_road = 1) -> None:
        self.duration = duration
        self.cadence = cadence
        self.flat_road = flat_road

    def __repr__(self) -> str:
        return f'ZFreeRide (duration: {self.duration} cadence: {self.cadence})'

    def write(self, root: ET.Element) -> ET.Element:
        interval = ET.SubElement(root, 'FreeRide')
        interval.set('Duration', str(self.duration))
        interval.set('FlatRoad', str(self.flat_road))
        if self.cadence > 0: interval.set("Cadence", str(self.cadence))
        pass 

def parse_workout_row(row):
    #we need two variants of parsing, one for absolute watts and another one for FTP 
    #each workout item has such a format %N%x[Optional] %T%min @ %W% W/FTP
    #so our strategy should be splitting by @ first which will give us two pieces
    #1) We need to find and remove the time per interval, which is defined as %T%min, %T%sec and %T%hr 
    #   plus their combination, so it's possible to see something like 1hr 30min 10sec 
    #2) If we still have content in the left part we need to gather the intervals count, it's defined 
    #   as Nx, so it's relatively easy to parse it as well 
    #3) Then we need to parse the prescribed intensity, it can be easily done by searching for W or 
    #   FTP and deciding what values are we being provided with. (Optionally make it so we can force the 
    #   page to always show FTP, maybe it should always happen instead)
    #4) If instead of @ we have from ... to or free ride, we need to parse them according to this as well 
    #   so bascially the separators will be ['from', 'free ride', '@']        
    pass 

def purify_workout_data(data : element.Tag): 
    workout = []
    for row in data.find_all('div'):
        workout_set = [] 
        for content in row.contents: 
            if isinstance(content, element.Tag): workout_set.append("".join(content.contents)) 
            else: workout_set.append(content)
        workout.append("".join(workout_set))
    return workout

#move to params 
url = "https://whatsonzwift.com/workouts/gran-fondo/week-2-1-long-tempo-intervals"
# url = "https://whatsonzwift.com/workouts/mattias-thyr-unstructured-workouts/szrgwo-021-"
# url = "https://whatsonzwift.com/workouts/gcn-zero-to-hero-plan/week-1-initial-testing-7-sat-or-sun-free-ride"

#move to file 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Vivaldi/4.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

import ssl
from urllib import request
import certifi
context = ssl.create_default_context(cafile=certifi.where())
req = request.Request(url, headers=headers)
response = request.urlopen(req, context=context)
content = response.read().decode('utf-8')
soup = BeautifulSoup(content, features='html.parser')

breadcrumbs = [item.string.strip() for item in soup.select_one('div.breadcrumbs')] 
breadcrumbs = [item for item in breadcrumbs if len(item) > 0 and item != '»' and item != 'Workouts']
filename = breadcrumbs.pop(-1)
directory = 'export/' + '/'.join(breadcrumbs)

workout_data = soup.select_one('div.one-third.column.workoutlist')
pure_workout_data = purify_workout_data(workout_data) 
parsed_workout = ZWorkout.parse(pure_workout_data)

workout_overview = soup.select_one('div.overview')
workout_author = 'Zwift Workouts Parser'
workout_desc = workout_overview.next_sibling
if 'Author' in workout_overview.next_sibling.string:
    workout_author = workout_overview.next_sibling
    workout_desc = workout_author.next_sibling

if not isinstance(workout_author, str) and 'Author' in workout_author.string: 
    _, workout_author = workout_author.string.split('Author:')
workout_desc = workout_desc.get_text("\n")

workout_file = ZWorkoutFile(parsed_workout, 
                            name=filename, author=workout_author.strip(), description=workout_desc) 
data = workout_file.write()
text = ET.tostring(data)
xml_header = b'<?xml version="1.0" encoding="utf-8"?>'
pretty_text = BeautifulSoup(text, 'xml').prettify().encode('utf-8')
pretty_text = pretty_text.replace(xml_header, b'').strip()

from os import path, makedirs
if not path.isdir(directory): makedirs(directory)

from utility import slugify
with open(f"{directory}/{slugify(filename, True)}.zwo", 'wb') as f: 
    f.write(pretty_text)