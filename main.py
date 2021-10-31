from __future__ import annotations
from typing import List

import ssl
from urllib import request
import certifi
import ssl 
from bs4 import BeautifulSoup, element
import xml.etree.ElementTree as ET 
import numpy as np

class Parsable: 
    def parse(row : str) -> Parsable: raise NotImplementedError() 

class XMLWritable: 
    def write(self, root : ET.Element) -> ET.Element: raise NotImplementedError() 

class ParseHelper: 
    def parse_interval(row : str) -> ZInterval: 
        if 'free ride' in row: return ZFreeRide.parse(row) 
        if 'from' in row and 'to' in row: return ZRangedInterval.parse(row)
        if ',' in row: return ZIntervalsSet.parse(row)
        return ZInterval.parse(row)
    def parse_ftp_power(row : str):
        if not '%' in row: return row
        power, _ = row.split('%')
        return power 

class ZWorkoutFile: 
    def __init__(self, **kwargs) -> None:
        def get(key, default): return kwargs[key] if key in kwargs else default

        self.author = get('author', 'Zwift Parser')
        self.name = get('name', 'Zwift Workout')
        self.descr = get('descr', 'Parsed Zwift Workout')
        self.sport_type = get('sport_type', 'bike')
        self.tags = get('tags', '')
        pass

class ZWorkout(Parsable, XMLWritable): 
    def parse(rows : List[str]) -> ZWorkout: 
        return ZWorkout([ParseHelper.parse_interval(r) for r in rows])

    def __init__(self, intervals : List[ZInterval]) -> None:
        self.intervals = intervals
        
    def __repr__(self) -> str:
        intervals_str = [f'{i}' for i in self.intervals]
        return f"ZWorkout [{intervals_str}]"

    def write(self, root : ET.Element) -> ET.Element: 
        root = ET.Element("workout_file")

        pass 

class ZInterval(Parsable): 
    def parse(row : str) -> ZInterval:
        duration, power = [r.strip() for r in row.split('@')]
        return ZInterval(duration, ParseHelper.parse_ftp_power(power))

    def __init__(self, duration, power) -> None:
        self.duration = duration 
        self.power = power 

    def __repr__(self) -> str:
        return f'ZInterval(duration: {self.duration} power: {self.power}'

class ZRangedInterval(ZInterval): 
    def parse(row : str) -> ZRangedInterval: 
        duration, rest = row.split('from')
        from_power, to_power = [ParseHelper.parse_ftp_power(p) for p in rest.split('to')]
        return ZRangedInterval(duration, from_power, to_power)

    def __init__(self, duration, from_power, to_power) -> None:
        self.duration = duration 
        self.from_power = from_power 
        self.to_power = to_power 

    def __repr__(self) -> str:
        return f'ZRangedInterval (duration: {self.duration} from_power: {self.from_power} to_power: {self.to_power})'

class ZIntervalsSet(ZInterval): 
    def parse(row : str) -> ZIntervalsSet: 
        number, rest =  row.split('x')
        first_interval, second_interval = [ZInterval.parse(r) for r in rest.split(',')]
        return ZIntervalsSet(number, first_interval, second_interval)

    def __init__(self, number, first_interval : ZInterval, second_interval : ZInterval) -> None:
        self.number = number
        self.first_interval = first_interval 
        self.second_interval = second_interval 

    def __repr__(self) -> str:
        return f'ZIntervalSet ({self.number} x {self.first_interval}, {self.second_interval})'

class ZFreeRide(ZInterval): 
    def parse(row : str) -> ZFreeRide: 
        pass 

    def __init__(self, duration) -> None:
        self.duration = duration

    def __repr__(self) -> str:
        return f'ZFreeRide ({self.duration} free ride)'

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

#move to file 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Vivaldi/4.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

context = ssl.create_default_context(cafile=certifi.where())
req = request.Request(url, headers=headers)
response = request.urlopen(req, context=context)
content = response.read().decode('utf-8')
soup = BeautifulSoup(content, features='html.parser')

workout_data = soup.select_one('div.one-third.column.workoutlist')
pure_workout_data = purify_workout_data(workout_data) 
parsed_workout = ZWorkout.parse(pure_workout_data)
print(parsed_workout)

data = ET.Element("root")

with open("test.zwo", 'wb') as f: 
    f.write(ET.tostring(data))